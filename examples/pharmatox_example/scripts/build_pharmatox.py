"""
PharmaTox Knowledge Graph Builder (YAML-Driven)

This script demonstrates building a biomedical knowledge graph using ISTA's
YAML-driven DataLoader pipeline. A single YAML mapping file declares all
classes, properties, data sources, and relationships — no manual schema
declaration or data wrangling needed.

IMPORTANT: This is a TOY EXAMPLE using SYNTHETIC DATA for testing and
demonstration purposes only. The relationships between drugs, genes, diseases,
etc. are fictitious and should NOT be used for any real biomedical research.
"""

import sys
from pathlib import Path

# Fix encoding for Windows console
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

from ista import owl2


def main():
    """Main entry point."""
    print("=" * 60)
    print("PHARMATOX KNOWLEDGE GRAPH BUILDER (YAML Pipeline)")
    print("=" * 60)
    print("\nThis example demonstrates building a biomedical knowledge graph")
    print("from multiple data sources using a single YAML mapping file.")
    print("\nIMPORTANT: This is a TOY EXAMPLE with SYNTHETIC DATA!")
    print("Do not use for real biomedical research.\n")

    # Check if owl2 is available
    if not owl2.is_available():
        print("ERROR: C++ OWL2 bindings are not available!")
        print("Please build the C++ extension first.")
        return 1

    print("C++ OWL2 bindings are available\n")

    # Determine paths
    script_dir = Path(__file__).parent
    example_dir = script_dir.parent
    config_file = example_dir / "config" / "pharmatox_mapping.yaml"
    output_file = example_dir / "pharmatox_populated.owl"

    # Check that SQLite database exists
    if not (example_dir / "data" / "pharmatox.db").exists():
        print("Database not found. Creating it first...")
        import subprocess

        subprocess.run([sys.executable, script_dir / "create_sqlite_db.py"])

    # Build the knowledge graph using YAML-driven pipeline
    print("[Step 1] Creating ontology and loading mapping spec...")
    onto = owl2.Ontology(owl2.IRI("http://example.org/pharmatox"))
    onto.register_prefix("ptox", "http://example.org/pharmatox#")

    loader = owl2.DataLoader(onto)
    loader.load_mapping_spec(str(config_file))

    print("[Step 2] Executing mappings (auto-schema + batch mode)...")
    stats = loader.execute()

    print("\n" + stats.summary())

    print("\n" + "=" * 60)
    print("PHARMATOX KNOWLEDGE GRAPH STATISTICS")
    print("=" * 60)
    print(onto.get_statistics())

    print(f"\n[Step 3] Saving ontology to {output_file}...")
    owl2.RDFXMLSerializer.serialize_to_file(onto, str(output_file))
    print("  Done!")

    print("\n" + "=" * 60)
    print("BUILD COMPLETE!")
    print("=" * 60)
    print(f"\nOutput: {output_file}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
