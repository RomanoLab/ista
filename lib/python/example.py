#!/usr/bin/env python3
"""
Example usage of the libista OWL2 Python bindings

This script demonstrates creating an ontology, adding axioms, and serializing
to OWL2 Functional Syntax.
"""

# Note: This assumes the module has been built and is in the Python path
# You may need to add the build directory to sys.path
import sys
import os

# Uncomment and adjust if needed:
# sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../build/lib/python'))

try:
    from libista_owl2 import (
        IRI,
        Class,
        ObjectProperty,
        DataProperty,
        NamedIndividual,
        Ontology,
        Declaration,
        EntityType,
        SubClassOf,
        EquivalentClasses,
        ClassAssertion,
        ObjectPropertyAssertion,
        DataPropertyAssertion,
        NamedClass,
        ObjectSomeValuesFrom,
        Literal,
        Annotation,
        AnnotationProperty,
        FunctionalSyntaxSerializer,
        xsd,
    )
except ImportError as e:
    print(f"Error importing libista_owl2: {e}")
    print("\nMake sure you have:")
    print("1. Built the Python bindings (see README.md)")
    print("2. Added the build directory to your PYTHONPATH")
    print("\nExample:")
    print("  export PYTHONPATH=/path/to/build/lib/python:$PYTHONPATH")
    sys.exit(1)


def main():
    print("Creating OWL2 Ontology using libista Python bindings\n")
    print("=" * 70)

    # ========================================================================
    # 1. Create Ontology and Register Prefixes
    # ========================================================================
    print("\n1. Creating ontology and registering prefixes...")

    onto_iri = IRI("http://example.org/university")
    onto = Ontology(onto_iri)

    # Register common prefixes
    onto.register_prefix("ex", "http://example.org/university#")
    onto.register_prefix("rdfs", "http://www.w3.org/2000/01/rdf-schema#")
    onto.register_prefix("owl", "http://www.w3.org/2002/07/owl#")

    print(f"  Created ontology: {onto_iri.get_full_iri()}")
    print(f"  Registered {len(onto.get_prefix_map())} prefixes")

    # ========================================================================
    # 2. Create Classes
    # ========================================================================
    print("\n2. Creating classes...")

    # Create class IRIs
    person_iri = IRI("ex", "Person", "http://example.org/university#")
    student_iri = IRI("ex", "Student", "http://example.org/university#")
    professor_iri = IRI("ex", "Professor", "http://example.org/university#")
    course_iri = IRI("ex", "Course", "http://example.org/university#")

    # Create class objects
    person = Class(person_iri)
    student = Class(student_iri)
    professor = Class(professor_iri)
    course = Class(course_iri)

    # Declare classes
    onto.add_axiom(Declaration(EntityType.CLASS, person_iri))
    onto.add_axiom(Declaration(EntityType.CLASS, student_iri))
    onto.add_axiom(Declaration(EntityType.CLASS, professor_iri))
    onto.add_axiom(Declaration(EntityType.CLASS, course_iri))

    print(f"  Created {onto.get_class_count()} classes")

    # ========================================================================
    # 3. Add Class Hierarchy
    # ========================================================================
    print("\n3. Adding class hierarchy...")

    # Student ⊑ Person
    onto.add_axiom(SubClassOf(NamedClass(student), NamedClass(person)))

    # Professor ⊑ Person
    onto.add_axiom(SubClassOf(NamedClass(professor), NamedClass(person)))

    print("  Added subclass axioms:")
    print("    Student ⊑ Person")
    print("    Professor ⊑ Person")

    # ========================================================================
    # 4. Create Properties
    # ========================================================================
    print("\n4. Creating properties...")

    # Object properties
    teaches_iri = IRI("ex", "teaches", "http://example.org/university#")
    attends_iri = IRI("ex", "attends", "http://example.org/university#")

    teaches = ObjectProperty(teaches_iri)
    attends = ObjectProperty(attends_iri)

    onto.add_axiom(Declaration(EntityType.OBJECT_PROPERTY, teaches_iri))
    onto.add_axiom(Declaration(EntityType.OBJECT_PROPERTY, attends_iri))

    # Data properties
    name_iri = IRI("ex", "name", "http://example.org/university#")
    age_iri = IRI("ex", "age", "http://example.org/university#")
    email_iri = IRI("ex", "email", "http://example.org/university#")

    name_prop = DataProperty(name_iri)
    age_prop = DataProperty(age_iri)
    email_prop = DataProperty(email_iri)

    onto.add_axiom(Declaration(EntityType.DATA_PROPERTY, name_iri))
    onto.add_axiom(Declaration(EntityType.DATA_PROPERTY, age_iri))
    onto.add_axiom(Declaration(EntityType.DATA_PROPERTY, email_iri))

    print(f"  Created {onto.get_object_property_count()} object properties")
    print(f"  Created {onto.get_data_property_count()} data properties")

    # ========================================================================
    # 5. Create Individuals and Assertions
    # ========================================================================
    print("\n5. Creating individuals and assertions...")

    # Create individuals
    john_iri = IRI("ex", "John", "http://example.org/university#")
    mary_iri = IRI("ex", "Mary", "http://example.org/university#")
    cs101_iri = IRI("ex", "CS101", "http://example.org/university#")

    john = NamedIndividual(john_iri)
    mary = NamedIndividual(mary_iri)
    cs101 = NamedIndividual(cs101_iri)

    onto.add_axiom(Declaration(EntityType.NAMED_INDIVIDUAL, john_iri))
    onto.add_axiom(Declaration(EntityType.NAMED_INDIVIDUAL, mary_iri))
    onto.add_axiom(Declaration(EntityType.NAMED_INDIVIDUAL, cs101_iri))

    # Class assertions
    onto.add_axiom(ClassAssertion(NamedClass(professor), john))
    onto.add_axiom(ClassAssertion(NamedClass(student), mary))
    onto.add_axiom(ClassAssertion(NamedClass(course), cs101))

    # Object property assertions
    onto.add_axiom(ObjectPropertyAssertion(teaches, john, cs101))
    onto.add_axiom(ObjectPropertyAssertion(attends, mary, cs101))

    # Data property assertions
    onto.add_axiom(DataPropertyAssertion(name_prop, john, Literal("John Smith", "en")))
    onto.add_axiom(DataPropertyAssertion(age_prop, john, Literal("45", xsd.INTEGER)))
    onto.add_axiom(
        DataPropertyAssertion(
            email_prop, john, Literal("john.smith@university.edu", xsd.STRING)
        )
    )

    onto.add_axiom(
        DataPropertyAssertion(name_prop, mary, Literal("Mary Johnson", "en"))
    )
    onto.add_axiom(DataPropertyAssertion(age_prop, mary, Literal("22", xsd.INTEGER)))

    print(f"  Created {onto.get_individual_count()} individuals")
    print("  Added class and property assertions")

    # ========================================================================
    # 6. Add Annotations
    # ========================================================================
    print("\n6. Adding annotations...")

    rdfs_label = AnnotationProperty(IRI("http://www.w3.org/2000/01/rdf-schema#label"))
    rdfs_comment = AnnotationProperty(
        IRI("http://www.w3.org/2000/01/rdf-schema#comment")
    )

    # Add ontology annotations
    onto.add_ontology_annotation(
        Annotation(rdfs_label, Literal("University Ontology", "en"))
    )
    onto.add_ontology_annotation(
        Annotation(
            rdfs_comment, Literal("An example ontology about universities", "en")
        )
    )

    print(f"  Added {len(onto.get_ontology_annotations())} ontology annotations")

    # ========================================================================
    # 7. Display Statistics
    # ========================================================================
    print("\n7. Ontology Statistics:")
    print("  " + "\n  ".join(onto.get_statistics().split("\n")))

    # ========================================================================
    # 8. Serialize to Functional Syntax
    # ========================================================================
    print("\n8. Serializing to OWL2 Functional Syntax...\n")
    print("=" * 70)

    functional_syntax = onto.to_functional_syntax()
    print(functional_syntax)

    # ========================================================================
    # 9. Save to File (optional)
    # ========================================================================
    output_file = "university_ontology.ofn"
    if FunctionalSyntaxSerializer.serialize_to_file(onto, output_file):
        print("\n" + "=" * 70)
        print(f"\nSuccessfully saved ontology to: {output_file}")
    else:
        print(f"\nFailed to save ontology to: {output_file}")

    # ========================================================================
    # 10. Query the Ontology
    # ========================================================================
    print("\n" + "=" * 70)
    print("\n10. Querying the ontology...")

    print(f"\nAll classes:")
    for cls in onto.get_classes():
        print(f"  - {cls.get_iri().get_abbreviated()}")

    print(f"\nSubclasses of Person:")
    subclass_axioms = onto.get_sub_class_axioms_for_super_class(person)
    for axiom in subclass_axioms:
        print(f"  - {axiom.to_functional_syntax()}")

    print(f"\nAssertions about John:")
    class_assertions = onto.get_class_assertions(john)
    for assertion in class_assertions:
        print(f"  - {assertion.to_functional_syntax()}")

    obj_prop_assertions = onto.get_object_property_assertions(john)
    for assertion in obj_prop_assertions:
        print(f"  - {assertion.to_functional_syntax()}")

    data_prop_assertions = onto.get_data_property_assertions(john)
    for assertion in data_prop_assertions:
        print(f"  - {assertion.to_functional_syntax()}")

    print("\n" + "=" * 70)
    print("\nExample completed successfully!")


if __name__ == "__main__":
    main()
