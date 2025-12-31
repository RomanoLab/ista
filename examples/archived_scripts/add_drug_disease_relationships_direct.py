"""
Example: Adding Drug-Disease Relationships to NeuroKB (Direct RDF Modification)

This example demonstrates how to:
1. Read an existing RDF ontology file
2. Add new drugTreatsDisease relationships by directly modifying the RDF
3. Save the modified ontology while preserving all original content

This approach avoids data loss that occurs when using RDFXMLParser.parse_from_file()
followed by RDFXMLSerializer.serialize_to_file(), which only preserves TBox (classes
and properties) but loses ABox (individuals and their assertions).

Prerequisites:
    Run indication_map.py first to generate drug_disease_mappings.csv
    Then run filter_mappings_by_ontology.py to filter
"""

from pathlib import Path
import pandas as pd
from datetime import datetime

# Load drug-disease mappings from CSV
filtered_mapping_file = Path("drug_disease_mappings_filtered.csv")
full_mapping_file = Path("drug_disease_mappings.csv")

if filtered_mapping_file.exists():
    print(f"Loading filtered mappings from {filtered_mapping_file}...")
    print("(These only include drugs/diseases that exist in neurokb)")
    df = pd.read_csv(filtered_mapping_file)
    print(f"  Loaded {len(df):,} drug-disease pairs")
elif full_mapping_file.exists():
    print(f"Loading mappings from {full_mapping_file}...")
    print("WARNING: This may include drugs/diseases not in neurokb.")
    df = pd.read_csv(full_mapping_file)
    print(f"  Loaded {len(df):,} drug-disease pairs")
else:
    print("Warning: No mapping files found!")
    print("Run: 1) indication_map.py, then 2) filter_mappings_by_ontology.py")
    data = {
        "drugbank_id": ["DB00001", "DB00002", "DB00003"],
        "disease_id": ["C0002395", "C0002736", "C0004135"],
    }
    df = pd.DataFrame(data)

# Read the original RDF file
input_file = "kg_projects/neurokb/neurokb-populated.rdf"
print(f"\nReading original RDF file: {input_file}")
input_path = Path(input_file)

with open(input_path, 'r', encoding='utf-8') as f:
    rdf_content = f.read()

original_size = input_path.stat().st_size
print(f"  Original file size: {original_size:,} bytes")

# Find the closing </rdf:RDF> tag
closing_tag = "</rdf:RDF>"
closing_pos = rdf_content.rfind(closing_tag)

if closing_pos == -1:
    raise ValueError("Could not find closing </rdf:RDF> tag in input file")

# Split content: everything before the closing tag, and the closing tag itself
content_before_close = rdf_content[:closing_pos]
content_closing = rdf_content[closing_pos:]

# Generate RDF for new property assertions
print(f"\nGenerating RDF for {len(df):,} drugTreatsDisease relationships...")

new_assertions = []
new_assertions.append("\n    <!-- Drug-Disease Treatment Relationships -->")
new_assertions.append(f"    <!-- Added by add_drug_disease_relationships_direct.py on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} -->")
new_assertions.append("")

for idx, row in df.iterrows():
    drug_id_lower = row["drugbank_id"].lower()
    disease_id_lower = row["disease_id"].lower()

    # Create ObjectPropertyAssertion in RDF/XML format
    assertion = f"""    <owl:NamedIndividual rdf:about="#drug_{drug_id_lower}">
        <drugTreatsDisease rdf:resource="#disease_{disease_id_lower}"/>
    </owl:NamedIndividual>
"""
    new_assertions.append(assertion)

    if (idx + 1) % 50 == 0:
        print(f"  Generated {idx + 1:,} assertions...")

print(f"  Generated all {len(df):,} assertions")

# Combine: original content + new assertions + closing tag
new_rdf_content = content_before_close + "\n".join(new_assertions) + "\n" + content_closing

# Save to output file
output_file = "kg_projects/neurokb/neurokb-with-indications.rdf"
print(f"\nSaving modified ontology to {output_file}...")

with open(output_file, 'w', encoding='utf-8') as f:
    f.write(new_rdf_content)

output_size = Path(output_file).stat().st_size
print(f"  Output file size: {output_size:,} bytes")

print(f"\nSize comparison:")
print(f"  Original: {original_size:,} bytes")
print(f"  Modified: {output_size:,} bytes")
print(f"  Added:    {output_size - original_size:,} bytes")

print(f"\nSummary:")
print(f"  Added {len(df):,} drugTreatsDisease relationships")
print(f"  Preserved all {original_size:,} bytes of original content")
print(f"  Output: {output_file}")
print("\nDone!")
