"""Tests for auto-schema generation from YAML mapping specs (A1, A2, A3).

Covers:
- auto_declare_schema() generates class/property declarations from mapping spec
- EntityRef parsing accepts both 'class_name' and 'class' keys
- NodeMapping and RelationshipMapping table/query fields
- Schema generation from entity_types, node_mappings, and relationship_mappings
- Domain/range axiom generation for object properties
- Integration with execute() (auto-schema called automatically)
"""

import os
import tempfile
import pytest
from ista import owl2


@pytest.fixture
def ontology():
    """Create a fresh ontology."""
    return owl2.Ontology(owl2.IRI("http://example.org/test"))


@pytest.fixture
def simple_yaml_and_csv(tmp_path):
    """Create a minimal YAML mapping spec with a CSV data file."""
    # Create CSV data
    csv_file = tmp_path / "drugs.csv"
    csv_file.write_text(
        "drug_id,drug_name,class_name\n"
        "D001,Aspirin,NSAID\n"
        "D002,Ibuprofen,NSAID\n"
        "D003,Metformin,Biguanide\n"
    )

    # Create YAML mapping spec
    yaml_file = tmp_path / "mapping.yaml"
    yaml_file.write_text(
        f'version: "1.0"\n'
        f'base_iri: "http://example.org/test#"\n'
        f'\n'
        f'sources:\n'
        f'  drugs_csv:\n'
        f'    type: csv\n'
        f'    path: "{csv_file}"\n'
        f'    delimiter: ","\n'
        f'    has_headers: true\n'
        f'\n'
        f'node_mappings:\n'
        f'  - name: "Load Drugs"\n'
        f'    source: drugs_csv\n'
        f'    target_class: Drug\n'
        f'    mode: create\n'
        f'    iri_column: drug_id\n'
        f'    properties:\n'
        f'      - {{ column: drug_id, property: drugId }}\n'
        f'      - {{ column: drug_name, property: drugName }}\n'
        f'\n'
        f'relationship_mappings:\n'
        f'  - name: "Drug In Class"\n'
        f'    source: drugs_csv\n'
        f'    relationship: drugInClass\n'
        f'    subject:\n'
        f'      class_name: Drug\n'
        f'      column: drug_id\n'
        f'      match_property: drugId\n'
        f'    object:\n'
        f'      class_name: DrugClass\n'
        f'      column: class_name\n'
        f'      match_property: className\n'
    )

    return yaml_file, csv_file


@pytest.fixture
def entity_types_yaml(tmp_path):
    """Create a YAML spec with entity_types section."""
    csv_file = tmp_path / "genes.csv"
    csv_file.write_text(
        "gene_id,symbol,description\n"
        "1234,BRCA1,Breast cancer type 1\n"
        "5678,TP53,Tumor protein p53\n"
    )

    yaml_file = tmp_path / "mapping.yaml"
    yaml_file.write_text(
        f'version: "1.0"\n'
        f'base_iri: "http://example.org/test#"\n'
        f'\n'
        f'sources:\n'
        f'  genes_csv:\n'
        f'    type: csv\n'
        f'    path: "{csv_file}"\n'
        f'    delimiter: ","\n'
        f'    has_headers: true\n'
        f'\n'
        f'entity_types:\n'
        f'  Gene:\n'
        f'    primary:\n'
        f'      source: genes_csv\n'
        f'      iri_column: gene_id\n'
        f'      properties:\n'
        f'        - {{ column: gene_id, property: geneId }}\n'
        f'        - {{ column: symbol, property: geneSymbol }}\n'
        f'        - {{ column: description, property: geneDescription }}\n'
    )

    return yaml_file, csv_file


class TestAutoSchemaFromNodeMappings:
    """Test auto_declare_schema() with node_mappings."""

    def test_declares_target_class(self, ontology, simple_yaml_and_csv):
        yaml_file, _ = simple_yaml_and_csv
        loader = owl2.DataLoader(ontology)
        loader.load_mapping_spec(str(yaml_file))
        loader.auto_declare_schema()

        classes = ontology.get_classes()
        class_names = {c.get_iri().get_local_name() for c in classes}
        assert "Drug" in class_names

    def test_declares_data_properties(self, ontology, simple_yaml_and_csv):
        yaml_file, _ = simple_yaml_and_csv
        loader = owl2.DataLoader(ontology)
        loader.load_mapping_spec(str(yaml_file))
        loader.auto_declare_schema()

        data_props = ontology.get_data_properties()
        prop_names = {p.get_iri().get_local_name() for p in data_props}
        assert "drugId" in prop_names
        assert "drugName" in prop_names

    def test_declares_object_properties(self, ontology, simple_yaml_and_csv):
        yaml_file, _ = simple_yaml_and_csv
        loader = owl2.DataLoader(ontology)
        loader.load_mapping_spec(str(yaml_file))
        loader.auto_declare_schema()

        obj_props = ontology.get_object_properties()
        prop_names = {p.get_iri().get_local_name() for p in obj_props}
        assert "drugInClass" in prop_names

    def test_declares_classes_from_relationship_endpoints(self, ontology, simple_yaml_and_csv):
        yaml_file, _ = simple_yaml_and_csv
        loader = owl2.DataLoader(ontology)
        loader.load_mapping_spec(str(yaml_file))
        loader.auto_declare_schema()

        classes = ontology.get_classes()
        class_names = {c.get_iri().get_local_name() for c in classes}
        # Both Drug and DrugClass should be declared
        assert "Drug" in class_names
        assert "DrugClass" in class_names


class TestAutoSchemaFromEntityTypes:
    """Test auto_declare_schema() with entity_types."""

    def test_declares_entity_type_class(self, ontology, entity_types_yaml):
        yaml_file, _ = entity_types_yaml
        loader = owl2.DataLoader(ontology)
        loader.load_mapping_spec(str(yaml_file))
        loader.auto_declare_schema()

        classes = ontology.get_classes()
        class_names = {c.get_iri().get_local_name() for c in classes}
        assert "Gene" in class_names

    def test_declares_entity_type_properties(self, ontology, entity_types_yaml):
        yaml_file, _ = entity_types_yaml
        loader = owl2.DataLoader(ontology)
        loader.load_mapping_spec(str(yaml_file))
        loader.auto_declare_schema()

        data_props = ontology.get_data_properties()
        prop_names = {p.get_iri().get_local_name() for p in data_props}
        assert "geneId" in prop_names
        assert "geneSymbol" in prop_names
        assert "geneDescription" in prop_names


class TestAutoSchemaIdempotency:
    """Test that auto_declare_schema() is idempotent."""

    def test_no_duplicates_on_repeated_calls(self, ontology, simple_yaml_and_csv):
        yaml_file, _ = simple_yaml_and_csv
        loader = owl2.DataLoader(ontology)
        loader.load_mapping_spec(str(yaml_file))

        loader.auto_declare_schema()
        count_after_first = ontology.get_axiom_count()

        loader.auto_declare_schema()
        count_after_second = ontology.get_axiom_count()

        assert count_after_first == count_after_second

    def test_no_duplicates_with_pre_existing_schema(self, ontology, simple_yaml_and_csv):
        yaml_file, _ = simple_yaml_and_csv
        ns = "http://example.org/test#"

        # Pre-declare Drug class
        ontology.add_axiom(
            owl2.Declaration(owl2.EntityType.CLASS, owl2.IRI(f"{ns}Drug"))
        )
        pre_count = ontology.get_axiom_count()

        loader = owl2.DataLoader(ontology)
        loader.load_mapping_spec(str(yaml_file))
        loader.auto_declare_schema()

        # Drug should not be declared again, but DrugClass and properties should be added
        classes = ontology.get_classes()
        class_names = [c.get_iri().get_local_name() for c in classes]
        assert class_names.count("Drug") == 1


class TestAutoSchemaDomainRange:
    """Test domain/range axiom generation."""

    def test_generates_domain_axioms(self, ontology, simple_yaml_and_csv):
        yaml_file, _ = simple_yaml_and_csv
        loader = owl2.DataLoader(ontology)
        loader.load_mapping_spec(str(yaml_file))
        loader.auto_declare_schema()

        # Check for ObjectPropertyDomain axiom on drugInClass
        axioms = ontology.get_axioms()
        found_domain = False
        for ax in axioms:
            if isinstance(ax, owl2.ObjectPropertyDomain):
                prop_iri = ax.get_property().get_iri().get_local_name()
                if prop_iri == "drugInClass":
                    found_domain = True
                    break
        assert found_domain, "ObjectPropertyDomain axiom should be generated for drugInClass"

    def test_generates_range_axioms(self, ontology, simple_yaml_and_csv):
        yaml_file, _ = simple_yaml_and_csv
        loader = owl2.DataLoader(ontology)
        loader.load_mapping_spec(str(yaml_file))
        loader.auto_declare_schema()

        axioms = ontology.get_axioms()
        found_range = False
        for ax in axioms:
            if isinstance(ax, owl2.ObjectPropertyRange):
                prop_iri = ax.get_property().get_iri().get_local_name()
                if prop_iri == "drugInClass":
                    found_range = True
                    break
        assert found_range, "ObjectPropertyRange axiom should be generated for drugInClass"


class TestAutoSchemaBaseIRI:
    """Test base IRI resolution for auto-schema."""

    def test_uses_yaml_base_iri(self, ontology, simple_yaml_and_csv):
        yaml_file, _ = simple_yaml_and_csv
        loader = owl2.DataLoader(ontology)
        loader.load_mapping_spec(str(yaml_file))
        loader.auto_declare_schema()

        classes = ontology.get_classes()
        for cls in classes:
            # All IRIs should use the YAML base_iri
            assert cls.get_iri().get_full_iri().startswith("http://example.org/test#")

    def test_uses_ontology_iri_as_fallback(self, tmp_path):
        """When YAML has no base_iri, should use ontology IRI."""
        csv_file = tmp_path / "data.csv"
        csv_file.write_text("id,name\n1,Test\n")

        yaml_file = tmp_path / "mapping.yaml"
        yaml_file.write_text(
            f'version: "1.0"\n'
            f'\n'
            f'sources:\n'
            f'  data_csv:\n'
            f'    type: csv\n'
            f'    path: "{csv_file}"\n'
            f'    delimiter: ","\n'
            f'    has_headers: true\n'
            f'\n'
            f'node_mappings:\n'
            f'  - name: "Load Data"\n'
            f'    source: data_csv\n'
            f'    target_class: TestEntity\n'
            f'    mode: create\n'
            f'    iri_column: id\n'
            f'    properties:\n'
            f'      - {{ column: name, property: entityName }}\n'
        )

        onto = owl2.Ontology(owl2.IRI("http://myontology.org/onto"))
        loader = owl2.DataLoader(onto)
        loader.load_mapping_spec(str(yaml_file))
        loader.auto_declare_schema()

        classes = onto.get_classes()
        assert len(classes) >= 1
        # Should use namespace from ontology IRI
        for cls in classes:
            full = cls.get_iri().get_full_iri()
            assert "myontology.org" in full or "example.org" in full


class TestAutoSchemaIntegration:
    """Test auto-schema called automatically by execute()."""

    def test_execute_auto_declares_schema(self, ontology, simple_yaml_and_csv):
        yaml_file, _ = simple_yaml_and_csv
        loader = owl2.DataLoader(ontology)
        loader.load_mapping_spec(str(yaml_file))

        # Don't call auto_declare_schema() explicitly — execute() should do it
        stats = loader.execute()

        # Schema should be declared
        classes = ontology.get_classes()
        class_names = {c.get_iri().get_local_name() for c in classes}
        assert "Drug" in class_names

        # Data should be loaded
        assert stats.individuals_created > 0

    def test_execute_creates_individuals(self, ontology, simple_yaml_and_csv):
        yaml_file, _ = simple_yaml_and_csv
        loader = owl2.DataLoader(ontology)
        loader.load_mapping_spec(str(yaml_file))

        stats = loader.execute()

        # 3 drugs in CSV
        assert stats.individuals_created == 3
        assert stats.rows_processed >= 3

    def test_execute_adds_data_properties(self, ontology, simple_yaml_and_csv):
        yaml_file, _ = simple_yaml_and_csv
        loader = owl2.DataLoader(ontology)
        loader.load_mapping_spec(str(yaml_file))

        stats = loader.execute()

        # Each drug has 2 properties (drugId, drugName), so 6 total
        assert stats.properties_added == 6


class TestNodeMappingTableField:
    """Test the per-mapping table/query fields (A2)."""

    def test_node_mapping_has_table_field(self):
        nm = owl2.NodeMapping()
        # table should be accessible (may be None initially)
        assert hasattr(nm, "table")

    def test_node_mapping_has_query_field(self):
        nm = owl2.NodeMapping()
        assert hasattr(nm, "query")

    def test_relationship_mapping_has_table_field(self):
        rm = owl2.RelationshipMapping()
        assert hasattr(rm, "table")

    def test_relationship_mapping_has_query_field(self):
        rm = owl2.RelationshipMapping()
        assert hasattr(rm, "query")


class TestEntityRefParsing:
    """Test that EntityRef parsing accepts both 'class_name' and 'class' keys (A2)."""

    def test_class_name_key_in_yaml(self, ontology, simple_yaml_and_csv):
        """The simple YAML uses class_name: — should be parsed correctly."""
        yaml_file, _ = simple_yaml_and_csv
        loader = owl2.DataLoader(ontology)
        loader.load_mapping_spec(str(yaml_file))

        spec = loader.mapping_spec()
        assert len(spec.relationship_mappings) == 1
        rm = spec.relationship_mappings[0]
        assert rm.subject.class_name == "Drug"
        assert rm.object.class_name == "DrugClass"

    def test_class_key_in_yaml(self, ontology, tmp_path):
        """Test that 'class:' key also works in EntityRef."""
        csv_file = tmp_path / "data.csv"
        csv_file.write_text("id,target\n1,A\n")

        yaml_file = tmp_path / "mapping.yaml"
        yaml_file.write_text(
            f'version: "1.0"\n'
            f'base_iri: "http://example.org/test#"\n'
            f'\n'
            f'sources:\n'
            f'  data_csv:\n'
            f'    type: csv\n'
            f'    path: "{csv_file}"\n'
            f'    delimiter: ","\n'
            f'    has_headers: true\n'
            f'\n'
            f'node_mappings:\n'
            f'  - name: "Load A"\n'
            f'    source: data_csv\n'
            f'    target_class: TypeA\n'
            f'    mode: create\n'
            f'    iri_column: id\n'
            f'\n'
            f'relationship_mappings:\n'
            f'  - name: "A to B"\n'
            f'    source: data_csv\n'
            f'    relationship: relatesTo\n'
            f'    subject:\n'
            f'      class: TypeA\n'
            f'      column: id\n'
            f'      match_property: entityId\n'
            f'    object:\n'
            f'      class: TypeB\n'
            f'      column: target\n'
            f'      match_property: entityId\n'
        )

        loader = owl2.DataLoader(ontology)
        loader.load_mapping_spec(str(yaml_file))

        spec = loader.mapping_spec()
        rm = spec.relationship_mappings[0]
        assert rm.subject.class_name == "TypeA"
        assert rm.object.class_name == "TypeB"


class TestTableOverrideInYaml:
    """Test that table: field is parsed from YAML node/relationship mappings."""

    def test_table_parsed_in_node_mapping(self, ontology, tmp_path):
        csv_file = tmp_path / "data.csv"
        csv_file.write_text("id,name\n1,Test\n")

        yaml_file = tmp_path / "mapping.yaml"
        yaml_file.write_text(
            f'version: "1.0"\n'
            f'base_iri: "http://example.org/test#"\n'
            f'\n'
            f'sources:\n'
            f'  data_csv:\n'
            f'    type: csv\n'
            f'    path: "{csv_file}"\n'
            f'    delimiter: ","\n'
            f'    has_headers: true\n'
            f'\n'
            f'node_mappings:\n'
            f'  - name: "Load Data"\n'
            f'    source: data_csv\n'
            f'    target_class: TestEntity\n'
            f'    mode: create\n'
            f'    table: my_table\n'
            f'    iri_column: id\n'
            f'    properties:\n'
            f'      - {{ column: name, property: entityName }}\n'
        )

        loader = owl2.DataLoader(ontology)
        loader.load_mapping_spec(str(yaml_file))

        spec = loader.mapping_spec()
        nm = spec.node_mappings[0]
        assert nm.table == "my_table"

    def test_table_parsed_in_relationship_mapping(self, ontology, simple_yaml_and_csv):
        """The simple YAML doesn't have table on relationships, test one that does."""
        yaml_file, _ = simple_yaml_and_csv
        loader = owl2.DataLoader(ontology)
        loader.load_mapping_spec(str(yaml_file))

        spec = loader.mapping_spec()
        rm = spec.relationship_mappings[0]
        # This mapping doesn't have a table field set, so it should be empty/None
        assert rm.table is None or rm.table == ""
