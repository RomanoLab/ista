"""
Example: Adding Both Drug Indication and Contraindication Relationships (Direct RDF)

This example demonstrates how to:
1. Read an existing RDF ontology file
2. Declare a new drugContraindicatedForDisease property
3. Add drugTreatsDisease relationships (indications)
4. Add drugContraindicatedForDisease relationships (contraindications)
5. Save the modified ontology while preserving all original content

This approach directly modifies the RDF file to avoid data loss.

Prerequisites:
    Run indication_map.py and filter_mappings_by_ontology.py
    Run contraindication_map.py and filter_contraindication_mappings_by_ontology.py
"""

from pathlib import Path
import pandas as pd
from datetime import datetime
import re

print("=" * 70)
print("Adding Drug-Disease Relationships to NeuroKB")
print("=" * 70)

# Load indication mappings
indication_file = Path("drug_disease_mappings_filtered.csv")
if indication_file.exists():
    print(f"\nLoading indications from {indication_file}...")
    df_indications = pd.read_csv(indication_file)
    print(f"  Loaded {len(df_indications):,} indication pairs")
else:
    print("\n⚠ Warning: drug_disease_mappings_filtered.csv not found. Skipping indications.")
    df_indications = pd.DataFrame(columns=['drugbank_id', 'disease_id'])

# Load contraindication mappings
contraindication_file = Path("drug_contraindication_mappings_filtered.csv")
if contraindication_file.exists():
    print(f"\nLoading contraindications from {contraindication_file}...")
    df_contraindications = pd.read_csv(contraindication_file)
    print(f"  Loaded {len(df_contraindications):,} contraindication pairs")
else:
    print("\n⚠ Warning: drug_contraindication_mappings_filtered.csv not found. Skipping contraindications.")
    df_contraindications = pd.DataFrame(columns=['drugbank_id', 'disease_id'])

# Read the original RDF file
input_file = "kg_projects/neurokb/neurokb-populated.rdf"
print(f"\nReading original RDF file: {input_file}")
input_path = Path(input_file)

with open(input_path, 'r', encoding='utf-8') as f:
    rdf_content = f.read()

original_size = input_path.stat().st_size
print(f"  Original file size: {original_size:,} bytes")

# ============================================================================
# STEP 1: Add drugContraindicatedForDisease property declaration
# ============================================================================
if len(df_contraindications) > 0:
    print("\nAdding drugContraindicatedForDisease property declaration...")

    # Find where to insert the new property declaration
    last_obj_prop_pattern = r'(<owl:ObjectProperty[^>]*>.*?</owl:ObjectProperty>)'
    matches = list(re.finditer(last_obj_prop_pattern, rdf_content, re.DOTALL))

    if not matches:
        raise ValueError("Could not find any ObjectProperty declarations")

    insertion_point = matches[-1].end()

    # Create the new property declaration
    new_property_decl = """
    <owl:ObjectProperty rdf:about="#drugContraindicatedForDisease">
        <rdfs:domain rdf:resource="#Chemical"/>
        <rdfs:range rdf:resource="#Disease"/>
        <rdfs:subPropertyOf rdf:resource="#chemicalObjectProperty"/>
        <rdfs:comment xml:lang="en">Indicates that a drug is contraindicated for a specific disease or condition.</rdfs:comment>
    </owl:ObjectProperty>
"""

    # Insert the property
    rdf_content = rdf_content[:insertion_point] + new_property_decl + rdf_content[insertion_point:]
    print("  Property declared")

# ============================================================================
# STEP 2: Find insertion point for new assertions (before closing tag)
# ============================================================================
closing_tag = "</rdf:RDF>"
closing_pos = rdf_content.rfind(closing_tag)

if closing_pos == -1:
    raise ValueError("Could not find closing </rdf:RDF> tag")

content_before_close = rdf_content[:closing_pos]
content_closing = rdf_content[closing_pos:]

# ============================================================================
# STEP 3: Generate indication assertions
# ============================================================================
all_assertions = []

if len(df_indications) > 0:
    print(f"\nGenerating {len(df_indications):,} indication relationships...")

    all_assertions.append("\n    <!-- Drug-Disease Treatment Relationships (Indications) -->")
    all_assertions.append(f"    <!-- Added on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} -->")
    all_assertions.append("")

    for idx, row in df_indications.iterrows():
        drug_id_lower = row["drugbank_id"].lower()
        disease_id_lower = row["disease_id"].lower()

        assertion = f"""    <owl:NamedIndividual rdf:about="#drug_{drug_id_lower}">
        <drugTreatsDisease rdf:resource="#disease_{disease_id_lower}"/>
    </owl:NamedIndividual>
"""
        all_assertions.append(assertion)

    print(f"  Generated {len(df_indications):,} indication assertions")

# ============================================================================
# STEP 4: Generate contraindication assertions
# ============================================================================
if len(df_contraindications) > 0:
    print(f"\nGenerating {len(df_contraindications):,} contraindication relationships...")

    all_assertions.append("\n    <!-- Drug-Disease Contraindication Relationships -->")
    all_assertions.append(f"    <!-- Added on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} -->")
    all_assertions.append("")

    for idx, row in df_contraindications.iterrows():
        drug_id_lower = row["drugbank_id"].lower()
        disease_id_lower = row["disease_id"].lower()

        assertion = f"""    <owl:NamedIndividual rdf:about="#drug_{drug_id_lower}">
        <drugContraindicatedForDisease rdf:resource="#disease_{disease_id_lower}"/>
    </owl:NamedIndividual>
"""
        all_assertions.append(assertion)

    print(f"  Generated {len(df_contraindications):,} contraindication assertions")

# ============================================================================
# STEP 5: Combine and save
# ============================================================================
new_rdf_content = content_before_close + "\n".join(all_assertions) + "\n" + content_closing

output_file = "kg_projects/neurokb/neurokb-with-drug-relationships.rdf"
print(f"\nSaving modified ontology to {output_file}...")

with open(output_file, 'w', encoding='utf-8') as f:
    f.write(new_rdf_content)

output_size = Path(output_file).stat().st_size
print(f"  Output file size: {output_size:,} bytes")

# ============================================================================
# Summary
# ============================================================================
print("\n" + "=" * 70)
print("Summary")
print("=" * 70)
print(f"  Original file size:     {original_size:,} bytes")
print(f"  Modified file size:     {output_size:,} bytes")
print(f"  Content added:          {output_size - original_size:,} bytes")
print(f"\n  Indications added:      {len(df_indications):,}")
print(f"  Contraindications added: {len(df_contraindications):,}")
print(f"  Total relationships:    {len(df_indications) + len(df_contraindications):,}")
print(f"\n  Preserved all original content")
print(f"  Output: {output_file}")
print("\nDone!")
