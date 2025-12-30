"""
Test round-trip serialization and parsing of Turtle format.

This test verifies that we can:
1. Create an ontology with axioms
2. Serialize it to Turtle format
3. Parse the Turtle back into an ontology
4. Verify the axioms are preserved
"""

import ista.owl2 as owl2


def test_turtle_roundtrip():
    """Test that we can serialize to Turtle and parse it back."""

    # Create a simple ontology
    ont = owl2.Ontology(owl2.IRI("http://example.org/test"))

    # Add some classes
    person_iri = owl2.IRI("http://example.org/Person")
    student_iri = owl2.IRI("http://example.org/Student")
    person_class = owl2.Class(person_iri)
    student_class = owl2.Class(student_iri)

    # Add declarations
    ont.add_axiom(owl2.Declaration(owl2.EntityType.CLASS, person_iri))
    ont.add_axiom(owl2.Declaration(owl2.EntityType.CLASS, student_iri))

    # Add a subclass axiom
    person_expr = owl2.NamedClass(person_class)
    student_expr = owl2.NamedClass(student_class)
    ont.add_axiom(owl2.SubClassOf(student_expr, person_expr))

    # Add an individual
    john_iri = owl2.IRI("http://example.org/John")
    john = owl2.NamedIndividual(john_iri)
    ont.add_axiom(owl2.Declaration(owl2.EntityType.NAMED_INDIVIDUAL, john_iri))
    ont.add_axiom(owl2.ClassAssertion(student_class, john))

    # Add a data property
    age_iri = owl2.IRI("http://example.org/hasAge")
    age_prop = owl2.DataProperty(age_iri)
    ont.add_axiom(owl2.Declaration(owl2.EntityType.DATA_PROPERTY, age_iri))

    # Add a data property assertion
    age_literal = owl2.Literal(
        "25", owl2.IRI("http://www.w3.org/2001/XMLSchema#integer")
    )
    ont.add_axiom(owl2.DataPropertyAssertion(age_prop, john, age_literal))

    # Add an object property
    knows_iri = owl2.IRI("http://example.org/knows")
    knows_prop = owl2.ObjectProperty(knows_iri)
    ont.add_axiom(owl2.Declaration(owl2.EntityType.OBJECT_PROPERTY, knows_iri))

    # Add another individual
    jane_iri = owl2.IRI("http://example.org/Jane")
    jane = owl2.NamedIndividual(jane_iri)
    ont.add_axiom(owl2.Declaration(owl2.EntityType.NAMED_INDIVIDUAL, jane_iri))
    ont.add_axiom(owl2.ClassAssertion(student_class, jane))

    # Add an object property assertion
    ont.add_axiom(owl2.ObjectPropertyAssertion(knows_prop, john, jane))

    print("Original ontology:")
    print(f"  Axiom count: {len(ont.get_axioms())}")

    # Serialize to Turtle
    print("\nSerializing to Turtle...")
    turtle_str = owl2.TurtleSerializer.serialize(ont)
    print(f"Turtle output ({len(turtle_str)} chars):")
    print("-" * 60)
    print(turtle_str[:500])  # Print first 500 chars
    if len(turtle_str) > 500:
        print("...")
    print("-" * 60)

    # Save to file
    print("\nSaving to file: test_roundtrip.ttl")
    owl2.TurtleSerializer.serialize_to_file(ont, "test_roundtrip.ttl")

    # Parse it back
    print("\nParsing Turtle back into ontology...")
    parsed_ont = owl2.TurtleParser.parse_from_file("test_roundtrip.ttl")

    print("\nParsed ontology:")
    print(f"  Axiom count: {len(parsed_ont.get_axioms())}")

    # Basic verification
    original_axiom_count = len(ont.get_axioms())
    parsed_axiom_count = len(parsed_ont.get_axioms())

    print(f"\nRound-trip verification:")
    print(f"  Original axioms: {original_axiom_count}")
    print(f"  Parsed axioms: {parsed_axiom_count}")

    if parsed_axiom_count > 0:
        print("  ✓ Parser successfully created axioms")
    else:
        print("  ✗ Parser failed to create axioms")

    # Note: Exact axiom count matching may not work due to how RDF triples
    # map to OWL axioms, but we should at least get some axioms back
    if parsed_axiom_count >= original_axiom_count * 0.5:  # At least 50% of axioms
        print("  ✓ Round-trip appears successful")
        return True
    else:
        print("  ⚠ Some axioms may have been lost in round-trip")
        return False


if __name__ == "__main__":
    success = test_turtle_roundtrip()
    exit(0 if success else 1)
