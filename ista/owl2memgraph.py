"""
owl2memgraph - Load OWL2 ontologies into Memgraph graph database.

This module provides a CLI tool and Python API for loading OWL2 ontologies
in various formats into Memgraph. It leverages ista's C++ parsers for
high-performance parsing of multiple ontology formats.

Supported Formats:
    - RDF/XML (.rdf, .owl, .xml)
    - Turtle (.ttl)
    - OWL Functional Syntax (.ofn, .owl)
    - Manchester Syntax (.omn)
    - OWL/XML (.owx)

Example CLI Usage:
    # Load an RDF/XML file
    owl2memgraph -i ontology.rdf

    # Load a Turtle file with explicit format
    owl2memgraph -i ontology.ttl --format turtle

    # Load with custom connection settings
    owl2memgraph -i ontology.owl --uri bolt://localhost:7687 --username admin

    # Keep existing data (don't clear database)
    owl2memgraph -i ontology.rdf --no-clear

Example Programmatic Usage:
    >>> from ista.owl2memgraph import OWL2MemgraphLoader
    >>> with OWL2MemgraphLoader() as loader:
    ...     stats = loader.load_file("ontology.ttl")
    ...     print(f"Loaded {stats['nodes']} nodes")
"""

import argparse
import re
import sys
import time
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

try:
    from neo4j import GraphDatabase

    HAS_NEO4J_DRIVER = True
except ImportError:
    HAS_NEO4J_DRIVER = False

try:
    from ista import owl2

    HAS_OWL2 = owl2.is_available()
except ImportError:
    HAS_OWL2 = False


# Supported file formats and their extensions
FORMAT_EXTENSIONS = {
    "rdfxml": [".rdf", ".owl", ".xml"],
    "turtle": [".ttl"],
    "functional": [".ofn", ".fss"],
    "manchester": [".omn"],
    "owlxml": [".owx"],
}

# Reverse mapping: extension -> format
EXTENSION_TO_FORMAT = {}
for fmt, exts in FORMAT_EXTENSIONS.items():
    for ext in exts:
        EXTENSION_TO_FORMAT[ext] = fmt


def detect_format(filepath: str) -> Optional[str]:
    """
    Detect ontology format from file extension.

    Parameters
    ----------
    filepath : str
        Path to ontology file.

    Returns
    -------
    str or None
        Detected format name, or None if unknown.
    """
    ext = Path(filepath).suffix.lower()
    return EXTENSION_TO_FORMAT.get(ext)


class OWL2MemgraphLoader:
    """
    Loader for OWL2 ontologies into Memgraph.

    This class handles parsing ontology files in various formats and loading
    individuals, data properties, and object properties into a Memgraph database.

    The loader uses ista's high-performance C++ parsers for parsing ontology
    files and provides progress callbacks for GUI integration.

    Parameters
    ----------
    uri : str
        Memgraph Bolt connection URI.
    username : str
        Username for authentication (empty for Memgraph default).
    password : str
        Password for authentication (empty for Memgraph default).
    progress_callback : callable, optional
        Function called with (current, total, message) for progress updates.
        Useful for GUI integration.

    Examples
    --------
    >>> with OWL2MemgraphLoader() as loader:
    ...     stats = loader.load_file("ontology.ttl")
    ...     print(f"Loaded {stats['nodes']} nodes")

    >>> # With progress callback for GUI
    >>> def on_progress(current, total, message):
    ...     print(f"{current}/{total}: {message}")
    >>> loader = OWL2MemgraphLoader(progress_callback=on_progress)
    """

    def __init__(
        self,
        uri: str = "bolt://localhost:7687",
        username: str = "",
        password: str = "",
        progress_callback: Optional[Callable[[int, int, str], None]] = None,
    ):
        if not HAS_NEO4J_DRIVER:
            raise ImportError(
                "The neo4j driver is required to use OWL2MemgraphLoader.\n"
                "Install it with: pip install neo4j"
            )

        if not HAS_OWL2:
            raise ImportError(
                "The ista OWL2 C++ bindings are required.\n"
                "Build with: pip install -e ."
            )

        self.uri = uri
        self.username = username
        self.password = password
        self.driver = None
        self.progress_callback = progress_callback

    def _report_progress(self, current: int, total: int, message: str):
        """Report progress via callback or print."""
        if self.progress_callback:
            self.progress_callback(current, total, message)
        else:
            print(f"  {message}")

    def connect(self):
        """Establish connection to Memgraph."""
        auth = (self.username, self.password) if self.username else None
        self.driver = GraphDatabase.driver(self.uri, auth=auth)

    def test_connection(self) -> bool:
        """
        Test if the database connection is working.

        Returns
        -------
        bool
            True if connection successful, False otherwise.
        """
        try:
            if not self.driver:
                self.connect()
            with self.driver.session() as session:
                session.run("RETURN 1")
            return True
        except Exception:
            return False

    def close(self):
        """Close database connection."""
        if self.driver:
            self.driver.close()
            self.driver = None

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def clear_database(self):
        """Clear all data from Memgraph."""
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
        self._report_progress(1, 1, "Database cleared")

    def create_indexes(self):
        """Create indexes for performance."""
        with self.driver.session() as session:
            try:
                session.run("CREATE INDEX ON :Individual(iri)")
                self._report_progress(1, 1, "Created index on Individual(iri)")
            except Exception as e:
                self._report_progress(1, 1, f"Index note: {e}")

    def _extract_fragment(self, iri: str) -> str:
        """Extract the fragment identifier from an IRI."""
        if "#" in iri:
            return iri.split("#")[-1]
        elif "/" in iri:
            return iri.split("/")[-1]
        return iri

    def _sanitize_label(self, label: str) -> str:
        """Make a label safe for use in Cypher."""
        sanitized = re.sub(r"[^a-zA-Z0-9_]", "_", label)
        if sanitized and not sanitized[0].isalpha():
            sanitized = "N_" + sanitized
        return sanitized or "Node"

    def parse_ontology_file(
        self, filepath: str, format: Optional[str] = None
    ) -> Tuple[Dict, List]:
        """
        Parse an ontology file using ista's C++ parsers.

        Parameters
        ----------
        filepath : str
            Path to ontology file.
        format : str, optional
            Explicit format. If None, detected from extension.

        Returns
        -------
        tuple
            Tuple of (individuals dict, relationships list).

        Raises
        ------
        ValueError
            If format cannot be detected or is unsupported.
        """
        if format is None:
            format = detect_format(filepath)
            if format is None:
                raise ValueError(
                    f"Cannot detect format from extension. "
                    f"Use --format to specify: {list(FORMAT_EXTENSIONS.keys())}"
                )

        self._report_progress(0, 1, f"Parsing {format.upper()} file: {filepath}")
        start_time = time.time()

        # Parse using appropriate parser
        if format == "rdfxml":
            ontology = owl2.RDFXMLParser.parse_from_file(filepath)
        elif format == "turtle":
            ontology = owl2.TurtleParser.parse_from_file(filepath)
        elif format == "functional":
            ontology = owl2.FunctionalParser.parse_from_file(filepath)
        elif format == "manchester":
            ontology = owl2.ManchesterParser.parse_from_file(filepath)
        elif format == "owlxml":
            ontology = owl2.OWLXMLParser.parse_from_file(filepath)
        else:
            raise ValueError(f"Unsupported format: {format}")

        # Extract individuals and relationships from the parsed ontology
        individuals, relationships = self._extract_from_ontology(ontology)

        elapsed = time.time() - start_time
        self._report_progress(
            1,
            1,
            f"Parsed {len(individuals):,} individuals, {len(relationships):,} relationships ({elapsed:.2f}s)",
        )

        return individuals, relationships

    def _extract_from_ontology(self, ontology) -> Tuple[Dict, List]:
        """
        Extract individuals and relationships from a parsed OWL2 ontology.

        Parameters
        ----------
        ontology : owl2.Ontology
            Parsed ontology object.

        Returns
        -------
        tuple
            Tuple of (individuals dict, relationships list).
        """
        individuals = {}
        relationships = []

        # Process all axioms
        for axiom in ontology.get_axioms():
            axiom_type = axiom.get_axiom_type()

            if axiom_type == "ClassAssertion":
                # Extract individual and its type
                try:
                    individual = axiom.get_individual()
                    class_expr = axiom.get_class_expression()

                    ind_iri = str(individual.get_iri())
                    if ind_iri not in individuals:
                        individuals[ind_iri] = {
                            "types": set(),
                            "properties": {},
                            "label": self._extract_fragment(ind_iri),
                        }

                    # Get class name if it's a named class
                    class_str = str(class_expr)
                    if class_str.startswith("NamedClass("):
                        # Extract IRI from NamedClass(IRI(...))
                        class_name = self._extract_fragment(class_str)
                    else:
                        class_name = self._extract_fragment(class_str)

                    if class_name and class_name != "NamedIndividual":
                        individuals[ind_iri]["types"].add(class_name)
                except Exception:
                    pass

            elif axiom_type == "DataPropertyAssertion":
                # Extract data property value
                try:
                    prop = axiom.get_property()
                    source = axiom.get_source()
                    target = axiom.get_target()

                    ind_iri = str(source.get_iri())
                    if ind_iri not in individuals:
                        individuals[ind_iri] = {
                            "types": set(),
                            "properties": {},
                            "label": self._extract_fragment(ind_iri),
                        }

                    prop_name = self._extract_fragment(str(prop.get_iri()))
                    value = target.get_lexical_form()

                    # Try to convert to appropriate type
                    datatype = str(target.get_datatype()) if hasattr(target, 'get_datatype') else ""
                    if "integer" in datatype or "int" in datatype:
                        try:
                            value = int(value)
                        except ValueError:
                            pass
                    elif "float" in datatype or "double" in datatype or "decimal" in datatype:
                        try:
                            value = float(value)
                        except ValueError:
                            pass
                    elif "boolean" in datatype:
                        value = value.lower() in ("true", "1", "yes")

                    individuals[ind_iri]["properties"][prop_name] = value
                except Exception:
                    pass

            elif axiom_type == "ObjectPropertyAssertion":
                # Extract relationship
                try:
                    prop = axiom.get_property()
                    source = axiom.get_source()
                    target = axiom.get_target()

                    source_iri = str(source.get_iri())
                    target_iri = str(target.get_iri())
                    prop_name = self._extract_fragment(str(prop.get_iri()))

                    # Ensure both individuals exist
                    for iri in [source_iri, target_iri]:
                        if iri not in individuals:
                            individuals[iri] = {
                                "types": set(),
                                "properties": {},
                                "label": self._extract_fragment(iri),
                            }

                    relationships.append((source_iri, prop_name, target_iri))
                except Exception:
                    pass

            elif axiom_type == "Declaration":
                # Handle individual declarations
                try:
                    entity_type = axiom.get_entity_type()
                    if str(entity_type) == "NAMED_INDIVIDUAL":
                        entity_iri = str(axiom.get_entity_iri())
                        if entity_iri not in individuals:
                            individuals[entity_iri] = {
                                "types": set(),
                                "properties": {},
                                "label": self._extract_fragment(entity_iri),
                            }
                except Exception:
                    pass

        return individuals, relationships

    def load_individuals(self, individuals: Dict, batch_size: int = 1000):
        """
        Load individuals as nodes into Memgraph.

        Parameters
        ----------
        individuals : dict
            Dictionary mapping IRI to individual data.
        batch_size : int
            Number of nodes to create per batch.
        """
        self._report_progress(
            0, len(individuals), f"Loading {len(individuals):,} individuals as nodes..."
        )
        start_time = time.time()

        individual_list = list(individuals.items())
        total = len(individual_list)

        with self.driver.session() as session:
            for i in range(0, total, batch_size):
                batch = individual_list[i : i + batch_size]

                for iri, data in batch:
                    labels = ["Individual"]
                    for type_name in data["types"]:
                        labels.append(self._sanitize_label(type_name))

                    if len(labels) == 1:
                        labels.append("Entity")

                    label_str = ":".join(labels)
                    props = {
                        "iri": iri,
                        "name": data["label"],
                        **data["properties"],
                    }

                    query = f"CREATE (n:{label_str}) SET n = $props"
                    session.run(query, props=props)

                self._report_progress(
                    min(i + batch_size, total),
                    total,
                    f"Loaded {min(i + batch_size, total):,}/{total:,} nodes",
                )

        elapsed = time.time() - start_time
        rate = total / elapsed if elapsed > 0 else 0
        self._report_progress(
            total, total, f"Created {total:,} nodes ({elapsed:.2f}s, {rate:.0f}/sec)"
        )

    def load_relationships(self, relationships: List, batch_size: int = 1000):
        """
        Load relationships (object properties) into Memgraph using UNWIND batching.

        Parameters
        ----------
        relationships : list
            List of (source_iri, property_name, target_iri) tuples.
        batch_size : int
            Number of relationships to create per batch.
        """
        self._report_progress(
            0, len(relationships), f"Loading {len(relationships):,} relationships..."
        )
        start_time = time.time()

        total = len(relationships)
        loaded = 0
        errors = 0

        for i in range(0, total, batch_size):
            batch = relationships[i : i + batch_size]

            # Group by relationship type for efficient UNWIND batching
            rels_by_type: Dict[str, List[Dict]] = {}
            for source_iri, prop_name, target_iri in batch:
                rel_type = self._sanitize_label(prop_name)
                if rel_type not in rels_by_type:
                    rels_by_type[rel_type] = []
                rels_by_type[rel_type].append(
                    {"source": source_iri, "target": target_iri}
                )

            with self.driver.session() as session:
                for rel_type, rels in rels_by_type.items():
                    try:
                        query = f"""
                        UNWIND $rels as rel
                        MATCH (a:Individual {{iri: rel.source}})
                        MATCH (b:Individual {{iri: rel.target}})
                        CREATE (a)-[:{rel_type}]->(b)
                        """
                        session.run(query, rels=rels)
                        loaded += len(rels)
                    except Exception as e:
                        errors += len(rels)
                        if errors <= 5:
                            self._report_progress(
                                i, total, f"Warning: Batch failed for {rel_type}: {e}"
                            )

            self._report_progress(
                min(i + batch_size, total),
                total,
                f"Loaded {min(i + batch_size, total):,}/{total:,} relationships",
            )

        elapsed = time.time() - start_time
        msg = f"Created {loaded:,} relationships ({elapsed:.2f}s"
        if loaded > 0 and elapsed > 0:
            msg += f", {loaded / elapsed:.0f}/sec"
        msg += ")"
        if errors > 0:
            msg += f" [{errors:,} errors]"
        self._report_progress(total, total, msg)

    def cleanup_owl_labels(self, labels_to_remove: Optional[List[str]] = None):
        """
        Remove OWL standard labels and delete nodes with no remaining labels.

        Parameters
        ----------
        labels_to_remove : list, optional
            Labels to remove. Defaults to common OWL infrastructure labels.
        """
        if labels_to_remove is None:
            labels_to_remove = [
                "DatatypeProperty",
                "FunctionalProperty",
                "Entity",
                "Individual",
            ]

        self._report_progress(
            0, len(labels_to_remove), "Cleaning up OWL standard labels..."
        )
        start_time = time.time()

        with self.driver.session() as session:
            for i, label in enumerate(labels_to_remove):
                try:
                    query = f"MATCH (n:{label}) REMOVE n:{label}"
                    session.run(query).consume()
                    self._report_progress(
                        i + 1, len(labels_to_remove), f"Removed :{label} labels"
                    )
                except Exception as e:
                    self._report_progress(
                        i + 1,
                        len(labels_to_remove),
                        f"Warning: Failed to remove :{label}: {e}",
                    )

            # Delete nodes with no labels
            try:
                result = session.run(
                    "MATCH (n) WHERE size(labels(n)) = 0 RETURN count(n) as count"
                )
                delete_count = result.single()["count"]

                if delete_count > 0:
                    session.run("MATCH (n) WHERE size(labels(n)) = 0 DETACH DELETE n")
                    self._report_progress(
                        len(labels_to_remove),
                        len(labels_to_remove),
                        f"Deleted {delete_count:,} nodes with no labels",
                    )
            except Exception as e:
                self._report_progress(
                    len(labels_to_remove),
                    len(labels_to_remove),
                    f"Warning: Failed to delete unlabeled nodes: {e}",
                )

        elapsed = time.time() - start_time
        self._report_progress(
            len(labels_to_remove),
            len(labels_to_remove),
            f"Cleanup complete ({elapsed:.2f}s)",
        )

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get database statistics.

        Returns
        -------
        dict
            Statistics including node count, relationship count, labels, and types.
        """
        with self.driver.session() as session:
            result = session.run("MATCH (n) RETURN count(n) as count")
            node_count = result.single()["count"]

            result = session.run("MATCH ()-[r]->() RETURN count(r) as count")
            rel_count = result.single()["count"]

            result = session.run(
                "MATCH (n) RETURN DISTINCT labels(n) as labels LIMIT 100"
            )
            all_labels = set()
            for record in result:
                all_labels.update(record["labels"])

            result = session.run("MATCH ()-[r]->() RETURN DISTINCT type(r) as type")
            rel_types = [record["type"] for record in result]

            return {
                "nodes": node_count,
                "relationships": rel_count,
                "labels": sorted(all_labels),
                "relationship_types": sorted(rel_types),
            }

    def load_file(
        self,
        filepath: str,
        format: Optional[str] = None,
        clear_existing: bool = True,
        create_indexes: bool = True,
        cleanup_labels: bool = True,
        batch_size: int = 1000,
    ) -> Dict[str, Any]:
        """
        Load an ontology file into Memgraph.

        This is the main entry point for loading ontology files.

        Parameters
        ----------
        filepath : str
            Path to ontology file.
        format : str, optional
            Explicit format (rdfxml, turtle, functional, manchester, owlxml).
            If None, detected from file extension.
        clear_existing : bool
            Whether to clear existing data before loading.
        create_indexes : bool
            Whether to create indexes for performance.
        cleanup_labels : bool
            Whether to remove OWL infrastructure labels after loading.
        batch_size : int
            Batch size for loading operations.

        Returns
        -------
        dict
            Statistics about the loaded graph.
        """
        # Detect format if not specified
        detected_format = format or detect_format(filepath)
        format_display = (detected_format or "unknown").upper()

        print("=" * 70)
        print(f"Loading {format_display} Ontology into Memgraph")
        print("=" * 70)

        if not self.driver:
            self.connect()

        if clear_existing:
            print("\nClearing database...")
            self.clear_database()

        if create_indexes:
            print("\nCreating indexes...")
            self.create_indexes()

        # Parse and load
        print("\nParsing ontology file...")
        individuals, relationships = self.parse_ontology_file(filepath, format)

        print("\nLoading nodes...")
        self.load_individuals(individuals, batch_size)

        print("\nLoading relationships...")
        self.load_relationships(relationships, batch_size)

        if cleanup_labels:
            print("\nCleaning up labels...")
            self.cleanup_owl_labels()

        # Final statistics
        print("\n" + "=" * 70)
        print("LOAD COMPLETE")
        print("=" * 70)
        stats = self.get_statistics()

        print(f"\nDatabase Statistics:")
        print(f"  Nodes: {stats['nodes']:,}")
        print(f"  Relationships: {stats['relationships']:,}")
        print(
            f"  Node Labels ({len(stats['labels'])}): {', '.join(stats['labels'][:10])}"
        )
        if len(stats["labels"]) > 10:
            print(f"    ... and {len(stats['labels']) - 10} more")
        print(
            f"  Relationship Types ({len(stats['relationship_types'])}): "
            f"{', '.join(stats['relationship_types'][:10])}"
        )
        if len(stats["relationship_types"]) > 10:
            print(f"    ... and {len(stats['relationship_types']) - 10} more")
        print("=" * 70)

        return stats

    def load_ontology(
        self,
        ontology,
        clear_existing: bool = True,
        create_indexes: bool = True,
        cleanup_labels: bool = True,
        batch_size: int = 1000,
    ) -> Dict[str, Any]:
        """
        Load an already-parsed OWL2 ontology into Memgraph.

        Parameters
        ----------
        ontology : owl2.Ontology
            Parsed ontology object.
        clear_existing : bool
            Whether to clear existing data before loading.
        create_indexes : bool
            Whether to create indexes for performance.
        cleanup_labels : bool
            Whether to remove OWL infrastructure labels after loading.
        batch_size : int
            Batch size for loading operations.

        Returns
        -------
        dict
            Statistics about the loaded graph.
        """
        print("=" * 70)
        print("Loading OWL2 Ontology into Memgraph")
        print("=" * 70)

        if not self.driver:
            self.connect()

        if clear_existing:
            print("\nClearing database...")
            self.clear_database()

        if create_indexes:
            print("\nCreating indexes...")
            self.create_indexes()

        # Extract from ontology
        print("\nExtracting individuals and relationships...")
        individuals, relationships = self._extract_from_ontology(ontology)
        self._report_progress(
            1,
            1,
            f"Found {len(individuals):,} individuals, {len(relationships):,} relationships",
        )

        print("\nLoading nodes...")
        self.load_individuals(individuals, batch_size)

        print("\nLoading relationships...")
        self.load_relationships(relationships, batch_size)

        if cleanup_labels:
            print("\nCleaning up labels...")
            self.cleanup_owl_labels()

        # Final statistics
        print("\n" + "=" * 70)
        print("LOAD COMPLETE")
        print("=" * 70)
        stats = self.get_statistics()

        print(f"\nDatabase Statistics:")
        print(f"  Nodes: {stats['nodes']:,}")
        print(f"  Relationships: {stats['relationships']:,}")

        return stats


# Backwards compatibility alias
RDFMemgraphLoader = OWL2MemgraphLoader


def create_parser() -> argparse.ArgumentParser:
    """
    Create the argument parser for the CLI.

    Returns
    -------
    argparse.ArgumentParser
        Configured argument parser.
    """
    format_list = ", ".join(FORMAT_EXTENSIONS.keys())

    parser = argparse.ArgumentParser(
        prog="owl2memgraph",
        description="Load OWL2 ontologies into Memgraph graph database.",
        epilog=f"""
Supported Formats:
  rdfxml     - RDF/XML format (.rdf, .owl, .xml)
  turtle     - Turtle format (.ttl)
  functional - OWL Functional Syntax (.ofn, .fss)
  manchester - Manchester Syntax (.omn)
  owlxml     - OWL/XML format (.owx)

Examples:
  owl2memgraph -i ontology.rdf
  owl2memgraph -i ontology.ttl --format turtle
  owl2memgraph -i ontology.owl --uri bolt://db.example.com:7687
  owl2memgraph -i ontology.rdf --no-clear --batch-size 500

For more information, visit: https://github.com/JDRomano2/ista
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # Required arguments
    parser.add_argument(
        "-i",
        "--input",
        type=str,
        required=True,
        metavar="FILE",
        help="Path to ontology file to load",
    )

    # Format options
    parser.add_argument(
        "-f",
        "--format",
        type=str,
        choices=list(FORMAT_EXTENSIONS.keys()),
        metavar="FORMAT",
        help=f"Ontology format ({format_list}). Auto-detected from extension if not specified.",
    )

    # Connection arguments
    conn_group = parser.add_argument_group("connection options")
    conn_group.add_argument(
        "--uri",
        type=str,
        default="bolt://localhost:7687",
        metavar="URI",
        help="Memgraph Bolt URI (default: bolt://localhost:7687)",
    )
    conn_group.add_argument(
        "--username",
        "-u",
        type=str,
        default="",
        metavar="USER",
        help="Username for authentication (default: none)",
    )
    conn_group.add_argument(
        "--password",
        "-p",
        type=str,
        default="",
        metavar="PASS",
        help="Password for authentication (default: none)",
    )

    # Loading options
    load_group = parser.add_argument_group("loading options")
    load_group.add_argument(
        "--no-clear",
        action="store_true",
        help="Don't clear existing data before loading",
    )
    load_group.add_argument(
        "--no-indexes",
        action="store_true",
        help="Don't create indexes",
    )
    load_group.add_argument(
        "--no-cleanup",
        action="store_true",
        help="Don't remove OWL infrastructure labels after loading",
    )
    load_group.add_argument(
        "--batch-size",
        type=int,
        default=1000,
        metavar="N",
        help="Batch size for loading operations (default: 1000)",
    )

    # Output options
    output_group = parser.add_argument_group("output options")
    output_group.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Suppress progress output",
    )
    output_group.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Show detailed output",
    )

    return parser


def main(args: Optional[List[str]] = None) -> int:
    """
    Main entry point for the CLI.

    Parameters
    ----------
    args : list, optional
        Command-line arguments. If None, uses sys.argv.

    Returns
    -------
    int
        Exit code (0 for success, non-zero for errors).
    """
    parser = create_parser()
    parsed = parser.parse_args(args)

    # Validate input file
    input_path = Path(parsed.input)
    if not input_path.exists():
        print(f"Error: File not found: {parsed.input}", file=sys.stderr)
        return 1

    if not input_path.is_file():
        print(f"Error: Not a file: {parsed.input}", file=sys.stderr)
        return 1

    # Detect or validate format
    format_name = parsed.format or detect_format(str(input_path))
    if format_name is None:
        print(
            f"Error: Cannot detect format from extension '{input_path.suffix}'.",
            file=sys.stderr,
        )
        print(
            f"Use --format to specify: {list(FORMAT_EXTENSIONS.keys())}",
            file=sys.stderr,
        )
        return 1

    # Show configuration
    if not parsed.quiet:
        print(f"Input file: {input_path}")
        print(f"Format: {format_name}")
        print(f"Memgraph URI: {parsed.uri}")
        if parsed.username:
            print(f"Username: {parsed.username}")
        print()

    # Load into Memgraph
    try:
        with OWL2MemgraphLoader(
            uri=parsed.uri,
            username=parsed.username,
            password=parsed.password,
        ) as loader:
            # Test connection first
            if not loader.test_connection():
                print(
                    f"\nError: Cannot connect to Memgraph at {parsed.uri}",
                    file=sys.stderr,
                )
                print("\nPlease ensure Memgraph is running:", file=sys.stderr)
                print(
                    "  docker run -p 7687:7687 -p 7444:7444 memgraph/memgraph-platform",
                    file=sys.stderr,
                )
                return 1

            stats = loader.load_file(
                str(input_path),
                format=format_name,
                clear_existing=not parsed.no_clear,
                create_indexes=not parsed.no_indexes,
                cleanup_labels=not parsed.no_cleanup,
                batch_size=parsed.batch_size,
            )

        if not parsed.quiet:
            print("\nSuccess! Your knowledge graph is now available in Memgraph.")
            print("\nAccess Memgraph Lab at: http://localhost:7444")
            print("\nExample Cypher queries:")
            print("  MATCH (n) RETURN labels(n), count(*) ORDER BY count(*) DESC;")
            print(
                "  MATCH (a)-[r]->(b) RETURN type(r), count(*) ORDER BY count(*) DESC;"
            )

        return 0

    except ImportError as e:
        print(f"\nError: {e}", file=sys.stderr)
        return 1
    except ValueError as e:
        print(f"\nError: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        if parsed.verbose:
            import traceback

            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
