"""
Example: Adding Drug-Disease Relationships to NeuroKB

This example demonstrates how to:
1. Load an existing RDF ontology (neurokb-populated.rdf)
2. Add new drugTreatsDisease relationships from a pandas DataFrame
3. Save the modified ontology

The drugTreatsDisease object property already exists in the neurokb ontology
with domain Chemical and range Disease.

Prerequisites:
    Run indication_map.py first to generate drug_disease_mappings.csv
    Or use your own CSV file with 'drugbank_id' and 'disease_id' columns
"""

from pathlib import Path

import pandas as pd

from ista import owl2

# Load the existing neurokb ontology
print("Loading neurokb ontology...")
onto = owl2.RDFXMLParser.parse_from_file("kg_projects/neurokb/neurokb-populated.rdf")

# Load drug-disease mappings from CSV
# Prefer the filtered version if it exists (contains only entities in neurokb)
filtered_mapping_file = Path("drug_disease_mappings_filtered.csv")
full_mapping_file = Path("drug_disease_mappings.csv")

if filtered_mapping_file.exists():
    print(f"\nLoading filtered mappings from {filtered_mapping_file}...")
    print("(These only include drugs/diseases that exist in neurokb)")
    df = pd.read_csv(filtered_mapping_file)
    print(f"  Loaded {len(df):,} drug-disease pairs")
elif full_mapping_file.exists():
    print(f"\nLoading mappings from {full_mapping_file}...")
    print("WARNING: This may include drugs/diseases not in neurokb.")
    print("Consider running filter_mappings_by_ontology.py first.")
    df = pd.read_csv(full_mapping_file)
    print(f"  Loaded {len(df):,} drug-disease pairs")
else:
    print(f"\nWarning: No mapping files found!")
    print("Using sample data instead.")
    print("Run: 1) indication_map.py, then 2) filter_mappings_by_ontology.py")
    # Fallback to sample data
    data = {
        "drugbank_id": ["DB00001", "DB00002", "DB00003"],
        "disease_id": ["C0002395", "C0002736", "C0004135"],
    }
    df = pd.DataFrame(data)

# Define the ontology namespace and drugTreatsDisease property
namespace = "http://jdr.bio/ontologies/alzkb.owl#"
drug_treats_iri = owl2.IRI(namespace + "drugTreatsDisease")
drug_treats_prop = owl2.ObjectProperty(drug_treats_iri)

# Note: We're skipping individual validation because the ista RDF parser
# may not extract individuals from typed declarations in RDF/XML.
# The individuals already exist in the loaded ontology, so we can safely
# add property assertions referencing them.

print(f"\nAdding {len(df):,} drugTreatsDisease relationships...")
print("(Adding first 10 shown below)")

added_count = 0

# Add object property assertions for each row in the DataFrame
for idx, row in df.iterrows():
    # Convert IDs to individual IRIs following neurokb naming conventions
    # Drugs: #drug_{drugbank_id_lowercase}
    # Diseases: #disease_{umls_cui_lowercase}
    drug_id_lower = row["drugbank_id"].lower()
    disease_id_lower = row["disease_id"].lower()

    drug_iri = owl2.IRI(namespace + f"drug_{drug_id_lower}")
    disease_iri = owl2.IRI(namespace + f"disease_{disease_id_lower}")

    drug_ind = owl2.NamedIndividual(drug_iri)
    disease_ind = owl2.NamedIndividual(disease_iri)

    # Add the relationship assertion
    onto.add_axiom(
        owl2.ObjectPropertyAssertion(drug_treats_prop, drug_ind, disease_ind)
    )

    added_count += 1
    if added_count <= 10:  # Print first 10 additions
        print(f"  {added_count}. {row['drugbank_id']} treats {row['disease_id']}")

# Print summary
print(f"\nCompleted!")
print(f"  Total relationships added: {added_count:,}")

# Save the modified ontology
output_file = "kg_projects/neurokb/neurokb-with-indications.rdf"
print(f"\nSaving modified ontology to {output_file}...")
owl2.RDFXMLSerializer.serialize_to_file(onto, output_file)

print("Done!")
print(f"\nOntology statistics:")
print(f"  Total axioms: {onto.get_axiom_count()}")
