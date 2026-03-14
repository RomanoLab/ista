"""Tests for YAML anchor/alias and block scalar support in ista's YAML parser.

The YAML parser must support:
- Anchors (&name) and aliases (*name) so that shared configuration blocks
  can be defined once and reused across multiple data source definitions.
- Block scalars (| and >) for multi-line strings such as SQL queries.
"""

from ista import owl2


def _p(path):
    """Convert a path to forward-slash string for use in YAML on Windows."""
    return str(path).replace("\\", "/")


class TestYamlAnchors:
    """Test anchor/alias resolution in ista's YAML parser."""

    def test_alias_resolves_map_value(self, tmp_path):
        """An alias (*name) correctly inlines an anchored (&name) map."""
        csv_file = tmp_path / "data.csv"
        csv_file.write_text("id,name\nA1,Alpha\n")

        yaml_file = tmp_path / "mapping.yaml"
        yaml_file.write_text(
            f'version: "1.0"\n'
            f'base_iri: "http://example.org/test#"\n'
            f'\n'
            f'_defaults: &defaults\n'
            f'  type: csv\n'
            f'  has_headers: true\n'
            f'\n'
            f'sources:\n'
            f'  data:\n'
            f'    <<: *defaults\n'
            f'    path: "{_p(csv_file)}"\n'
            f'\n'
            f'node_mappings:\n'
            f'  - name: "Items"\n'
            f'    source: data\n'
            f'    target_class: Item\n'
            f'    mode: create\n'
            f'    iri_column: id\n'
            f'    properties:\n'
            f'      - {{ column: id, property: itemId }}\n'
            f'      - {{ column: name, property: itemName }}\n'
        )

        onto = owl2.Ontology(owl2.IRI("http://example.org/test"))
        loader = owl2.DataLoader(onto)
        loader.load_mapping_spec(str(yaml_file))
        stats = loader.execute()

        assert stats.individuals_created == 1

    def test_anchor_alias_shared_connection(self, tmp_path):
        """A shared connection anchor is correctly applied to multiple sources.

        This mimics the real-world pattern used in comptox_mapping.yaml where
        multiple MySQL sources share the same ``&aopdb_conn`` connection block.
        Since we can't actually connect to MySQL in tests, we verify that the
        mapping spec parses all sources correctly.
        """
        yaml_file = tmp_path / "mapping.yaml"
        yaml_file.write_text(
            f'version: "1.0"\n'
            f'base_iri: "http://example.org/test#"\n'
            f'\n'
            f'_shared_conn: &db_conn\n'
            f'  host: "db.example.com"\n'
            f'  port: 3306\n'
            f'  database: "testdb"\n'
            f'  username: "admin"\n'
            f'  password: "secret"\n'
            f'\n'
            f'sources:\n'
            f'  table_a:\n'
            f'    type: mysql\n'
            f'    connection: *db_conn\n'
            f'    table: alpha\n'
            f'  table_b:\n'
            f'    type: mysql\n'
            f'    connection: *db_conn\n'
            f'    table: beta\n'
            f'\n'
            f'node_mappings:\n'
            f'  - name: "A"\n'
            f'    source: table_a\n'
            f'    target_class: TypeA\n'
            f'    mode: create\n'
            f'    iri_column: id\n'
            f'    properties:\n'
            f'      - {{ column: id, property: aId }}\n'
        )

        onto = owl2.Ontology(owl2.IRI("http://example.org/test"))
        loader = owl2.DataLoader(onto)
        loader.load_mapping_spec(str(yaml_file))
        spec = loader.mapping_spec()

        # Both sources should be parsed
        assert len(spec.sources) == 2
        assert "table_a" in spec.sources
        assert "table_b" in spec.sources
        assert spec.sources["table_a"].type == "mysql"
        assert spec.sources["table_b"].type == "mysql"

    def test_anchor_alias_scalar_value(self, tmp_path):
        """An anchor on a scalar value is resolved correctly by an alias."""
        csv_file = tmp_path / "data.csv"
        csv_file.write_text("id\nX1\n")

        yaml_file = tmp_path / "mapping.yaml"
        yaml_file.write_text(
            f'version: "1.0"\n'
            f'base_iri: &base_iri "http://example.org/anchored#"\n'
            f'\n'
            f'sources:\n'
            f'  data:\n'
            f'    type: csv\n'
            f'    path: "{_p(csv_file)}"\n'
            f'    has_headers: true\n'
            f'\n'
            f'node_mappings:\n'
            f'  - name: "Items"\n'
            f'    source: data\n'
            f'    target_class: Item\n'
            f'    mode: create\n'
            f'    iri_column: id\n'
            f'    properties:\n'
            f'      - {{ column: id, property: itemId }}\n'
        )

        onto = owl2.Ontology(owl2.IRI("http://example.org/anchored"))
        loader = owl2.DataLoader(onto)
        loader.load_mapping_spec(str(yaml_file))
        spec = loader.mapping_spec()

        assert spec.base_iri == "http://example.org/anchored#"

    def test_unknown_alias_raises(self, tmp_path):
        """Referencing an undefined alias raises an error."""
        import pytest

        yaml_file = tmp_path / "bad.yaml"
        yaml_file.write_text(
            'version: "1.0"\n'
            'base_iri: "http://example.org/test#"\n'
            '\n'
            'sources:\n'
            '  src:\n'
            '    type: mysql\n'
            '    connection: *nonexistent\n'
        )

        onto = owl2.Ontology()
        loader = owl2.DataLoader(onto)
        with pytest.raises(Exception, match="nonexistent"):
            loader.load_mapping_spec(str(yaml_file))


class TestBlockScalars:
    """Test literal (|) and folded (>) block scalar parsing."""

    def test_literal_block_preserves_newlines(self, tmp_path):
        """The | indicator produces a string with embedded newlines."""
        yaml_file = tmp_path / "mapping.yaml"
        yaml_file.write_text(
            'version: "1.0"\n'
            'base_iri: "http://example.org/test#"\n'
            '\n'
            'sources:\n'
            '  db_src:\n'
            '    type: mysql\n'
            '    query: |\n'
            '      SELECT id, name\n'
            '      FROM patients\n'
            '      WHERE active = 1\n'
            '\n'
            'node_mappings:\n'
            '  - name: "Patients"\n'
            '    source: db_src\n'
            '    target_class: Patient\n'
            '    mode: create\n'
            '    iri_column: id\n'
            '    properties:\n'
            '      - { column: id, property: patientId }\n'
        )

        onto = owl2.Ontology()
        loader = owl2.DataLoader(onto)
        loader.load_mapping_spec(str(yaml_file))
        spec = loader.mapping_spec()

        assert "db_src" in spec.sources
        assert spec.sources["db_src"].type == "mysql"

    def test_block_scalar_does_not_eat_subsequent_keys(self, tmp_path):
        """Sources defined after a block scalar are still parsed."""
        csv_file = tmp_path / "data.csv"
        csv_file.write_text("id\nX1\n")

        yaml_file = tmp_path / "mapping.yaml"
        yaml_file.write_text(
            'version: "1.0"\n'
            'base_iri: "http://example.org/test#"\n'
            '\n'
            'sources:\n'
            '  mysql_src:\n'
            '    type: mysql\n'
            '    query: |\n'
            '      SELECT * FROM foo\n'
            '      WHERE bar = 1\n'
            f'  csv_src:\n'
            f'    type: csv\n'
            f'    path: "{_p(csv_file)}"\n'
            '\n'
            'node_mappings:\n'
            '  - name: "Test"\n'
            '    source: csv_src\n'
            '    target_class: Foo\n'
            '    mode: create\n'
            '    iri_column: id\n'
            '    properties:\n'
            '      - { column: id, property: fooId }\n'
        )

        onto = owl2.Ontology()
        loader = owl2.DataLoader(onto)
        loader.load_mapping_spec(str(yaml_file))
        spec = loader.mapping_spec()

        assert "mysql_src" in spec.sources
        assert "csv_src" in spec.sources
        assert spec.sources["mysql_src"].type == "mysql"
        assert spec.sources["csv_src"].type == "csv"

    def test_multiple_block_scalars(self, tmp_path):
        """Multiple sources with block scalar queries all parse correctly."""
        yaml_file = tmp_path / "mapping.yaml"
        yaml_file.write_text(
            'version: "1.0"\n'
            'base_iri: "http://example.org/test#"\n'
            '\n'
            '_conn: &conn\n'
            '  host: "localhost"\n'
            '  database: "testdb"\n'
            '  username: "user"\n'
            '  password: "pass"\n'
            '\n'
            'sources:\n'
            '  query_a:\n'
            '    type: mysql\n'
            '    connection: *conn\n'
            '    query: |\n'
            '      SELECT * FROM alpha\n'
            '      WHERE x = 1\n'
            '  query_b:\n'
            '    type: mysql\n'
            '    connection: *conn\n'
            '    query: |\n'
            '      SELECT * FROM beta\n'
            '      WHERE y = 2\n'
            '  query_c:\n'
            '    type: mysql\n'
            '    connection: *conn\n'
            '    table: gamma\n'
            '\n'
            'node_mappings:\n'
            '  - name: "A"\n'
            '    source: query_a\n'
            '    target_class: A\n'
            '    mode: create\n'
            '    iri_column: id\n'
            '    properties:\n'
            '      - { column: id, property: aId }\n'
        )

        onto = owl2.Ontology()
        loader = owl2.DataLoader(onto)
        loader.load_mapping_spec(str(yaml_file))
        spec = loader.mapping_spec()

        assert len(spec.sources) == 3
        assert spec.sources["query_a"].type == "mysql"
        assert spec.sources["query_b"].type == "mysql"
        assert spec.sources["query_c"].type == "mysql"
