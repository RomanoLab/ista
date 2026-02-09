"""
Tests for project configuration and the populated_ontology_path field.

Covers:
- DataMappingSpec.populated_ontology_path YAML roundtrip (save + reload)
- Empty populated_ontology_path defaults to empty string
- resolve_source_paths() resolves populated_ontology_path
- Python bindings for newly exposed metadata fields
- New project YAML structure matches expected format
"""

import os
import sys
import tempfile

import pytest

# Ensure the C++ extension module build directory is on the path
_build_dir = os.path.join(os.path.dirname(__file__), '..', 'build', 'lib', 'python')
if os.path.isdir(_build_dir) and os.path.abspath(_build_dir) not in sys.path:
    sys.path.insert(0, os.path.abspath(_build_dir))

import _libista_owl2 as owl2


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def minimal_spec():
    """Create a minimal DataMappingSpec with project metadata."""
    spec = owl2.DataMappingSpec()
    spec.version = "1.0"
    spec.project_name = "PharmaTox Analysis"
    spec.project_description = "Biomedical knowledge graph for drug-toxicity data"
    spec.ontology_path = "ontologies/pharmatox.owl"
    spec.populated_ontology_path = "ontologies/pharmatox-populated.ttl"
    spec.base_iri = "http://example.org/pharmatox#"
    spec.created_at = "2025-01-15T10:30:00Z"
    spec.modified_at = "2025-01-15T12:00:00Z"
    spec.created_by = "test_user"
    return spec


@pytest.fixture
def yaml_with_populated_path(tmp_path):
    """Write a YAML project file that includes populated_ontology_path."""
    yaml_content = '''\
version: "1.0"
project_name: "Drug Interaction Study"
project_description: "Analysis of drug-drug interactions"
ontology_path: "pharmatox.owl"
populated_ontology_path: "pharmatox-populated.ttl"
created_at: "2025-06-01T08:00:00Z"
modified_at: "2025-06-01T09:00:00Z"
created_by: "researcher"
base_iri: "http://example.org/pharmatox#"

sources:
  drug_data:
    type: csv
    path: "data/drugs.csv"
'''
    yaml_file = tmp_path / "project.yaml"
    yaml_file.write_text(yaml_content)
    return str(yaml_file)


# ---------------------------------------------------------------------------
# Tests: populated_ontology_path field
# ---------------------------------------------------------------------------

class TestPopulatedOntologyPath:
    """Tests for the populated_ontology_path field on DataMappingSpec."""

    def test_default_is_empty(self):
        """populated_ontology_path defaults to an empty string."""
        spec = owl2.DataMappingSpec()
        assert spec.populated_ontology_path == ""

    def test_set_and_get(self):
        """Can set and read back populated_ontology_path."""
        spec = owl2.DataMappingSpec()
        spec.populated_ontology_path = "output/my-ontology-populated.ttl"
        assert spec.populated_ontology_path == "output/my-ontology-populated.ttl"

    def test_yaml_roundtrip(self, minimal_spec, tmp_path):
        """Save a spec to YAML and reload; populated_ontology_path is preserved."""
        filepath = str(tmp_path / "roundtrip.yaml")
        minimal_spec.save_to_file(filepath)

        loaded = owl2.DataMappingSpec.load_from_file(filepath)
        assert loaded.populated_ontology_path == "ontologies/pharmatox-populated.ttl"

    def test_yaml_roundtrip_empty(self, tmp_path):
        """When populated_ontology_path is empty, it does not appear in YAML
        and reloads as empty string."""
        spec = owl2.DataMappingSpec()
        spec.version = "1.0"
        spec.ontology_path = "test.owl"

        filepath = str(tmp_path / "no_pop.yaml")
        spec.save_to_file(filepath)

        loaded = owl2.DataMappingSpec.load_from_file(filepath)
        assert loaded.populated_ontology_path == ""

        # Verify the key is not in the YAML text
        with open(filepath) as f:
            content = f.read()
        assert "populated_ontology_path" not in content

    def test_parse_from_yaml_string(self):
        """parse() reads populated_ontology_path from a YAML string."""
        yaml_str = '''\
version: "1.0"
ontology_path: "neuro.owl"
populated_ontology_path: "neuro-populated.ttl"
base_iri: "http://example.org/neuro#"
'''
        spec = owl2.DataMappingSpec.parse(yaml_str)
        assert spec.populated_ontology_path == "neuro-populated.ttl"

    def test_load_from_file_with_populated_path(self, yaml_with_populated_path):
        """load_from_file correctly reads populated_ontology_path."""
        spec = owl2.DataMappingSpec.load_from_file(yaml_with_populated_path)
        assert spec.populated_ontology_path == "pharmatox-populated.ttl"
        assert spec.project_name == "Drug Interaction Study"

    def test_to_yaml_includes_populated_path(self, minimal_spec):
        """to_yaml() includes populated_ontology_path when set."""
        yaml_str = minimal_spec.to_yaml()
        assert 'populated_ontology_path: "ontologies/pharmatox-populated.ttl"' in yaml_str


# ---------------------------------------------------------------------------
# Tests: resolve_source_paths with populated_ontology_path
# ---------------------------------------------------------------------------

class TestResolveSourcePaths:
    """Tests that resolve_source_paths() resolves populated_ontology_path."""

    def test_resolves_relative_populated_path(self):
        """Relative populated_ontology_path is resolved against base_path."""
        spec = owl2.DataMappingSpec()
        spec.base_path = "/projects/pharma/"
        spec.ontology_path = "ontologies/pharmatox.owl"
        spec.populated_ontology_path = "output/pharmatox-populated.ttl"

        spec.resolve_source_paths()

        assert spec.ontology_path == "/projects/pharma/ontologies/pharmatox.owl"
        assert spec.populated_ontology_path == "/projects/pharma/output/pharmatox-populated.ttl"

    def test_absolute_path_unchanged(self):
        """Absolute populated_ontology_path is not modified by resolve."""
        spec = owl2.DataMappingSpec()
        spec.base_path = "/projects/pharma/"
        spec.populated_ontology_path = "/absolute/path/populated.ttl"

        spec.resolve_source_paths()

        assert spec.populated_ontology_path == "/absolute/path/populated.ttl"

    def test_empty_base_path_noop(self):
        """When base_path is empty, resolve_source_paths does nothing."""
        spec = owl2.DataMappingSpec()
        spec.populated_ontology_path = "relative/path.ttl"

        spec.resolve_source_paths()

        assert spec.populated_ontology_path == "relative/path.ttl"


# ---------------------------------------------------------------------------
# Tests: Python bindings for newly exposed metadata fields
# ---------------------------------------------------------------------------

class TestMetadataBindings:
    """Tests for metadata fields exposed through Python bindings."""

    def test_project_name_binding(self):
        """project_name is readable and writable."""
        spec = owl2.DataMappingSpec()
        assert spec.project_name == ""
        spec.project_name = "Cardiology KB"
        assert spec.project_name == "Cardiology KB"

    def test_project_description_binding(self):
        """project_description is readable and writable."""
        spec = owl2.DataMappingSpec()
        spec.project_description = "Heart disease ontology analysis"
        assert spec.project_description == "Heart disease ontology analysis"

    def test_ontology_path_binding(self):
        """ontology_path is readable and writable."""
        spec = owl2.DataMappingSpec()
        spec.ontology_path = "cardio.owl"
        assert spec.ontology_path == "cardio.owl"

    def test_created_at_binding(self):
        """created_at is readable and writable."""
        spec = owl2.DataMappingSpec()
        spec.created_at = "2025-03-01T00:00:00Z"
        assert spec.created_at == "2025-03-01T00:00:00Z"

    def test_modified_at_binding(self):
        """modified_at is readable and writable."""
        spec = owl2.DataMappingSpec()
        spec.modified_at = "2025-03-02T12:00:00Z"
        assert spec.modified_at == "2025-03-02T12:00:00Z"

    def test_created_by_binding(self):
        """created_by is readable and writable."""
        spec = owl2.DataMappingSpec()
        spec.created_by = "Dr. Smith"
        assert spec.created_by == "Dr. Smith"

    def test_metadata_yaml_roundtrip(self, tmp_path):
        """All metadata fields survive a save + load cycle."""
        spec = owl2.DataMappingSpec()
        spec.version = "1.0"
        spec.project_name = "Genomics Pipeline"
        spec.project_description = "Gene-disease associations"
        spec.ontology_path = "genomics.owl"
        spec.populated_ontology_path = "genomics-populated.ttl"
        spec.created_at = "2025-04-01T10:00:00Z"
        spec.modified_at = "2025-04-02T15:30:00Z"
        spec.created_by = "lab_team"
        spec.base_iri = "http://example.org/genomics#"

        filepath = str(tmp_path / "metadata_test.yaml")
        spec.save_to_file(filepath)

        loaded = owl2.DataMappingSpec.load_from_file(filepath)
        assert loaded.project_name == "Genomics Pipeline"
        assert loaded.project_description == "Gene-disease associations"
        assert loaded.ontology_path == "genomics.owl"
        assert loaded.populated_ontology_path == "genomics-populated.ttl"
        assert loaded.created_at == "2025-04-01T10:00:00Z"
        assert loaded.modified_at == "2025-04-02T15:30:00Z"
        assert loaded.created_by == "lab_team"
        assert loaded.base_iri == "http://example.org/genomics#"


# ---------------------------------------------------------------------------
# Tests: New project YAML structure
# ---------------------------------------------------------------------------

class TestNewProjectYaml:
    """Tests for YAML structure produced by a minimal new project spec."""

    def test_minimal_project_yaml_structure(self, tmp_path):
        """A new project spec produces valid YAML with expected keys."""
        spec = owl2.DataMappingSpec()
        spec.version = "1.0"
        spec.project_name = "NeuroKB"
        spec.ontology_path = "neuro.owl"
        spec.created_at = "2025-05-01T09:00:00Z"
        spec.modified_at = "2025-05-01T09:00:00Z"

        filepath = str(tmp_path / "new_project.yaml")
        spec.save_to_file(filepath)

        with open(filepath) as f:
            content = f.read()

        # Verify required keys are present
        assert 'version: "1.0"' in content
        assert 'project_name: "NeuroKB"' in content
        assert 'ontology_path: "neuro.owl"' in content
        assert 'created_at:' in content
        assert 'modified_at:' in content

        # Verify optional keys are absent when not set
        assert "populated_ontology_path" not in content
        assert "created_by" not in content

    def test_project_reloadable(self, tmp_path):
        """A saved project can be reloaded with all data intact."""
        spec = owl2.DataMappingSpec()
        spec.version = "1.0"
        spec.project_name = "Proteomics Study"
        spec.ontology_path = "proteins.owl"
        spec.populated_ontology_path = "proteins-populated.ttl"
        spec.base_iri = "http://example.org/proteins#"
        spec.created_at = "2025-07-01T00:00:00Z"
        spec.modified_at = "2025-07-01T00:00:00Z"

        filepath = str(tmp_path / "proteomics.yaml")
        spec.save_to_file(filepath)

        reloaded = owl2.DataMappingSpec.load_from_file(filepath)
        assert reloaded.version == "1.0"
        assert reloaded.project_name == "Proteomics Study"
        assert reloaded.ontology_path == "proteins.owl"
        assert reloaded.populated_ontology_path == "proteins-populated.ttl"
        assert reloaded.base_iri == "http://example.org/proteins#"


# ---------------------------------------------------------------------------
# Tests: Source name preservation during YAML roundtrip
# ---------------------------------------------------------------------------

class TestSourceNamePreservation:
    """Tests that source names survive a save/load roundtrip without renaming.

    Regression test: the GUI was regenerating source names from filenames
    (e.g. 'drugs_csv' -> 'drugs') which broke mapping references.
    """

    def test_source_names_survive_roundtrip(self, tmp_path):
        """Source names with type suffixes (drugs_csv, pharmatox_db) are preserved."""
        yaml_content = '''\
version: "1.0"
base_iri: "http://example.org/pharmatox#"

sources:
  drugs_csv:
    type: csv
    path: "data/drugs.csv"
  pharmatox_db:
    type: sqlite
    path: "data/pharmatox.db"

node_mappings:
  - name: "DrugClass from CSV"
    source: drugs_csv
    target_class: DrugClass
    mode: create
    iri_column: drug_class
    properties:
      - column: drug_class
        property: commonName
'''
        filepath = str(tmp_path / "test.yaml")
        with open(filepath, "w") as f:
            f.write(yaml_content)

        spec = owl2.DataMappingSpec.load_from_file(filepath)

        # Verify source names loaded correctly
        assert "drugs_csv" in spec.sources
        assert "pharmatox_db" in spec.sources

        # Save and reload
        out_path = str(tmp_path / "roundtrip.yaml")
        spec.save_to_file(out_path)

        reloaded = owl2.DataMappingSpec.load_from_file(out_path)
        assert "drugs_csv" in reloaded.sources
        assert "pharmatox_db" in reloaded.sources

        # Verify node mapping still references the correct source name
        assert len(reloaded.node_mappings) == 1
        assert reloaded.node_mappings[0].source == "drugs_csv"

    def test_mapping_source_references_match_source_keys(self, tmp_path):
        """All source references in mappings must exist as keys in sources."""
        yaml_content = '''\
version: "1.0"
base_iri: "http://example.org/test#"

sources:
  gene_data_tsv:
    type: tsv
    path: "data/genes.tsv"
  interactions_db:
    type: sqlite
    path: "data/interactions.db"

node_mappings:
  - name: "Genes"
    source: gene_data_tsv
    target_class: Gene
    mode: create
    iri_column: gene_id
    properties:
      - column: gene_id
        property: geneId

relationship_mappings:
  - name: "Gene Interacts"
    source: interactions_db
    relationship: interactsWith
    subject:
      class_name: Gene
      column: gene_a
      match_property: geneId
    object:
      class_name: Gene
      column: gene_b
      match_property: geneId
'''
        filepath = str(tmp_path / "ref_check.yaml")
        with open(filepath, "w") as f:
            f.write(yaml_content)

        spec = owl2.DataMappingSpec.load_from_file(filepath)

        # Verify all mapping source references exist in sources
        for nm in spec.node_mappings:
            assert nm.source in spec.sources, (
                f"node mapping '{nm.name}' references unknown source '{nm.source}'"
            )
        for rm in spec.relationship_mappings:
            assert rm.source in spec.sources, (
                f"relationship mapping '{rm.name}' references unknown source '{rm.source}'"
            )

    def test_pharmatox_config_source_consistency(self):
        """The pharmatox example config has consistent source names."""
        config_path = os.path.join(
            os.path.dirname(__file__), "..",
            "examples", "pharmatox_example", "config", "pharmatox_mapping.yaml"
        )
        if not os.path.exists(config_path):
            pytest.skip("pharmatox config not found")

        spec = owl2.DataMappingSpec.load_from_file(config_path)

        # Verify node mapping sources exist
        for nm in spec.node_mappings:
            assert nm.source in spec.sources, (
                f"node mapping '{nm.name}' references unknown source '{nm.source}'; "
                f"available sources: {list(spec.sources.keys())}"
            )

        # Verify relationship mapping sources exist
        for rm in spec.relationship_mappings:
            assert rm.source in spec.sources, (
                f"relationship mapping '{rm.name}' references unknown source '{rm.source}'; "
                f"available sources: {list(spec.sources.keys())}"
            )

        # Verify entity_type sources exist (if expanded)
        all_node_mappings = spec.get_all_node_mappings()
        for nm in all_node_mappings:
            assert nm.source in spec.sources, (
                f"expanded mapping '{nm.name}' references unknown source '{nm.source}'; "
                f"available sources: {list(spec.sources.keys())}"
            )


# ---------------------------------------------------------------------------
# Tests: Per-mapping table field for database sources
# ---------------------------------------------------------------------------

class TestMappingTableField:
    """Tests for the per-mapping 'table' field on NodeMapping and RelationshipMapping.

    Database sources (e.g. SQLite) may contain multiple tables. The 'table'
    field allows each mapping to specify which table to read from.
    """

    def test_node_mapping_table_default_none(self):
        """NodeMapping.table defaults to None."""
        nm = owl2.NodeMapping()
        assert nm.table is None

    def test_node_mapping_table_set_and_get(self):
        """Can set and read back NodeMapping.table."""
        nm = owl2.NodeMapping()
        nm.table = "adverse_events"
        assert nm.table == "adverse_events"

    def test_node_mapping_table_clear(self):
        """Setting NodeMapping.table to None clears the value."""
        nm = owl2.NodeMapping()
        nm.table = "cell_types"
        assert nm.table == "cell_types"
        nm.table = None
        assert nm.table is None

    def test_relationship_mapping_table_default_none(self):
        """RelationshipMapping.table defaults to None."""
        rm = owl2.RelationshipMapping()
        assert rm.table is None

    def test_relationship_mapping_table_set_and_get(self):
        """Can set and read back RelationshipMapping.table."""
        rm = owl2.RelationshipMapping()
        rm.table = "drug_treats_disease"
        assert rm.table == "drug_treats_disease"

    def test_relationship_mapping_table_clear(self):
        """Setting RelationshipMapping.table to None clears the value."""
        rm = owl2.RelationshipMapping()
        rm.table = "gene_pathway"
        assert rm.table == "gene_pathway"
        rm.table = None
        assert rm.table is None

    def test_table_yaml_roundtrip_node_mapping(self, tmp_path):
        """NodeMapping table field survives a YAML save/load cycle."""
        yaml_content = '''\
version: "1.0"
base_iri: "http://example.org/pharmatox#"

sources:
  pharmatox_db:
    type: sqlite
    path: "data/pharmatox.db"

node_mappings:
  - name: "AdverseEvents from SQLite"
    source: pharmatox_db
    target_class: AdverseEvent
    mode: create
    table: adverse_events
    iri_column: meddra_id
    properties:
      - column: meddra_id
        property: xrefMeddra
'''
        filepath = str(tmp_path / "table_node.yaml")
        with open(filepath, "w") as f:
            f.write(yaml_content)

        spec = owl2.DataMappingSpec.load_from_file(filepath)
        assert len(spec.node_mappings) == 1
        assert spec.node_mappings[0].table == "adverse_events"

        # Save and reload
        out_path = str(tmp_path / "table_node_roundtrip.yaml")
        spec.save_to_file(out_path)

        reloaded = owl2.DataMappingSpec.load_from_file(out_path)
        assert reloaded.node_mappings[0].table == "adverse_events"

    def test_table_yaml_roundtrip_relationship_mapping(self, tmp_path):
        """RelationshipMapping table field survives a YAML save/load cycle."""
        yaml_content = '''\
version: "1.0"
base_iri: "http://example.org/pharmatox#"

sources:
  pharmatox_db:
    type: sqlite
    path: "data/pharmatox.db"

relationship_mappings:
  - name: "Drug Targets Gene"
    source: pharmatox_db
    table: drug_targets_gene
    relationship: drugTargetsGene
    subject:
      class_name: Drug
      column: drugbank_id
      match_property: xrefDrugbank
    object:
      class_name: Gene
      column: ncbi_gene_id
      match_property: xrefNcbiGene
'''
        filepath = str(tmp_path / "table_rel.yaml")
        with open(filepath, "w") as f:
            f.write(yaml_content)

        spec = owl2.DataMappingSpec.load_from_file(filepath)
        assert len(spec.relationship_mappings) == 1
        assert spec.relationship_mappings[0].table == "drug_targets_gene"

        # Save and reload
        out_path = str(tmp_path / "table_rel_roundtrip.yaml")
        spec.save_to_file(out_path)

        reloaded = owl2.DataMappingSpec.load_from_file(out_path)
        assert reloaded.relationship_mappings[0].table == "drug_targets_gene"

    def test_table_absent_from_yaml_when_not_set(self, tmp_path):
        """When table is not set, it does not appear in serialized YAML."""
        yaml_content = '''\
version: "1.0"
base_iri: "http://example.org/test#"

sources:
  data_csv:
    type: csv
    path: "data/test.csv"

node_mappings:
  - name: "Simple CSV Mapping"
    source: data_csv
    target_class: Patient
    mode: create
    iri_column: patient_id
    properties:
      - column: patient_id
        property: patientId
'''
        filepath = str(tmp_path / "no_table.yaml")
        with open(filepath, "w") as f:
            f.write(yaml_content)

        spec = owl2.DataMappingSpec.load_from_file(filepath)
        assert spec.node_mappings[0].table is None

        out_path = str(tmp_path / "no_table_out.yaml")
        spec.save_to_file(out_path)

        with open(out_path) as f:
            content = f.read()
        # "table:" should not appear for a mapping without a table set
        # Check within the node_mappings section only
        assert "table:" not in content

    def test_pharmatox_table_fields_parsed(self):
        """The pharmatox example config parses table fields correctly."""
        config_path = os.path.join(
            os.path.dirname(__file__), "..",
            "examples", "pharmatox_example", "config", "pharmatox_mapping.yaml"
        )
        if not os.path.exists(config_path):
            pytest.skip("pharmatox config not found")

        spec = owl2.DataMappingSpec.load_from_file(config_path)

        # Node mappings with table fields
        db_node_mappings = {
            nm.name: nm.table for nm in spec.node_mappings if nm.table is not None
        }
        assert "AdverseEvents from SQLite" in db_node_mappings
        assert db_node_mappings["AdverseEvents from SQLite"] == "adverse_events"
        assert "CellTypes from SQLite" in db_node_mappings
        assert db_node_mappings["CellTypes from SQLite"] == "cell_types"

        # CSV node mapping should have no table
        csv_mappings = [nm for nm in spec.node_mappings if nm.table is None]
        assert any(nm.name == "DrugClass from CSV" for nm in csv_mappings)

        # Relationship mappings with table fields
        db_rel_mappings = {
            rm.name: rm.table for rm in spec.relationship_mappings if rm.table is not None
        }
        assert "Drug Treats Disease" in db_rel_mappings
        assert db_rel_mappings["Drug Treats Disease"] == "drug_treats_disease"
        assert "Drug Targets Gene" in db_rel_mappings
        assert db_rel_mappings["Drug Targets Gene"] == "drug_targets_gene"

        # CSV relationship mapping should have no table
        csv_rels = [rm for rm in spec.relationship_mappings if rm.table is None]
        assert any(rm.name == "Drug In Class" for rm in csv_rels)

    def test_to_yaml_includes_table(self):
        """to_yaml() output includes the table field when set."""
        yaml_content = '''\
version: "1.0"
base_iri: "http://example.org/test#"

sources:
  mydb:
    type: sqlite
    path: "data/test.db"

node_mappings:
  - name: "Test"
    source: mydb
    target_class: Specimen
    mode: create
    table: specimens
    iri_column: specimen_id
    properties:
      - column: specimen_id
        property: specimenId
'''
        spec = owl2.DataMappingSpec.parse(yaml_content)
        yaml_str = spec.to_yaml()
        assert "table:" in yaml_str
        assert "specimens" in yaml_str


# ---------------------------------------------------------------------------
# Tests: Single source of truth for version
# ---------------------------------------------------------------------------

class TestVersionConsistency:
    """Tests that the version is consistent across the Python bindings and
    the VERSION file at the repository root."""

    def test_bindings_version_matches_version_file(self):
        """The C++ bindings __version__ must match the VERSION file."""
        version_file = os.path.join(os.path.dirname(__file__), "..", "VERSION")
        with open(version_file) as f:
            expected = f.read().strip()
        assert owl2.__version__ == expected

    def test_version_is_semver(self):
        """The version string must be a valid semantic version (MAJOR.MINOR.PATCH)."""
        parts = owl2.__version__.split(".")
        assert len(parts) == 3, f"Expected MAJOR.MINOR.PATCH, got {owl2.__version__}"
        for part in parts:
            assert part.isdigit(), f"Non-numeric version component: {part}"


# ---------------------------------------------------------------------------
# Tests: entity_types serialization and expansion
# ---------------------------------------------------------------------------

class TestEntityTypesSerialization:
    """Tests that entity_types survive a YAML save/load roundtrip.

    Regression test: to_yaml() was not serializing the entity_types section,
    causing Drug/Gene/Disease/Pathway definitions to be lost when the GUI
    re-saved a mapping file.
    """

    ENTITY_TYPES_YAML = '''\
version: "1.0"
base_iri: "http://example.org/pharmatox#"

sources:
  drugs_csv:
    type: csv
    path: "data/drugs.csv"
  toxicity_csv:
    type: csv
    path: "data/toxicity.csv"
  genes_tsv:
    type: tsv
    path: "data/genes.tsv"

entity_types:
  Drug:
    primary:
      source: drugs_csv
      iri_column: drugbank_id
      properties:
        - column: drugbank_id
          property: xrefDrugbank
        - column: common_name
          property: commonName
    enrichments:
      - name: "Drug Toxicity Data"
        source: toxicity_csv
        match:
          source_column: cas_number
          target_property: xrefCasRN
        properties:
          - column: ld50_value
            property: ld50Value
            datatype: float
  Gene:
    primary:
      source: genes_tsv
      iri_column: gene_symbol
      properties:
        - column: ncbi_gene_id
          property: xrefNcbiGene
        - column: gene_symbol
          property: geneSymbol
'''

    def test_entity_types_parsed(self):
        """entity_types section is parsed from YAML string."""
        spec = owl2.DataMappingSpec.parse(self.ENTITY_TYPES_YAML)
        assert len(spec.entity_types) == 2
        assert "Drug" in spec.entity_types
        assert "Gene" in spec.entity_types

    def test_entity_types_primary_fields(self):
        """Primary source fields are correctly parsed."""
        spec = owl2.DataMappingSpec.parse(self.ENTITY_TYPES_YAML)
        drug = spec.entity_types["Drug"]
        assert drug.class_name == "Drug"
        assert drug.primary["source"] == "drugs_csv"
        assert drug.primary["iri_column"] == "drugbank_id"
        assert len(drug.primary["properties"]) == 2

    def test_entity_types_enrichment_fields(self):
        """Enrichment source fields are correctly parsed."""
        spec = owl2.DataMappingSpec.parse(self.ENTITY_TYPES_YAML)
        drug = spec.entity_types["Drug"]
        assert len(drug.enrichments) == 1
        enrich = drug.enrichments[0]
        assert enrich.name == "Drug Toxicity Data"
        assert enrich.source == "toxicity_csv"
        assert enrich.match.source_column == "cas_number"
        assert enrich.match.target_property == "xrefCasRN"
        assert len(enrich.properties) == 1

    def test_to_yaml_includes_entity_types(self):
        """to_yaml() output includes the entity_types section."""
        spec = owl2.DataMappingSpec.parse(self.ENTITY_TYPES_YAML)
        yaml_str = spec.to_yaml()
        assert "entity_types:" in yaml_str
        assert "Drug:" in yaml_str
        assert "Gene:" in yaml_str
        assert "primary:" in yaml_str
        assert "iri_column: drugbank_id" in yaml_str

    def test_entity_types_yaml_roundtrip(self, tmp_path):
        """entity_types survive a save + load roundtrip."""
        spec = owl2.DataMappingSpec.parse(self.ENTITY_TYPES_YAML)

        filepath = str(tmp_path / "entity_types_roundtrip.yaml")
        spec.save_to_file(filepath)

        reloaded = owl2.DataMappingSpec.load_from_file(filepath)
        assert len(reloaded.entity_types) == 2
        assert "Drug" in reloaded.entity_types
        assert "Gene" in reloaded.entity_types

        # Verify Drug primary
        drug = reloaded.entity_types["Drug"]
        assert drug.primary["source"] == "drugs_csv"
        assert drug.primary["iri_column"] == "drugbank_id"
        assert len(drug.primary["properties"]) == 2

        # Verify Drug enrichment
        assert len(drug.enrichments) == 1
        enrich = drug.enrichments[0]
        assert enrich.name == "Drug Toxicity Data"
        assert enrich.source == "toxicity_csv"
        assert enrich.match.source_column == "cas_number"

        # Verify Gene primary
        gene = reloaded.entity_types["Gene"]
        assert gene.primary["source"] == "genes_tsv"
        assert gene.primary["iri_column"] == "gene_symbol"
        assert len(gene.primary["properties"]) == 2

    def test_entity_types_enrichment_datatype_roundtrip(self, tmp_path):
        """Property datatype on enrichment survives roundtrip."""
        spec = owl2.DataMappingSpec.parse(self.ENTITY_TYPES_YAML)

        filepath = str(tmp_path / "datatype_roundtrip.yaml")
        spec.save_to_file(filepath)

        reloaded = owl2.DataMappingSpec.load_from_file(filepath)
        enrich = reloaded.entity_types["Drug"].enrichments[0]
        assert enrich.properties[0].datatype == "float"

    def test_get_all_node_mappings_includes_entity_types(self):
        """get_all_node_mappings() expands entity_types into node mappings."""
        spec = owl2.DataMappingSpec.parse(self.ENTITY_TYPES_YAML)
        all_mappings = spec.get_all_node_mappings()

        # Should have Drug primary, Drug enrichment, Gene primary = 3
        assert len(all_mappings) == 3

        names = [m.name for m in all_mappings]
        assert "Drug (primary)" in names
        assert "Drug (Drug Toxicity Data)" in names
        assert "Gene (primary)" in names

    def test_get_all_node_mappings_combined(self, tmp_path):
        """get_all_node_mappings() returns both node_mappings and entity_types."""
        yaml_content = '''\
version: "1.0"
base_iri: "http://example.org/test#"

sources:
  src_csv:
    type: csv
    path: "data/src.csv"

entity_types:
  Disease:
    primary:
      source: src_csv
      iri_column: disease_id
      properties:
        - column: disease_id
          property: diseaseId

node_mappings:
  - name: "Explicit Node Mapping"
    source: src_csv
    target_class: Symptom
    mode: create
    iri_column: symptom_id
    properties:
      - column: symptom_id
        property: symptomId
'''
        spec = owl2.DataMappingSpec.parse(yaml_content)
        all_mappings = spec.get_all_node_mappings()

        # 1 explicit node_mapping + 1 entity_type primary = 2
        assert len(all_mappings) == 2
        names = [m.name for m in all_mappings]
        assert "Explicit Node Mapping" in names
        assert "Disease (primary)" in names

    def test_pharmatox_entity_types_expansion(self):
        """The pharmatox example expands entity_types into full node mappings."""
        config_path = os.path.join(
            os.path.dirname(__file__), "..",
            "examples", "pharmatox_example", "config", "pharmatox_mapping.yaml"
        )
        if not os.path.exists(config_path):
            pytest.skip("pharmatox config not found")

        spec = owl2.DataMappingSpec.load_from_file(config_path)

        # Pharmatox has 4 entity_types: Drug, Gene, Disease, Pathway
        assert len(spec.entity_types) == 4
        for name in ["Drug", "Gene", "Disease", "Pathway"]:
            assert name in spec.entity_types, f"Missing entity_type: {name}"

        # get_all_node_mappings should include both explicit and expanded
        all_mappings = spec.get_all_node_mappings()
        # 3 explicit node_mappings + 4 primary + 1 enrichment (Drug Toxicity) = 8
        assert len(all_mappings) == 8

        # Verify Drug has both primary and enrichment
        drug_mappings = [m for m in all_mappings if "Drug" in m.name and "Class" not in m.name]
        assert len(drug_mappings) == 2  # primary + enrichment
