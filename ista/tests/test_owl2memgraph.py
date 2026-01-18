"""
Tests for the owl2memgraph CLI tool.

These tests cover:
- CLI argument parsing
- Format detection from file extensions
- Ontology file parsing (without database connection)
- Integration tests with live Memgraph (skipped if not available)
"""

import os
import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from ista.owl2memgraph import (
    OWL2MemgraphLoader,
    RDFMemgraphLoader,
    create_parser,
    main,
    detect_format,
    FORMAT_EXTENSIONS,
    EXTENSION_TO_FORMAT,
)


# Path to test fixtures
TESTS_DIR = Path(__file__).parent.parent.parent / "tests"
SIMPLE_RDF = TESTS_DIR / "test_family_simple.rdf"


class TestFormatDetection:
    """Tests for format detection from file extensions."""

    def test_detect_rdfxml_formats(self):
        """Test detection of RDF/XML format."""
        assert detect_format("ontology.rdf") == "rdfxml"
        assert detect_format("ontology.owl") == "rdfxml"
        assert detect_format("ontology.xml") == "rdfxml"

    def test_detect_turtle_format(self):
        """Test detection of Turtle format."""
        assert detect_format("ontology.ttl") == "turtle"

    def test_detect_functional_format(self):
        """Test detection of Functional Syntax format."""
        assert detect_format("ontology.ofn") == "functional"
        assert detect_format("ontology.fss") == "functional"

    def test_detect_manchester_format(self):
        """Test detection of Manchester Syntax format."""
        assert detect_format("ontology.omn") == "manchester"

    def test_detect_owlxml_format(self):
        """Test detection of OWL/XML format."""
        assert detect_format("ontology.owx") == "owlxml"

    def test_detect_unknown_format(self):
        """Test that unknown extensions return None."""
        assert detect_format("ontology.txt") is None
        assert detect_format("ontology.json") is None
        assert detect_format("ontology") is None

    def test_detect_case_insensitive(self):
        """Test that detection is case-insensitive."""
        assert detect_format("ontology.RDF") == "rdfxml"
        assert detect_format("ontology.TTL") == "turtle"
        assert detect_format("ontology.OWL") == "rdfxml"

    def test_format_extensions_complete(self):
        """Test that all formats have extensions defined."""
        expected_formats = {"rdfxml", "turtle", "functional", "manchester", "owlxml"}
        assert set(FORMAT_EXTENSIONS.keys()) == expected_formats

    def test_extension_to_format_mapping(self):
        """Test the reverse mapping is consistent."""
        for fmt, exts in FORMAT_EXTENSIONS.items():
            for ext in exts:
                assert EXTENSION_TO_FORMAT[ext] == fmt


class TestArgumentParsing:
    """Tests for CLI argument parsing."""

    def test_create_parser(self):
        """Test that parser is created successfully."""
        parser = create_parser()
        assert parser.prog == "owl2memgraph"

    def test_required_input_argument(self):
        """Test that input argument is required."""
        parser = create_parser()
        with pytest.raises(SystemExit):
            parser.parse_args([])

    def test_input_argument(self):
        """Test input argument parsing."""
        parser = create_parser()
        args = parser.parse_args(["-i", "test.rdf"])
        assert args.input == "test.rdf"

    def test_format_argument(self):
        """Test format argument parsing."""
        parser = create_parser()
        args = parser.parse_args(["-i", "test.owl", "--format", "turtle"])
        assert args.format == "turtle"

        args = parser.parse_args(["-i", "test.owl", "-f", "functional"])
        assert args.format == "functional"

    def test_format_choices(self):
        """Test that only valid formats are accepted."""
        parser = create_parser()
        with pytest.raises(SystemExit):
            parser.parse_args(["-i", "test.owl", "--format", "invalid"])

    def test_connection_arguments(self):
        """Test connection argument parsing."""
        parser = create_parser()
        args = parser.parse_args([
            "-i", "test.rdf",
            "--uri", "bolt://custom:7687",
            "--username", "admin",
            "--password", "secret"
        ])
        assert args.uri == "bolt://custom:7687"
        assert args.username == "admin"
        assert args.password == "secret"

    def test_default_connection_values(self):
        """Test default connection values."""
        parser = create_parser()
        args = parser.parse_args(["-i", "test.rdf"])
        assert args.uri == "bolt://localhost:7687"
        assert args.username == ""
        assert args.password == ""

    def test_loading_options(self):
        """Test loading option flags."""
        parser = create_parser()
        args = parser.parse_args([
            "-i", "test.rdf",
            "--no-clear",
            "--no-indexes",
            "--no-cleanup",
            "--batch-size", "500"
        ])
        assert args.no_clear is True
        assert args.no_indexes is True
        assert args.no_cleanup is True
        assert args.batch_size == 500

    def test_output_options(self):
        """Test output option flags."""
        parser = create_parser()
        args = parser.parse_args(["-i", "test.rdf", "-q"])
        assert args.quiet is True

        args = parser.parse_args(["-i", "test.rdf", "-v"])
        assert args.verbose is True


class TestLoaderUtilities:
    """Tests for loader utility methods (no database required)."""

    @pytest.fixture
    def loader(self):
        """Create a loader instance without connecting."""
        with patch('ista.owl2memgraph.HAS_NEO4J_DRIVER', True):
            with patch('ista.owl2memgraph.HAS_OWL2', True):
                with patch('ista.owl2memgraph.GraphDatabase'):
                    loader = OWL2MemgraphLoader()
                    yield loader

    def test_extract_fragment_with_hash(self, loader):
        """Test IRI fragment extraction with hash."""
        assert loader._extract_fragment("http://example.org/onto#Person") == "Person"

    def test_extract_fragment_with_slash(self, loader):
        """Test IRI fragment extraction with slash."""
        assert loader._extract_fragment("http://example.org/onto/Person") == "Person"

    def test_extract_fragment_simple(self, loader):
        """Test IRI fragment extraction with no delimiter."""
        assert loader._extract_fragment("Person") == "Person"

    def test_sanitize_label_valid(self, loader):
        """Test label sanitization with valid input."""
        assert loader._sanitize_label("Person") == "Person"
        assert loader._sanitize_label("DrugTarget") == "DrugTarget"

    def test_sanitize_label_special_chars(self, loader):
        """Test label sanitization removes special characters."""
        assert loader._sanitize_label("Drug-Target") == "Drug_Target"
        assert loader._sanitize_label("has value") == "has_value"

    def test_sanitize_label_starts_with_number(self, loader):
        """Test label sanitization when starting with number."""
        assert loader._sanitize_label("123Class").startswith("N_")

    def test_sanitize_label_empty(self, loader):
        """Test label sanitization with empty input."""
        assert loader._sanitize_label("") == "Node"


class TestMainFunction:
    """Tests for the main CLI entry point."""

    def test_main_file_not_found(self):
        """Test main returns error for non-existent file."""
        result = main(["-i", "nonexistent_file.rdf"])
        assert result == 1

    def test_main_not_a_file(self, tmp_path):
        """Test main returns error for directory."""
        result = main(["-i", str(tmp_path)])
        assert result == 1

    def test_main_unknown_format(self, tmp_path):
        """Test main returns error for unknown file extension."""
        unknown_file = tmp_path / "ontology.xyz"
        unknown_file.write_text("content")
        result = main(["-i", str(unknown_file)])
        assert result == 1

    @pytest.mark.skipif(not SIMPLE_RDF.exists(), reason="Test RDF file not found")
    def test_main_connection_failure(self):
        """Test main handles connection failure gracefully."""
        with patch('ista.owl2memgraph.OWL2MemgraphLoader') as MockLoader:
            mock_instance = MagicMock()
            mock_instance.test_connection.return_value = False
            mock_instance.__enter__ = Mock(return_value=mock_instance)
            mock_instance.__exit__ = Mock(return_value=False)
            MockLoader.return_value = mock_instance

            result = main(["-i", str(SIMPLE_RDF), "-q"])
            assert result == 1


class TestProgressCallback:
    """Tests for progress callback functionality."""

    def test_progress_callback_invoked(self):
        """Test that progress callback is invoked."""
        progress_calls = []

        def callback(current, total, message):
            progress_calls.append((current, total, message))

        with patch('ista.owl2memgraph.HAS_NEO4J_DRIVER', True):
            with patch('ista.owl2memgraph.HAS_OWL2', True):
                with patch('ista.owl2memgraph.GraphDatabase'):
                    loader = OWL2MemgraphLoader(progress_callback=callback)
                    loader._report_progress(1, 10, "Test message")

        assert len(progress_calls) == 1
        assert progress_calls[0] == (1, 10, "Test message")


class TestLoaderContextManager:
    """Tests for loader context manager behavior."""

    def test_context_manager_connects(self):
        """Test that context manager establishes connection."""
        with patch('ista.owl2memgraph.HAS_NEO4J_DRIVER', True):
            with patch('ista.owl2memgraph.HAS_OWL2', True):
                mock_driver = MagicMock()
                with patch('ista.owl2memgraph.GraphDatabase') as MockGD:
                    MockGD.driver.return_value = mock_driver

                    with OWL2MemgraphLoader() as loader:
                        assert loader.driver is mock_driver

                    MockGD.driver.assert_called_once()

    def test_context_manager_closes(self):
        """Test that context manager closes connection on exit."""
        with patch('ista.owl2memgraph.HAS_NEO4J_DRIVER', True):
            with patch('ista.owl2memgraph.HAS_OWL2', True):
                mock_driver = MagicMock()
                with patch('ista.owl2memgraph.GraphDatabase') as MockGD:
                    MockGD.driver.return_value = mock_driver

                    with OWL2MemgraphLoader() as loader:
                        pass

                    mock_driver.close.assert_called_once()

    def test_context_manager_closes_on_exception(self):
        """Test that context manager closes connection on exception."""
        with patch('ista.owl2memgraph.HAS_NEO4J_DRIVER', True):
            with patch('ista.owl2memgraph.HAS_OWL2', True):
                mock_driver = MagicMock()
                with patch('ista.owl2memgraph.GraphDatabase') as MockGD:
                    MockGD.driver.return_value = mock_driver

                    try:
                        with OWL2MemgraphLoader() as loader:
                            raise ValueError("Test error")
                    except ValueError:
                        pass

                    mock_driver.close.assert_called_once()


class TestImportErrors:
    """Tests for handling missing dependencies."""

    def test_import_error_without_neo4j_driver(self):
        """Test that ImportError is raised when neo4j is not installed."""
        with patch('ista.owl2memgraph.HAS_NEO4J_DRIVER', False):
            with patch('ista.owl2memgraph.HAS_OWL2', True):
                with pytest.raises(ImportError) as exc_info:
                    OWL2MemgraphLoader()

                assert "neo4j" in str(exc_info.value).lower()

    def test_import_error_without_owl2(self):
        """Test that ImportError is raised when owl2 bindings are not available."""
        with patch('ista.owl2memgraph.HAS_NEO4J_DRIVER', True):
            with patch('ista.owl2memgraph.HAS_OWL2', False):
                with pytest.raises(ImportError) as exc_info:
                    OWL2MemgraphLoader()

                assert "owl2" in str(exc_info.value).lower()


class TestBackwardsCompatibility:
    """Tests for backwards compatibility aliases."""

    def test_rdfmemgraphloader_alias(self):
        """Test that RDFMemgraphLoader is an alias for OWL2MemgraphLoader."""
        assert RDFMemgraphLoader is OWL2MemgraphLoader
