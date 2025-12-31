"""
Test what the RDF parser is actually loading
"""

import sys
from pathlib import Path

# Add parent directory to path to import ista
sys.path.insert(0, str(Path(__file__).parent.parent))

from ista import owl2

print("Loading neurokb ontology...")
onto = owl2.RDFXMLParser.parse_from_file("kg_projects/neurokb/neurokb-populated.rdf")

print("\nOntology Statistics:")
stats = onto.get_statistics()
print(stats)

print(f"\nAxiom count: {onto.get_axiom_count()}")

print("\nGetting entities...")
classes = onto.get_classes()
obj_props = onto.get_object_properties()
data_props = onto.get_data_properties()
individuals = onto.get_individuals()

print(f"  Classes: {len(classes)}")
print(f"  Object Properties: {len(obj_props)}")
print(f"  Data Properties: {len(data_props)}")
print(f"  Individuals: {len(individuals)}")

if len(classes) > 0:
    print("\nFirst 10 classes:")
    for cls in list(classes)[:10]:
        print(f"  {cls.get_iri().to_string()}")

if len(obj_props) > 0:
    print("\nFirst 10 object properties:")
    for prop in list(obj_props)[:10]:
        print(f"  {prop.get_iri().to_string()}")

if len(individuals) > 0:
    print("\nFirst 10 individuals:")
    for ind in list(individuals)[:10]:
        print(f"  {ind.get_iri().to_string()}")
else:
    print("\nWARNING: No individuals found!")
    print("This suggests the RDF parser may not be loading individual declarations.")

print("\nChecking for specific axiom types...")
# Try to get all axioms and see what types we have
print("(This might take a moment for a large ontology)")
