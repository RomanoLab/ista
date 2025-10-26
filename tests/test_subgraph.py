"""
Test script for C++ subgraph extraction features.

This module tests the high-performance C++ subgraph extraction functionality
exposed through Python bindings, including filtering, neighborhood extraction,
path finding, and random sampling operations.
"""

import sys

from ista.owl2 import (
    Ontology,
    IRI,
    Class,
    NamedIndividual,
    ObjectProperty,
    ClassAssertion,
    ObjectPropertyAssertion,
    OntologyFilter,
    FilterCriteria,
)


def create_test_ontology():
    """
    Create a test ontology representing a social network.

    Constructs a small ontology with Person and Organization classes,
    several named individuals (Alice, Bob, Carol, Dave, Eve, AcmeCorp),
    and relationships between them (knows, worksFor).

    Returns
    -------
    Ontology
        An ontology with 6 individuals, 2 classes, and 15 axioms
        representing a social network structure.

    Notes
    -----
    The social network has the following structure:
    - Alice knows Bob and Carol, works for AcmeCorp
    - Bob knows Carol and Dave, works for AcmeCorp
    - Carol knows Dave, works for AcmeCorp
    - Dave knows Eve
    - This creates a connected graph with path length 3 from Alice to Eve
    """
    ont = Ontology(IRI("http://example.org/social"))

    # Classes
    person_cls = Class(IRI("http://example.org/social#Person"))
    organization_cls = Class(IRI("http://example.org/social#Organization"))

    # Properties
    knows_prop = ObjectProperty(IRI("http://example.org/social#knows"))
    works_for_prop = ObjectProperty(IRI("http://example.org/social#worksFor"))

    # Individuals
    alice = NamedIndividual(IRI("http://example.org/social#Alice"))
    bob = NamedIndividual(IRI("http://example.org/social#Bob"))
    carol = NamedIndividual(IRI("http://example.org/social#Carol"))
    dave = NamedIndividual(IRI("http://example.org/social#Dave"))
    eve = NamedIndividual(IRI("http://example.org/social#Eve"))
    acme = NamedIndividual(IRI("http://example.org/social#AcmeCorp"))

    # Add class assertions
    ont.add_axiom(ClassAssertion(person_cls, alice))
    ont.add_axiom(ClassAssertion(person_cls, bob))
    ont.add_axiom(ClassAssertion(person_cls, carol))
    ont.add_axiom(ClassAssertion(person_cls, dave))
    ont.add_axiom(ClassAssertion(person_cls, eve))
    ont.add_axiom(ClassAssertion(organization_cls, acme))

    # Add relationships - create a connected network
    # Alice knows Bob and Carol
    ont.add_axiom(ObjectPropertyAssertion(knows_prop, alice, bob))
    ont.add_axiom(ObjectPropertyAssertion(knows_prop, alice, carol))

    # Bob knows Carol and Dave
    ont.add_axiom(ObjectPropertyAssertion(knows_prop, bob, carol))
    ont.add_axiom(ObjectPropertyAssertion(knows_prop, bob, dave))

    # Carol knows Dave
    ont.add_axiom(ObjectPropertyAssertion(knows_prop, carol, dave))

    # Dave knows Eve
    ont.add_axiom(ObjectPropertyAssertion(knows_prop, dave, eve))

    # Work relationships
    ont.add_axiom(ObjectPropertyAssertion(works_for_prop, alice, acme))
    ont.add_axiom(ObjectPropertyAssertion(works_for_prop, bob, acme))
    ont.add_axiom(ObjectPropertyAssertion(works_for_prop, carol, acme))

    return ont


def test_filter_by_individuals():
    """
    Test filtering by specific individuals.

    Verifies that OntologyFilter.filter_by_individuals() correctly extracts
    only the axioms related to specified individuals.

    Raises
    ------
    AssertionError
        If the filtered ontology doesn't have fewer axioms than the original.
    """
    print("\n=== Test 1: Filter by Individuals ===")
    ont = create_test_ontology()

    original_count = ont.get_axiom_count()
    print(f"Original ontology has {original_count} axioms")

    # Create filter for just Alice and Bob
    filter_obj = OntologyFilter(ont)
    alice_iri = IRI("http://example.org/social#Alice")
    bob_iri = IRI("http://example.org/social#Bob")

    result = filter_obj.filter_by_individuals({alice_iri, bob_iri})

    print(f"Filtered ontology has {result.filtered_axiom_count} axioms")
    print(f"Included {result.filtered_individual_count} individuals")
    print(f"Original had {result.original_individual_count} individuals")

    assert result.filtered_axiom_count < result.original_axiom_count
    print("✓ Filter by individuals works!")


def test_extract_neighborhood():
    """
    Test neighborhood extraction.

    Verifies that OntologyFilter.extract_neighborhood() correctly extracts
    k-hop neighborhoods around a seed individual. Tests both 1-hop and 2-hop
    neighborhoods and confirms that 2-hop neighborhoods are larger.

    Raises
    ------
    AssertionError
        If neighborhood extraction doesn't include expected individuals or
        if 2-hop neighborhood isn't larger than 1-hop.
    """
    print("\n=== Test 2: Extract Neighborhood ===")
    ont = create_test_ontology()

    # Extract Alice's 1-hop neighborhood
    filter_obj = OntologyFilter(ont)
    alice_iri = IRI("http://example.org/social#Alice")

    result = filter_obj.extract_neighborhood(alice_iri, 1)

    print(
        f"Alice's 1-hop neighborhood has {result.filtered_individual_count} individuals"
    )
    print(f"Contains {result.filtered_axiom_count} axioms")

    # Alice should connect to Bob, Carol, and AcmeCorp (1-hop)
    assert result.filtered_individual_count >= 3
    print("✓ Neighborhood extraction works!")

    # Test 2-hop neighborhood
    result2 = filter_obj.extract_neighborhood(alice_iri, 2)
    print(
        f"Alice's 2-hop neighborhood has {result2.filtered_individual_count} individuals"
    )

    # 2-hop should include more individuals
    assert result2.filtered_individual_count > result.filtered_individual_count
    print("✓ Multi-hop neighborhood works!")


def test_extract_path():
    """
    Test path extraction between individuals.

    Verifies that OntologyFilter.extract_path() correctly finds and extracts
    the path between two individuals in the graph.

    Raises
    ------
    AssertionError
        If the path doesn't include the expected minimum number of individuals.

    Notes
    -----
    Tests path finding from Alice to Eve, which requires traversing through
    intermediate individuals (Bob or Carol, then Dave).
    """
    print("\n=== Test 3: Extract Path ===")
    ont = create_test_ontology()

    filter_obj = OntologyFilter(ont)
    alice_iri = IRI("http://example.org/social#Alice")
    eve_iri = IRI("http://example.org/social#Eve")

    result = filter_obj.extract_path(alice_iri, eve_iri)

    print(
        f"Path from Alice to Eve includes {result.filtered_individual_count} individuals"
    )
    print(f"Path has {result.filtered_axiom_count} axioms")

    # There should be a path: Alice -> Bob -> Dave -> Eve (or Alice -> Carol -> Dave -> Eve)
    assert result.filtered_individual_count >= 4
    print("✓ Path extraction works!")


def test_random_sample():
    """
    Test random sampling.

    Verifies that OntologyFilter.random_sample() correctly samples a specified
    number of individuals from the ontology.

    Raises
    ------
    AssertionError
        If the sample contains more individuals than requested.

    Notes
    -----
    Uses a fixed random seed (42) for reproducible results.
    """
    print("\n=== Test 4: Random Sample ===")
    ont = create_test_ontology()

    filter_obj = OntologyFilter(ont)
    result = filter_obj.random_sample(3, 42)

    print(
        f"Random sample of 3 individuals has {result.filtered_individual_count} individuals"
    )
    print(f"Sample contains {result.filtered_axiom_count} axioms")

    assert result.filtered_individual_count <= 3
    print("✓ Random sampling works!")


def test_filter_by_class():
    """
    Test filtering by class membership.

    Verifies that OntologyFilter.filter_by_classes() correctly extracts
    all individuals belonging to specified classes.

    Raises
    ------
    AssertionError
        If the filtered ontology doesn't contain exactly 5 Person individuals.

    Notes
    -----
    Tests filtering by the Person class, which should return Alice, Bob,
    Carol, Dave, and Eve (but not AcmeCorp which is an Organization).
    """
    print("\n=== Test 5: Filter by Class ===")
    ont = create_test_ontology()

    filter_obj = OntologyFilter(ont)
    person_iri = IRI("http://example.org/social#Person")

    result = filter_obj.filter_by_classes({person_iri})

    print(
        f"Filtering by Person class gives {result.filtered_individual_count} individuals"
    )
    print(f"Contains {result.filtered_axiom_count} axioms")

    # Should have 5 persons (Alice, Bob, Carol, Dave, Eve)
    assert result.filtered_individual_count == 5
    print("✓ Filter by class works!")


def test_ontology_convenience_methods():
    """
    Test convenience methods on Ontology class.

    Verifies that convenience methods on the Ontology class work correctly:
    - get_individuals_of_class(): Get all individuals of a specific class
    - get_neighbors(): Get k-hop neighbors of an individual
    - has_path(): Check if a path exists between two individuals

    Raises
    ------
    AssertionError
        If any of the convenience methods return unexpected results.

    See Also
    --------
    OntologyFilter : For more advanced filtering and subgraph extraction
    """
    print("\n=== Test 6: Ontology Convenience Methods ===")
    ont = create_test_ontology()

    # Test getIndividualsOfClass
    person_cls = Class(IRI("http://example.org/social#Person"))
    persons = ont.get_individuals_of_class(person_cls)
    print(f"Found {len(persons)} individuals of class Person")
    assert len(persons) == 5

    # Test getNeighbors
    alice = NamedIndividual(IRI("http://example.org/social#Alice"))
    neighbors = ont.get_neighbors(alice, 1)
    print(f"Alice has {len(neighbors)} 1-hop neighbors")
    assert len(neighbors) >= 3

    # Test hasPath
    eve = NamedIndividual(IRI("http://example.org/social#Eve"))
    has_path = ont.has_path(alice, eve)
    print(f"Path from Alice to Eve exists: {has_path}")
    assert has_path

    print("✓ Convenience methods work!")


if __name__ == "__main__":
    print("Testing C++ Subgraph Extraction Features")
    print("=" * 50)

    try:
        test_filter_by_individuals()
        test_extract_neighborhood()
        test_extract_path()
        test_random_sample()
        test_filter_by_class()
        test_ontology_convenience_methods()

        print("\n" + "=" * 50)
        print("All tests passed! ✓")
        print("=" * 50)

    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
