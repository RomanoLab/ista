"""
Filter drug-disease contraindication mappings to only include entities that exist in neurokb

This script reads the RDF file directly (not through the parser) to find
which drugs and diseases actually exist, then filters the mappings accordingly.
"""

import pandas as pd
import re

# Read the RDF file to find existing drugs and diseases
print("Reading neurokb RDF file...")
rdf_file = "kg_projects/neurokb/neurokb-populated.rdf"

with open(rdf_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Extract drug and disease IRIs using regex
drug_pattern = r'<Drug rdf:about="#drug_([^"]+)">'
disease_pattern = r'<Disease rdf:about="#disease_([^"]+)">'

drug_ids_in_rdf = set(re.findall(drug_pattern, content))
disease_ids_in_rdf = set(re.findall(disease_pattern, content))

print(f"  Found {len(drug_ids_in_rdf):,} drugs in neurokb")
print(f"  Found {len(disease_ids_in_rdf):,} diseases in neurokb")

# Load the contraindication mappings
print("\nLoading drug_contraindication_mappings.csv...")
df = pd.read_csv("drug_contraindication_mappings.csv")
print(f"  Total mappings: {len(df):,}")

# Convert drugbank IDs and disease IDs to the format used in RDF
# Drugs: "DB00001" -> "db00001"
# Diseases: "C0002395" -> "c0002395"
df['drug_id_rdf'] = df['drugbank_id'].str.lower()
df['disease_id_rdf'] = df['disease_id'].str.lower()

# Filter to only include rows where both entities exist
print("\nFiltering mappings...")
df_filtered = df[
    df['drug_id_rdf'].isin(drug_ids_in_rdf) &
    df['disease_id_rdf'].isin(disease_ids_in_rdf)
].copy()

# Drop the temporary columns
df_filtered = df_filtered.drop(columns=['drug_id_rdf', 'disease_id_rdf'])

print(f"  Mappings after filtering: {len(df_filtered):,}")
print(f"  Removed: {len(df) - len(df_filtered):,}")

# Show breakdown of what was removed
drugs_not_in_ontology = df[~df['drug_id_rdf'].isin(drug_ids_in_rdf)]['drugbank_id'].nunique()
diseases_not_in_ontology = df[~df['disease_id_rdf'].isin(disease_ids_in_rdf)]['disease_id'].nunique()

print(f"\nDrugs in mappings but not in neurokb: {drugs_not_in_ontology:,}")
print(f"Diseases in mappings but not in neurokb: {diseases_not_in_ontology:,}")

# Save filtered mappings
output_file = "drug_contraindication_mappings_filtered.csv"
df_filtered.to_csv(output_file, index=False)
print(f"\nSaved filtered mappings to: {output_file}")

print("\nSummary:")
print(f"  Original: {len(df):,} contraindication mappings")
print(f"  Filtered: {len(df_filtered):,} mappings")
print(f"  Unique drugs: {df_filtered['drugbank_id'].nunique():,}")
print(f"  Unique diseases: {df_filtered['disease_id'].nunique():,}")
