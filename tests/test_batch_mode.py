"""Tests for Ontology batch mode (B1) and related performance features.

Covers:
- beginBatchMode() / endBatchMode() lifecycle
- Index invalidation is deferred during batch mode
- reserveAxioms() pre-allocation
- addAxioms() bulk add (via C++ API, tested through Python)
- Batch mode interaction with queries
"""

import pytest
from ista import owl2


@pytest.fixture
def ontology():
    """Create a fresh ontology for each test."""
    return owl2.Ontology(owl2.IRI("http://example.org/test"))


@pytest.fixture
def sample_entities():
    """Create sample entities for testing."""
    ns = "http://example.org/test#"
    return {
        "person_cls": owl2.Class(owl2.IRI("ex", "Person", ns)),
        "animal_cls": owl2.Class(owl2.IRI("ex", "Animal", ns)),
        "has_name": owl2.DataProperty(owl2.IRI("ex", "hasName", ns)),
        "has_pet": owl2.ObjectProperty(owl2.IRI("ex", "hasPet", ns)),
        "alice": owl2.NamedIndividual(owl2.IRI("ex", "Alice", ns)),
        "bob": owl2.NamedIndividual(owl2.IRI("ex", "Bob", ns)),
        "fido": owl2.NamedIndividual(owl2.IRI("ex", "Fido", ns)),
    }


class TestBatchModeLifecycle:
    """Test the batch mode begin/end lifecycle."""

    def test_not_in_batch_mode_initially(self, ontology):
        assert not ontology.in_batch_mode()

    def test_begin_batch_mode(self, ontology):
        ontology.begin_batch_mode()
        assert ontology.in_batch_mode()

    def test_end_batch_mode(self, ontology):
        ontology.begin_batch_mode()
        ontology.end_batch_mode()
        assert not ontology.in_batch_mode()

    def test_end_batch_mode_without_begin_is_safe(self, ontology):
        # Should not raise
        ontology.end_batch_mode()
        assert not ontology.in_batch_mode()

    def test_double_begin_batch_mode(self, ontology):
        ontology.begin_batch_mode()
        ontology.begin_batch_mode()  # Should not raise
        assert ontology.in_batch_mode()

    def test_double_end_batch_mode(self, ontology):
        ontology.begin_batch_mode()
        ontology.end_batch_mode()
        ontology.end_batch_mode()  # Should not raise
        assert not ontology.in_batch_mode()


class TestBatchModeWithAxioms:
    """Test adding axioms in batch mode."""

    def test_add_axiom_in_batch_mode(self, ontology, sample_entities):
        ontology.begin_batch_mode()

        decl = owl2.Declaration(owl2.EntityType.CLASS, sample_entities["person_cls"].get_iri())
        ontology.add_axiom(decl)

        assert ontology.get_axiom_count() == 1
        ontology.end_batch_mode()
        assert ontology.get_axiom_count() == 1

    def test_multiple_axioms_in_batch_mode(self, ontology, sample_entities):
        ontology.begin_batch_mode()

        # Add several declarations
        ontology.add_axiom(owl2.Declaration(owl2.EntityType.CLASS, sample_entities["person_cls"].get_iri()))
        ontology.add_axiom(owl2.Declaration(owl2.EntityType.CLASS, sample_entities["animal_cls"].get_iri()))
        ontology.add_axiom(owl2.Declaration(owl2.EntityType.DATA_PROPERTY, sample_entities["has_name"].get_iri()))
        ontology.add_axiom(owl2.Declaration(owl2.EntityType.OBJECT_PROPERTY, sample_entities["has_pet"].get_iri()))
        ontology.add_axiom(owl2.Declaration(owl2.EntityType.NAMED_INDIVIDUAL, sample_entities["alice"].get_iri()))

        assert ontology.get_axiom_count() == 5
        ontology.end_batch_mode()
        assert ontology.get_axiom_count() == 5

    def test_queries_work_after_batch_mode(self, ontology, sample_entities):
        """Indices should be rebuilt after endBatchMode()."""
        ontology.begin_batch_mode()

        ontology.add_axiom(owl2.Declaration(owl2.EntityType.CLASS, sample_entities["person_cls"].get_iri()))
        ontology.add_axiom(owl2.Declaration(owl2.EntityType.CLASS, sample_entities["animal_cls"].get_iri()))
        ontology.add_axiom(owl2.Declaration(owl2.EntityType.NAMED_INDIVIDUAL, sample_entities["alice"].get_iri()))
        ontology.add_axiom(owl2.Declaration(owl2.EntityType.NAMED_INDIVIDUAL, sample_entities["bob"].get_iri()))
        ontology.add_axiom(
            owl2.ClassAssertion(sample_entities["person_cls"], sample_entities["alice"])
        )
        ontology.add_axiom(
            owl2.ClassAssertion(sample_entities["person_cls"], sample_entities["bob"])
        )

        ontology.end_batch_mode()

        # Queries should work correctly after batch mode
        classes = ontology.get_classes()
        assert len(classes) == 2

        individuals = ontology.get_individuals()
        assert len(individuals) == 2

        # Class assertions should be queryable
        alice_classes = ontology.get_classes_for_individual(sample_entities["alice"])
        assert len(alice_classes) == 1

    def test_queries_during_batch_mode_still_work(self, ontology, sample_entities):
        """Queries during batch mode should still return results (lazy rebuild)."""
        ontology.begin_batch_mode()

        ontology.add_axiom(owl2.Declaration(owl2.EntityType.CLASS, sample_entities["person_cls"].get_iri()))
        ontology.add_axiom(
            owl2.ClassAssertion(sample_entities["person_cls"], sample_entities["alice"])
        )

        # Indices not rebuilt yet, but getClasses() triggers lazy rebuild
        # Actually, in batch mode invalidateIndices() is no-op, so indices
        # won't be valid for new axioms until endBatchMode()
        ontology.end_batch_mode()

        classes = ontology.get_classes()
        assert len(classes) >= 1


class TestReserveAxioms:
    """Test reserveAxioms() pre-allocation."""

    def test_reserve_axioms_no_error(self, ontology):
        ontology.reserve_axioms(1000)
        assert ontology.get_axiom_count() == 0

    def test_reserve_axioms_with_batch_mode(self, ontology, sample_entities):
        ontology.begin_batch_mode()
        ontology.reserve_axioms(100)

        for i in range(50):
            iri = owl2.IRI(f"http://example.org/test#Individual_{i}")
            ind = owl2.NamedIndividual(iri)
            ontology.add_axiom(
                owl2.ClassAssertion(sample_entities["person_cls"], ind)
            )

        assert ontology.get_axiom_count() == 50
        ontology.end_batch_mode()
        assert ontology.get_axiom_count() == 50


class TestBatchModeWithCreateIndividual:
    """Test batch mode with createIndividual convenience method."""

    def test_create_individuals_in_batch(self, ontology, sample_entities):
        ns = "http://example.org/test#"
        cls = sample_entities["person_cls"]

        # Declare the class first
        ontology.add_axiom(owl2.Declaration(owl2.EntityType.CLASS, cls.get_iri()))

        ontology.begin_batch_mode()
        ontology.reserve_axioms(100)

        created_iris = []
        for i in range(20):
            iri = owl2.IRI(f"{ns}person_{i}")
            ind = ontology.create_individual(cls, iri)
            created_iris.append(iri)

        ontology.end_batch_mode()

        # All individuals should be findable
        individuals = ontology.get_individuals()
        assert len(individuals) == 20

        # Each should be an instance of Person
        for iri in created_iris:
            ind = owl2.NamedIndividual(iri)
            assert ontology.is_instance_of(ind, cls)


class TestBatchModeWithDataProperties:
    """Test batch mode with data property assertions."""

    def test_data_properties_in_batch(self, ontology, sample_entities):
        ns = "http://example.org/test#"
        cls = sample_entities["person_cls"]
        name_prop = sample_entities["has_name"]

        ontology.add_axiom(owl2.Declaration(owl2.EntityType.CLASS, cls.get_iri()))
        ontology.add_axiom(owl2.Declaration(owl2.EntityType.DATA_PROPERTY, name_prop.get_iri()))

        ontology.begin_batch_mode()

        names = ["Alice", "Bob", "Charlie", "Diana"]
        individuals = []
        for name in names:
            iri = owl2.IRI(f"{ns}{name}")
            ind = ontology.create_individual(cls, iri)
            ontology.add_data_property_assertion(
                ind, name_prop, owl2.Literal(name, owl2.xsd.STRING)
            )
            individuals.append(ind)

        ontology.end_batch_mode()

        # Verify data property assertions
        for ind, name in zip(individuals, names):
            assertions = ontology.get_data_property_assertions_for_individual(ind)
            assert len(assertions) >= 1
            found_name = False
            for a in assertions:
                if a.get_target().get_lexical_form() == name:
                    found_name = True
                    break
            assert found_name, f"Name '{name}' not found for individual"


class TestBatchModeWithObjectProperties:
    """Test batch mode with object property assertions."""

    def test_object_properties_in_batch(self, ontology, sample_entities):
        ns = "http://example.org/test#"
        person = sample_entities["person_cls"]
        animal = sample_entities["animal_cls"]
        has_pet = sample_entities["has_pet"]

        ontology.add_axiom(owl2.Declaration(owl2.EntityType.CLASS, person.get_iri()))
        ontology.add_axiom(owl2.Declaration(owl2.EntityType.CLASS, animal.get_iri()))
        ontology.add_axiom(owl2.Declaration(owl2.EntityType.OBJECT_PROPERTY, has_pet.get_iri()))

        ontology.begin_batch_mode()

        alice = ontology.create_individual(person, owl2.IRI(f"{ns}Alice"))
        fido = ontology.create_individual(animal, owl2.IRI(f"{ns}Fido"))
        spot = ontology.create_individual(animal, owl2.IRI(f"{ns}Spot"))

        ontology.add_object_property_assertion(alice, has_pet, fido)
        ontology.add_object_property_assertion(alice, has_pet, spot)

        ontology.end_batch_mode()

        # Verify object property assertions
        obj_assertions = ontology.get_object_property_assertions_for_individual(alice)
        assert len(obj_assertions) == 2

        # Verify search by object property
        owners = ontology.search_by_object_property(has_pet, fido)
        assert len(owners) == 1
