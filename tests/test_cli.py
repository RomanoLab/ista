"""Tests for CLI entry points (ista_populate, owl2memgraph).

Covers:
- Argument parsing for ista_populate (valid args, missing required args)
- End-to-end: run populate main() with a YAML + CSV, verify output
- Output format selection (rdfxml, turtle, functional)
- owl2memgraph argument parser creation
"""

import os
import textwrap

import pytest
from ista import owl2

# Skip the entire module if C++ bindings are not available
pytestmark = pytest.mark.skipif(
    not owl2.is_available(),
    reason="C++ OWL2 bindings not available",
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def simple_csv(tmp_path):
    """Create a minimal CSV data file with drug records."""
    f = tmp_path / "drugs.csv"
    f.write_text(
        "drug_id,drug_name\n"
        "DB001,Aspirin\n"
        "DB002,Ibuprofen\n"
    )
    return f


@pytest.fixture
def simple_mapping(tmp_path, simple_csv):
    """Create a minimal YAML mapping that reads from simple_csv."""
    f = tmp_path / "mapping.yaml"
    f.write_text(textwrap.dedent(f"""\
        version: "1.0"
        base_iri: "http://example.org/test#"

        sources:
          drugs_csv:
            type: csv
            path: "{simple_csv.name}"
            delimiter: ","
            has_headers: true

        entity_types:
          Drug:
            primary:
              source: drugs_csv
              iri_column: drug_id
              properties:
                - {{ column: drug_id, property: drugId }}
                - {{ column: drug_name, property: drugName }}
    """))
    return f


# ---------------------------------------------------------------------------
# ista_populate — argument parsing
# ---------------------------------------------------------------------------

class TestPopulateArgParsing:
    """Tests for ista_populate argument parsing."""

    def test_create_parser(self):
        from ista.populate import create_parser

        parser = create_parser()
        assert parser.prog == "ista_populate"

    def test_valid_args(self, simple_mapping, tmp_path):
        from ista.populate import create_parser

        parser = create_parser()
        out = tmp_path / "out.owl"
        parsed = parser.parse_args(["-m", str(simple_mapping), "-o", str(out)])
        assert parsed.mapping == str(simple_mapping)
        assert parsed.output == str(out)
        assert parsed.format is None
        assert parsed.iri is None
        assert not parsed.quiet
        assert not parsed.verbose

    def test_all_flags(self, simple_mapping, tmp_path):
        from ista.populate import create_parser

        parser = create_parser()
        out = tmp_path / "out.ttl"
        parsed = parser.parse_args([
            "-m", str(simple_mapping),
            "-o", str(out),
            "-f", "turtle",
            "--iri", "http://example.org/custom",
            "-q",
        ])
        assert parsed.format == "turtle"
        assert parsed.iri == "http://example.org/custom"
        assert parsed.quiet

    def test_missing_mapping_arg(self):
        from ista.populate import create_parser

        parser = create_parser()
        with pytest.raises(SystemExit):
            parser.parse_args(["-o", "out.owl"])

    def test_missing_output_arg(self, simple_mapping):
        from ista.populate import create_parser

        parser = create_parser()
        with pytest.raises(SystemExit):
            parser.parse_args(["-m", str(simple_mapping)])

    def test_invalid_format_arg(self, simple_mapping, tmp_path):
        from ista.populate import create_parser

        parser = create_parser()
        with pytest.raises(SystemExit):
            parser.parse_args([
                "-m", str(simple_mapping),
                "-o", str(tmp_path / "out.owl"),
                "-f", "json",
            ])

    def test_quiet_verbose_mutually_exclusive(self, simple_mapping, tmp_path):
        from ista.populate import create_parser

        parser = create_parser()
        with pytest.raises(SystemExit):
            parser.parse_args([
                "-m", str(simple_mapping),
                "-o", str(tmp_path / "out.owl"),
                "-q", "-v",
            ])


# ---------------------------------------------------------------------------
# ista_populate — format detection
# ---------------------------------------------------------------------------

class TestPopulateFormatDetection:
    """Tests for output format auto-detection."""

    def test_detect_rdfxml_owl(self):
        from ista.populate import detect_output_format

        assert detect_output_format("ontology.owl") == "rdfxml"

    def test_detect_rdfxml_rdf(self):
        from ista.populate import detect_output_format

        assert detect_output_format("ontology.rdf") == "rdfxml"

    def test_detect_rdfxml_xml(self):
        from ista.populate import detect_output_format

        assert detect_output_format("ontology.xml") == "rdfxml"

    def test_detect_turtle(self):
        from ista.populate import detect_output_format

        assert detect_output_format("ontology.ttl") == "turtle"

    def test_detect_functional(self):
        from ista.populate import detect_output_format

        assert detect_output_format("ontology.ofn") == "functional"

    def test_detect_unknown(self):
        from ista.populate import detect_output_format

        assert detect_output_format("ontology.json") is None


# ---------------------------------------------------------------------------
# ista_populate — end-to-end
# ---------------------------------------------------------------------------

class TestPopulateEndToEnd:
    """End-to-end tests: run main() and verify output files."""

    def test_rdfxml_output(self, simple_mapping, tmp_path):
        from ista.populate import main

        out = tmp_path / "output.owl"
        rc = main(["-m", str(simple_mapping), "-o", str(out)])
        assert rc == 0
        assert out.exists()
        content = out.read_text()
        assert "rdf:RDF" in content or "Ontology" in content
        # Verify entities made it into the output
        assert "DB001" in content
        assert "DB002" in content

    def test_turtle_output(self, simple_mapping, tmp_path):
        from ista.populate import main

        out = tmp_path / "output.ttl"
        rc = main(["-m", str(simple_mapping), "-o", str(out), "-f", "turtle"])
        assert rc == 0
        assert out.exists()
        content = out.read_text()
        assert "DB001" in content
        assert "DB002" in content

    def test_functional_output(self, simple_mapping, tmp_path):
        from ista.populate import main

        out = tmp_path / "output.ofn"
        rc = main(["-m", str(simple_mapping), "-o", str(out), "-f", "functional"])
        assert rc == 0
        assert out.exists()
        content = out.read_text()
        assert "DB001" in content

    def test_format_autodetect_from_extension(self, simple_mapping, tmp_path):
        from ista.populate import main

        out = tmp_path / "output.ttl"
        # No -f flag; should auto-detect turtle from .ttl extension
        rc = main(["-m", str(simple_mapping), "-o", str(out)])
        assert rc == 0
        assert out.exists()

    def test_custom_iri(self, simple_mapping, tmp_path):
        from ista.populate import main

        out = tmp_path / "output.owl"
        custom_iri = "http://example.org/custom_ontology"
        rc = main([
            "-m", str(simple_mapping),
            "-o", str(out),
            "--iri", custom_iri,
        ])
        assert rc == 0
        content = out.read_text()
        assert custom_iri in content

    def test_quiet_mode(self, simple_mapping, tmp_path, capsys):
        from ista.populate import main

        out = tmp_path / "output.owl"
        rc = main(["-m", str(simple_mapping), "-o", str(out), "-q"])
        assert rc == 0
        captured = capsys.readouterr()
        # In quiet mode, no progress output should appear
        assert "Mapping:" not in captured.out

    def test_missing_mapping_file(self, tmp_path):
        from ista.populate import main

        rc = main([
            "-m", str(tmp_path / "nonexistent.yaml"),
            "-o", str(tmp_path / "out.owl"),
        ])
        assert rc == 1

    def test_unknown_output_extension(self, simple_mapping, tmp_path):
        from ista.populate import main

        rc = main([
            "-m", str(simple_mapping),
            "-o", str(tmp_path / "out.jsonld"),
        ])
        assert rc == 1


# ---------------------------------------------------------------------------
# owl2memgraph — argument parsing
# ---------------------------------------------------------------------------

class TestOwl2MemgraphArgParsing:
    """Tests for owl2memgraph argument parser creation."""

    def test_create_parser(self):
        from ista.owl2memgraph import create_parser

        parser = create_parser()
        assert parser.prog == "owl2memgraph"

    def test_valid_args(self, tmp_path):
        from ista.owl2memgraph import create_parser

        # Create a dummy file so the parser can reference it
        dummy = tmp_path / "test.owl"
        dummy.write_text("<rdf:RDF/>")

        parser = create_parser()
        parsed = parser.parse_args(["-i", str(dummy)])
        assert parsed.input == str(dummy)
        assert parsed.format is None
        assert parsed.uri == "bolt://localhost:7687"
        assert not parsed.quiet
        assert not parsed.verbose

    def test_all_connection_args(self, tmp_path):
        from ista.owl2memgraph import create_parser

        dummy = tmp_path / "test.owl"
        dummy.write_text("<rdf:RDF/>")

        parser = create_parser()
        parsed = parser.parse_args([
            "-i", str(dummy),
            "--uri", "bolt://db.example.com:7687",
            "-u", "admin",
            "-p", "secret",
            "--no-clear",
            "--batch-size", "500",
            "-q",
        ])
        assert parsed.uri == "bolt://db.example.com:7687"
        assert parsed.username == "admin"
        assert parsed.password == "secret"
        assert parsed.no_clear
        assert parsed.batch_size == 500
        assert parsed.quiet

    def test_missing_input_arg(self):
        from ista.owl2memgraph import create_parser

        parser = create_parser()
        with pytest.raises(SystemExit):
            parser.parse_args([])

    def test_format_choices(self, tmp_path):
        from ista.owl2memgraph import create_parser

        dummy = tmp_path / "test.owl"
        dummy.write_text("<rdf:RDF/>")

        parser = create_parser()
        parsed = parser.parse_args(["-i", str(dummy), "-f", "turtle"])
        assert parsed.format == "turtle"

    def test_format_detect(self):
        from ista.owl2memgraph import detect_format

        assert detect_format("ontology.ttl") == "turtle"
        assert detect_format("ontology.owl") == "rdfxml"
        assert detect_format("ontology.ofn") == "functional"
        assert detect_format("ontology.json") is None
