"""Tests for additional_classes feature in ENRICH mode node mappings.

This feature allows enrichment mappings to add OWL class assertions to
existing individuals, implementing the ``append_class`` pattern needed
for MolecularInitiatingEvent / AdverseOutcome classification of KeyEvents.
"""

from ista import owl2


def _p(path):
    """Convert a path to forward-slash string for use in YAML on Windows."""
    return str(path).replace("\\", "/")


class TestAdditionalClasses:
    """Test that ENRICH mode can add additional OWL class assertions."""

    def test_additional_class_added(self, tmp_path):
        """An enrichment mapping with additional_classes adds class assertions."""
        events_csv = tmp_path / "events.csv"
        events_csv.write_text(
            "event_id,event_name,event_type\n"
            "KE1,Acetylcholinesterase Inhibition,molecular-initiating-event\n"
            "KE2,Neuronal Cell Death,key-event\n"
            "KE3,Learning and Memory Impairment,adverse-outcome\n"
        )

        mie_csv = tmp_path / "mie_events.csv"
        mie_csv.write_text("event_id\nKE1\n")

        ao_csv = tmp_path / "ao_events.csv"
        ao_csv.write_text("event_id\nKE3\n")

        yaml_file = tmp_path / "mapping.yaml"
        yaml_file.write_text(
            f'version: "1.0"\n'
            f'base_iri: "http://example.org/aop#"\n'
            f'\n'
            f'sources:\n'
            f'  events:\n'
            f'    type: csv\n'
            f'    path: "{_p(events_csv)}"\n'
            f'    has_headers: true\n'
            f'  mie_events:\n'
            f'    type: csv\n'
            f'    path: "{_p(mie_csv)}"\n'
            f'    has_headers: true\n'
            f'  ao_events:\n'
            f'    type: csv\n'
            f'    path: "{_p(ao_csv)}"\n'
            f'    has_headers: true\n'
            f'\n'
            f'node_mappings:\n'
            f'  - name: "Key Events"\n'
            f'    source: events\n'
            f'    target_class: KeyEvent\n'
            f'    mode: create\n'
            f'    iri_column: event_id\n'
            f'    properties:\n'
            f'      - {{ column: event_id, property: eventId }}\n'
            f'      - {{ column: event_name, property: commonName }}\n'
            f'\n'
            f'  - name: "MIE Classification"\n'
            f'    source: mie_events\n'
            f'    target_class: KeyEvent\n'
            f'    mode: enrich\n'
            f'    match:\n'
            f'      source_column: event_id\n'
            f'      target_property: eventId\n'
            f'    additional_classes:\n'
            f'      - MolecularInitiatingEvent\n'
            f'\n'
            f'  - name: "AO Classification"\n'
            f'    source: ao_events\n'
            f'    target_class: KeyEvent\n'
            f'    mode: enrich\n'
            f'    match:\n'
            f'      source_column: event_id\n'
            f'      target_property: eventId\n'
            f'    additional_classes:\n'
            f'      - AdverseOutcome\n'
        )

        onto = owl2.Ontology(owl2.IRI("http://example.org/aop"))
        loader = owl2.DataLoader(onto)
        loader.load_mapping_spec(str(yaml_file))
        stats = loader.execute()

        assert stats.individuals_created == 3
        assert stats.individuals_enriched == 2

        # Verify auto-declared classes include additional classes
        class_names = {c.get_iri().get_local_name() for c in onto.get_classes()}
        assert "KeyEvent" in class_names
        assert "MolecularInitiatingEvent" in class_names
        assert "AdverseOutcome" in class_names

        # Verify the MIE individual has both KeyEvent and MolecularInitiatingEvent
        individuals = onto.get_individuals()
        for ind in individuals:
            if "ke1" in ind.get_iri().get_full_iri().lower():
                classes = onto.get_classes_for_individual(ind)
                class_local_names = {c.get_iri().get_local_name() for c in classes}
                assert "KeyEvent" in class_local_names
                assert "MolecularInitiatingEvent" in class_local_names
                break

    def test_additional_class_without_properties(self, tmp_path):
        """ENRICH with additional_classes but no properties still works."""
        items_csv = tmp_path / "items.csv"
        items_csv.write_text("id,name\nI1,Alpha\nI2,Beta\n")

        classify_csv = tmp_path / "classify.csv"
        classify_csv.write_text("id\nI1\n")

        yaml_file = tmp_path / "mapping.yaml"
        yaml_file.write_text(
            f'version: "1.0"\n'
            f'base_iri: "http://example.org/test#"\n'
            f'\n'
            f'sources:\n'
            f'  items:\n'
            f'    type: csv\n'
            f'    path: "{_p(items_csv)}"\n'
            f'    has_headers: true\n'
            f'  classify:\n'
            f'    type: csv\n'
            f'    path: "{_p(classify_csv)}"\n'
            f'    has_headers: true\n'
            f'\n'
            f'node_mappings:\n'
            f'  - name: "Items"\n'
            f'    source: items\n'
            f'    target_class: Item\n'
            f'    mode: create\n'
            f'    iri_column: id\n'
            f'    properties:\n'
            f'      - {{ column: id, property: itemId }}\n'
            f'\n'
            f'  - name: "Special Items"\n'
            f'    source: classify\n'
            f'    target_class: Item\n'
            f'    mode: enrich\n'
            f'    match:\n'
            f'      source_column: id\n'
            f'      target_property: itemId\n'
            f'    additional_classes:\n'
            f'      - SpecialItem\n'
        )

        onto = owl2.Ontology(owl2.IRI("http://example.org/test"))
        loader = owl2.DataLoader(onto)
        loader.load_mapping_spec(str(yaml_file))
        stats = loader.execute()

        assert stats.individuals_created == 2
        assert stats.individuals_enriched == 1

        class_names = {c.get_iri().get_local_name() for c in onto.get_classes()}
        assert "SpecialItem" in class_names

    def test_multiple_additional_classes(self, tmp_path):
        """An individual can receive multiple additional class assertions."""
        data_csv = tmp_path / "data.csv"
        data_csv.write_text("id,name\nX1,TestItem\n")

        enrich_csv = tmp_path / "enrich.csv"
        enrich_csv.write_text("id\nX1\n")

        yaml_file = tmp_path / "mapping.yaml"
        yaml_file.write_text(
            f'version: "1.0"\n'
            f'base_iri: "http://example.org/test#"\n'
            f'\n'
            f'sources:\n'
            f'  data:\n'
            f'    type: csv\n'
            f'    path: "{_p(data_csv)}"\n'
            f'    has_headers: true\n'
            f'  enrich:\n'
            f'    type: csv\n'
            f'    path: "{_p(enrich_csv)}"\n'
            f'    has_headers: true\n'
            f'\n'
            f'node_mappings:\n'
            f'  - name: "Create"\n'
            f'    source: data\n'
            f'    target_class: Base\n'
            f'    mode: create\n'
            f'    iri_column: id\n'
            f'    properties:\n'
            f'      - {{ column: id, property: baseId }}\n'
            f'\n'
            f'  - name: "Multi-Classify"\n'
            f'    source: enrich\n'
            f'    target_class: Base\n'
            f'    mode: enrich\n'
            f'    match:\n'
            f'      source_column: id\n'
            f'      target_property: baseId\n'
            f'    additional_classes:\n'
            f'      - TypeA\n'
            f'      - TypeB\n'
        )

        onto = owl2.Ontology(owl2.IRI("http://example.org/test"))
        loader = owl2.DataLoader(onto)
        loader.load_mapping_spec(str(yaml_file))
        stats = loader.execute()

        class_names = {c.get_iri().get_local_name() for c in onto.get_classes()}
        assert "TypeA" in class_names
        assert "TypeB" in class_names

        # Check the individual has all three classes (Base + TypeA + TypeB)
        for ind in onto.get_individuals():
            classes = onto.get_classes_for_individual(ind)
            class_local_names = {c.get_iri().get_local_name() for c in classes}
            assert "Base" in class_local_names
            assert "TypeA" in class_local_names
            assert "TypeB" in class_local_names

    def test_no_additional_classes_is_backward_compatible(self, tmp_path):
        """Existing mappings without additional_classes still work normally."""
        csv_file = tmp_path / "data.csv"
        csv_file.write_text("id,name\n1,Test\n")

        enrich_csv = tmp_path / "enrich.csv"
        enrich_csv.write_text("id,extra\n1,bonus\n")

        yaml_file = tmp_path / "mapping.yaml"
        yaml_file.write_text(
            f'version: "1.0"\n'
            f'base_iri: "http://example.org/test#"\n'
            f'\n'
            f'sources:\n'
            f'  data:\n'
            f'    type: csv\n'
            f'    path: "{_p(csv_file)}"\n'
            f'    has_headers: true\n'
            f'  enrich:\n'
            f'    type: csv\n'
            f'    path: "{_p(enrich_csv)}"\n'
            f'    has_headers: true\n'
            f'\n'
            f'node_mappings:\n'
            f'  - name: "Create"\n'
            f'    source: data\n'
            f'    target_class: Entity\n'
            f'    mode: create\n'
            f'    iri_column: id\n'
            f'    properties:\n'
            f'      - {{ column: id, property: entityId }}\n'
            f'\n'
            f'  - name: "Enrich"\n'
            f'    source: enrich\n'
            f'    target_class: Entity\n'
            f'    mode: enrich\n'
            f'    match:\n'
            f'      source_column: id\n'
            f'      target_property: entityId\n'
            f'    properties:\n'
            f'      - {{ column: extra, property: extraProp }}\n'
        )

        onto = owl2.Ontology(owl2.IRI("http://example.org/test"))
        loader = owl2.DataLoader(onto)
        loader.load_mapping_spec(str(yaml_file))
        stats = loader.execute()

        assert stats.individuals_created == 1
        assert stats.individuals_enriched == 1
        assert stats.properties_added >= 2  # entityId + extraProp
