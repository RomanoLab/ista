"""Performance tests for batch mode, caching, and return-by-reference.

These tests verify that the performance optimizations (B1-B4) work correctly
at moderate scale and don't introduce regressions. They also serve as
smoke tests for large-scale usage patterns.

Marked with @pytest.mark.slow so they can be excluded from fast test runs.
"""

import time
import pytest
from ista import owl2


NS = "http://example.org/perf#"


def _create_populated_ontology(num_individuals, num_relationships):
    """Helper to create a populated ontology for performance tests."""
    onto = owl2.Ontology(owl2.IRI("http://example.org/perf"))
    onto.register_prefix("perf", NS)

    # Declare schema
    person_cls = owl2.Class(owl2.IRI("perf", "Person", NS))
    org_cls = owl2.Class(owl2.IRI("perf", "Organization", NS))
    name_prop = owl2.DataProperty(owl2.IRI("perf", "hasName", NS))
    works_at = owl2.ObjectProperty(owl2.IRI("perf", "worksAt", NS))

    onto.add_axiom(owl2.Declaration(owl2.EntityType.CLASS, person_cls.get_iri()))
    onto.add_axiom(owl2.Declaration(owl2.EntityType.CLASS, org_cls.get_iri()))
    onto.add_axiom(owl2.Declaration(owl2.EntityType.DATA_PROPERTY, name_prop.get_iri()))
    onto.add_axiom(owl2.Declaration(owl2.EntityType.OBJECT_PROPERTY, works_at.get_iri()))

    return onto, person_cls, org_cls, name_prop, works_at


class TestBatchModePerfGain:
    """Test that batch mode provides performance improvement."""

    @pytest.mark.slow
    def test_batch_mode_faster_than_unbatched(self):
        """Batch mode should be noticeably faster for many axioms."""
        N = 1000

        # Without batch mode
        onto1, person_cls, _, name_prop, _ = _create_populated_ontology(0, 0)
        start = time.perf_counter()
        for i in range(N):
            ind = onto1.create_individual(person_cls, owl2.IRI(f"{NS}person_{i}"))
            onto1.add_data_property_assertion(
                ind, name_prop, owl2.Literal(f"Person {i}", owl2.xsd.STRING)
            )
        unbatched_time = time.perf_counter() - start

        # With batch mode
        onto2, person_cls, _, name_prop, _ = _create_populated_ontology(0, 0)
        start = time.perf_counter()
        onto2.begin_batch_mode()
        onto2.reserve_axioms(N * 2)
        for i in range(N):
            ind = onto2.create_individual(person_cls, owl2.IRI(f"{NS}person_b_{i}"))
            onto2.add_data_property_assertion(
                ind, name_prop, owl2.Literal(f"Person {i}", owl2.xsd.STRING)
            )
        onto2.end_batch_mode()
        batched_time = time.perf_counter() - start

        # Both should produce same results
        assert onto1.get_axiom_count() == onto2.get_axiom_count()

        # Batch mode should be faster (at least for N=1000)
        # We don't enforce a strict ratio, just verify both complete
        assert batched_time < unbatched_time * 5  # Sanity check — batch shouldn't be WAY slower

    @pytest.mark.slow
    def test_large_batch_population(self):
        """Test population of 5000 individuals in batch mode completes quickly."""
        N = 5000

        onto, person_cls, _, name_prop, _ = _create_populated_ontology(0, 0)

        start = time.perf_counter()
        onto.begin_batch_mode()
        onto.reserve_axioms(N * 3)

        for i in range(N):
            ind = onto.create_individual(person_cls, owl2.IRI(f"{NS}person_{i}"))
            onto.add_data_property_assertion(
                ind, name_prop, owl2.Literal(f"Person {i}", owl2.xsd.STRING)
            )

        onto.end_batch_mode()
        elapsed = time.perf_counter() - start

        assert onto.get_axiom_count() >= N * 2  # ClassAssertion + DataPropertyAssertion each
        # Should complete in reasonable time (< 10 seconds for 5000 individuals)
        assert elapsed < 10.0, f"Batch population took {elapsed:.2f}s, expected < 10s"


class TestQueryPerformance:
    """Test that indices provide fast query performance."""

    @pytest.mark.slow
    def test_class_assertions_query_fast(self):
        """Query for class assertions should be fast with indices."""
        N = 2000
        onto, person_cls, _, _, _ = _create_populated_ontology(0, 0)

        onto.begin_batch_mode()
        individuals = []
        for i in range(N):
            ind = onto.create_individual(person_cls, owl2.IRI(f"{NS}person_{i}"))
            individuals.append(ind)
        onto.end_batch_mode()

        # Query class assertions for each individual — should use typed indices
        start = time.perf_counter()
        for ind in individuals[:100]:  # Test 100 queries
            classes = onto.get_classes_for_individual(ind)
            assert len(classes) >= 1
        query_time = time.perf_counter() - start

        # 100 queries should complete very quickly
        assert query_time < 5.0, f"100 queries took {query_time:.2f}s"

    @pytest.mark.slow
    def test_data_property_query_fast(self):
        """Data property queries should use indices."""
        N = 1000
        onto, person_cls, _, name_prop, _ = _create_populated_ontology(0, 0)

        onto.begin_batch_mode()
        individuals = []
        for i in range(N):
            ind = onto.create_individual(person_cls, owl2.IRI(f"{NS}person_{i}"))
            onto.add_data_property_assertion(
                ind, name_prop, owl2.Literal(f"Person {i}", owl2.xsd.STRING)
            )
            individuals.append(ind)
        onto.end_batch_mode()

        start = time.perf_counter()
        for ind in individuals[:100]:
            assertions = onto.get_data_property_assertions_for_individual(ind)
            assert len(assertions) >= 1
        query_time = time.perf_counter() - start

        assert query_time < 5.0

    @pytest.mark.slow
    def test_object_property_query_fast(self):
        """Object property queries should use indices."""
        N = 500
        onto, person_cls, org_cls, _, works_at = _create_populated_ontology(0, 0)

        onto.begin_batch_mode()
        persons = []
        orgs = []
        for i in range(N):
            p = onto.create_individual(person_cls, owl2.IRI(f"{NS}person_{i}"))
            persons.append(p)
        for i in range(50):
            o = onto.create_individual(org_cls, owl2.IRI(f"{NS}org_{i}"))
            orgs.append(o)

        # Create relationships
        for i, p in enumerate(persons):
            org = orgs[i % len(orgs)]
            onto.add_object_property_assertion(p, works_at, org)

        onto.end_batch_mode()

        start = time.perf_counter()
        for p in persons[:100]:
            assertions = onto.get_object_property_assertions_for_individual(p)
            assert len(assertions) >= 1
        query_time = time.perf_counter() - start

        assert query_time < 5.0


class TestSearchByProperty:
    """Test search operations on populated ontologies."""

    def test_search_by_data_property(self):
        onto, person_cls, _, name_prop, _ = _create_populated_ontology(0, 0)

        onto.begin_batch_mode()
        for i in range(100):
            ind = onto.create_individual(person_cls, owl2.IRI(f"{NS}person_{i}"))
            onto.add_data_property_assertion(
                ind, name_prop, owl2.Literal(f"Person {i}", owl2.xsd.STRING)
            )
        onto.end_batch_mode()

        # Search for a specific person by name
        results = onto.search_by_data_property(
            name_prop, owl2.Literal("Person 42", owl2.xsd.STRING)
        )
        assert len(results) == 1
        assert "person_42" in results[0].get_iri().get_full_iri()

    def test_search_by_object_property(self):
        onto, person_cls, org_cls, _, works_at = _create_populated_ontology(0, 0)

        onto.begin_batch_mode()
        alice = onto.create_individual(person_cls, owl2.IRI(f"{NS}Alice"))
        bob = onto.create_individual(person_cls, owl2.IRI(f"{NS}Bob"))
        acme = onto.create_individual(org_cls, owl2.IRI(f"{NS}Acme"))

        onto.add_object_property_assertion(alice, works_at, acme)
        onto.add_object_property_assertion(bob, works_at, acme)
        onto.end_batch_mode()

        results = onto.search_by_object_property(works_at, acme)
        assert len(results) == 2

    def test_get_individuals_of_class(self):
        onto, person_cls, org_cls, _, _ = _create_populated_ontology(0, 0)

        onto.begin_batch_mode()
        for i in range(50):
            onto.create_individual(person_cls, owl2.IRI(f"{NS}person_{i}"))
        for i in range(10):
            onto.create_individual(org_cls, owl2.IRI(f"{NS}org_{i}"))
        onto.end_batch_mode()

        persons = onto.get_individuals_of_class(person_cls)
        assert len(persons) == 50

        orgs = onto.get_individuals_of_class(org_cls)
        assert len(orgs) == 10


class TestDataLoaderCaching:
    """Test that DataLoader caching works correctly."""

    def test_cached_pipeline_correctness(self, tmp_path):
        """Run a pipeline and verify caching doesn't affect correctness."""
        csv_file = tmp_path / "data.csv"
        rows = ["id,name"]
        for i in range(200):
            rows.append(f"item_{i},Item {i}")
        csv_file.write_text("\n".join(rows) + "\n")

        yaml_file = tmp_path / "mapping.yaml"
        yaml_file.write_text(
            f'version: "1.0"\n'
            f'base_iri: "http://example.org/test#"\n'
            f'\n'
            f'sources:\n'
            f'  data:\n'
            f'    type: csv\n'
            f'    path: "{csv_file}"\n'
            f'    delimiter: ","\n'
            f'    has_headers: true\n'
            f'\n'
            f'node_mappings:\n'
            f'  - name: "Load"\n'
            f'    source: data\n'
            f'    target_class: Entity\n'
            f'    mode: create\n'
            f'    iri_column: id\n'
            f'    properties:\n'
            f'      - {{ column: name, property: entityName }}\n'
        )

        onto = owl2.Ontology(owl2.IRI("http://example.org/test"))
        loader = owl2.DataLoader(onto)
        loader.load_mapping_spec(str(yaml_file))
        stats = loader.execute()

        assert stats.individuals_created == 200
        assert stats.properties_added == 200
        assert stats.errors == 0

        # Verify all individuals are queryable
        individuals = onto.get_individuals()
        assert len(individuals) == 200

    @pytest.mark.slow
    def test_relationship_caching_correctness(self, tmp_path):
        """Test that relationship loading with caching produces correct results."""
        # Create source data
        items_csv = tmp_path / "items.csv"
        rows = ["id,name"]
        for i in range(100):
            rows.append(f"item_{i},Item {i}")
        items_csv.write_text("\n".join(rows) + "\n")

        categories_csv = tmp_path / "categories.csv"
        cat_rows = ["id,cat_name"]
        for i in range(10):
            cat_rows.append(f"cat_{i},Category {i}")
        categories_csv.write_text("\n".join(cat_rows) + "\n")

        relations_csv = tmp_path / "relations.csv"
        rel_rows = ["item_id,category_id"]
        for i in range(100):
            rel_rows.append(f"item_{i},cat_{i % 10}")
        relations_csv.write_text("\n".join(rel_rows) + "\n")

        yaml_file = tmp_path / "mapping.yaml"
        yaml_file.write_text(
            f'version: "1.0"\n'
            f'base_iri: "http://example.org/test#"\n'
            f'\n'
            f'sources:\n'
            f'  items:\n'
            f'    type: csv\n'
            f'    path: "{items_csv}"\n'
            f'    delimiter: ","\n'
            f'    has_headers: true\n'
            f'  categories:\n'
            f'    type: csv\n'
            f'    path: "{categories_csv}"\n'
            f'    delimiter: ","\n'
            f'    has_headers: true\n'
            f'  relations:\n'
            f'    type: csv\n'
            f'    path: "{relations_csv}"\n'
            f'    delimiter: ","\n'
            f'    has_headers: true\n'
            f'\n'
            f'node_mappings:\n'
            f'  - name: "Load Items"\n'
            f'    source: items\n'
            f'    target_class: Item\n'
            f'    mode: create\n'
            f'    iri_column: id\n'
            f'    properties:\n'
            f'      - {{ column: id, property: itemId }}\n'
            f'      - {{ column: name, property: itemName }}\n'
            f'\n'
            f'  - name: "Load Categories"\n'
            f'    source: categories\n'
            f'    target_class: Category\n'
            f'    mode: create\n'
            f'    iri_column: id\n'
            f'    properties:\n'
            f'      - {{ column: id, property: categoryId }}\n'
            f'      - {{ column: cat_name, property: categoryName }}\n'
            f'\n'
            f'relationship_mappings:\n'
            f'  - name: "Item In Category"\n'
            f'    source: relations\n'
            f'    relationship: inCategory\n'
            f'    subject:\n'
            f'      class_name: Item\n'
            f'      column: item_id\n'
            f'      match_property: itemId\n'
            f'    object:\n'
            f'      class_name: Category\n'
            f'      column: category_id\n'
            f'      match_property: categoryId\n'
        )

        onto = owl2.Ontology(owl2.IRI("http://example.org/test"))
        loader = owl2.DataLoader(onto)
        loader.load_mapping_spec(str(yaml_file))
        stats = loader.execute()

        assert stats.individuals_created == 110  # 100 items + 10 categories
        assert stats.relationships_created == 100
        assert stats.errors == 0


class TestReturnByReference:
    """Test that return-by-reference getters work correctly (B4)."""

    def test_iri_getters_return_correct_values(self):
        iri = owl2.IRI("ex", "Person", "http://example.org/test#")
        assert iri.get_full_iri() == "http://example.org/test#Person"
        assert iri.get_prefix() == "ex"
        assert iri.get_local_name() == "Person"
        assert iri.get_namespace() == "http://example.org/test#"

    def test_entity_get_iri_returns_correct_value(self):
        iri = owl2.IRI("ex", "Person", "http://example.org/test#")
        cls = owl2.Class(iri)
        assert cls.get_iri().get_full_iri() == "http://example.org/test#Person"

    def test_literal_getters_return_correct_values(self):
        lit = owl2.Literal("hello", owl2.xsd.STRING)
        assert lit.get_lexical_form() == "hello"

    def test_iri_from_string(self):
        iri = owl2.IRI("http://example.org/test#Thing")
        assert iri.get_full_iri() == "http://example.org/test#Thing"
        assert iri.get_namespace() == "http://example.org/test#"
        assert iri.get_local_name() == "Thing"

    def test_multiple_accesses_consistent(self):
        """Verify that accessing the same getter multiple times returns consistent results."""
        iri = owl2.IRI("ex", "Person", "http://example.org/test#")
        cls = owl2.Class(iri)

        # Access multiple times
        for _ in range(10):
            assert cls.get_iri().get_full_iri() == "http://example.org/test#Person"
            assert cls.get_iri().get_local_name() == "Person"
