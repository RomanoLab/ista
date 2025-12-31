"""
Example: Adding Drug-Disease Adverse Event Relationships to NeuroKB (Direct RDF Modification)

This example demonstrates how to:
1. Read an existing RDF ontology file
2. Declare a new drugCausesAdverseEvent property
3. Add new drugCausesAdverseEvent relationships by directly modifying the RDF
4. Save the modified ontology while preserving all original content

Prerequisites:
    Run adverse_event_map.py first
    Then run filter_adverse_event_mappings_by_ontology.py to filter
"""

from pathlib import Path
import pandas as pd
from datetime import datetime
import re

# Load drug-disease adverse event mappings from CSV
filtered_mapping_file = Path("drug_adverse_event_mappings_filtered.csv")
full_mapping_file = Path("drug_adverse_event_mappings.csv")

if filtered_mapping_file.exists():
    print(f"Loading filtered adverse event mappings from {filtered_mapping_file}...")
    print("(These only include drugs/diseases that exist in neurokb)")
    df = pd.read_csv(filtered_mapping_file)
    print(f"  Loaded {len(df):,} drug-disease adverse event pairs")
elif full_mapping_file.exists():
    print(f"Loading mappings from {full_mapping_file}...")
    print("WARNING: This may include drugs/diseases not in neurokb.")
    df = pd.read_csv(full_mapping_file)
    print(f"  Loaded {len(df):,} drug-disease adverse event pairs")
else:
    print("Warning: No mapping files found!")
    print("Run: 1) adverse_event_map.py, then 2) filter_adverse_event_mappings_by_ontology.py")
    data = {
        "drugbank_id": ["DB00001", "DB00002"],
        "disease_id": ["C0027497", "C0751354"],
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

# Find where to insert the new property declaration
# Look for the last ObjectProperty declaration
last_obj_prop_pattern = r'(<owl:ObjectProperty[^>]*>.*?</owl:ObjectProperty>)'
matches = list(re.finditer(last_obj_prop_pattern, rdf_content, re.DOTALL))

if not matches:
    raise ValueError("Could not find any ObjectProperty declarations in input file")

# Insert new property after the last existing property
insertion_point = matches[-1].end()

# Create the new property declaration
new_property_decl = """
    <owl:ObjectProperty rdf:about="#drugCausesAdverseEvent">
        <rdfs:domain rdf:resource="#Chemical"/>
        <rdfs:range rdf:resource="#Disease"/>
        <rdfs:subPropertyOf rdf:resource="#chemicalObjectProperty"/>
        <rdfs:comment xml:lang="en">Indicates that a drug can cause an adverse event (side effect) manifesting as a specific disease or condition.</rdfs:comment>
    </owl:ObjectProperty>
"""

# Insert the property declaration
content_with_property = rdf_content[:insertion_point] + new_property_decl + rdf_content[insertion_point:]

print("  Added drugCausesAdverseEvent property declaration")

# Find the closing </rdf:RDF> tag
closing_tag = "</rdf:RDF>"
closing_pos = content_with_property.rfind(closing_tag)

if closing_pos == -1:
    raise ValueError("Could not find closing </rdf:RDF> tag")

# Split content
content_before_close = content_with_property[:closing_pos]
content_closing = content_with_property[closing_pos:]

# Generate RDF for new property assertions
print(f"\nGenerating RDF for {len(df):,} drugCausesAdverseEvent relationships...")

new_assertions = []
new_assertions.append("\n    <!-- Drug-Disease Adverse Event Relationships -->")
new_assertions.append(f"    <!-- Added by add_drug_adverse_event_relationships_direct.py on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} -->")
new_assertions.append("")

for idx, row in df.iterrows():
    drug_id_lower = row["drugbank_id"].lower()
    disease_id_lower = row["disease_id"].lower()

    # Create ObjectPropertyAssertion in RDF/XML format
    assertion = f"""    <owl:NamedIndividual rdf:about="#drug_{drug_id_lower}">
        <drugCausesAdverseEvent rdf:resource="#disease_{disease_id_lower}"/>
    </owl:NamedIndividual>
"""
    new_assertions.append(assertion)

    if (idx + 1) % 50 == 0:
        print(f"  Generated {idx + 1:,} assertions...")

print(f"  Generated all {len(df):,} assertions")

# Combine everything
new_rdf_content = content_before_close + "\n".join(new_assertions) + "\n" + content_closing

# Save to output file
output_file = "kg_projects/neurokb/neurokb-with-adverse-events.rdf"
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
print(f"  Declared drugCausesAdverseEvent property")
print(f"  Added {len(df):,} adverse event relationships")
print(f"  Preserved all {original_size:,} bytes of original content")
print(f"  Output: {output_file}")
print("\nDone!")
