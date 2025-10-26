#!/usr/bin/env python3
"""
Test script for simplified Python bindings.
This demonstrates the essential functionality of the simplified OWL2 bindings.
"""

import sys

sys.path.insert(0, r"D:\projects\ista\build\lib\python\Release")

import _libista_owl2 as owl2


def main():
    print("Testing simplified OWL2 Python bindings...")
    print(f"Version: {owl2.__version__}")
    print()

    # Create an ontology
    print("1. Creating ontology...")
    onto_iri = owl2.IRI("http://example.org/family")
    onto = owl2.Ontology(onto_iri)
    print(f"   Created: {onto}")
    print()

    # Register prefixes
    print("2. Registering prefixes...")
    onto.register_prefix("fam", "http://example.org/family#")
    onto.register_prefix("owl", "http://www.w3.org/2002/07/owl#")
    onto.register_prefix("rdf", "http://www.w3.org/1999/02/22-rdf-syntax-ns#")
    onto.register_prefix("rdfs", "http://www.w3.org/2000/01/rdf-schema#")
    onto.register_prefix("xsd", "http://www.w3.org/2001/XMLSchema#")
    print(f"   Registered {len(onto.get_prefix_map())} prefixes")
    print()

    # Create entities
    print("3. Creating entities...")
    person_cls = owl2.Class(owl2.IRI("fam", "Person", "http://example.org/family#"))
    parent_cls = owl2.Class(owl2.IRI("fam", "Parent", "http://example.org/family#"))

    has_child_prop = owl2.ObjectProperty(
        owl2.IRI("fam", "hasChild", "http://example.org/family#")
    )
    age_prop = owl2.DataProperty(owl2.IRI("fam", "age", "http://example.org/family#"))

    john = owl2.NamedIndividual(owl2.IRI("fam", "John", "http://example.org/family#"))
    mary = owl2.NamedIndividual(owl2.IRI("fam", "Mary", "http://example.org/family#"))

    print(f"   Created class: {person_cls}")
    print(f"   Created class: {parent_cls}")
    print(f"   Created object property: {has_child_prop}")
    print(f"   Created data property: {age_prop}")
    print(f"   Created individual: {john}")
    print(f"   Created individual: {mary}")
    print()

    # Add declarations
    print("4. Adding declarations...")
    onto.add_axiom(owl2.Declaration(owl2.EntityType.CLASS, person_cls.get_iri()))
    onto.add_axiom(owl2.Declaration(owl2.EntityType.CLASS, parent_cls.get_iri()))
    onto.add_axiom(
        owl2.Declaration(owl2.EntityType.OBJECT_PROPERTY, has_child_prop.get_iri())
    )
    onto.add_axiom(owl2.Declaration(owl2.EntityType.DATA_PROPERTY, age_prop.get_iri()))
    onto.add_axiom(owl2.Declaration(owl2.EntityType.NAMED_INDIVIDUAL, john.get_iri()))
    onto.add_axiom(owl2.Declaration(owl2.EntityType.NAMED_INDIVIDUAL, mary.get_iri()))
    print(f"   Added 6 declaration axioms")
    print()

    # Add SubClassOf axiom
    print("5. Adding SubClassOf axiom...")
    person_expr = owl2.NamedClass(person_cls)
    parent_expr = owl2.NamedClass(parent_cls)
    subclass_axiom = owl2.SubClassOf(parent_expr, person_expr)
    onto.add_axiom(subclass_axiom)
    print(f"   Added: Parent ⊑ Person")
    print(f"   Functional syntax: {subclass_axiom.to_functional_syntax()}")
    print()

    # Add ClassAssertion axioms
    print("6. Adding ClassAssertion axioms...")
    onto.add_axiom(owl2.ClassAssertion(person_expr, john))
    onto.add_axiom(owl2.ClassAssertion(parent_expr, mary))
    print(f"   Added: John is a Person")
    print(f"   Added: Mary is a Parent")
    print()

    # Add property domain/range axioms
    print("7. Adding property domain/range axioms...")
    onto.add_axiom(owl2.ObjectPropertyDomain(has_child_prop, person_expr))
    onto.add_axiom(owl2.ObjectPropertyRange(has_child_prop, person_expr))
    onto.add_axiom(owl2.DataPropertyDomain(age_prop, person_expr))
    print(f"   Added domain/range axioms for hasChild and age")
    print()

    # Add functional property axioms
    print("8. Adding functional property axioms...")
    onto.add_axiom(owl2.FunctionalDataProperty(age_prop))
    print(f"   Added: age is functional")
    print()

    # Display statistics
    print("9. Ontology statistics:")
    print(f"   Total axioms: {onto.get_axiom_count()}")
    print(f"   Total entities: {onto.get_entity_count()}")
    print(f"   Classes: {onto.get_class_count()}")
    print(f"   Object properties: {onto.get_object_property_count()}")
    print(f"   Data properties: {onto.get_data_property_count()}")
    print(f"   Individuals: {onto.get_individual_count()}")
    print()

    # Serialize to Functional Syntax
    print("10. Serializing to Functional Syntax...")
    fs_output = owl2.FunctionalSyntaxSerializer.serialize(onto, "    ")
    print("First 500 characters:")
    print(fs_output[:500])
    print("...")
    print()

    # Save to files
    print("11. Saving to files...")
    fs_file = r"D:\projects\ista\test_family_simple.ofn"
    rdf_file = r"D:\projects\ista\test_family_simple.rdf"

    owl2.FunctionalSyntaxSerializer.serialize_to_file(onto, fs_file)
    print(f"   Saved Functional Syntax to: {fs_file}")

    owl2.RDFXMLSerializer.serialize_to_file(onto, rdf_file)
    print(f"   Saved RDF/XML to: {rdf_file}")
    print()

    # Test IRI functionality
    print("12. Testing IRI functionality...")
    test_iri = owl2.IRI("ex", "Test", "http://example.org/test#")
    print(f"   Full IRI: {test_iri.get_full_iri()}")
    print(f"   Abbreviated: {test_iri.get_abbreviated()}")
    print(f"   Prefix: {test_iri.get_prefix()}")
    print(f"   Local name: {test_iri.get_local_name()}")
    print(f"   Namespace: {test_iri.get_namespace()}")
    print(f"   Is abbreviated: {test_iri.is_abbreviated()}")
    print()

    # Test Literal functionality
    print("13. Testing Literal functionality...")
    plain_lit = owl2.Literal("Hello", "en")
    typed_lit = owl2.Literal("42", owl2.xsd.INTEGER)
    print(f"   Plain literal: {plain_lit}")
    print(f"   Has language tag: {plain_lit.has_language_tag()}")
    print(f"   Language tag: {plain_lit.get_language_tag()}")
    print(f"   Typed literal: {typed_lit}")
    print(f"   Is typed: {typed_lit.is_typed()}")
    print(f"   Datatype: {typed_lit.get_datatype()}")
    print()

    # Test XSD constants
    print("14. Testing XSD constants...")
    print(f"   xsd:string = {owl2.xsd.STRING}")
    print(f"   xsd:integer = {owl2.xsd.INTEGER}")
    print(f"   xsd:int = {owl2.xsd.INT}")
    print(f"   xsd:double = {owl2.xsd.DOUBLE}")
    print(f"   xsd:boolean = {owl2.xsd.BOOLEAN}")
    print(f"   xsd:dateTime = {owl2.xsd.DATE_TIME}")
    print()

    print("✓ All tests passed successfully!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
