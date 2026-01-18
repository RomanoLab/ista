"""
NeuroKB Knowledge Graph Population Script

This script populates the NeuroKB ontology with data from various biomedical sources
using the new DataLoader API with YAML mapping specifications.

Data sources (all configured in neurokb_mapping.yaml):
    - DrugBank: Drug information and identifiers (CSV)
    - NCBI Gene: Human gene data (TSV)
    - Hetionet: Biomedical knowledge graph nodes and edges (TSV)
    - DisGeNET: Disease-gene associations (TSV)
    - AOP-DB: Adverse Outcome Pathway database (MySQL)

Usage:
    Set the required environment variables:

    For flat file sources:
        export DATA_DIR=/path/to/data  (Linux/Mac)
        set DATA_DIR=D:\\data          (Windows)

    For MySQL sources (AOP-DB):
        export MYSQL_HOST=localhost
        export MYSQL_USER=username
        export MYSQL_PASSWORD=password

    Then run:
        python neurokb_new.py

Note:
    All data source connections (including MySQL) are now configured in the
    YAML mapping specification. The DataLoader handles both file-based and
    database sources transparently.
"""

import os
import sys

from ista import owl2
from ista.util import print_onto_stats


def load_from_yaml_spec(onto: owl2.Ontology, mapping_file: str) -> owl2.LoadingStats:
    """
    Load data into the ontology using a YAML mapping specification.

    Parameters
    ----------
    onto : owl2.Ontology
        The ontology to populate.
    mapping_file : str
        Path to the YAML mapping specification file.

    Returns
    -------
    owl2.LoadingStats
        Statistics about the loading process.
    """
    # Create loader
    loader = owl2.DataLoader(onto)

    # Load mapping specification
    print(f"Loading mapping specification from: {mapping_file}")
    loader.load_mapping_spec(mapping_file)

    # Set up progress callback
    def on_progress(current: int, total: int, mapping_name: str):
        if total > 0:
            pct = (current / total) * 100
            print(f"  {mapping_name}: {current}/{total} ({pct:.1f}%)")
        else:
            # Total unknown, just show current count
            if current % 1000 == 0:
                print(f"  {mapping_name}: {current} rows processed...")

    loader.set_progress_callback(on_progress)

    # Validate before loading
    print("\nValidating mapping specification against ontology...")
    result = loader.validate()

    if not result.is_valid:
        print("Validation FAILED:")
        for error in result.errors:
            print(f"  ERROR: {error}")
        sys.exit(1)

    if result.warnings:
        print("Validation warnings:")
        for warning in result.warnings:
            print(f"  WARNING: {warning}")

    print("Validation passed.\n")

    # Execute all mappings
    print("Executing data loading...")
    print("-" * 60)

    stats = loader.execute()

    print("-" * 60)
    print("\nLoading complete.")
    print(stats.summary())

    return stats


def check_environment():
    """Check that required environment variables are set."""
    missing = []

    # DATA_DIR is required for flat file sources
    if not os.environ.get("DATA_DIR"):
        missing.append("DATA_DIR")

    # MySQL variables are optional but warn if missing
    mysql_vars = ["MYSQL_HOST", "MYSQL_USER", "MYSQL_PASSWORD"]
    missing_mysql = [v for v in mysql_vars if not os.environ.get(v)]

    if missing:
        print("ERROR: Required environment variables not set:")
        for var in missing:
            print(f"  - {var}")
        print("\nPlease set the required environment variables:")
        print("  Linux/Mac: export DATA_DIR=/path/to/data")
        print("  Windows:   set DATA_DIR=D:\\data")
        sys.exit(1)

    if missing_mysql:
        print("WARNING: MySQL environment variables not set. AOP-DB sources will fail:")
        for var in missing_mysql:
            print(f"  - {var}")
        print("\nTo enable MySQL sources, set:")
        print("  MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD")
        print("")


def main():
    """Main entry point for NeuroKB population script."""
    # Configuration
    script_dir = os.path.dirname(os.path.abspath(__file__))
    ontology_file = os.path.join(script_dir, "neurokb.rdf")
    mapping_file = os.path.join(script_dir, "neurokb_mapping.yaml")
    output_file = os.path.join(script_dir, "neurokb-populated.rdf")

    # Check environment variables
    check_environment()

    data_dir = os.environ.get("DATA_DIR")

    print("=" * 60)
    print("NeuroKB Knowledge Graph Population")
    print("=" * 60)
    print(f"Ontology file: {ontology_file}")
    print(f"Mapping file:  {mapping_file}")
    print(f"Data directory: {data_dir}")
    print(f"Output file:   {output_file}")
    print("=" * 60)

    # Load ontology
    print("\nLoading base ontology...")
    onto = owl2.RDFXMLParser.parse_from_file(ontology_file)
    print("Ontology loaded successfully.")

    # Load all data from YAML mapping specification
    # This includes both file-based sources (CSV, TSV) and database sources (MySQL)
    stats = load_from_yaml_spec(onto, mapping_file)

    # Print final statistics
    print("\n" + "=" * 60)
    print("Final Ontology Statistics")
    print("=" * 60)
    print_onto_stats(onto)

    # Save populated ontology
    print(f"\nSaving populated ontology to: {output_file}")
    owl2.RDFXMLSerializer.serialize_to_file(onto, output_file)
    print("Done!")


if __name__ == "__main__":
    main()
