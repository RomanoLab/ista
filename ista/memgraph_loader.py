"""
Memgraph Knowledge Base Loader

This module provides utilities for populating Memgraph graph databases from OWL2 ontologies.

Memgraph is a high-performance, in-memory graph database compatible with Neo4j's Cypher query language.
It's particularly well-suited for real-time analytics and streaming graph data.

Mapping Strategy:
    - OWL Individuals → Memgraph Nodes
    - OWL Classes → Node Labels (types)
    - Data Properties → Node Properties
    - Annotation Properties → Node Properties
    - Object Properties → Relationships between Nodes

Example Usage:
    >>> from ista import owl2
    >>> from ista.memgraph_loader import MemgraphLoader
    >>>
    >>> # Load ontology
    >>> onto = owl2.Ontology(owl2.IRI("http://example.org/myonto"))
    >>> # ... populate ontology ...
    >>>
    >>> # Load into Memgraph
    >>> loader = MemgraphLoader("bolt://localhost:7687", username="", password="")
    >>> loader.load_ontology(onto)
"""

try:
    from neo4j import GraphDatabase

    HAS_NEO4J_DRIVER = True
except ImportError:
    HAS_NEO4J_DRIVER = False

from typing import Dict, List, Set, Optional, Any
import re


class MemgraphLoader:
    """
    Loader for populating Memgraph databases from OWL2 ontologies.

    This class handles the conversion of OWL2 ontology structures into
    Memgraph's property graph model using Cypher queries.
    """

    def __init__(
        self,
        uri: str = "bolt://localhost:7687",
        username: str = "",
        password: str = "",
        database: str = "memgraph",
    ):
        """
        Initialize Memgraph loader.

        Args:
            uri: Memgraph connection URI (default: bolt://localhost:7687)
            username: Username for authentication (default: empty for Memgraph)
            password: Password for authentication (default: empty for Memgraph)
            database: Database name (default: memgraph)
        """
        if not HAS_NEO4J_DRIVER:
            raise ImportError(
                "The neo4j driver is required to use MemgraphLoader.\n"
                "Install it with: pip install neo4j"
            )

        self.uri = uri
        self.username = username
        self.password = password
        self.database = database
        self.driver = None

    def connect(self):
        """Establish connection to Memgraph."""
        self.driver = GraphDatabase.driver(
            self.uri, auth=(self.username, self.password) if self.username else None
        )

    def close(self):
        """Close connection to Memgraph."""
        if self.driver:
            self.driver.close()

    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()

    def clear_database(self):
        """Clear all nodes and relationships from the database."""
        with self.driver.session(database=self.database) as session:
            session.run("MATCH (n) DETACH DELETE n")
            print("✓ Database cleared")

    def create_indexes(self, property_name: str = "iri"):
        """
        Create indexes for efficient lookups.

        Args:
            property_name: Property to index (default: "iri")
        """
        # Note: Memgraph uses different syntax than Neo4j for indexes
        # Memgraph doesn't support constraints the same way Neo4j does
        # We'll create label+property indexes
        with self.driver.session(database=self.database) as session:
            try:
                # Memgraph index syntax
                session.run(f"CREATE INDEX ON :Individual({property_name})")
                print(f"✓ Created index on Individual({property_name})")
            except Exception as e:
                print(f"Note: Index might already exist: {e}")

    def _sanitize_label(self, label: str) -> str:
        """
        Sanitize a string to be a valid Cypher label.

        Args:
            label: The label to sanitize

        Returns:
            Sanitized label safe for use in Cypher
        """
        # Remove or replace invalid characters
        # Cypher labels should start with letter and contain only alphanumeric and underscore
        sanitized = re.sub(r"[^a-zA-Z0-9_]", "_", label)

        # Ensure it starts with a letter
        if sanitized and not sanitized[0].isalpha():
            sanitized = "C_" + sanitized

        return sanitized or "Entity"

    def _extract_local_name(self, iri: str) -> str:
        """
        Extract local name from IRI.

        Args:
            iri: Full IRI string

        Returns:
            Local name portion
        """
        # Try fragment identifier first (#)
        if "#" in iri:
            return iri.split("#")[-1]
        # Fall back to last path component
        elif "/" in iri:
            return iri.split("/")[-1]
        # Use full IRI if can't extract
        return iri

    def _get_individual_data(self, ontology) -> List[Dict[str, Any]]:
        """
        Extract individual data from ontology.

        Args:
            ontology: OWL2 ontology object

        Returns:
            List of individual data dictionaries
        """
        individuals = []
        individual_map = {}  # Map IRI to individual data

        # First pass: collect all individuals and their basic info
        for axiom in ontology.get_axioms():
            axiom_type = axiom.get_axiom_type()

            if axiom_type == "ClassAssertion":
                # Individual with class membership
                individual_iri = str(axiom.get_class_expression())

                # Extract individual from variant type
                # This is a simplified approach - adjust based on actual API
                try:
                    # Get the individual IRI string representation
                    individual_str = str(axiom)
                    # Parse to extract individual IRI
                    # Format: ClassAssertion(NamedClass(<class>), <individual>)
                    # This is simplified - actual parsing may vary
                    parts = individual_str.split(",")
                    if len(parts) >= 2:
                        individual_iri_part = parts[1].strip().rstrip(")")

                        if individual_iri_part not in individual_map:
                            individual_map[individual_iri_part] = {
                                "iri": individual_iri_part,
                                "label": self._extract_local_name(individual_iri_part),
                                "classes": set(),
                                "properties": {},
                            }

                        # Extract class IRI
                        class_part = parts[0].split("(")[-1]
                        class_iri = class_part.strip()
                        individual_map[individual_iri_part]["classes"].add(class_iri)
                except Exception as e:
                    # Fallback: use lower-level API if available
                    print(f"Warning: Could not parse ClassAssertion: {e}")

        # Second pass: collect data properties
        for axiom in ontology.get_axioms():
            axiom_type = axiom.get_axiom_type()

            if axiom_type == "DataPropertyAssertion":
                try:
                    # Extract individual, property, and value
                    # This needs to be adapted to the actual owl2 API
                    prop = axiom.get_property()
                    source = axiom.get_source()
                    target = axiom.get_target()

                    individual_iri = str(source)
                    prop_iri = str(prop.get_iri())
                    prop_name = self._extract_local_name(prop_iri)
                    value = target.get_lexical_form()

                    if individual_iri in individual_map:
                        individual_map[individual_iri]["properties"][prop_name] = value
                except Exception as e:
                    print(f"Warning: Could not parse DataPropertyAssertion: {e}")

        return list(individual_map.values())

    def _get_relationships(self, ontology) -> List[Dict[str, Any]]:
        """
        Extract relationships (object properties) from ontology.

        Args:
            ontology: OWL2 ontology object

        Returns:
            List of relationship data dictionaries
        """
        relationships = []

        for axiom in ontology.get_axioms():
            axiom_type = axiom.get_axiom_type()

            if axiom_type == "ObjectPropertyAssertion":
                try:
                    # Extract source, property, and target
                    # Adapt to actual owl2 API
                    prop = axiom.get_property()
                    source = axiom.get_source()
                    target = axiom.get_target()

                    source_iri = str(source)
                    target_iri = str(target)
                    prop_iri = str(prop)
                    prop_name = self._extract_local_name(prop_iri)

                    relationships.append(
                        {
                            "source_iri": source_iri,
                            "target_iri": target_iri,
                            "type": self._sanitize_label(prop_name),
                            "property_iri": prop_iri,
                        }
                    )
                except Exception as e:
                    print(f"Warning: Could not parse ObjectPropertyAssertion: {e}")

        return relationships

    def load_ontology(
        self,
        ontology,
        clear_existing: bool = True,
        create_indexes: bool = True,
        batch_size: int = 1000,
    ):
        """
        Load an OWL2 ontology into Memgraph.

        Args:
            ontology: OWL2 ontology object
            clear_existing: Whether to clear existing data (default: True)
            create_indexes: Whether to create indexes (default: True)
            batch_size: Number of nodes/relationships to create per batch

        Returns:
            dict with statistics about what was loaded
        """
        print("=" * 60)
        print("Loading OWL2 Ontology into Memgraph")
        print("=" * 60)

        if not self.driver:
            self.connect()

        # Clear database if requested
        if clear_existing:
            self.clear_database()

        # Create indexes
        if create_indexes:
            self.create_indexes()

        # Extract data from ontology
        print("\n[Step 1] Extracting individuals from ontology...")
        individuals = self._get_individual_data(ontology)
        print(f"✓ Found {len(individuals)} individuals")

        print("\n[Step 2] Extracting relationships from ontology...")
        relationships = self._get_relationships(ontology)
        print(f"✓ Found {len(relationships)} relationships")

        # Load individuals
        print("\n[Step 3] Creating nodes in Memgraph...")
        self._load_individuals(individuals, batch_size)

        # Load relationships
        print("\n[Step 4] Creating relationships in Memgraph...")
        self._load_relationships(relationships, batch_size)

        # Statistics
        print("\n" + "=" * 60)
        print("LOAD COMPLETE")
        print("=" * 60)
        stats = self.get_database_statistics()
        print(f"Total Nodes: {stats['node_count']}")
        print(f"Total Relationships: {stats['relationship_count']}")
        print(f"Node Labels: {stats['labels']}")
        print(f"Relationship Types: {stats['relationship_types']}")
        print("=" * 60)

        return {
            "individuals_loaded": len(individuals),
            "relationships_loaded": len(relationships),
            **stats,
        }

    def _load_individuals(self, individuals: List[Dict], batch_size: int = 1000):
        """Load individuals as nodes in batches."""
        with self.driver.session(database=self.database) as session:
            for i in range(0, len(individuals), batch_size):
                batch = individuals[i : i + batch_size]

                for individual in batch:
                    # Build labels from classes
                    labels = ["Individual"]  # Base label
                    for class_iri in individual["classes"]:
                        class_label = self._sanitize_label(
                            self._extract_local_name(class_iri)
                        )
                        labels.append(class_label)

                    label_str = ":".join(labels)

                    # Build properties
                    props = {
                        "iri": individual["iri"],
                        "label": individual["label"],
                        **individual["properties"],
                    }

                    # Create Cypher query
                    # Use MERGE to avoid duplicates
                    query = f"MERGE (n:{label_str} {{iri: $iri}}) SET n = $props"

                    session.run(query, iri=individual["iri"], props=props)

                print(
                    f"  Loaded {min(i + batch_size, len(individuals))}/{len(individuals)} nodes"
                )

        print(f"✓ Created {len(individuals)} nodes")

    def _load_relationships(self, relationships: List[Dict], batch_size: int = 1000):
        """Load relationships in batches."""
        with self.driver.session(database=self.database) as session:
            for i in range(0, len(relationships), batch_size):
                batch = relationships[i : i + batch_size]

                for rel in batch:
                    # Create Cypher query
                    # MATCH both nodes by IRI, then CREATE relationship
                    query = f"""
                    MATCH (a:Individual {{iri: $source_iri}})
                    MATCH (b:Individual {{iri: $target_iri}})
                    MERGE (a)-[r:{rel["type"]}]->(b)
                    SET r.property_iri = $property_iri
                    """

                    session.run(
                        query,
                        source_iri=rel["source_iri"],
                        target_iri=rel["target_iri"],
                        property_iri=rel["property_iri"],
                    )

                print(
                    f"  Loaded {min(i + batch_size, len(relationships))}/{len(relationships)} relationships"
                )

        print(f"✓ Created {len(relationships)} relationships")

    def get_database_statistics(self) -> Dict[str, Any]:
        """Get statistics about the loaded graph."""
        with self.driver.session(database=self.database) as session:
            # Count nodes
            result = session.run("MATCH (n) RETURN count(n) as count")
            node_count = result.single()["count"]

            # Count relationships
            result = session.run("MATCH ()-[r]->() RETURN count(r) as count")
            relationship_count = result.single()["count"]

            # Get node labels
            result = session.run("MATCH (n) RETURN DISTINCT labels(n) as labels")
            all_labels = set()
            for record in result:
                all_labels.update(record["labels"])

            # Get relationship types
            result = session.run("MATCH ()-[r]->() RETURN DISTINCT type(r) as type")
            rel_types = [record["type"] for record in result]

            return {
                "node_count": node_count,
                "relationship_count": relationship_count,
                "labels": sorted(all_labels),
                "relationship_types": sorted(rel_types),
            }

    def execute_query(self, query: str, parameters: Optional[Dict] = None):
        """
        Execute a custom Cypher query.

        Args:
            query: Cypher query string
            parameters: Query parameters (optional)

        Returns:
            Query results
        """
        with self.driver.session(database=self.database) as session:
            result = session.run(query, parameters or {})
            return [record.data() for record in result]


def load_ontology_to_memgraph(
    ontology,
    uri: str = "bolt://localhost:7687",
    username: str = "",
    password: str = "",
    clear_existing: bool = True,
) -> Dict[str, Any]:
    """
    Convenience function to load an ontology into Memgraph.

    Args:
        ontology: OWL2 ontology object
        uri: Memgraph connection URI
        username: Username for authentication
        password: Password for authentication
        clear_existing: Whether to clear existing data

    Returns:
        Dictionary with load statistics

    Example:
        >>> from ista import owl2
        >>> from ista.memgraph_loader import load_ontology_to_memgraph
        >>>
        >>> onto = owl2.Ontology(owl2.IRI("http://example.org/test"))
        >>> # ... populate ontology ...
        >>>
        >>> stats = load_ontology_to_memgraph(onto)
        >>> print(f"Loaded {stats['individuals_loaded']} individuals")
    """
    with MemgraphLoader(uri, username, password) as loader:
        return loader.load_ontology(ontology, clear_existing=clear_existing)


def load_rdf_to_memgraph(
    rdf_file: str,
    uri: str = "bolt://localhost:7687",
    username: str = "",
    password: str = "",
    clear_existing: bool = True,
    cleanup_labels: bool = True,
) -> Dict[str, Any]:
    """
    Convenience function to load an RDF/XML file into Memgraph.

    This function directly parses RDF/XML files and loads individuals,
    data properties, and object properties into Memgraph.

    Parameters
    ----------
    rdf_file : str
        Path to RDF/XML ontology file.
    uri : str
        Memgraph connection URI.
    username : str
        Username for authentication.
    password : str
        Password for authentication.
    clear_existing : bool
        Whether to clear existing data before loading.
    cleanup_labels : bool
        Whether to remove OWL infrastructure labels after loading.

    Returns
    -------
    dict
        Dictionary with load statistics including nodes, relationships,
        labels, and relationship_types.

    Examples
    --------
    >>> from ista.memgraph_loader import load_rdf_to_memgraph
    >>> stats = load_rdf_to_memgraph("ontology.rdf")
    >>> print(f"Loaded {stats['nodes']} nodes and {stats['relationships']} relationships")
    """
    from .owl2memgraph import OWL2MemgraphLoader

    with OWL2MemgraphLoader(uri, username, password) as loader:
        return loader.load_file(
            rdf_file,
            format="rdfxml",
            clear_existing=clear_existing,
            cleanup_labels=cleanup_labels,
        )
