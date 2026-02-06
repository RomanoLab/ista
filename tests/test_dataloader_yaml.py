"""Integration tests for the YAML-driven DataLoader pipeline.

Tests the end-to-end flow: YAML spec + data files → populated ontology.
Covers:
- Full execute() pipeline (auto-schema + batch mode + caching)
- Node creation from CSV/TSV
- Data property assignment
- Relationship creation between entities
- Entity enrichment (ENRICH mode)
- Serialization of the populated ontology
"""

import pytest
from ista import owl2


@pytest.fixture
def drugs_csv(tmp_path):
    """Create a drugs CSV file."""
    f = tmp_path / "drugs.csv"
    f.write_text(
        "drug_id,drug_name,cas_number,drug_class\n"
        "DB001,Aspirin,50-78-2,NSAID\n"
        "DB002,Ibuprofen,15687-27-1,NSAID\n"
        "DB003,Metformin,657-24-9,Biguanide\n"
        "DB004,Lisinopril,83915-83-7,ACEInhibitor\n"
    )
    return f


@pytest.fixture
def genes_tsv(tmp_path):
    """Create a genes TSV file."""
    f = tmp_path / "genes.tsv"
    f.write_text(
        "gene_id\tgene_symbol\tgene_name\n"
        "672\tBRCA1\tBreast Cancer 1\n"
        "7157\tTP53\tTumor Protein P53\n"
        "1956\tEGFR\tEpidermal Growth Factor Receptor\n"
    )
    return f


@pytest.fixture
def drug_gene_csv(tmp_path):
    """Create a drug-gene relationship CSV."""
    f = tmp_path / "drug_gene.csv"
    f.write_text(
        "drug_id,gene_id\n"
        "DB001,672\n"
        "DB002,7157\n"
        "DB003,1956\n"
    )
    return f


@pytest.fixture
def drug_toxicity_csv(tmp_path):
    """Create drug toxicity enrichment data."""
    f = tmp_path / "toxicity.csv"
    f.write_text(
        "cas_number,ld50_value,ld50_units\n"
        "50-78-2,200,mg/kg\n"
        "15687-27-1,636,mg/kg\n"
    )
    return f


@pytest.fixture
def full_yaml(tmp_path, drugs_csv, genes_tsv, drug_gene_csv, drug_toxicity_csv):
    """Create a YAML mapping spec with multiple sources and mappings."""
    yaml_file = tmp_path / "mapping.yaml"
    yaml_file.write_text(
        f'version: "1.0"\n'
        f'base_iri: "http://example.org/pharma#"\n'
        f'\n'
        f'sources:\n'
        f'  drugs_csv:\n'
        f'    type: csv\n'
        f'    path: "{drugs_csv}"\n'
        f'    delimiter: ","\n'
        f'    has_headers: true\n'
        f'\n'
        f'  genes_tsv:\n'
        f'    type: tsv\n'
        f'    path: "{genes_tsv}"\n'
        f'    has_headers: true\n'
        f'\n'
        f'  drug_gene_csv:\n'
        f'    type: csv\n'
        f'    path: "{drug_gene_csv}"\n'
        f'    delimiter: ","\n'
        f'    has_headers: true\n'
        f'\n'
        f'  toxicity_csv:\n'
        f'    type: csv\n'
        f'    path: "{drug_toxicity_csv}"\n'
        f'    delimiter: ","\n'
        f'    has_headers: true\n'
        f'\n'
        f'entity_types:\n'
        f'  Drug:\n'
        f'    primary:\n'
        f'      source: drugs_csv\n'
        f'      iri_column: drug_id\n'
        f'      properties:\n'
        f'        - {{ column: drug_id, property: drugId }}\n'
        f'        - {{ column: drug_name, property: drugName }}\n'
        f'        - {{ column: cas_number, property: casNumber }}\n'
        f'    enrichments:\n'
        f'      - name: "Toxicity Enrichment"\n'
        f'        source: toxicity_csv\n'
        f'        match:\n'
        f'          source_column: cas_number\n'
        f'          target_property: casNumber\n'
        f'        properties:\n'
        f'          - {{ column: ld50_value, property: ld50Value }}\n'
        f'          - {{ column: ld50_units, property: ld50Units }}\n'
        f'\n'
        f'node_mappings:\n'
        f'  - name: "Load Genes"\n'
        f'    source: genes_tsv\n'
        f'    target_class: Gene\n'
        f'    mode: create\n'
        f'    iri_column: gene_id\n'
        f'    properties:\n'
        f'      - {{ column: gene_id, property: geneId }}\n'
        f'      - {{ column: gene_symbol, property: geneSymbol }}\n'
        f'      - {{ column: gene_name, property: geneName }}\n'
        f'\n'
        f'  - name: "Load Drug Classes"\n'
        f'    source: drugs_csv\n'
        f'    target_class: DrugClass\n'
        f'    mode: create\n'
        f'    iri_column: drug_class\n'
        f'    properties:\n'
        f'      - {{ column: drug_class, property: className }}\n'
        f'\n'
        f'relationship_mappings:\n'
        f'  - name: "Drug Targets Gene"\n'
        f'    source: drug_gene_csv\n'
        f'    relationship: drugTargetsGene\n'
        f'    subject:\n'
        f'      class_name: Drug\n'
        f'      column: drug_id\n'
        f'      match_property: drugId\n'
        f'    object:\n'
        f'      class_name: Gene\n'
        f'      column: gene_id\n'
        f'      match_property: geneId\n'
        f'\n'
        f'  - name: "Drug In Class"\n'
        f'    source: drugs_csv\n'
        f'    relationship: drugInClass\n'
        f'    subject:\n'
        f'      class_name: Drug\n'
        f'      column: drug_id\n'
        f'      match_property: drugId\n'
        f'    object:\n'
        f'      class_name: DrugClass\n'
        f'      column: drug_class\n'
        f'      match_property: className\n'
    )
    return yaml_file


class TestFullPipeline:
    """Test the complete YAML-driven pipeline."""

    def test_execute_returns_stats(self, full_yaml):
        onto = owl2.Ontology(owl2.IRI("http://example.org/pharma"))
        loader = owl2.DataLoader(onto)
        loader.load_mapping_spec(str(full_yaml))
        stats = loader.execute()

        assert stats.rows_processed > 0
        assert stats.individuals_created > 0

    def test_schema_declared(self, full_yaml):
        onto = owl2.Ontology(owl2.IRI("http://example.org/pharma"))
        loader = owl2.DataLoader(onto)
        loader.load_mapping_spec(str(full_yaml))
        loader.execute()

        class_names = {c.get_iri().get_local_name() for c in onto.get_classes()}
        assert "Drug" in class_names
        assert "Gene" in class_names
        assert "DrugClass" in class_names

    def test_data_properties_declared(self, full_yaml):
        onto = owl2.Ontology(owl2.IRI("http://example.org/pharma"))
        loader = owl2.DataLoader(onto)
        loader.load_mapping_spec(str(full_yaml))
        loader.execute()

        prop_names = {p.get_iri().get_local_name() for p in onto.get_data_properties()}
        assert "drugId" in prop_names
        assert "drugName" in prop_names
        assert "geneSymbol" in prop_names

    def test_object_properties_declared(self, full_yaml):
        onto = owl2.Ontology(owl2.IRI("http://example.org/pharma"))
        loader = owl2.DataLoader(onto)
        loader.load_mapping_spec(str(full_yaml))
        loader.execute()

        prop_names = {p.get_iri().get_local_name() for p in onto.get_object_properties()}
        assert "drugTargetsGene" in prop_names
        assert "drugInClass" in prop_names


class TestNodeCreation:
    """Test individual creation from data sources."""

    def test_drugs_created(self, full_yaml):
        onto = owl2.Ontology(owl2.IRI("http://example.org/pharma"))
        loader = owl2.DataLoader(onto)
        loader.load_mapping_spec(str(full_yaml))
        stats = loader.execute()

        # 4 drugs + 3 genes + 4 drug classes (may have duplicates collapsed)
        assert stats.individuals_created >= 7

    def test_individual_has_class_assertion(self, full_yaml):
        onto = owl2.Ontology(owl2.IRI("http://example.org/pharma"))
        loader = owl2.DataLoader(onto)
        loader.load_mapping_spec(str(full_yaml))
        loader.execute()

        individuals = onto.get_individuals()
        assert len(individuals) > 0

        # At least one individual should have class assertions
        found_class_assertion = False
        for ind in individuals:
            classes = onto.get_classes_for_individual(ind)
            if len(classes) > 0:
                found_class_assertion = True
                break
        assert found_class_assertion

    def test_individual_has_data_properties(self, full_yaml):
        onto = owl2.Ontology(owl2.IRI("http://example.org/pharma"))
        loader = owl2.DataLoader(onto)
        loader.load_mapping_spec(str(full_yaml))
        loader.execute()

        # Find an individual and check its properties
        individuals = onto.get_individuals()
        found_data_prop = False
        for ind in individuals:
            assertions = onto.get_data_property_assertions_for_individual(ind)
            if len(assertions) > 0:
                found_data_prop = True
                break
        assert found_data_prop


class TestRelationshipCreation:
    """Test relationship creation between entities."""

    def test_relationships_created(self, full_yaml):
        onto = owl2.Ontology(owl2.IRI("http://example.org/pharma"))
        loader = owl2.DataLoader(onto)
        loader.load_mapping_spec(str(full_yaml))
        stats = loader.execute()

        assert stats.relationships_created > 0

    def test_object_property_assertions_exist(self, full_yaml):
        onto = owl2.Ontology(owl2.IRI("http://example.org/pharma"))
        loader = owl2.DataLoader(onto)
        loader.load_mapping_spec(str(full_yaml))
        loader.execute()

        # Find the drugTargetsGene object property
        obj_props = onto.get_object_properties()
        targets_prop = None
        for p in obj_props:
            if p.get_iri().get_local_name() == "drugTargetsGene":
                targets_prop = p
                break

        assert targets_prop is not None

        # Check assertions for this property
        assertions = onto.get_object_property_assertions_for_property(targets_prop)
        assert len(assertions) > 0


class TestEnrichment:
    """Test data enrichment (ENRICH mode) via entity_types enrichments."""

    def test_enriched_properties_added(self, full_yaml):
        onto = owl2.Ontology(owl2.IRI("http://example.org/pharma"))
        loader = owl2.DataLoader(onto)
        loader.load_mapping_spec(str(full_yaml))
        stats = loader.execute()

        # Enrichments should have added ld50Value/ld50Units to some drugs
        assert stats.individuals_enriched > 0

    def test_enriched_data_available(self, full_yaml):
        onto = owl2.Ontology(owl2.IRI("http://example.org/pharma"))
        loader = owl2.DataLoader(onto)
        loader.load_mapping_spec(str(full_yaml))
        loader.execute()

        # Check that ld50Value property exists and has data
        prop_names = {p.get_iri().get_local_name() for p in onto.get_data_properties()}
        assert "ld50Value" in prop_names


class TestSerialization:
    """Test serialization of populated ontology."""

    def test_serialize_to_rdfxml(self, full_yaml, tmp_path):
        onto = owl2.Ontology(owl2.IRI("http://example.org/pharma"))
        loader = owl2.DataLoader(onto)
        loader.load_mapping_spec(str(full_yaml))
        loader.execute()

        output_file = tmp_path / "output.owl"
        owl2.RDFXMLSerializer.serialize_to_file(onto, str(output_file))

        assert output_file.exists()
        content = output_file.read_text()
        assert "http://example.org/pharma" in content
        assert len(content) > 100  # Not just an empty skeleton

    def test_serialize_to_functional_syntax(self, full_yaml):
        onto = owl2.Ontology(owl2.IRI("http://example.org/pharma"))
        loader = owl2.DataLoader(onto)
        loader.load_mapping_spec(str(full_yaml))
        loader.execute()

        fs = onto.to_functional_syntax()
        assert "Declaration" in fs
        assert len(fs) > 100


class TestSimpleCSVOnly:
    """Test a minimal CSV-only pipeline to isolate basic functionality."""

    def test_minimal_csv_pipeline(self, tmp_path):
        csv_file = tmp_path / "items.csv"
        csv_file.write_text(
            "id,name,weight\n"
            "item_1,Widget,1.5\n"
            "item_2,Gadget,2.3\n"
        )

        yaml_file = tmp_path / "mapping.yaml"
        yaml_file.write_text(
            f'version: "1.0"\n'
            f'base_iri: "http://example.org/items#"\n'
            f'\n'
            f'sources:\n'
            f'  items:\n'
            f'    type: csv\n'
            f'    path: "{csv_file}"\n'
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
            f'      - {{ column: name, property: itemName }}\n'
            f'      - {{ column: weight, property: itemWeight }}\n'
        )

        onto = owl2.Ontology(owl2.IRI("http://example.org/items"))
        loader = owl2.DataLoader(onto)
        loader.load_mapping_spec(str(yaml_file))
        stats = loader.execute()

        assert stats.individuals_created == 2
        assert stats.properties_added == 4  # 2 items * 2 properties
        assert stats.errors == 0

        # Verify schema was auto-declared
        class_names = {c.get_iri().get_local_name() for c in onto.get_classes()}
        assert "Item" in class_names

        prop_names = {p.get_iri().get_local_name() for p in onto.get_data_properties()}
        assert "itemName" in prop_names
        assert "itemWeight" in prop_names


class TestLoadingStats:
    """Test LoadingStats reporting."""

    def test_stats_summary(self, tmp_path):
        csv_file = tmp_path / "data.csv"
        csv_file.write_text("id,name\n1,Test\n2,Test2\n")

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

        summary = stats.summary()
        assert "Rows processed" in summary
        assert "Individuals created" in summary
        assert "2" in summary  # 2 individuals

    def test_stats_fields_are_readonly(self):
        """LoadingStats fields are read-only (set by C++ internals)."""
        stats = owl2.LoadingStats()
        # Fields should be accessible but read-only
        assert stats.rows_processed == 0
        assert stats.individuals_created == 0
        assert stats.properties_added == 0
        assert stats.relationships_created == 0
        assert stats.errors == 0

        # Attempting to set a read-only field should raise AttributeError
        with pytest.raises(AttributeError):
            stats.rows_processed = 10

    def test_stats_merge_via_pipeline(self, tmp_path):
        """Test that stats accumulate correctly across a real pipeline execution."""
        csv_file = tmp_path / "data.csv"
        csv_file.write_text("id,name\n1,A\n2,B\n3,C\n")

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

        assert stats.rows_processed == 3
        assert stats.individuals_created == 3
        assert stats.properties_added == 3


class TestProgressCallback:
    """Test progress callback during loading."""

    def test_progress_callback_called(self, tmp_path):
        csv_file = tmp_path / "data.csv"
        csv_file.write_text("id,name\n1,A\n2,B\n3,C\n")

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
        )

        onto = owl2.Ontology(owl2.IRI("http://example.org/test"))
        loader = owl2.DataLoader(onto)
        loader.load_mapping_spec(str(yaml_file))

        progress_calls = []
        loader.set_progress_callback(
            lambda current, total, name: progress_calls.append((current, total, name))
        )

        loader.execute()

        assert len(progress_calls) > 0
        # Last call should have current == total for the mapping
        last_call = progress_calls[-1]
        assert last_call[0] == last_call[1]


class TestEmptyData:
    """Test handling of edge cases."""

    def test_empty_csv(self, tmp_path):
        csv_file = tmp_path / "empty.csv"
        csv_file.write_text("id,name\n")  # Headers only, no data

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
        )

        onto = owl2.Ontology(owl2.IRI("http://example.org/test"))
        loader = owl2.DataLoader(onto)
        loader.load_mapping_spec(str(yaml_file))
        stats = loader.execute()

        assert stats.individuals_created == 0
        assert stats.errors == 0

    def test_missing_column_skips_gracefully(self, tmp_path):
        csv_file = tmp_path / "data.csv"
        csv_file.write_text("id,name\n1,Test\n")

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
            f'      - {{ column: nonexistent_column, property: missingProp }}\n'
        )

        onto = owl2.Ontology(owl2.IRI("http://example.org/test"))
        loader = owl2.DataLoader(onto)
        loader.load_mapping_spec(str(yaml_file))
        stats = loader.execute()

        # Should still create the individual, just skip the missing property
        assert stats.individuals_created == 1
        assert stats.properties_added == 0
