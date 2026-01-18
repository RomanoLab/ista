"""
Load NeuroKB RDF Ontology into Memgraph

This script loads an instantiated RDF ontology (like neurokb-with-all-drug-relationships.rdf)
directly into Memgraph by parsing the RDF/XML file.

It bypasses the ista OWL2 parser (which doesn't load individuals properly) and instead
parses the RDF/XML directly using Python's xml.etree.ElementTree.

Mapping:
    - RDF individuals → Memgraph nodes
    - rdf:type → Node labels
    - Data properties → Node properties
    - Object properties → Relationships

Prerequisites:
    - Memgraph running: docker run -p 7687:7687 -p 7444:7444 memgraph/memgraph-platform
    - neo4j driver: pip install neo4j

Usage:
    python load_neurokb_to_memgraph.py
"""

import xml.etree.ElementTree as ET
from neo4j import GraphDatabase
from collections import defaultdict
from typing import Dict, List, Set, Tuple
import re
import time

# RDF and OWL namespaces
NS = {
    'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
    'rdfs': 'http://www.w3.org/2000/01/rdf-schema#',
    'owl': 'http://www.w3.org/2002/07/owl#',
    'xsd': 'http://www.w3.org/2001/XMLSchema#',
}


class RDFMemgraphLoader:
    """Loader for RDF/XML ontology files into Memgraph."""

    def __init__(self, uri="bolt://localhost:7687", username="", password=""):
        """
        Initialize loader.

        Args:
            uri: Memgraph Bolt URI
            username: Username (empty for Memgraph default)
            password: Password (empty for Memgraph default)
        """
        self.uri = uri
        self.driver = GraphDatabase.driver(
            uri, auth=(username, password) if username else None
        )

    def test_connection(self) -> bool:
        """
        Test if the database connection is working.

        Returns:
            True if connection successful, False otherwise
        """
        import sys
        import os
        try:
            # Temporarily suppress stderr to hide connection error messages
            old_stderr = sys.stderr
            sys.stderr = open(os.devnull, 'w')

            try:
                with self.driver.session() as session:
                    session.run("RETURN 1")
                return True
            finally:
                sys.stderr.close()
                sys.stderr = old_stderr
        except Exception:
            return False

    def close(self):
        """Close database connection."""
        if self.driver:
            self.driver.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def clear_database(self):
        """Clear all data from Memgraph."""
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
        print("  Database cleared")

    def create_indexes(self):
        """Create indexes for performance."""
        with self.driver.session() as session:
            try:
                session.run("CREATE INDEX ON :Individual(iri)")
                print("  Created index on Individual(iri)")
            except Exception as e:
                print(f"  Index creation note: {e}")

    def _extract_fragment(self, iri: str) -> str:
        """Extract the fragment identifier from an IRI."""
        if '#' in iri:
            return iri.split('#')[-1]
        elif '/' in iri:
            return iri.split('/')[-1]
        return iri

    def _sanitize_label(self, label: str) -> str:
        """Make a label safe for use in Cypher."""
        # Replace invalid characters with underscore
        sanitized = re.sub(r'[^a-zA-Z0-9_]', '_', label)
        # Ensure starts with letter
        if sanitized and not sanitized[0].isalpha():
            sanitized = 'N_' + sanitized
        return sanitized or 'Node'

    def parse_rdf_file(self, rdf_file: str) -> Tuple[Dict, List]:
        """
        Parse RDF/XML file to extract individuals and relationships.

        Args:
            rdf_file: Path to RDF/XML file

        Returns:
            Tuple of (individuals dict, relationships list)
        """
        print(f"\nParsing RDF file: {rdf_file}")
        start_time = time.time()

        tree = ET.parse(rdf_file)
        root = tree.getroot()

        # Storage
        individuals = {}  # iri -> {types: set, properties: dict}
        relationships = []  # list of (source_iri, property, target_iri)

        # Get ontology base namespace
        ont_elem = root.find('owl:Ontology', NS)
        base_namespace = ont_elem.get('{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about', '') if ont_elem is not None else ''
        if base_namespace and not base_namespace.endswith('#'):
            base_namespace += '#'

        print(f"  Base namespace: {base_namespace}")

        # Find all individuals (elements with rdf:about that aren't Ontology/Class/ObjectProperty)
        skip_types = {'Ontology', 'Class', 'ObjectProperty', 'DataProperty', 'AnnotationProperty'}

        for elem in root:
            # Get the element's tag (without namespace)
            tag = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag

            # Skip ontology metadata elements
            if tag in skip_types:
                continue

            # Get IRI from rdf:about
            iri = elem.get('{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about')
            if not iri:
                continue

            # Convert relative IRI (#drug_db00001) to absolute
            if iri.startswith('#'):
                iri = base_namespace.rstrip('#') + iri

            # Initialize individual if not seen
            if iri not in individuals:
                individuals[iri] = {
                    'types': set(),
                    'properties': {},
                    'label': self._extract_fragment(iri)
                }

            # Add the element tag as a type (e.g., "Drug", "Disease")
            if tag not in ['NamedIndividual', 'Description']:
                individuals[iri]['types'].add(tag)

            # Process child elements (properties)
            for child in elem:
                child_tag = child.tag.split('}')[-1] if '}' in child.tag else child.tag

                # Check for rdf:type (class assertion)
                if child_tag == 'type':
                    type_iri = child.get('{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource', '')
                    if type_iri:
                        type_name = self._extract_fragment(type_iri)
                        if type_name and type_name != 'NamedIndividual':
                            individuals[iri]['types'].add(type_name)

                # Check for object property (rdf:resource)
                elif '{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource' in child.attrib:
                    target_iri = child.get('{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource')

                    # Convert relative IRI
                    if target_iri.startswith('#'):
                        target_iri = base_namespace.rstrip('#') + target_iri

                    relationships.append((iri, child_tag, target_iri))

                # Check for data property (text content or datatype)
                elif child.text:
                    prop_name = child_tag
                    prop_value = child.text.strip()

                    # Try to convert to appropriate Python type
                    datatype = child.get('{http://www.w3.org/1999/02/22-rdf-syntax-ns#}datatype', '')
                    if 'integer' in datatype or 'int' in datatype:
                        try:
                            prop_value = int(prop_value)
                        except ValueError:
                            pass
                    elif 'float' in datatype or 'double' in datatype or 'decimal' in datatype:
                        try:
                            prop_value = float(prop_value)
                        except ValueError:
                            pass
                    elif 'boolean' in datatype:
                        prop_value = prop_value.lower() in ('true', '1', 'yes')

                    individuals[iri]['properties'][prop_name] = prop_value

        elapsed = time.time() - start_time
        print(f"  Parsed {len(individuals):,} individuals")
        print(f"  Parsed {len(relationships):,} relationships")
        print(f"  Time: {elapsed:.2f}s")

        return individuals, relationships

    def load_individuals(self, individuals: Dict, batch_size: int = 1000):
        """Load individuals as nodes into Memgraph."""
        print(f"\nLoading {len(individuals):,} individuals as nodes...")
        start_time = time.time()

        individual_list = list(individuals.items())
        total = len(individual_list)

        with self.driver.session() as session:
            for i in range(0, total, batch_size):
                batch = individual_list[i:i + batch_size]

                for iri, data in batch:
                    # Build labels
                    labels = ['Individual']
                    for type_name in data['types']:
                        labels.append(self._sanitize_label(type_name))

                    # If no specific types, use generic
                    if len(labels) == 1:
                        labels.append('Entity')

                    label_str = ':'.join(labels)

                    # Build properties
                    props = {
                        'iri': iri,
                        'name': data['label'],
                        **data['properties']
                    }

                    # Create node
                    query = f"CREATE (n:{label_str}) SET n = $props"
                    session.run(query, props=props)

                if (i + batch_size) % 10000 == 0 or i + batch_size >= total:
                    print(f"  Loaded {min(i + batch_size, total):,}/{total:,} nodes")

        elapsed = time.time() - start_time
        print(f"  Time: {elapsed:.2f}s")
        print(f"  Rate: {total / elapsed:.0f} nodes/sec")

    def load_relationships(self, relationships: List, batch_size: int = 1000):
        """Load relationships (object properties) into Memgraph."""
        print(f"\nLoading {len(relationships):,} relationships...")
        start_time = time.time()

        total = len(relationships)
        errors = 0

        with self.driver.session() as session:
            for i in range(0, total, batch_size):
                batch = relationships[i:i + batch_size]

                try:
                    # Use a transaction for the batch
                    tx = session.begin_transaction()
                    try:
                        for source_iri, prop_name, target_iri in batch:
                            # Sanitize relationship type
                            rel_type = self._sanitize_label(prop_name)

                            # Create relationship - skip if nodes don't exist
                            query = f"""
                            MATCH (a:Individual {{iri: $source}})
                            MATCH (b:Individual {{iri: $target}})
                            CREATE (a)-[:{rel_type}]->(b)
                            """

                            try:
                                tx.run(query, source=source_iri, target=target_iri)
                            except Exception as e:
                                errors += 1
                                if errors <= 10:  # Only print first 10 errors
                                    print(f"  Warning: Failed to create relationship {source_iri} -> {target_iri}: {e}")

                        tx.commit()
                    except Exception as e:
                        tx.rollback()
                        print(f"  Error in batch at {i}: {e}")
                        errors += len(batch)
                except Exception as e:
                    print(f"  Error starting transaction at {i}: {e}")
                    errors += len(batch)

                if (i + batch_size) % 50000 == 0 or i + batch_size >= total:
                    print(f"  Loaded {min(i + batch_size, total):,}/{total:,} relationships (errors: {errors})")

        elapsed = time.time() - start_time
        print(f"  Time: {elapsed:.2f}s")
        if total - errors > 0:
            print(f"  Rate: {(total - errors) / elapsed:.0f} relationships/sec")
        if errors > 0:
            print(f"  Total errors: {errors:,}")

    def cleanup_owl_labels(self):
        """Remove OWL standard labels and delete nodes with no meaningful labels."""
        print("\nCleaning up OWL standard labels...")
        start_time = time.time()

        owl_labels = ['DatatypeProperty', 'FunctionalProperty', 'Entity', 'Individual']

        with self.driver.session() as session:
            # Remove each OWL standard label from all nodes
            for label in owl_labels:
                try:
                    query = f"MATCH (n:{label}) REMOVE n:{label}"
                    result = session.run(query)
                    result.consume()
                    print(f"  Removed :{label} labels from nodes")
                except Exception as e:
                    print(f"  Warning: Failed to remove :{label} labels: {e}")

            # Delete nodes that have no labels remaining
            try:
                # First, count how many nodes will be deleted
                count_query = "MATCH (n) WHERE size(labels(n)) = 0 RETURN count(n) as count"
                result = session.run(count_query)
                delete_count = result.single()['count']

                if delete_count > 0:
                    print(f"  Deleting {delete_count:,} nodes with no remaining labels...")
                    delete_query = "MATCH (n) WHERE size(labels(n)) = 0 DETACH DELETE n"
                    session.run(delete_query)
                    print(f"  Deleted {delete_count:,} nodes")
                else:
                    print("  No nodes to delete (all have meaningful labels)")

            except Exception as e:
                print(f"  Warning: Failed to delete unlabeled nodes: {e}")

        elapsed = time.time() - start_time
        print(f"  Cleanup time: {elapsed:.2f}s")

    def get_statistics(self) -> Dict:
        """Get database statistics."""
        with self.driver.session() as session:
            # Count nodes
            result = session.run("MATCH (n) RETURN count(n) as count")
            node_count = result.single()['count']

            # Count relationships
            result = session.run("MATCH ()-[r]->() RETURN count(r) as count")
            rel_count = result.single()['count']

            # Get node labels
            result = session.run("MATCH (n) RETURN DISTINCT labels(n) as labels LIMIT 100")
            all_labels = set()
            for record in result:
                all_labels.update(record['labels'])

            # Get relationship types
            result = session.run("MATCH ()-[r]->() RETURN DISTINCT type(r) as type")
            rel_types = [record['type'] for record in result]

            return {
                'nodes': node_count,
                'relationships': rel_count,
                'labels': sorted(all_labels),
                'relationship_types': sorted(rel_types)
            }

    def load_rdf_file(self, rdf_file: str, clear_existing: bool = True,
                     create_indexes: bool = True, batch_size: int = 1000):
        """
        Load an RDF/XML file into Memgraph.

        Args:
            rdf_file: Path to RDF/XML file
            clear_existing: Whether to clear existing data
            create_indexes: Whether to create indexes
            batch_size: Batch size for loading

        Returns:
            Statistics dictionary
        """
        print("=" * 70)
        print("Loading RDF Ontology into Memgraph")
        print("=" * 70)

        # Clear database if requested
        if clear_existing:
            print("\nClearing database...")
            self.clear_database()

        # Create indexes
        if create_indexes:
            print("\nCreating indexes...")
            self.create_indexes()

        # Parse RDF file
        individuals, relationships = self.parse_rdf_file(rdf_file)

        # Load individuals
        self.load_individuals(individuals, batch_size)

        # Load relationships
        self.load_relationships(relationships, batch_size)

        # Clean up OWL standard labels
        self.cleanup_owl_labels()

        # Get statistics
        print("\n" + "=" * 70)
        print("LOAD COMPLETE")
        print("=" * 70)
        stats = self.get_statistics()

        print(f"\nDatabase Statistics:")
        print(f"  Nodes: {stats['nodes']:,}")
        print(f"  Relationships: {stats['relationships']:,}")
        print(f"  Node Labels ({len(stats['labels'])}): {', '.join(stats['labels'][:10])}")
        if len(stats['labels']) > 10:
            print(f"    ... and {len(stats['labels']) - 10} more")
        print(f"  Relationship Types ({len(stats['relationship_types'])}): {', '.join(stats['relationship_types'][:10])}")
        if len(stats['relationship_types']) > 10:
            print(f"    ... and {len(stats['relationship_types']) - 10} more")

        print("\n" + "=" * 70)

        return stats


if __name__ == "__main__":
    import sys

    # RDF file to load
    rdf_file = "../kg_projects/neurokb/neurokb-with-all-drug-relationships.rdf"

    # Check if file exists
    from pathlib import Path
    if not Path(rdf_file).exists():
        print(f"Error: File not found: {rdf_file}")
        print("\nPlease ensure you have run the DrugBank integration scripts first:")
        print("  1. python add_all_drug_relationships_direct.py")
        print(f"\nOr specify a different RDF file as argument:")
        print(f"  python {sys.argv[0]} path/to/your/file.rdf")
        sys.exit(1)

    # Allow specifying different file
    if len(sys.argv) > 1:
        rdf_file = sys.argv[1]

    print(f"Loading: {rdf_file}")
    print(f"Connecting to Memgraph at bolt://localhost:7687")
    print()

    # Load into Memgraph
    try:
        with RDFMemgraphLoader() as loader:
            # Test connection first
            if not loader.test_connection():
                print("\nError: Cannot connect to Memgraph at bolt://localhost:7687")
                print("\nPlease start Memgraph first:")
                print("  docker run -p 7687:7687 -p 7444:7444 memgraph/memgraph-platform")
                print("\nOr if using a different configuration, update the connection settings in the script.")
                sys.exit(1)

            stats = loader.load_rdf_file(rdf_file, batch_size=1000)

        print("\nSuccess! Your knowledge graph is now available in Memgraph.")
        print("\nAccess Memgraph Lab at: http://localhost:7444")
        print("\nExample Cypher queries to try:")
        print("  // Count nodes by type")
        print("  MATCH (n) RETURN labels(n) as type, count(*) as count ORDER BY count DESC;")
        print()
        print("  // Find a specific drug")
        print("  MATCH (d:Drug) WHERE d.name CONTAINS 'Lepirudin' RETURN d LIMIT 1;")
        print()
        print("  // Find drug interactions")
        print("  MATCH (d1:Drug)-[r:drugInteractsWithDrug]->(d2:Drug)")
        print("  RETURN d1.name, d2.name LIMIT 10;")
        print()
        print("  // Find drugs that treat Alzheimer's")
        print("  MATCH (d:Drug)-[:drugTreatsDisease]->(dis:Disease)")
        print("  WHERE dis.commonName CONTAINS 'Alzheimer'")
        print("  RETURN d.commonName, dis.commonName;")

    except Exception as e:
        print(f"\nError: {e}")
        print("\nPlease ensure:")
        print("  1. Memgraph is running: docker run -p 7687:7687 -p 7444:7444 memgraph/memgraph-platform")
        print("  2. neo4j driver is installed: pip install neo4j")
        import traceback
        traceback.print_exc()
        sys.exit(1)
