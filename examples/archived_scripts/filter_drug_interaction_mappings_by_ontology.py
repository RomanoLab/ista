"""
Filter drug-drug interaction mappings to only include drugs that exist in neurokb

This script reads the RDF file directly (not through the parser) to find
which drugs actually exist, then filters the interactions accordingly.
"""

import pandas as pd
import re

# Read the RDF file to find existing drugs
print("Reading neurokb RDF file...")
rdf_file = "kg_projects/neurokb/neurokb-populated.rdf"

with open(rdf_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Extract drug IRIs using regex
drug_pattern = r'<Drug rdf:about="#drug_([^"]+)">'
drug_ids_in_rdf = set(re.findall(drug_pattern, content))

print(f"  Found {len(drug_ids_in_rdf):,} drugs in neurokb")

# Load the drug interaction mappings
print("\nLoading drug_interaction_mappings.csv...")
df = pd.read_csv("drug_interaction_mappings.csv")
print(f"  Total mappings: {len(df):,}")

# Convert drugbank IDs to the format used in RDF
# Drugs: "DB00001" -> "db00001"
df['subject_drug_id_rdf'] = df['subject_drugbank_id'].str.lower()
df['affected_drug_id_rdf'] = df['affected_drugbank_id'].str.lower()

# Filter to only include rows where BOTH drugs exist in the ontology
print("\nFiltering mappings...")
df_filtered = df[
    df['subject_drug_id_rdf'].isin(drug_ids_in_rdf) &
    df['affected_drug_id_rdf'].isin(drug_ids_in_rdf)
].copy()

# Drop the temporary columns
df_filtered = df_filtered.drop(columns=['subject_drug_id_rdf', 'affected_drug_id_rdf'])

print(f"  Mappings after filtering: {len(df_filtered):,}")
print(f"  Removed: {len(df) - len(df_filtered):,}")

# Show breakdown of what was removed
subject_drugs_not_in_ontology = df[~df['subject_drug_id_rdf'].isin(drug_ids_in_rdf)]['subject_drugbank_id'].nunique()
affected_drugs_not_in_ontology = df[~df['affected_drug_id_rdf'].isin(drug_ids_in_rdf)]['affected_drugbank_id'].nunique()
both_in_ontology = df[
    df['subject_drug_id_rdf'].isin(drug_ids_in_rdf) &
    df['affected_drug_id_rdf'].isin(drug_ids_in_rdf)
]['subject_drugbank_id'].nunique()

print(f"\nSubject drugs in mappings but not in neurokb: {subject_drugs_not_in_ontology:,}")
print(f"Affected drugs in mappings but not in neurokb: {affected_drugs_not_in_ontology:,}")
print(f"Drugs with interactions in neurokb: {both_in_ontology:,}")

# Save filtered mappings
output_file = "drug_interaction_mappings_filtered.csv"
df_filtered.to_csv(output_file, index=False)
print(f"\nSaved filtered mappings to: {output_file}")

print("\nSummary:")
print(f"  Original: {len(df):,} drug-drug interaction pairs (major severity)")
print(f"  Filtered: {len(df_filtered):,} interaction pairs")
print(f"  Unique subject drugs: {df_filtered['subject_drugbank_id'].nunique():,}")
print(f"  Unique affected drugs: {df_filtered['affected_drugbank_id'].nunique():,}")
