"""
Test script for new ista.owl2 API features that replace owlready2 functionality.

This demonstrates the new individual creation, property assertion, and search APIs.
"""

import sys

sys.path.insert(0, "D:/projects/ista/build/lib/python/Debug")

import ista.owl2 as owl2

# Create a new ontology
onto = owl2.Ontology(owl2.IRI("http://example.org/test"))

print("=" * 60)
print("Testing New ista.owl2 API Features")
print("=" * 60)
print()

# Create classes
drug_class = owl2.Class(owl2.IRI("http://example.org/test#Drug"))
gene_class = owl2.Class(owl2.IRI("http://example.org/test#Gene"))

# Create properties
has_name = owl2.DataProperty(owl2.IRI("http://example.org/test#hasName"))
targets_gene = owl2.ObjectProperty(owl2.IRI("http://example.org/test#targetsGene"))
drugbank_id = owl2.DataProperty(owl2.IRI("http://example.org/test#drugbankId"))

print("1. Creating individuals using create_individual()...")
# Create individuals using the new API
aspirin = onto.create_individual(
    drug_class, owl2.IRI("http://example.org/test#aspirin")
)
ibuprofen = onto.create_individual(
    drug_class, owl2.IRI("http://example.org/test#ibuprofen")
)
cox1 = onto.create_individual(gene_class, owl2.IRI("http://example.org/test#COX1"))
cox2 = onto.create_individual(gene_class, owl2.IRI("http://example.org/test#COX2"))
print(f"   Created {aspirin}")
print(f"   Created {ibuprofen}")
print(f"   Created {cox1}")
print(f"   Created {cox2}")
print()

print("2. Adding data property assertions...")
# Add data properties
onto.add_data_property_assertion(aspirin, has_name, owl2.Literal("Aspirin"))
onto.add_data_property_assertion(aspirin, drugbank_id, owl2.Literal("DB00945"))
onto.add_data_property_assertion(ibuprofen, has_name, owl2.Literal("Ibuprofen"))
onto.add_data_property_assertion(ibuprofen, drugbank_id, owl2.Literal("DB01050"))
onto.add_data_property_assertion(cox1, has_name, owl2.Literal("COX-1"))
onto.add_data_property_assertion(cox2, has_name, owl2.Literal("COX-2"))
print("   Added names and IDs to all individuals")
print()

print("3. Adding object property assertions...")
# Add object properties
onto.add_object_property_assertion(aspirin, targets_gene, cox1)
onto.add_object_property_assertion(aspirin, targets_gene, cox2)
onto.add_object_property_assertion(ibuprofen, targets_gene, cox1)
onto.add_object_property_assertion(ibuprofen, targets_gene, cox2)
print("   Added drug-gene targeting relationships")
print()

print("4. Searching by data property...")
# Search for drug with specific DrugBank ID
results = onto.search_by_data_property(drugbank_id, owl2.Literal("DB00945"))
print(f"   Search for drugbankId='DB00945': {len(results)} result(s)")
for ind in results:
    print(f"      Found: {ind}")
print()

print("5. Searching by object property...")
# Search for drugs targeting COX1
drugs_targeting_cox1 = onto.search_by_object_property(targets_gene, cox1)
print(f"   Drugs targeting COX1: {len(drugs_targeting_cox1)} result(s)")
for drug in drugs_targeting_cox1:
    print(f"      {drug}")
print()

print("6. Getting all assertions for a property...")
# Get all drug-gene relationships
relationships = onto.get_object_property_assertions_for_property(targets_gene)
print(f"   All targetsGene relationships: {len(relationships)} total")
for subject, obj in relationships:
    print(
        f"      {subject.get_iri().get_local_name()} -> {obj.get_iri().get_local_name()}"
    )
print()

print("7. Getting classes for an individual...")
# Check what classes aspirin belongs to
classes = onto.get_classes_for_individual(aspirin)
print(f"   Classes for aspirin: {len(classes)}")
for cls in classes:
    print(f"      {cls.get_iri().get_local_name()}")
print()

print("8. Checking instance membership...")
# Check if aspirin is a drug
is_drug = onto.is_instance_of(aspirin, drug_class)
is_gene = onto.is_instance_of(aspirin, gene_class)
print(f"   Is aspirin a Drug? {is_drug}")
print(f"   Is aspirin a Gene? {is_gene}")
print()

print("9. Adding additional class assertion...")
# Add a second class to an individual
disease_modifying_drug = owl2.Class(
    owl2.IRI("http://example.org/test#DiseaseModifyingDrug")
)
onto.add_class_assertion(aspirin, disease_modifying_drug)
classes_after = onto.get_classes_for_individual(aspirin)
print(f"   Classes for aspirin after adding DiseaseModifyingDrug: {len(classes_after)}")
for cls in classes_after:
    print(f"      {cls.get_iri().get_local_name()}")
print()

print("10. Ontology statistics...")
print(f"   Total axioms: {onto.get_axiom_count()}")
print(f"   Total classes: {onto.get_class_count()}")
print(f"   Total individuals: {onto.get_individual_count()}")
print(f"   Total object properties: {onto.get_object_property_count()}")
print(f"   Total data properties: {onto.get_data_property_count()}")
print()

print("=" * 60)
print("All tests completed successfully!")
print("=" * 60)
