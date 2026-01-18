"""
Load NeuroKB RDF Ontology into Memgraph - Example Script

This example demonstrates how to use ista's Memgraph loader to load an RDF/XML
ontology into Memgraph. It shows both the CLI tool approach and the
programmatic API.

Prerequisites:
    - Memgraph running: docker run -p 7687:7687 -p 7444:7444 memgraph/memgraph-platform
    - neo4j driver: pip install neo4j

Usage:
    # Using the CLI tool (recommended):
    owl2memgraph -i ../kg_projects/neurokb/neurokb-with-all-drug-relationships.rdf

    # Or run this script directly:
    python load_neurokb_to_memgraph.py [path/to/file.rdf]

    # The CLI supports multiple formats:
    owl2memgraph -i ontology.ttl              # Turtle
    owl2memgraph -i ontology.ofn              # OWL Functional Syntax
    owl2memgraph -i ontology.omn              # Manchester Syntax
    owl2memgraph -i ontology.owx              # OWL/XML
"""

import sys
from pathlib import Path


def main():
    """Load an RDF/XML ontology into Memgraph."""
    # Default RDF file
    rdf_file = "../kg_projects/neurokb/neurokb-with-all-drug-relationships.rdf"

    # Allow specifying different file via command line
    if len(sys.argv) > 1:
        rdf_file = sys.argv[1]

    rdf_path = Path(rdf_file)
    if not rdf_path.exists():
        print(f"Error: File not found: {rdf_file}")
        print("\nUsage:")
        print(f"  python {sys.argv[0]} [path/to/file.rdf]")
        print("\nOr use the CLI tool:")
        print("  owl2memgraph -i path/to/file.rdf")
        return 1

    print(f"Loading: {rdf_path}")
    print(f"Connecting to Memgraph at bolt://localhost:7687")
    print()

    try:
        # Import the ista Memgraph loader
        from ista import load_rdf_to_memgraph, OWL2MemgraphLoader

        # Method 1: Using the convenience function
        # stats = load_rdf_to_memgraph(str(rdf_path))

        # Method 2: Using the loader class directly (more control)
        with OWL2MemgraphLoader() as loader:
            if not loader.test_connection():
                print("\nError: Cannot connect to Memgraph at bolt://localhost:7687")
                print("\nPlease start Memgraph first:")
                print("  docker run -p 7687:7687 -p 7444:7444 memgraph/memgraph-platform")
                return 1

            stats = loader.load_rdf_file(str(rdf_path), batch_size=1000)

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

        return 0

    except ImportError as e:
        print(f"\nError: {e}")
        print("\nPlease ensure ista is installed with Memgraph support:")
        print("  pip install ista[neo4j]")
        return 1
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
