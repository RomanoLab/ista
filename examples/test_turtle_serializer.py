"""
Test script for Turtle serializer.

Demonstrates Turtle serialization for ontologies with many individuals,
showing the compact and human-readable output.
"""

from ista import owl2


def create_test_ontology():
    """Create a simple test ontology with individuals."""

    # Create ontology
    base_iri = "http://example.org/biomedical#"
    ont = owl2.Ontology(owl2.IRI(base_iri + "ontology"))

    # Helper for creating IRIs
    def make_iri(name):
        return owl2.IRI("bio", name, base_iri)

    # Define classes
    person_iri = make_iri("Person")
    person = owl2.Class(person_iri)
    ont.add_axiom(owl2.Declaration(owl2.EntityType.CLASS, person_iri))

    disease_iri = make_iri("Disease")
    disease = owl2.Class(disease_iri)
    ont.add_axiom(owl2.Declaration(owl2.EntityType.CLASS, disease_iri))

    # Define properties
    has_name_iri = make_iri("hasName")
    has_name = owl2.DataProperty(has_name_iri)
    ont.add_axiom(owl2.Declaration(owl2.EntityType.DATA_PROPERTY, has_name_iri))

    has_age_iri = make_iri("hasAge")
    has_age = owl2.DataProperty(has_age_iri)
    ont.add_axiom(owl2.Declaration(owl2.EntityType.DATA_PROPERTY, has_age_iri))

    has_diagnosis_iri = make_iri("hasDiagnosis")
    has_diagnosis = owl2.ObjectProperty(has_diagnosis_iri)
    ont.add_axiom(owl2.Declaration(owl2.EntityType.OBJECT_PROPERTY, has_diagnosis_iri))

    # Create individuals with properties
    print("Creating individuals...")

    # Create 10 people
    for i in range(1, 11):
        person_individual_iri = make_iri(f"Person{i}")
        person_individual = ont.create_individual(person, person_individual_iri)

        # Add data properties
        name_literal = owl2.Literal(f"Patient {i}")
        ont.add_data_property_assertion(person_individual, has_name, name_literal)

        age_literal = owl2.Literal(str(25 + i * 3))
        ont.add_data_property_assertion(person_individual, has_age, age_literal)

    # Create 3 diseases
    for i in range(1, 4):
        disease_individual_iri = make_iri(f"Disease{i}")
        disease_individual = ont.create_individual(disease, disease_individual_iri)

        disease_name = owl2.Literal(f"Condition {i}")
        ont.add_data_property_assertion(disease_individual, has_name, disease_name)

    # Add some diagnoses (object properties linking people to diseases)
    print("Adding relationships...")
    person1 = owl2.NamedIndividual(make_iri("Person1"))
    person5 = owl2.NamedIndividual(make_iri("Person5"))
    person8 = owl2.NamedIndividual(make_iri("Person8"))

    disease1 = owl2.NamedIndividual(make_iri("Disease1"))
    disease2 = owl2.NamedIndividual(make_iri("Disease2"))

    ont.add_object_property_assertion(person1, has_diagnosis, disease1)
    ont.add_object_property_assertion(person5, has_diagnosis, disease2)
    ont.add_object_property_assertion(person8, has_diagnosis, disease1)

    print(f"Created ontology with {ont.get_axiom_count()} axioms")

    return ont


def test_turtle_serialization():
    """Test Turtle serialization."""

    print("=" * 70)
    print("TURTLE SERIALIZER TEST")
    print("=" * 70)
    print()

    # Create test ontology
    ont = create_test_ontology()

    # Serialize to Turtle
    print("\nSerializing to Turtle format...")
    turtle_content = owl2.TurtleSerializer.serialize(ont)

    print(f"\nTurtle output ({len(turtle_content)} bytes):")
    print("-" * 70)
    print(turtle_content)
    print("-" * 70)

    # Save to file
    output_file = "test_output.ttl"
    print(f"\nSaving to {output_file}...")
    success = owl2.TurtleSerializer.serialize_to_file(ont, output_file)

    if success:
        print(f"✓ Successfully saved to {output_file}")

        # Read back and show file size
        with open(output_file, "r") as f:
            content = f.read()
            print(f"  File size: {len(content)} bytes")
            print(f"  Lines: {len(content.splitlines())}")
    else:
        print("✗ Failed to save file")

    # Compare with RDF/XML for size
    print("\nComparing with RDF/XML...")
    rdfxml_content = owl2.RDFXMLSerializer.serialize(ont)
    print(f"  RDF/XML size: {len(rdfxml_content)} bytes")
    print(f"  Turtle size:  {len(turtle_content)} bytes")
    print(
        f"  Savings:      {len(rdfxml_content) - len(turtle_content)} bytes ({100 * (1 - len(turtle_content) / len(rdfxml_content)):.1f}% smaller)"
    )

    print("\n" + "=" * 70)
    print("TEST COMPLETE")
    print("=" * 70)


def test_custom_prefixes():
    """Test Turtle serialization with custom prefixes."""

    print("\n\n" + "=" * 70)
    print("CUSTOM PREFIXES TEST")
    print("=" * 70)
    print()

    # Create simple ontology
    ont = owl2.Ontology(owl2.IRI("http://example.org/test"))

    disease_iri = owl2.IRI("http://purl.obolibrary.org/obo/DOID_4")
    disease_class = owl2.Class(disease_iri)
    ont.add_axiom(owl2.Declaration(owl2.EntityType.CLASS, disease_iri))

    # Serialize with custom prefix
    custom_prefixes = {"obo": "http://purl.obolibrary.org/obo/"}

    turtle_content = owl2.TurtleSerializer.serialize(ont, custom_prefixes)

    print("Turtle with custom 'obo:' prefix:")
    print("-" * 70)
    print(turtle_content)
    print("-" * 70)

    if "obo:DOID_4" in turtle_content:
        print("\n✓ Custom prefix successfully used!")
    else:
        print("\n✗ Custom prefix not found in output")


if __name__ == "__main__":
    test_turtle_serialization()
    test_custom_prefixes()
