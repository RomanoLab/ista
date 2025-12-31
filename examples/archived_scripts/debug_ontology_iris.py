"""
Debug script to examine actual IRIs in the neurokb ontology
"""

import sys
from pathlib import Path

# Add parent directory to path to import ista
sys.path.insert(0, str(Path(__file__).parent.parent))

from ista import owl2

print("Loading neurokb ontology...")
onto = owl2.RDFXMLParser.parse_from_file("kg_projects/neurokb/neurokb-populated.rdf")

print("\nGetting all individuals...")
individuals = onto.get_individuals()
print(f"Total individuals: {len(individuals)}")

# Get drug individuals
print("\nFirst 20 drug individuals:")
drug_count = 0
for ind in individuals:
    iri_str = ind.get_iri().to_string()
    if 'drug_' in iri_str.lower():
        print(f"  {iri_str}")
        drug_count += 1
        if drug_count >= 20:
            break

# Get disease individuals
print("\nFirst 20 disease individuals:")
disease_count = 0
for ind in individuals:
    iri_str = ind.get_iri().to_string()
    if 'disease_' in iri_str.lower():
        print(f"  {iri_str}")
        disease_count += 1
        if disease_count >= 20:
            break

print(f"\nTotal drugs found: {sum(1 for ind in individuals if 'drug_' in ind.get_iri().to_string().lower())}")
print(f"Total diseases found: {sum(1 for ind in individuals if 'disease_' in ind.get_iri().to_string().lower())}")

# Check a specific example
print("\nChecking specific examples:")
namespace = "http://jdr.bio/ontologies/alzkb.owl#"
test_cases = [
    "drug_db00001",
    "drug_DB00001",
    "Drug_db00001",
    "disease_c0002395",
    "disease_C0002395",
    "Disease_c0002395"
]

existing_iris = {ind.get_iri().to_string() for ind in individuals}

for test in test_cases:
    full_iri = namespace + test
    exists = full_iri in existing_iris
    print(f"  {test}: {exists}")
