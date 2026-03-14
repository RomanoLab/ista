"""Tests for multi_value_delimiter feature in relationship mappings.

This feature allows a single column value to contain multiple
delimiter-separated identifiers (e.g. ``"12; 45; 78"``), automatically
expanding each row into one relationship per value.
"""

from ista import owl2


def _p(path):
    """Convert a path to forward-slash string for use in YAML on Windows."""
    return str(path).replace("\\", "/")


class TestMultiValueDelimiter:
    """Test that relationship mappings expand multi-value delimited fields."""

    def test_semicolon_delimiter_expands_relationships(self, tmp_path):
        """Semicolon-delimited object column creates multiple relationships."""
        events_csv = tmp_path / "events.csv"
        events_csv.write_text(
            "event_id,event_name,aop_ids\n"
            "KE1,Event Alpha,AOP1; AOP2; AOP3\n"
            "KE2,Event Beta,AOP2\n"
            "KE3,Event Gamma,AOP1; AOP3\n"
        )

        aops_csv = tmp_path / "aops.csv"
        aops_csv.write_text(
            "aop_id,aop_name\n"
            "AOP1,Pathway One\n"
            "AOP2,Pathway Two\n"
            "AOP3,Pathway Three\n"
        )

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
            f'  aops:\n'
            f'    type: csv\n'
            f'    path: "{_p(aops_csv)}"\n'
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
            f'      - {{ column: event_name, property: eventName }}\n'
            f'\n'
            f'  - name: "AOPs"\n'
            f'    source: aops\n'
            f'    target_class: AOP\n'
            f'    mode: create\n'
            f'    iri_column: aop_id\n'
            f'    properties:\n'
            f'      - {{ column: aop_id, property: aopId }}\n'
            f'      - {{ column: aop_name, property: aopName }}\n'
            f'\n'
            f'relationship_mappings:\n'
            f'  - name: "KE In AOP"\n'
            f'    source: events\n'
            f'    relationship: keIncludedInAOP\n'
            f'    subject:\n'
            f'      class: KeyEvent\n'
            f'      column: event_id\n'
            f'      match_property: eventId\n'
            f'    object:\n'
            f'      class: AOP\n'
            f'      column: aop_ids\n'
            f'      match_property: aopId\n'
            f'      multi_value_delimiter: "; "\n'
        )

        onto = owl2.Ontology(owl2.IRI("http://example.org/aop"))
        loader = owl2.DataLoader(onto)
        loader.load_mapping_spec(str(yaml_file))
        stats = loader.execute()

        assert stats.individuals_created == 6  # 3 events + 3 AOPs
        # KE1→AOP1,AOP2,AOP3 (3) + KE2→AOP2 (1) + KE3→AOP1,AOP3 (2) = 6
        assert stats.relationships_created == 6

    def test_single_value_no_expansion(self, tmp_path):
        """A row with only one value (no delimiter) creates one relationship."""
        items_csv = tmp_path / "items.csv"
        items_csv.write_text("id,name,group\nI1,Alpha,G1\n")

        groups_csv = tmp_path / "groups.csv"
        groups_csv.write_text("group_id,group_name\nG1,GroupOne\n")

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
            f'  groups:\n'
            f'    type: csv\n'
            f'    path: "{_p(groups_csv)}"\n'
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
            f'  - name: "Groups"\n'
            f'    source: groups\n'
            f'    target_class: Group\n'
            f'    mode: create\n'
            f'    iri_column: group_id\n'
            f'    properties:\n'
            f'      - {{ column: group_id, property: groupId }}\n'
            f'\n'
            f'relationship_mappings:\n'
            f'  - name: "Item In Group"\n'
            f'    source: items\n'
            f'    relationship: itemInGroup\n'
            f'    subject:\n'
            f'      class: Item\n'
            f'      column: id\n'
            f'      match_property: itemId\n'
            f'    object:\n'
            f'      class: Group\n'
            f'      column: group\n'
            f'      match_property: groupId\n'
            f'      multi_value_delimiter: "; "\n'
        )

        onto = owl2.Ontology(owl2.IRI("http://example.org/test"))
        loader = owl2.DataLoader(onto)
        loader.load_mapping_spec(str(yaml_file))
        stats = loader.execute()

        assert stats.relationships_created == 1

    def test_subject_multi_value(self, tmp_path):
        """Multi-value delimiter works on the subject side too."""
        links_csv = tmp_path / "links.csv"
        links_csv.write_text("sources,target\nA|B,T1\nC,T2\n")

        nodes_csv = tmp_path / "nodes.csv"
        nodes_csv.write_text("id\nA\nB\nC\nT1\nT2\n")

        yaml_file = tmp_path / "mapping.yaml"
        yaml_file.write_text(
            f'version: "1.0"\n'
            f'base_iri: "http://example.org/test#"\n'
            f'\n'
            f'sources:\n'
            f'  nodes:\n'
            f'    type: csv\n'
            f'    path: "{_p(nodes_csv)}"\n'
            f'    has_headers: true\n'
            f'  links:\n'
            f'    type: csv\n'
            f'    path: "{_p(links_csv)}"\n'
            f'    has_headers: true\n'
            f'\n'
            f'node_mappings:\n'
            f'  - name: "Nodes"\n'
            f'    source: nodes\n'
            f'    target_class: Node\n'
            f'    mode: create\n'
            f'    iri_column: id\n'
            f'    properties:\n'
            f'      - {{ column: id, property: nodeId }}\n'
            f'\n'
            f'relationship_mappings:\n'
            f'  - name: "Links"\n'
            f'    source: links\n'
            f'    relationship: linksTo\n'
            f'    subject:\n'
            f'      class: Node\n'
            f'      column: sources\n'
            f'      match_property: nodeId\n'
            f'      multi_value_delimiter: "|"\n'
            f'    object:\n'
            f'      class: Node\n'
            f'      column: target\n'
            f'      match_property: nodeId\n'
        )

        onto = owl2.Ontology(owl2.IRI("http://example.org/test"))
        loader = owl2.DataLoader(onto)
        loader.load_mapping_spec(str(yaml_file))
        stats = loader.execute()

        # A→T1, B→T1, C→T2 = 3 relationships
        assert stats.relationships_created == 3

    def test_empty_tokens_skipped(self, tmp_path):
        """Empty tokens from splitting are skipped gracefully."""
        items_csv = tmp_path / "items.csv"
        items_csv.write_text("id,groups\nI1,G1; ; G2\n")

        groups_csv = tmp_path / "groups.csv"
        groups_csv.write_text("group_id\nG1\nG2\n")

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
            f'  groups:\n'
            f'    type: csv\n'
            f'    path: "{_p(groups_csv)}"\n'
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
            f'  - name: "Groups"\n'
            f'    source: groups\n'
            f'    target_class: Group\n'
            f'    mode: create\n'
            f'    iri_column: group_id\n'
            f'    properties:\n'
            f'      - {{ column: group_id, property: groupId }}\n'
            f'\n'
            f'relationship_mappings:\n'
            f'  - name: "Item In Group"\n'
            f'    source: items\n'
            f'    relationship: itemInGroup\n'
            f'    subject:\n'
            f'      class: Item\n'
            f'      column: id\n'
            f'      match_property: itemId\n'
            f'    object:\n'
            f'      class: Group\n'
            f'      column: groups\n'
            f'      match_property: groupId\n'
            f'      multi_value_delimiter: "; "\n'
        )

        onto = owl2.Ontology(owl2.IRI("http://example.org/test"))
        loader = owl2.DataLoader(onto)
        loader.load_mapping_spec(str(yaml_file))
        stats = loader.execute()

        # "G1; ; G2" → ["G1", "G2"] (empty token skipped), so 2 relationships
        assert stats.relationships_created == 2

    def test_no_delimiter_backward_compatible(self, tmp_path):
        """Relationships without multi_value_delimiter still work normally."""
        a_csv = tmp_path / "a.csv"
        a_csv.write_text("id\nA1\nA2\n")

        b_csv = tmp_path / "b.csv"
        b_csv.write_text("id\nB1\n")

        links_csv = tmp_path / "links.csv"
        links_csv.write_text("a_id,b_id\nA1,B1\nA2,B1\n")

        yaml_file = tmp_path / "mapping.yaml"
        yaml_file.write_text(
            f'version: "1.0"\n'
            f'base_iri: "http://example.org/test#"\n'
            f'\n'
            f'sources:\n'
            f'  a:\n'
            f'    type: csv\n'
            f'    path: "{_p(a_csv)}"\n'
            f'    has_headers: true\n'
            f'  b:\n'
            f'    type: csv\n'
            f'    path: "{_p(b_csv)}"\n'
            f'    has_headers: true\n'
            f'  links:\n'
            f'    type: csv\n'
            f'    path: "{_p(links_csv)}"\n'
            f'    has_headers: true\n'
            f'\n'
            f'node_mappings:\n'
            f'  - name: "A"\n'
            f'    source: a\n'
            f'    target_class: TypeA\n'
            f'    mode: create\n'
            f'    iri_column: id\n'
            f'    properties:\n'
            f'      - {{ column: id, property: aId }}\n'
            f'  - name: "B"\n'
            f'    source: b\n'
            f'    target_class: TypeB\n'
            f'    mode: create\n'
            f'    iri_column: id\n'
            f'    properties:\n'
            f'      - {{ column: id, property: bId }}\n'
            f'\n'
            f'relationship_mappings:\n'
            f'  - name: "A links B"\n'
            f'    source: links\n'
            f'    relationship: aLinksB\n'
            f'    subject:\n'
            f'      class: TypeA\n'
            f'      column: a_id\n'
            f'      match_property: aId\n'
            f'    object:\n'
            f'      class: TypeB\n'
            f'      column: b_id\n'
            f'      match_property: bId\n'
        )

        onto = owl2.Ontology(owl2.IRI("http://example.org/test"))
        loader = owl2.DataLoader(onto)
        loader.load_mapping_spec(str(yaml_file))
        stats = loader.execute()

        assert stats.relationships_created == 2
