"""
Example: Adding All Drug Relationships and Properties to NeuroKB (Direct RDF Modification)

This example demonstrates how to add:
1. drugTreatsDisease (indications)
2. drugContraindicatedForDisease (contraindications)
3. drugCausesAdverseEvent (adverse events/side effects)
4. drugInteractsWithDrug (major severity drug-drug interactions)
5. bbb (blood-brain barrier penetration)
6. bbbProbability (BBB penetration probability)

Prerequisites:
    Run all mapping and filtering scripts first:
    - indication_map.py + filter_mappings_by_ontology.py
    - contraindication_map.py + filter_contraindication_mappings_by_ontology.py
    - adverse_event_map.py + filter_adverse_event_mappings_by_ontology.py
    - drug_interaction_map.py + filter_drug_interaction_mappings_by_ontology.py

    And ensure DrugBank ADMET data is available:
    - /d/data/drugbank/2025-11-19/drug_predicted_admet_properties.csv
"""

import re
from datetime import datetime
from pathlib import Path

import pandas as pd

print("=" * 70)
print("Adding All Drug Relationships and Properties to NeuroKB")
print("=" * 70)

# Load all mapping files
mapping_files = {
    "indications": "drug_disease_mappings_filtered.csv",
    "contraindications": "drug_contraindication_mappings_filtered.csv",
    "adverse_events": "drug_adverse_event_mappings_filtered.csv",
    "interactions": "drug_interaction_mappings_filtered.csv",
}

data = {}
for key, filename in mapping_files.items():
    filepath = Path(filename)
    if filepath.exists():
        data[key] = pd.read_csv(filepath)
        print(f"\nLoaded {key}: {len(data[key]):,} pairs")
    else:
        print(f"\nWarning: {filename} not found. Skipping {key}.")
        data[key] = None

# Load BBB data
bbb_file = Path("D:/data/drugbank/2025-11-19/drug_predicted_admet_properties.csv")
if bbb_file.exists():
    print(f"\nLoading BBB data from {bbb_file}...")
    bbb_data = pd.read_csv(bbb_file)
    # Filter to only drugs with BBB probability data
    bbb_data = bbb_data[["drug_id", "bbb", "bbb_probability"]].dropna()
    # Convert drug_id to DrugBank ID format (DB#####)
    bbb_data["drugbank_id"] = "DB" + bbb_data["drug_id"].astype(str).str.zfill(5)
    print(f"  Loaded BBB data for {len(bbb_data):,} drugs")
else:
    print(f"\nWarning: BBB data file not found at {bbb_file}. Skipping BBB properties.")
    bbb_data = None

# Read the original RDF file
input_file = "kg_projects/neurokb/neurokb-populated.rdf"
print(f"\nReading original RDF file: {input_file}")
input_path = Path(input_file)

with open(input_path, "r", encoding="utf-8") as f:
    rdf_content = f.read()

original_size = input_path.stat().st_size
print(f"  Original file size: {original_size:,} bytes")

# ============================================================================
# STEP 1: Add all new property declarations
# ============================================================================
print("\n" + "=" * 70)
print("STEP 1: Adding Property Declarations")
print("=" * 70)

# Find where to insert properties
last_obj_prop_pattern = r"(<owl:ObjectProperty[^>]*>.*?</owl:ObjectProperty>)"
matches = list(re.finditer(last_obj_prop_pattern, rdf_content, re.DOTALL))

if not matches:
    raise ValueError("Could not find any ObjectProperty declarations")

insertion_point = matches[-1].end()

# Define new properties (drugTreatsDisease already exists, so we skip it)
new_properties = []

# Add BBB data properties first
if bbb_data is not None and len(bbb_data) > 0:
    new_properties.append("""
    <owl:DatatypeProperty rdf:about="#bbb">
        <rdfs:subPropertyOf rdf:resource="#chemicalDataProperty"/>
        <rdf:type rdf:resource="http://www.w3.org/2002/07/owl#FunctionalProperty"/>
        <rdfs:domain rdf:resource="#Chemical"/>
        <rdfs:range rdf:resource="http://www.w3.org/2001/XMLSchema#boolean"/>
        <rdfs:comment xml:lang="en">Indicates whether a drug can penetrate the blood-brain barrier. Predicted using machine learning models based on molecular structure.</rdfs:comment>
    </owl:DatatypeProperty>
""")
    new_properties.append("""
    <owl:DatatypeProperty rdf:about="#bbbProbability">
        <rdfs:subPropertyOf rdf:resource="#chemicalDataProperty"/>
        <rdf:type rdf:resource="http://www.w3.org/2002/07/owl#FunctionalProperty"/>
        <rdfs:domain rdf:resource="#Chemical"/>
        <rdfs:range rdf:resource="http://www.w3.org/2001/XMLSchema#float"/>
        <rdfs:comment xml:lang="en">The predicted probability (0.0-1.0) that a drug can penetrate the blood-brain barrier, based on machine learning models.</rdfs:comment>
    </owl:DatatypeProperty>
""")
    print("  Adding bbb and bbbProbability data properties")

if data["contraindications"] is not None and len(data["contraindications"]) > 0:
    new_properties.append("""
    <owl:ObjectProperty rdf:about="#drugContraindicatedForDisease">
        <rdfs:domain rdf:resource="#Chemical"/>
        <rdfs:range rdf:resource="#Disease"/>
        <rdfs:subPropertyOf rdf:resource="#chemicalObjectProperty"/>
        <rdfs:comment xml:lang="en">Indicates that a drug is contraindicated for a specific disease or condition.</rdfs:comment>
    </owl:ObjectProperty>
""")
    print("  Adding drugContraindicatedForDisease property")

if data["adverse_events"] is not None and len(data["adverse_events"]) > 0:
    new_properties.append("""
    <owl:ObjectProperty rdf:about="#drugCausesAdverseEvent">
        <rdfs:domain rdf:resource="#Chemical"/>
        <rdfs:range rdf:resource="#Disease"/>
        <rdfs:subPropertyOf rdf:resource="#chemicalObjectProperty"/>
        <rdfs:comment xml:lang="en">Indicates that a drug can cause an adverse event (side effect) manifesting as a specific disease or condition.</rdfs:comment>
    </owl:ObjectProperty>
""")
    print("  Adding drugCausesAdverseEvent property")

if data["interactions"] is not None and len(data["interactions"]) > 0:
    new_properties.append("""
    <owl:ObjectProperty rdf:about="#drugInteractsWithDrug">
        <rdfs:domain rdf:resource="#Chemical"/>
        <rdfs:range rdf:resource="#Chemical"/>
        <rdfs:subPropertyOf rdf:resource="#chemicalObjectProperty"/>
        <rdf:type rdf:resource="http://www.w3.org/2002/07/owl#SymmetricProperty"/>
        <rdfs:comment xml:lang="en">Indicates a major severity drug-drug interaction where one drug significantly affects the pharmacokinetics or pharmacodynamics of another.</rdfs:comment>
    </owl:ObjectProperty>
""")
    print("  Adding drugInteractsWithDrug property")

# Insert all new properties
rdf_content = (
    rdf_content[:insertion_point]
    + "".join(new_properties)
    + rdf_content[insertion_point:]
)

# ============================================================================
# STEP 2: Find insertion point for assertions
# ============================================================================
closing_tag = "</rdf:RDF>"
closing_pos = rdf_content.rfind(closing_tag)

if closing_pos == -1:
    raise ValueError("Could not find closing </rdf:RDF> tag")

content_before_close = rdf_content[:closing_pos]
content_closing = rdf_content[closing_pos:]

all_assertions = []

# ============================================================================
# STEP 3: Generate indications (drugTreatsDisease)
# ============================================================================
if data["indications"] is not None and len(data["indications"]) > 0:
    print("\n" + "=" * 70)
    print(f"STEP 3: Generating {len(data['indications']):,} Indication Relationships")
    print("=" * 70)

    all_assertions.append(
        "\n    <!-- Drug-Disease Treatment Relationships (Indications) -->"
    )
    all_assertions.append(
        f"    <!-- Added on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} -->"
    )
    all_assertions.append("")

    for idx, row in data["indications"].iterrows():
        drug_id = row["drugbank_id"].lower()
        disease_id = row["disease_id"].lower()

        all_assertions.append(f"""    <owl:NamedIndividual rdf:about="#drug_{drug_id}">
        <drugTreatsDisease rdf:resource="#disease_{disease_id}"/>
    </owl:NamedIndividual>
""")

    print(f"  Generated {len(data['indications']):,} indication assertions")

# ============================================================================
# STEP 4: Generate contraindications
# ============================================================================
if data["contraindications"] is not None and len(data["contraindications"]) > 0:
    print("\n" + "=" * 70)
    print(
        f"STEP 4: Generating {len(data['contraindications']):,} Contraindication Relationships"
    )
    print("=" * 70)

    all_assertions.append("\n    <!-- Drug-Disease Contraindication Relationships -->")
    all_assertions.append(
        f"    <!-- Added on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} -->"
    )
    all_assertions.append("")

    for idx, row in data["contraindications"].iterrows():
        drug_id = row["drugbank_id"].lower()
        disease_id = row["disease_id"].lower()

        all_assertions.append(f"""    <owl:NamedIndividual rdf:about="#drug_{drug_id}">
        <drugContraindicatedForDisease rdf:resource="#disease_{disease_id}"/>
    </owl:NamedIndividual>
""")

    print(f"  Generated {len(data['contraindications']):,} contraindication assertions")

# ============================================================================
# STEP 5: Generate adverse events
# ============================================================================
if data["adverse_events"] is not None and len(data["adverse_events"]) > 0:
    print("\n" + "=" * 70)
    print(
        f"STEP 5: Generating {len(data['adverse_events']):,} Adverse Event Relationships"
    )
    print("=" * 70)

    all_assertions.append("\n    <!-- Drug-Disease Adverse Event Relationships -->")
    all_assertions.append(
        f"    <!-- Added on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} -->"
    )
    all_assertions.append("")

    for idx, row in data["adverse_events"].iterrows():
        drug_id = row["drugbank_id"].lower()
        disease_id = row["disease_id"].lower()

        all_assertions.append(f"""    <owl:NamedIndividual rdf:about="#drug_{drug_id}">
        <drugCausesAdverseEvent rdf:resource="#disease_{disease_id}"/>
    </owl:NamedIndividual>
""")

    print(f"  Generated {len(data['adverse_events']):,} adverse event assertions")

# ============================================================================
# STEP 6: Generate drug interactions
# ============================================================================
if data["interactions"] is not None and len(data["interactions"]) > 0:
    print("\n" + "=" * 70)
    print(
        f"STEP 6: Generating {len(data['interactions']):,} Drug Interaction Relationships"
    )
    print("=" * 70)

    all_assertions.append(
        "\n    <!-- Drug-Drug Interaction Relationships (Major Severity) -->"
    )
    all_assertions.append(
        f"    <!-- Added on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} -->"
    )
    all_assertions.append("")

    for idx, row in data["interactions"].iterrows():
        subject_id = row["subject_drugbank_id"].lower()
        affected_id = row["affected_drugbank_id"].lower()

        all_assertions.append(f"""    <owl:NamedIndividual rdf:about="#drug_{subject_id}">
        <drugInteractsWithDrug rdf:resource="#drug_{affected_id}"/>
    </owl:NamedIndividual>
""")

        if (idx + 1) % 10000 == 0:
            print(f"  Generated {idx + 1:,} drug interaction assertions...")

    print(f"  Generated all {len(data['interactions']):,} drug interaction assertions")

# ============================================================================
# STEP 7: Generate BBB properties
# ============================================================================
if bbb_data is not None and len(bbb_data) > 0:
    print("\n" + "=" * 70)
    print(f"STEP 7: Generating BBB Properties for {len(bbb_data):,} Drugs")
    print("=" * 70)

    all_assertions.append("\n    <!-- Blood-Brain Barrier Properties -->")
    all_assertions.append(
        f"    <!-- Added on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} -->"
    )
    all_assertions.append("")

    for idx, row in bbb_data.iterrows():
        drug_id = row["drugbank_id"].lower()
        bbb_value = "true" if row["bbb"] == 1 else "false"
        bbb_prob = row["bbb_probability"]

        all_assertions.append(f"""    <owl:NamedIndividual rdf:about="#drug_{drug_id}">
        <bbb rdf:datatype="http://www.w3.org/2001/XMLSchema#boolean">{bbb_value}</bbb>
        <bbbProbability rdf:datatype="http://www.w3.org/2001/XMLSchema#float">{bbb_prob}</bbbProbability>
    </owl:NamedIndividual>
""")

        if (idx + 1) % 1000 == 0:
            print(f"  Generated {idx + 1:,} BBB property assertions...")

    print(f"  Generated all {len(bbb_data):,} BBB property assertions")

# ============================================================================
# STEP 8: Combine and save
# ============================================================================
print("\n" + "=" * 70)
print("STEP 8: Saving Modified Ontology")
print("=" * 70)

new_rdf_content = (
    content_before_close + "\n".join(all_assertions) + "\n" + content_closing
)

output_file = "kg_projects/neurokb/neurokb-with-all-drug-relationships.rdf"
print(f"\nSaving modified ontology to {output_file}...")

with open(output_file, "w", encoding="utf-8") as f:
    f.write(new_rdf_content)

output_size = Path(output_file).stat().st_size

# ============================================================================
# Summary
# ============================================================================
print("\n" + "=" * 70)
print("Summary")
print("=" * 70)
print(f"  Original file size:     {original_size:,} bytes")
print(f"  Modified file size:     {output_size:,} bytes")
print(f"  Content added:          {output_size - original_size:,} bytes")
print(f"\n  Relationships added:")

total = 0
for key, df in data.items():
    if df is not None:
        count = len(df)
        total += count
        key_name = key.replace("_", " ").title()
        print(f"    {key_name:25s} {count:,}")

print(f"    {'Total':25s} {total:,}")

if bbb_data is not None:
    print(f"\n  Drug properties added:")
    print(f"    {'BBB Properties':25s} {len(bbb_data):,} drugs")

print(f"\n  Preserved all original content")
print(f"  Output: {output_file}")
print("\nDone!")
