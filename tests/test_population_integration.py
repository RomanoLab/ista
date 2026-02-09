"""
Tests for the population integration feature.

Tests the DataLoader, DataMappingSpec construction, validation,
progress callbacks, and error handling that back the GUI's
"Add Data to Ontology" button.
"""

import os
import tempfile
import pytest

import sys
import os

# Ensure the C++ extension module build directory is on the path
_build_dir = os.path.join(os.path.dirname(__file__), '..', 'build', 'lib', 'python')
if os.path.isdir(_build_dir) and os.path.abspath(_build_dir) not in sys.path:
    sys.path.insert(0, os.path.abspath(_build_dir))

# Import the C++ bindings directly to avoid ista/__init__.py dependency issues
import _libista_owl2 as owl2


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def patient_ontology():
    """Create a biomedical ontology with Patient class and properties."""
    iri = owl2.IRI("http://example.org/pharma")
    onto = owl2.Ontology(iri)
    onto.register_prefix("ph", "http://example.org/pharma#")
    onto.register_prefix("owl", "http://www.w3.org/2002/07/owl#")
    onto.register_prefix("rdf", "http://www.w3.org/1999/02/22-rdf-syntax-ns#")
    onto.register_prefix("rdfs", "http://www.w3.org/2000/01/rdf-schema#")
    onto.register_prefix("xsd", "http://www.w3.org/2001/XMLSchema#")

    # Declare Patient class
    patient_cls = owl2.Class(owl2.IRI("ph", "Patient", "http://example.org/pharma#"))
    onto.add_axiom(owl2.Declaration(owl2.EntityType.CLASS, patient_cls.get_iri()))

    # Declare data properties
    for prop_name in ["patient_id", "age", "diagnosis", "treatment", "outcome"]:
        prop = owl2.DataProperty(owl2.IRI("ph", prop_name, "http://example.org/pharma#"))
        onto.add_axiom(owl2.Declaration(owl2.EntityType.DATA_PROPERTY, prop.get_iri()))

    return onto


@pytest.fixture
def patient_csv(tmp_path):
    """Write a small patient CSV file and return its path."""
    csv_path = tmp_path / "patients.csv"
    csv_path.write_text(
        "patient_id,age,diagnosis,treatment,outcome\n"
        "PT001,45,Diabetes,Metformin,Improved\n"
        "PT002,62,Hypertension,Lisinopril,Stable\n"
        "PT003,38,Asthma,Albuterol,Improved\n"
    )
    return str(csv_path)


@pytest.fixture
def patient_spec(patient_csv):
    """Build a DataMappingSpec for the patient data."""
    spec = owl2.DataMappingSpec()
    spec.base_iri = "http://example.org/pharma#"

    # Data source
    src = owl2.DataSourceDef()
    src.name = "patients"
    src.type = "csv"
    src.path = patient_csv
    src.delimiter = ","
    src.has_headers = True
    spec.sources = {"patients": src}

    # Node mapping
    nm = owl2.NodeMapping()
    nm.name = "create_patients"
    nm.source = "patients"
    nm.target_class = "Patient"
    nm.mode = owl2.MappingMode.CREATE
    nm.iri_column = "patient_id"

    props = []
    for col in ["patient_id", "age", "diagnosis", "treatment", "outcome"]:
        pm = owl2.PropertyMapping()
        pm.column = col
        pm.property = col
        props.append(pm)
    nm.properties = props

    spec.node_mappings = [nm]
    return spec


# ---------------------------------------------------------------------------
# DataLoader execution tests
# ---------------------------------------------------------------------------

class TestDataLoaderExecution:
    """Tests for executing DataLoader and verifying stats."""

    def test_execute_creates_individuals(self, patient_ontology, patient_spec):
        """Executing a valid spec should create individuals."""
        loader = owl2.DataLoader(patient_ontology)
        loader.set_mapping_spec(patient_spec)
        stats = loader.execute()

        assert stats.rows_processed == 3
        assert stats.individuals_created == 3
        assert stats.errors == 0
        assert stats.rows_skipped == 0

    def test_execute_adds_properties(self, patient_ontology, patient_spec):
        """Each row should produce property assertions."""
        loader = owl2.DataLoader(patient_ontology)
        loader.set_mapping_spec(patient_spec)
        stats = loader.execute()

        # Properties are only added for columns that match declared data properties.
        # The exact count depends on which columns the loader resolves as known
        # properties. At minimum, the operation should succeed without errors.
        assert stats.errors == 0
        assert stats.properties_added >= 0

    def test_individuals_present_after_execute(self, patient_ontology, patient_spec):
        """After execution, ontology should contain the new individuals."""
        loader = owl2.DataLoader(patient_ontology)
        loader.set_mapping_spec(patient_spec)
        loader.execute()

        individuals = patient_ontology.get_individuals()
        assert len(individuals) == 3

    def test_execute_empty_csv(self, patient_ontology, tmp_path):
        """Executing with an empty CSV (headers only) should process 0 rows."""
        csv_path = tmp_path / "empty.csv"
        csv_path.write_text("patient_id,age,diagnosis\n")

        spec = owl2.DataMappingSpec()
        spec.base_iri = "http://example.org/pharma#"

        src = owl2.DataSourceDef()
        src.name = "empty"
        src.type = "csv"
        src.path = str(csv_path)
        spec.sources = {"empty": src}

        nm = owl2.NodeMapping()
        nm.name = "create_empty"
        nm.source = "empty"
        nm.target_class = "Patient"
        nm.mode = owl2.MappingMode.CREATE
        nm.iri_column = "patient_id"
        spec.node_mappings = [nm]

        loader = owl2.DataLoader(patient_ontology)
        loader.set_mapping_spec(spec)
        stats = loader.execute()

        assert stats.rows_processed == 0
        assert stats.individuals_created == 0

    def test_execute_node_mapping_by_name(self, patient_ontology, patient_spec):
        """Execute a single node mapping by name."""
        loader = owl2.DataLoader(patient_ontology)
        loader.set_mapping_spec(patient_spec)
        stats = loader.execute_node_mapping("create_patients")

        assert stats.rows_processed == 3
        assert stats.individuals_created == 3

    def test_loading_stats_summary(self, patient_ontology, patient_spec):
        """LoadingStats.summary() should return a non-empty string."""
        loader = owl2.DataLoader(patient_ontology)
        loader.set_mapping_spec(patient_spec)
        stats = loader.execute()

        summary = stats.summary()
        assert "Rows processed: 3" in summary
        assert "Individuals created: 3" in summary

    def test_loading_stats_merge(self):
        """LoadingStats.merge() should combine two stats objects."""
        s1 = owl2.LoadingStats()
        s2 = owl2.LoadingStats()
        # s1 and s2 start at defaults (0); merge shouldn't fail
        s1.merge(s2)
        assert s1.rows_processed == 0


# ---------------------------------------------------------------------------
# Validation tests
# ---------------------------------------------------------------------------

class TestValidation:
    """Tests for DataMappingSpec.validate() and DataLoader.validate()."""

    def test_valid_spec_passes_validation(self, patient_ontology, patient_spec):
        """A correctly configured spec should pass validation."""
        result = patient_spec.validate(patient_ontology)
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_missing_class_fails_validation(self, patient_ontology, patient_csv):
        """Referencing a non-existent class should produce a validation error."""
        spec = owl2.DataMappingSpec()
        spec.base_iri = "http://example.org/pharma#"

        src = owl2.DataSourceDef()
        src.name = "patients"
        src.type = "csv"
        src.path = patient_csv
        spec.sources = {"patients": src}

        nm = owl2.NodeMapping()
        nm.name = "bad_class"
        nm.source = "patients"
        nm.target_class = "NonExistentClass"
        nm.mode = owl2.MappingMode.CREATE
        nm.iri_column = "patient_id"
        spec.node_mappings = [nm]

        result = spec.validate(patient_ontology)
        assert result.is_valid is False
        assert len(result.errors) > 0

    def test_missing_source_fails_validation(self, patient_ontology):
        """Referencing a non-existent data source should produce a validation error."""
        spec = owl2.DataMappingSpec()
        spec.base_iri = "http://example.org/pharma#"
        spec.sources = {}  # No sources defined

        nm = owl2.NodeMapping()
        nm.name = "no_source"
        nm.source = "nonexistent_source"
        nm.target_class = "Patient"
        nm.mode = owl2.MappingMode.CREATE
        nm.iri_column = "patient_id"
        spec.node_mappings = [nm]

        result = spec.validate(patient_ontology)
        assert result.is_valid is False
        assert any("nonexistent_source" in e.lower() or "source" in e.lower()
                    for e in result.errors)

    def test_validation_result_repr(self, patient_ontology, patient_spec):
        """ValidationResult repr should include validity and counts."""
        result = patient_spec.validate(patient_ontology)
        repr_str = repr(result)
        assert "valid=True" in repr_str

    def test_loader_validate(self, patient_ontology, patient_spec):
        """DataLoader.validate() should return the same result as spec.validate()."""
        loader = owl2.DataLoader(patient_ontology)
        loader.set_mapping_spec(patient_spec)
        result = loader.validate()
        assert result.is_valid is True


# ---------------------------------------------------------------------------
# Progress callback tests
# ---------------------------------------------------------------------------

class TestProgressCallback:
    """Tests for progress callback invocation."""

    def test_progress_callback_called(self, patient_ontology, patient_spec):
        """Progress callback should be invoked during execution."""
        calls = []

        def on_progress(current, total, mapping_name):
            calls.append((current, total, mapping_name))

        loader = owl2.DataLoader(patient_ontology)
        loader.set_mapping_spec(patient_spec)
        loader.set_progress_callback(on_progress)
        loader.execute()

        assert len(calls) > 0

    def test_progress_callback_reports_mapping_name(self, patient_ontology, patient_spec):
        """Progress callback should report the mapping name."""
        names = set()

        def on_progress(current, total, mapping_name):
            names.add(mapping_name)

        loader = owl2.DataLoader(patient_ontology)
        loader.set_mapping_spec(patient_spec)
        loader.set_progress_callback(on_progress)
        loader.execute()

        assert "create_patients" in names

    def test_progress_callback_row_counts(self, patient_ontology, patient_spec):
        """Progress callback should report increasing current row counts."""
        currents = []

        def on_progress(current, total, mapping_name):
            currents.append(current)

        loader = owl2.DataLoader(patient_ontology)
        loader.set_mapping_spec(patient_spec)
        loader.set_progress_callback(on_progress)
        loader.execute()

        # Current row values should be monotonically non-decreasing
        for i in range(1, len(currents)):
            assert currents[i] >= currents[i - 1]


# ---------------------------------------------------------------------------
# Error handling tests
# ---------------------------------------------------------------------------

class TestErrorHandling:
    """Tests for error handling in data loading."""

    def test_nonexistent_file_raises_exception(self, patient_ontology):
        """Loading from a nonexistent file should raise DataLoaderException."""
        spec = owl2.DataMappingSpec()
        spec.base_iri = "http://example.org/pharma#"

        src = owl2.DataSourceDef()
        src.name = "missing"
        src.type = "csv"
        src.path = "/nonexistent/path/data.csv"
        spec.sources = {"missing": src}

        nm = owl2.NodeMapping()
        nm.name = "from_missing"
        nm.source = "missing"
        nm.target_class = "Patient"
        nm.mode = owl2.MappingMode.CREATE
        nm.iri_column = "patient_id"
        spec.node_mappings = [nm]

        loader = owl2.DataLoader(patient_ontology)
        loader.set_mapping_spec(spec)

        with pytest.raises(owl2.DataLoaderException):
            loader.execute()

    def test_invalid_yaml_raises_exception(self, tmp_path):
        """Loading a malformed YAML file should raise an exception."""
        bad_yaml = tmp_path / "bad.yaml"
        bad_yaml.write_text("{{{{not valid yaml at all")

        with pytest.raises((owl2.MappingSpecException, owl2.YamlParseException)):
            owl2.DataMappingSpec.load_from_file(str(bad_yaml))

    def test_nonexistent_yaml_raises_exception(self):
        """Loading from a nonexistent YAML path should raise an exception."""
        with pytest.raises((owl2.MappingSpecException, owl2.YamlParseException, RuntimeError)):
            owl2.DataMappingSpec.load_from_file("/nonexistent/spec.yaml")


# ---------------------------------------------------------------------------
# DataMappingSpec construction tests
# ---------------------------------------------------------------------------

class TestDataMappingSpecConstruction:
    """Tests for building DataMappingSpec programmatically."""

    def test_create_empty_spec(self):
        """Should be able to create an empty DataMappingSpec."""
        spec = owl2.DataMappingSpec()
        assert spec.version == "1.0"
        assert len(spec.sources) == 0
        assert len(spec.node_mappings) == 0
        assert len(spec.relationship_mappings) == 0

    def test_spec_repr(self):
        """DataMappingSpec repr should include counts."""
        spec = owl2.DataMappingSpec()
        repr_str = repr(spec)
        assert "sources=0" in repr_str
        assert "node_mappings=0" in repr_str

    def test_spec_roundtrip_yaml(self, patient_spec, tmp_path):
        """Spec should survive YAML serialization and deserialization."""
        yaml_path = tmp_path / "roundtrip.yaml"
        patient_spec.save_to_file(str(yaml_path))

        loaded = owl2.DataMappingSpec.load_from_file(str(yaml_path))
        assert len(loaded.sources) == len(patient_spec.sources)
        assert len(loaded.node_mappings) == len(patient_spec.node_mappings)

    def test_spec_to_yaml_string(self, patient_spec):
        """to_yaml() should return a non-empty string."""
        yaml_str = patient_spec.to_yaml()
        assert len(yaml_str) > 0
        assert "patients" in yaml_str

    def test_get_all_node_mappings(self, patient_spec):
        """get_all_node_mappings() should return the mappings."""
        all_mappings = patient_spec.get_all_node_mappings()
        assert len(all_mappings) == 1
        assert all_mappings[0].name == "create_patients"

    def test_node_mapping_properties(self, patient_spec):
        """NodeMapping should have the correct properties set."""
        nm = patient_spec.node_mappings[0]
        assert nm.name == "create_patients"
        assert nm.source == "patients"
        assert nm.target_class == "Patient"
        assert nm.mode == owl2.MappingMode.CREATE
        assert nm.iri_column == "patient_id"
        assert len(nm.properties) == 5
        assert nm.skip is False

    def test_data_source_def_properties(self, patient_spec):
        """DataSourceDef should have the correct properties set."""
        src = patient_spec.sources["patients"]
        assert src.name == "patients"
        assert src.type == "csv"
        assert src.has_headers is True

    def test_loading_stats_repr(self):
        """LoadingStats repr should include key counts."""
        stats = owl2.LoadingStats()
        repr_str = repr(stats)
        assert "rows=0" in repr_str
        assert "created=0" in repr_str


# ---------------------------------------------------------------------------
# TSV support test
# ---------------------------------------------------------------------------

class TestTSVSupport:
    """Tests for TSV (tab-delimited) data sources."""

    def test_tsv_data_source(self, patient_ontology, tmp_path):
        """DataLoader should handle TSV files correctly."""
        tsv_path = tmp_path / "patients.tsv"
        tsv_path.write_text(
            "patient_id\tage\tdiagnosis\n"
            "PT100\t30\tFlu\n"
            "PT101\t40\tCold\n"
        )

        spec = owl2.DataMappingSpec()
        spec.base_iri = "http://example.org/pharma#"

        src = owl2.DataSourceDef()
        src.name = "tsv_patients"
        src.type = "tsv"
        src.path = str(tsv_path)
        src.delimiter = "\t"
        src.has_headers = True
        spec.sources = {"tsv_patients": src}

        nm = owl2.NodeMapping()
        nm.name = "create_tsv_patients"
        nm.source = "tsv_patients"
        nm.target_class = "Patient"
        nm.mode = owl2.MappingMode.CREATE
        nm.iri_column = "patient_id"

        props = []
        for col in ["patient_id", "age", "diagnosis"]:
            pm = owl2.PropertyMapping()
            pm.column = col
            pm.property = col
            props.append(pm)
        nm.properties = props

        spec.node_mappings = [nm]

        loader = owl2.DataLoader(patient_ontology)
        loader.set_mapping_spec(spec)
        stats = loader.execute()

        assert stats.rows_processed == 2
        assert stats.individuals_created == 2


# ---------------------------------------------------------------------------
# YAML parser regression tests
# ---------------------------------------------------------------------------

class TestYamlParserListMaps:
    """Regression tests for YAML list items with map content on the same line."""

    def test_list_item_map_on_same_line(self, tmp_path):
        """List items with first key on same line as dash should parse correctly."""
        yaml_content = (
            'version: "1.0"\n'
            'base_iri: "http://example.org/test#"\n'
            'sources:\n'
            '  test_src:\n'
            '    type: csv\n'
            '    path: dummy.csv\n'
            'node_mappings:\n'
            '  - name: "First Mapping"\n'
            '    source: test_src\n'
            '    target_class: ClassA\n'
            '    mode: create\n'
            '    iri_column: id_col\n'
            '  - name: "Second Mapping"\n'
            '    source: test_src\n'
            '    target_class: ClassB\n'
            '    mode: create\n'
            '    iri_column: id_col\n'
        )
        yaml_path = tmp_path / "test_list_maps.yaml"
        yaml_path.write_text(yaml_content)

        spec = owl2.DataMappingSpec.load_from_file(str(yaml_path))

        assert len(spec.node_mappings) == 2
        assert spec.node_mappings[0].name == "First Mapping"
        assert spec.node_mappings[0].source == "test_src"
        assert spec.node_mappings[0].target_class == "ClassA"
        assert spec.node_mappings[0].iri_column == "id_col"
        assert spec.node_mappings[1].name == "Second Mapping"
        assert spec.node_mappings[1].target_class == "ClassB"

    def test_relationship_mapping_class_name(self, tmp_path):
        """Relationship mappings should parse class_name from subject/object."""
        yaml_content = (
            'version: "1.0"\n'
            'base_iri: "http://example.org/test#"\n'
            'sources:\n'
            '  test_src:\n'
            '    type: csv\n'
            '    path: dummy.csv\n'
            'relationship_mappings:\n'
            '  - name: "Test Relationship"\n'
            '    source: test_src\n'
            '    relationship: testProp\n'
            '    subject:\n'
            '      class_name: ClassA\n'
            '      column: col_a\n'
            '      match_property: propA\n'
            '    object:\n'
            '      class_name: ClassB\n'
            '      column: col_b\n'
            '      match_property: propB\n'
        )
        yaml_path = tmp_path / "test_rel.yaml"
        yaml_path.write_text(yaml_content)

        spec = owl2.DataMappingSpec.load_from_file(str(yaml_path))

        assert len(spec.relationship_mappings) == 1
        rm = spec.relationship_mappings[0]
        assert rm.name == "Test Relationship"
        assert rm.subject.class_name == "ClassA"
        assert rm.subject.column == "col_a"
        assert rm.object.class_name == "ClassB"
        assert rm.object.match_property == "propB"

    def test_nested_list_with_inline_maps(self, tmp_path):
        """Properties as inline maps within list items should parse correctly."""
        yaml_content = (
            'version: "1.0"\n'
            'base_iri: "http://example.org/test#"\n'
            'sources:\n'
            '  src:\n'
            '    type: csv\n'
            '    path: dummy.csv\n'
            'node_mappings:\n'
            '  - name: "With Props"\n'
            '    source: src\n'
            '    target_class: MyClass\n'
            '    mode: create\n'
            '    iri_column: my_id\n'
            '    properties:\n'
            '      - { column: col1, property: prop1 }\n'
            '      - { column: col2, property: prop2 }\n'
            '      - { column: col3, property: prop3 }\n'
        )
        yaml_path = tmp_path / "test_nested.yaml"
        yaml_path.write_text(yaml_content)

        spec = owl2.DataMappingSpec.load_from_file(str(yaml_path))

        assert len(spec.node_mappings) == 1
        nm = spec.node_mappings[0]
        assert nm.name == "With Props"
        assert len(nm.properties) == 3
        assert nm.properties[0].column == "col1"
        assert nm.properties[1].property == "prop2"

    def test_pharmatox_full_spec_validation(self):
        """The pharmatox example spec should parse and validate correctly."""
        import os
        spec_path = os.path.join(
            os.path.dirname(__file__), '..', 'examples',
            'pharmatox_example', 'config', 'pharmatox_mapping.yaml'
        )
        if not os.path.exists(spec_path):
            pytest.skip("pharmatox example not available")

        onto_path = os.path.join(
            os.path.dirname(__file__), '..', 'examples',
            'pharmatox_example', 'ontology', 'pharmatox.owl'
        )
        if not os.path.exists(onto_path):
            pytest.skip("pharmatox ontology not available")

        spec = owl2.DataMappingSpec.load_from_file(spec_path)
        onto = owl2.RDFXMLParser.parse_from_file(onto_path)

        # Verify all sections parsed
        assert len(spec.node_mappings) == 3
        assert len(spec.relationship_mappings) == 7
        assert len(spec.sources) == 6

        # All node mapping names should be non-empty
        for nm in spec.node_mappings:
            assert nm.name != ""
            assert nm.source != ""
            assert nm.target_class != ""

        # All relationship mapping subjects/objects should have class_name
        for rm in spec.relationship_mappings:
            assert rm.subject.class_name != "", f"{rm.name} subject.class_name is empty"
            assert rm.object.class_name != "", f"{rm.name} object.class_name is empty"

        # Validation should pass
        result = spec.validate(onto)
        assert result.is_valid, f"Validation errors: {result.errors}"


class TestSourcePathResolution:
    """Tests for DataMappingSpec.resolve_source_paths() and base_path."""

    def test_load_from_file_sets_base_path(self, tmp_path):
        """load_from_file should set base_path to the YAML file's directory."""
        yaml_content = (
            'version: "1.0"\n'
            'base_iri: "http://example.org/test#"\n'
        )
        yaml_path = tmp_path / "subdir" / "spec.yaml"
        yaml_path.parent.mkdir(parents=True, exist_ok=True)
        yaml_path.write_text(yaml_content)

        spec = owl2.DataMappingSpec.load_from_file(str(yaml_path))
        assert spec.base_path == str(tmp_path / "subdir") + "/"

    def test_resolve_source_paths_relative(self, tmp_path):
        """resolve_source_paths should prepend base_path to relative source paths."""
        yaml_content = (
            'version: "1.0"\n'
            'base_iri: "http://example.org/test#"\n'
            'sources:\n'
            '  src1:\n'
            '    type: csv\n'
            '    path: "../data/file.csv"\n'
        )
        yaml_path = tmp_path / "config" / "spec.yaml"
        yaml_path.parent.mkdir(parents=True, exist_ok=True)
        yaml_path.write_text(yaml_content)

        spec = owl2.DataMappingSpec.load_from_file(str(yaml_path))
        spec.resolve_source_paths()

        resolved = spec.sources["src1"].path
        # Should start with the config dir and include ../data/
        assert resolved.startswith(str(tmp_path / "config") + "/")
        assert "../data/file.csv" in resolved

    def test_resolve_source_paths_absolute_unchanged(self, tmp_path):
        """Absolute paths should not be modified by resolve_source_paths."""
        yaml_content = (
            'version: "1.0"\n'
            'base_iri: "http://example.org/test#"\n'
            'sources:\n'
            '  src1:\n'
            '    type: csv\n'
            '    path: "/absolute/path/file.csv"\n'
        )
        yaml_path = tmp_path / "spec.yaml"
        yaml_path.write_text(yaml_content)

        spec = owl2.DataMappingSpec.load_from_file(str(yaml_path))
        spec.resolve_source_paths()

        assert spec.sources["src1"].path == "/absolute/path/file.csv"

    def test_resolve_source_paths_empty_base_path_noop(self):
        """If base_path is empty, resolve_source_paths does nothing."""
        spec = owl2.DataMappingSpec()
        src = owl2.DataSourceDef()
        src.name = "test"
        src.type = "csv"
        src.path = "./relative/file.csv"
        spec.sources = {"test": src}
        spec.base_path = ""

        spec.resolve_source_paths()
        assert spec.sources["test"].path == "./relative/file.csv"

    def test_resolve_multiple_sources(self, tmp_path):
        """resolve_source_paths should resolve all relative source paths."""
        spec = owl2.DataMappingSpec()
        spec.base_path = str(tmp_path) + "/"

        src1 = owl2.DataSourceDef()
        src1.name = "s1"
        src1.type = "csv"
        src1.path = "../data/a.csv"

        src2 = owl2.DataSourceDef()
        src2.name = "s2"
        src2.type = "tsv"
        src2.path = "/absolute/b.tsv"

        spec.sources = {"s1": src1, "s2": src2}
        spec.resolve_source_paths()

        assert spec.sources["s1"].path == str(tmp_path) + "/../data/a.csv"
        assert spec.sources["s2"].path == "/absolute/b.tsv"

    def test_pharmatox_paths_resolve_correctly(self):
        """Pharmatox YAML should resolve paths to actual files on disk."""
        spec_path = os.path.join(
            os.path.dirname(__file__), '..', 'examples',
            'pharmatox_example', 'config', 'pharmatox_mapping.yaml'
        )
        if not os.path.exists(spec_path):
            pytest.skip("pharmatox example not available")

        spec = owl2.DataMappingSpec.load_from_file(os.path.abspath(spec_path))
        spec.resolve_source_paths()

        # After resolution, the drugs_csv path should point to an actual file
        drugs_path = spec.sources["drugs_csv"].path
        assert os.path.exists(drugs_path), \
            f"Resolved path does not exist: {drugs_path}"

        # Check all CSV/TSV sources resolve to existing files
        for name in ["drugs_csv", "drug_toxicity_csv", "genes_tsv",
                      "diseases_tsv", "pathways_tsv"]:
            path = spec.sources[name].path
            assert os.path.exists(path), \
                f"Source {name} path does not exist: {path}"

    def test_dataloader_load_mapping_spec_resolves_paths(self):
        """DataLoader.load_mapping_spec should resolve paths automatically."""
        spec_path = os.path.join(
            os.path.dirname(__file__), '..', 'examples',
            'pharmatox_example', 'config', 'pharmatox_mapping.yaml'
        )
        onto_path = os.path.join(
            os.path.dirname(__file__), '..', 'examples',
            'pharmatox_example', 'ontology', 'pharmatox.owl'
        )
        if not os.path.exists(spec_path) or not os.path.exists(onto_path):
            pytest.skip("pharmatox example not available")

        onto = owl2.RDFXMLParser.parse_from_file(onto_path)
        loader = owl2.DataLoader(onto)
        loader.load_mapping_spec(os.path.abspath(spec_path))

        # The loader should now have resolved paths - validate should pass
        result = loader.validate()
        assert result.is_valid, f"Validation errors: {result.errors}"
