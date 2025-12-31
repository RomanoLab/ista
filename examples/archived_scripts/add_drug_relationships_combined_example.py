"""
Example: Adding Both Drug Indication and Contraindication Relationships to NeuroKB

This example demonstrates how to:
1. Load an existing RDF ontology (neurokb-populated.rdf)
2. Add drugTreatsDisease relationships (indications)
3. Create and add drugContraindicatedForDisease relationships (contraindications)
4. Save the modified ontology with both types of relationships

Prerequisites:
    Run indication_map.py and filter_mappings_by_ontology.py for indications
    Run contraindication_map.py and filter_contraindication_mappings_by_ontology.py for contraindications
"""

from pathlib import Path

import pandas as pd

from ista import owl2

# Load the existing neurokb ontology
print("=" * 70)
print("Loading NeuroKB Ontology and Adding Drug-Disease Relationships")
print("=" * 70)
print("\nLoading neurokb ontology...")
onto = owl2.RDFXMLParser.parse_from_file("kg_projects/neurokb/neurokb-populated.rdf")
print(f"  Initial axiom count: {onto.get_axiom_count():,}")

# Define the ontology namespace
namespace = "http://jdr.bio/ontologies/alzkb.owl#"

# ============================================================================
# PART 1: Add Drug Indication Relationships (drugTreatsDisease)
# ============================================================================
print("\n" + "=" * 70)
print("PART 1: Adding Drug Indications (drugTreatsDisease)")
print("=" * 70)

# Load indication mappings
indication_file = Path("drug_disease_mappings_filtered.csv")
if indication_file.exists():
    print(f"\nLoading indications from {indication_file}...")
    df_indications = pd.read_csv(indication_file)
    print(f"  Loaded {len(df_indications):,} drug-disease indication pairs")
else:
    print("\nWarning: drug_disease_mappings_filtered.csv not found. Skipping indications.")
    df_indications = pd.DataFrame(columns=['drugbank_id', 'disease_id'])

if len(df_indications) > 0:
    # Use existing drugTreatsDisease property
    drug_treats_iri = owl2.IRI(namespace + "drugTreatsDisease")
    drug_treats_prop = owl2.ObjectProperty(drug_treats_iri)

    print(f"Adding {len(df_indications):,} indication relationships...")
    indication_count = 0

    for idx, row in df_indications.iterrows():
        drug_id_lower = row["drugbank_id"].lower()
        disease_id_lower = row["disease_id"].lower()

        drug_iri = owl2.IRI(namespace + f"drug_{drug_id_lower}")
        disease_iri = owl2.IRI(namespace + f"disease_{disease_id_lower}")

        drug_ind = owl2.NamedIndividual(drug_iri)
        disease_ind = owl2.NamedIndividual(disease_iri)

        onto.add_axiom(
            owl2.ObjectPropertyAssertion(drug_treats_prop, drug_ind, disease_ind)
        )

        indication_count += 1
        if indication_count <= 5:
            print(f"  {indication_count}. {row['drugbank_id']} treats {row['disease_id']}")

    if indication_count > 5:
        print(f"  ... and {indication_count - 5} more")

    print(f"\n✓ Added {indication_count:,} indication relationships")
else:
    indication_count = 0
    print("✗ No indications to add")

# ============================================================================
# PART 2: Add Drug Contraindication Relationships (drugContraindicatedForDisease)
# ============================================================================
print("\n" + "=" * 70)
print("PART 2: Adding Drug Contraindications (drugContraindicatedForDisease)")
print("=" * 70)

# Load contraindication mappings
contraindication_file = Path("drug_contraindication_mappings_filtered.csv")
if contraindication_file.exists():
    print(f"\nLoading contraindications from {contraindication_file}...")
    df_contraindications = pd.read_csv(contraindication_file)
    print(f"  Loaded {len(df_contraindications):,} drug-disease contraindication pairs")
else:
    print("\nWarning: drug_contraindication_mappings_filtered.csv not found. Skipping contraindications.")
    df_contraindications = pd.DataFrame(columns=['drugbank_id', 'disease_id'])

if len(df_contraindications) > 0:
    # Create new drugContraindicatedForDisease property
    print("\nCreating new object property: drugContraindicatedForDisease")
    drug_contraindicated_iri = owl2.IRI(namespace + "drugContraindicatedForDisease")
    drug_contraindicated_prop = owl2.ObjectProperty(drug_contraindicated_iri)

    # Declare the property
    onto.add_axiom(owl2.Declaration(owl2.EntityType.OBJECT_PROPERTY, drug_contraindicated_iri))

    # Set domain and range
    chemical_class_iri = owl2.IRI(namespace + "Chemical")
    disease_class_iri = owl2.IRI(namespace + "Disease")
    chemical_class = owl2.Class(chemical_class_iri)
    disease_class = owl2.Class(disease_class_iri)

    onto.add_axiom(owl2.ObjectPropertyDomain(drug_contraindicated_prop, chemical_class))
    onto.add_axiom(owl2.ObjectPropertyRange(drug_contraindicated_prop, disease_class))

    print("  ✓ Property declared with domain: Chemical, range: Disease")

    print(f"\nAdding {len(df_contraindications):,} contraindication relationships...")
    contraindication_count = 0

    for idx, row in df_contraindications.iterrows():
        drug_id_lower = row["drugbank_id"].lower()
        disease_id_lower = row["disease_id"].lower()

        drug_iri = owl2.IRI(namespace + f"drug_{drug_id_lower}")
        disease_iri = owl2.IRI(namespace + f"disease_{disease_id_lower}")

        drug_ind = owl2.NamedIndividual(drug_iri)
        disease_ind = owl2.NamedIndividual(disease_iri)

        onto.add_axiom(
            owl2.ObjectPropertyAssertion(drug_contraindicated_prop, drug_ind, disease_ind)
        )

        contraindication_count += 1
        if contraindication_count <= 5:
            print(f"  {contraindication_count}. {row['drugbank_id']} contraindicated for {row['disease_id']}")

    if contraindication_count > 5:
        print(f"  ... and {contraindication_count - 5} more")

    print(f"\n✓ Added {contraindication_count:,} contraindication relationships")
else:
    contraindication_count = 0
    print("✗ No contraindications to add")

# ============================================================================
# PART 3: Save Modified Ontology
# ============================================================================
print("\n" + "=" * 70)
print("PART 3: Saving Modified Ontology")
print("=" * 70)

output_file = "kg_projects/neurokb/neurokb-with-drug-relationships.rdf"
print(f"\nSaving modified ontology to {output_file}...")
owl2.RDFXMLSerializer.serialize_to_file(onto, output_file)

print("\n" + "=" * 70)
print("Summary")
print("=" * 70)
print(f"  Indication relationships added: {indication_count:,}")
print(f"  Contraindication relationships added: {contraindication_count:,}")
print(f"  Total new relationships: {indication_count + contraindication_count:,}")
print(f"\n  Final axiom count: {onto.get_axiom_count():,}")
print(f"  Output file: {output_file}")
print("\n✓ Done!")
