"""
Simple test to see IRI format without running full script
"""

# Read the RDF file and manually check IRI patterns
rdf_file = "kg_projects/neurokb/neurokb-populated.rdf"

print("Reading RDF file to check IRI patterns...")
with open(rdf_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Find some drug declarations
import re
drug_pattern = r'<Drug rdf:about="([^"]+)">'
disease_pattern = r'<Disease rdf:about="([^"]+)">'

drugs = re.findall(drug_pattern, content)
diseases = re.findall(disease_pattern, content)

print(f"\nFound {len(drugs)} drugs")
print("First 10 drug IRIs:")
for drug in drugs[:10]:
    print(f"  {drug}")

print(f"\nFound {len(diseases)} diseases")
print("First 10 disease IRIs:")
for disease in diseases[:10]:
    print(f"  {disease}")

# Now test the construction logic
print("\n" + "="*60)
print("Testing construction logic:")
print("="*60)

namespace = "http://jdr.bio/ontologies/alzkb.owl#"

test_drugbank_ids = ["DB00001", "DB00643", "DB10670"]

for db_id in test_drugbank_ids:
    drug_id_lower = db_id.lower()
    drug_suffix = f"drug_{drug_id_lower}"
    full_iri_with_hash = f"#{drug_suffix}"
    full_iri_with_namespace = f"{namespace}{drug_suffix}"

    print(f"\nDrugBank ID: {db_id}")
    print(f"  drug_suffix: {drug_suffix}")
    print(f"  Constructed (with #): {full_iri_with_hash}")
    print(f"  Constructed (with namespace): {full_iri_with_namespace}")
    print(f"  Exists in RDF (with #)?: {full_iri_with_hash in drugs}")
    print(f"  Exists in RDF (with namespace)?: {full_iri_with_namespace in drugs}")
