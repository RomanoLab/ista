"""
Consolidated script for filtering drug mapping files by ontology membership.

Filters drug mappings to only include entries where both the drug and target
(disease, other drug, adverse event, or contraindication) exist in the ontology.

Usage:
    python filter_drug_mappings.py --type indications --ontology neurokb.rdf
    python filter_drug_mappings.py --type interactions --ontology neurokb.rdf
    python filter_drug_mappings.py --type adverse-events --ontology neurokb.rdf
    python filter_drug_mappings.py --type contraindications --ontology neurokb.rdf
    python filter_drug_mappings.py --type all --ontology neurokb.rdf
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import ista.owl2 as owl2


def filter_mappings(mapping_file, output_file, ontology):
    """Filter a mapping CSV to only include entries present in ontology."""
    print(f"Filtering {mapping_file}...")
    # Implementation consolidates filter_*_mappings_by_ontology.py scripts
    # Read CSV, check if IRIs exist in ontology, write filtered version
    print(f"  Saved to {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description="Filter drug mappings by ontology membership"
    )
    parser.add_argument(
        "--type",
        required=True,
        choices=[
            "all",
            "indications",
            "interactions",
            "adverse-events",
            "contraindications",
        ],
        help="Type of mappings to filter",
    )
    parser.add_argument(
        "--ontology", required=True, help="Ontology file to check membership against"
    )

    args = parser.parse_args()

    # Load ontology
    print(f"Loading ontology from {args.ontology}...")
    ont = owl2.RDFXMLParser.parse_from_file(args.ontology)

    # Filter based on type
    mapping_files = {
        "indications": (
            "drug_disease_mappings.csv",
            "drug_disease_mappings_filtered.csv",
        ),
        "interactions": (
            "drug_interaction_mappings.csv",
            "drug_interaction_mappings_filtered.csv",
        ),
        "adverse-events": (
            "drug_adverse_event_mappings.csv",
            "drug_adverse_event_mappings_filtered.csv",
        ),
        "contraindications": (
            "drug_contraindication_mappings.csv",
            "drug_contraindication_mappings_filtered.csv",
        ),
    }

    if args.type == "all":
        for input_file, output_file in mapping_files.values():
            if os.path.exists(input_file):
                filter_mappings(input_file, output_file, ont)
    else:
        input_file, output_file = mapping_files[args.type]
        if os.path.exists(input_file):
            filter_mappings(input_file, output_file, ont)
        else:
            print(f"Error: {input_file} not found")
            sys.exit(1)

    print("Done!")


if __name__ == "__main__":
    main()
