"""
Example: Adding Drug-Drug Interaction Relationships to NeuroKB (Direct RDF Modification)

This example demonstrates how to:
1. Read an existing RDF ontology file
2. Declare a new drugInteractsWithDrug property
3. Add new drugInteractsWithDrug relationships by directly modifying the RDF
4. Save the modified ontology while preserving all original content

Note: This adds MAJOR severity drug-drug interactions only (severity = 2)

Prerequisites:
    Run drug_interaction_map.py first
    Then run filter_drug_interaction_mappings_by_ontology.py to filter
"""

from pathlib import Path
import pandas as pd
from datetime import datetime
import re

# Load drug-drug interaction mappings from CSV
filtered_mapping_file = Path("drug_interaction_mappings_filtered.csv")
full_mapping_file = Path("drug_interaction_mappings.csv")

if filtered_mapping_file.exists():
    print(f"Loading filtered drug interaction mappings from {filtered_mapping_file}...")
    print("(These only include drugs that exist in neurokb)")
    df = pd.read_csv(filtered_mapping_file)
    print(f"  Loaded {len(df):,} drug-drug interaction pairs (major severity)")
elif full_mapping_file.exists():
    print(f"Loading mappings from {full_mapping_file}...")
    print("WARNING: This may include drugs not in neurokb.")
    df = pd.read_csv(full_mapping_file)
    print(f"  Loaded {len(df):,} drug-drug interaction pairs")
else:
    print("Warning: No mapping files found!")
    print("Run: 1) drug_interaction_map.py, then 2) filter_drug_interaction_mappings_by_ontology.py")
    data = {
        "subject_drugbank_id": ["DB00005", "DB00065"],
        "affected_drugbank_id": ["DB01281", "DB01281"],
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
    <owl:ObjectProperty rdf:about="#drugInteractsWithDrug">
        <rdfs:domain rdf:resource="#Chemical"/>
        <rdfs:range rdf:resource="#Chemical"/>
        <rdfs:subPropertyOf rdf:resource="#chemicalObjectProperty"/>
        <rdf:type rdf:resource="http://www.w3.org/2002/07/owl#SymmetricProperty"/>
        <rdfs:comment xml:lang="en">Indicates a major severity drug-drug interaction where one drug significantly affects the pharmacokinetics or pharmacodynamics of another, potentially causing serious adverse effects.</rdfs:comment>
    </owl:ObjectProperty>
"""

# Insert the property declaration
content_with_property = rdf_content[:insertion_point] + new_property_decl + rdf_content[insertion_point:]

print("  Added drugInteractsWithDrug property declaration")

# Find the closing </rdf:RDF> tag
closing_tag = "</rdf:RDF>"
closing_pos = content_with_property.rfind(closing_tag)

if closing_pos == -1:
    raise ValueError("Could not find closing </rdf:RDF> tag")

# Split content
content_before_close = content_with_property[:closing_pos]
content_closing = content_with_property[closing_pos:]

# Generate RDF for new property assertions
print(f"\nGenerating RDF for {len(df):,} drugInteractsWithDrug relationships...")

new_assertions = []
new_assertions.append("\n    <!-- Drug-Drug Interaction Relationships (Major Severity) -->")
new_assertions.append(f"    <!-- Added by add_drug_interaction_relationships_direct.py on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} -->")
new_assertions.append("")

for idx, row in df.iterrows():
    subject_drug_id_lower = row["subject_drugbank_id"].lower()
    affected_drug_id_lower = row["affected_drugbank_id"].lower()

    # Create ObjectPropertyAssertion in RDF/XML format
    # Note: drugInteractsWithDrug is symmetric, but we only need to assert it once
    assertion = f"""    <owl:NamedIndividual rdf:about="#drug_{subject_drug_id_lower}">
        <drugInteractsWithDrug rdf:resource="#drug_{affected_drug_id_lower}"/>
    </owl:NamedIndividual>
"""
    new_assertions.append(assertion)

    if (idx + 1) % 10000 == 0:
        print(f"  Generated {idx + 1:,} assertions...")

print(f"  Generated all {len(df):,} assertions")

# Combine everything
new_rdf_content = content_before_close + "\n".join(new_assertions) + "\n" + content_closing

# Save to output file
output_file = "kg_projects/neurokb/neurokb-with-drug-interactions.rdf"
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
print(f"  Declared drugInteractsWithDrug property (symmetric)")
print(f"  Added {len(df):,} major severity drug-drug interaction relationships")
print(f"  Preserved all {original_size:,} bytes of original content")
print(f"  Output: {output_file}")
print("\nDone!")
