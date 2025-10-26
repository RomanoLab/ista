#!/usr/bin/env python3
"""
OWL2 Example - Demonstrating the ista.owl2 Python bindings

This example shows how to use the C++ OWL2 library through Python bindings
to create ontologies, define classes, add axioms, and serialize to various formats.
"""

from ista import owl2


def main():
    print("=" * 70)
    print("OWL2 Python Bindings Example")
    print("=" * 70)
    print()

    # Step 1: Check if bindings are available
    print("1. Checking if C++ OWL2 bindings are available...")
    if not owl2.is_available():
        print("   ERROR: C++ OWL2 bindings are not available!")
        print("   Please build the C++ extension first:")
        print("   - pip install -e .")
        print(
            "   - Or manually: mkdir build && cd build && cmake .. && cmake --build ."
        )
        return 1
    print("   SUCCESS: C++ OWL2 bindings are loaded and ready!")
    print()

    # Step 2: Create an Ontology with an IRI
    print("2. Creating an ontology with IRI...")
    ontology_iri = owl2.IRI("http://example.org/animals")
    onto = owl2.Ontology(ontology_iri)
    print(f"   Created ontology: {ontology_iri.get_full_iri()}")
    print()

    # Step 3: Register namespace prefixes
    print("3. Registering namespace prefixes...")
    onto.register_prefix("animals", "http://example.org/animals#")
    onto.register_prefix("rdfs", "http://www.w3.org/2000/01/rdf-schema#")
    onto.register_prefix("owl", "http://www.w3.org/2002/07/owl#")
    print("   Registered prefixes:")
    for prefix, namespace in onto.get_prefix_map().items():
        print(f"     {prefix} -> {namespace}")
    print()

    # Step 4: Create Class entities
    print("4. Creating class entities...")

    # Create IRIs for our classes
    animal_iri = owl2.IRI("animals", "Animal", "http://example.org/animals#")
    mammal_iri = owl2.IRI("animals", "Mammal", "http://example.org/animals#")
    bird_iri = owl2.IRI("animals", "Bird", "http://example.org/animals#")
    dog_iri = owl2.IRI("animals", "Dog", "http://example.org/animals#")
    cat_iri = owl2.IRI("animals", "Cat", "http://example.org/animals#")

    # Create Class objects
    animal_class = owl2.Class(animal_iri)
    mammal_class = owl2.Class(mammal_iri)
    bird_class = owl2.Class(bird_iri)
    dog_class = owl2.Class(dog_iri)
    cat_class = owl2.Class(cat_iri)

    print(f"   Created classes:")
    print(f"     - {animal_iri.get_abbreviated()}")
    print(f"     - {mammal_iri.get_abbreviated()}")
    print(f"     - {bird_iri.get_abbreviated()}")
    print(f"     - {dog_iri.get_abbreviated()}")
    print(f"     - {cat_iri.get_abbreviated()}")
    print()

    # Step 5: Declare the classes with Declaration axioms
    print("5. Adding Declaration axioms for all classes...")

    # Declare each class
    onto.add_axiom(owl2.Declaration(owl2.EntityType.CLASS, animal_iri))
    onto.add_axiom(owl2.Declaration(owl2.EntityType.CLASS, mammal_iri))
    onto.add_axiom(owl2.Declaration(owl2.EntityType.CLASS, bird_iri))
    onto.add_axiom(owl2.Declaration(owl2.EntityType.CLASS, dog_iri))
    onto.add_axiom(owl2.Declaration(owl2.EntityType.CLASS, cat_iri))

    print(f"   Declared {len(onto.get_declaration_axioms())} classes")
    print()

    # Step 6: Add SubClassOf axioms to create a class hierarchy
    print("6. Adding SubClassOf axioms to create hierarchy...")

    # Create class expressions (NamedClass wraps a Class)
    animal_expr = owl2.NamedClass(animal_class)
    mammal_expr = owl2.NamedClass(mammal_class)
    bird_expr = owl2.NamedClass(bird_class)
    dog_expr = owl2.NamedClass(dog_class)
    cat_expr = owl2.NamedClass(cat_class)

    # Add hierarchical relationships
    # Mammal subClassOf Animal
    onto.add_axiom(owl2.SubClassOf(mammal_expr, animal_expr))
    print("   - Mammal subClassOf Animal")

    # Bird subClassOf Animal
    onto.add_axiom(owl2.SubClassOf(bird_expr, animal_expr))
    print("   - Bird subClassOf Animal")

    # Dog subClassOf Mammal
    onto.add_axiom(owl2.SubClassOf(dog_expr, mammal_expr))
    print("   - Dog subClassOf Mammal")

    # Cat subClassOf Mammal
    onto.add_axiom(owl2.SubClassOf(cat_expr, mammal_expr))
    print("   - Cat subClassOf Mammal")
    print()

    # Step 7: Print ontology statistics
    print("7. Ontology statistics:")
    print("-" * 70)
    print(onto.get_statistics())
    print("-" * 70)
    print()

    # Additional statistics
    print("   Detailed counts:")
    print(f"     - Total axioms: {onto.get_axiom_count()}")
    print(f"     - Total entities: {onto.get_entity_count()}")
    print(f"     - Classes: {onto.get_class_count()}")
    print(f"     - Object properties: {onto.get_object_property_count()}")
    print(f"     - Data properties: {onto.get_data_property_count()}")
    print(f"     - Individuals: {onto.get_individual_count()}")
    print()

    # Step 8: Save to Functional Syntax (.ofn)
    print("8. Serializing to OWL2 Functional Syntax...")

    functional_syntax_file = "D:\\projects\\ista\\examples\\animals_example.ofn"
    owl2.FunctionalSyntaxSerializer.serialize_to_file(onto, functional_syntax_file)
    print(f"   Saved to: {functional_syntax_file}")

    # Also print a preview to console
    print()
    print("   Preview of Functional Syntax:")
    print("   " + "-" * 66)
    functional_syntax = owl2.FunctionalSyntaxSerializer.serialize(onto)
    for line in functional_syntax.split("\n")[:20]:  # Show first 20 lines
        print(f"   {line}")
    if len(functional_syntax.split("\n")) > 20:
        print("   ...")
    print("   " + "-" * 66)
    print()

    # Step 9: Save to RDF/XML (.owl)
    print("9. Serializing to RDF/XML format...")

    rdfxml_file = "D:\\projects\\ista\\examples\\animals_example.owl"
    owl2.RDFXMLSerializer.serialize_to_file(onto, rdfxml_file)
    print(f"   Saved to: {rdfxml_file}")

    # Also print a preview to console
    print()
    print("   Preview of RDF/XML:")
    print("   " + "-" * 66)
    rdfxml = owl2.RDFXMLSerializer.serialize(onto)
    for line in rdfxml.split("\n")[:20]:  # Show first 20 lines
        print(f"   {line}")
    if len(rdfxml.split("\n")) > 20:
        print("   ...")
    print("   " + "-" * 66)
    print()

    print("=" * 70)
    print("Example completed successfully!")
    print("=" * 70)
    print()
    print("Summary of what was demonstrated:")
    print("  1. Checked C++ binding availability with owl2.is_available()")
    print("  2. Created an Ontology with an IRI")
    print("  3. Registered namespace prefixes")
    print("  4. Created Class entities with IRIs")
    print("  5. Added Declaration axioms for all classes")
    print("  6. Added SubClassOf axioms to build a hierarchy")
    print("  7. Printed ontology statistics")
    print("  8. Saved to Functional Syntax (.ofn)")
    print("  9. Saved to RDF/XML (.owl)")
    print()

    return 0


if __name__ == "__main__":
    exit(main())
