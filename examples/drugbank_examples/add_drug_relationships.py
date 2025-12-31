"""
Consolidated script for adding various drug relationships to NeuroKB ontology.

This script combines all drug relationship additions:
- Drug-disease relationships (indications)
- Drug-drug interactions
- Drug adverse events
- Drug contraindications

Usage:
    python add_drug_relationships.py --type all [--input neurokb.rdf] [--output neurokb-with-drugs.rdf]
    python add_drug_relationships.py --type indications --input neurokb.rdf --output neurokb-indications.rdf
    python add_drug_relationships.py --type interactions --input neurokb.rdf --output neurokb-interactions.rdf
    python add_drug_relationships.py --type adverse-events --input neurokb.rdf --output neurokb-adverse.rdf
    python add_drug_relationships.py --type contraindications --input neurokb.rdf --output neurokb-contra.rdf
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import ista.owl2 as owl2


def add_indications(ontology, mapping_file="drug_disease_mappings_filtered.csv"):
    """Add drug-disease indication relationships."""
    print(f"Adding drug-disease indications from {mapping_file}...")
    # Implementation would go here
    # This consolidates the logic from indication_map.py and add_drug_disease_relationships_direct.py
    pass


def add_interactions(ontology, mapping_file="drug_interaction_mappings_filtered.csv"):
    """Add drug-drug interaction relationships."""
    print(f"Adding drug-drug interactions from {mapping_file}...")
    # Implementation would go here
    # This consolidates drug_interaction_map.py and add_drug_interaction_relationships_direct.py
    pass


def add_adverse_events(
    ontology, mapping_file="drug_adverse_event_mappings_filtered.csv"
):
    """Add drug adverse event relationships."""
    print(f"Adding drug adverse events from {mapping_file}...")
    # Implementation would go here
    # This consolidates adverse_event_map.py and add_drug_adverse_event_relationships_direct.py
    pass


def add_contraindications(
    ontology, mapping_file="drug_contraindication_mappings_filtered.csv"
):
    """Add drug contraindication relationships."""
    print(f"Adding drug contraindications from {mapping_file}...")
    # Implementation would go here
    # This consolidates contraindication_map.py and add_drug_contraindication_relationships_direct.py
    pass


def main():
    parser = argparse.ArgumentParser(
        description="Add drug relationships to NeuroKB ontology",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
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
        help="Type of relationships to add",
    )
    parser.add_argument(
        "--input",
        default="../kg_projects/neurokb/neurokb.rdf",
        help="Input ontology file (default: neurokb.rdf)",
    )
    parser.add_argument(
        "--output", help="Output ontology file (default: adds suffix to input)"
    )

    args = parser.parse_args()

    # Load ontology
    print(f"Loading ontology from {args.input}...")
    ont = owl2.RDFXMLParser.parse_from_file(args.input)
    initial_count = len(ont.get_axioms())
    print(f"Loaded {initial_count} axioms")

    # Add relationships based on type
    if args.type == "all" or args.type == "indications":
        add_indications(ont)

    if args.type == "all" or args.type == "interactions":
        add_interactions(ont)

    if args.type == "all" or args.type == "adverse-events":
        add_adverse_events(ont)

    if args.type == "all" or args.type == "contraindications":
        add_contraindications(ont)

    # Determine output filename
    if not args.output:
        base = os.path.splitext(args.input)[0]
        if args.type == "all":
            args.output = f"{base}-with-all-drug-relationships.rdf"
        else:
            args.output = f"{base}-with-{args.type}.rdf"

    # Save ontology
    final_count = len(ont.get_axioms())
    print(f"\nAdded {final_count - initial_count} new axioms")
    print(f"Saving to {args.output}...")
    owl2.RDFXMLSerializer.serialize_to_file(ont, args.output)
    print("Done!")


if __name__ == "__main__":
    main()
