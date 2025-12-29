"""
Example: Adding Drug-Disease Contraindication Relationships to NeuroKB

This example demonstrates how to:
1. Load an existing RDF ontology (neurokb-populated.rdf)
2. Declare a new object property: drugContraindicatedForDisease
3. Add new drugContraindicatedForDisease relationships from a pandas DataFrame
4. Save the modified ontology

The drugContraindicatedForDisease object property will be created with:
- Domain: Chemical (drug class)
- Range: Disease

Prerequisites:
    Run contraindication_map.py first to generate drug_contraindication_mappings.csv
    Then run filter_contraindication_mappings_by_ontology.py to filter
    Or use your own CSV file with 'drugbank_id' and 'disease_id' columns
"""

from pathlib import Path

import pandas as pd

from ista import owl2

# Load the existing neurokb ontology
print("Loading neurokb ontology...")
onto = owl2.RDFXMLParser.parse_from_file("kg_projects/neurokb/neurokb-populated.rdf")

# Load drug-disease contraindication mappings from CSV
# Prefer the filtered version if it exists (contains only entities in neurokb)
filtered_mapping_file = Path("drug_contraindication_mappings_filtered.csv")
full_mapping_file = Path("drug_contraindication_mappings.csv")

if filtered_mapping_file.exists():
    print(f"\nLoading filtered contraindication mappings from {filtered_mapping_file}...")
    print("(These only include drugs/diseases that exist in neurokb)")
    df = pd.read_csv(filtered_mapping_file)
    print(f"  Loaded {len(df):,} drug-disease contraindication pairs")
elif full_mapping_file.exists():
    print(f"\nLoading mappings from {full_mapping_file}...")
    print("WARNING: This may include drugs/diseases not in neurokb.")
    print("Consider running filter_contraindication_mappings_by_ontology.py first.")
    df = pd.read_csv(full_mapping_file)
    print(f"  Loaded {len(df):,} drug-disease contraindication pairs")
else:
    print(f"\nWarning: No mapping files found!")
    print("Using sample data instead.")
    print("Run: 1) contraindication_map.py, then 2) filter_contraindication_mappings_by_ontology.py")
    # Fallback to sample data
    data = {
        "drugbank_id": ["DB00331", "DB00328"],
        "disease_id": ["C0035078", "C0856716"],
    }
    df = pd.DataFrame(data)

# Define the ontology namespace
namespace = "http://jdr.bio/ontologies/alzkb.owl#"

# Create and declare the new drugContraindicatedForDisease object property
print("\nCreating new object property: drugContraindicatedForDisease")
drug_contraindicated_iri = owl2.IRI(namespace + "drugContraindicatedForDisease")
drug_contraindicated_prop = owl2.ObjectProperty(drug_contraindicated_iri)

# Declare the property in the ontology
onto.add_axiom(owl2.Declaration(owl2.EntityType.OBJECT_PROPERTY, drug_contraindicated_iri))
print("  ✓ Property declared")

# Set domain and range
# Domain: Chemical (the drug class in neurokb)
# Range: Disease
chemical_class_iri = owl2.IRI(namespace + "Chemical")
disease_class_iri = owl2.IRI(namespace + "Disease")

chemical_class = owl2.Class(chemical_class_iri)
disease_class = owl2.Class(disease_class_iri)

onto.add_axiom(owl2.ObjectPropertyDomain(drug_contraindicated_prop, chemical_class))
onto.add_axiom(owl2.ObjectPropertyRange(drug_contraindicated_prop, disease_class))
print("  ✓ Domain set to Chemical")
print("  ✓ Range set to Disease")

# Note: We're skipping individual validation because the ista RDF parser
# may not extract individuals from typed declarations in RDF/XML.
# The individuals already exist in the loaded ontology, so we can safely
# add property assertions referencing them.

print(f"\nAdding {len(df):,} drugContraindicatedForDisease relationships...")
print("(First 10 shown below)")

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

    # Add the contraindication relationship assertion
    onto.add_axiom(
        owl2.ObjectPropertyAssertion(drug_contraindicated_prop, drug_ind, disease_ind)
    )

    added_count += 1
    if added_count <= 10:  # Print first 10 additions
        print(f"  {added_count}. {row['drugbank_id']} contraindicated for {row['disease_id']}")

# Print summary
print(f"\nCompleted!")
print(f"  Total contraindication relationships added: {added_count:,}")

# Save the modified ontology
output_file = "kg_projects/neurokb/neurokb-with-contraindications.rdf"
print(f"\nSaving modified ontology to {output_file}...")
owl2.RDFXMLSerializer.serialize_to_file(onto, output_file)

print("Done!")
print(f"\nOntology statistics:")
print(f"  Total axioms: {onto.get_axiom_count()}")
