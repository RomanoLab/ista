"""
Tests for OWL2 parser bindings.

Tests all parser classes to ensure Python bindings are working correctly.
"""

import pytest

from ista import owl2


class TestRDFXMLParser:
    """Tests for RDFXMLParser."""

    def test_parser_exists(self):
        """Test that RDFXMLParser class exists."""
        assert hasattr(owl2, "RDFXMLParser")

    def test_parse_method_exists(self):
        """Test that parse method exists."""
        assert hasattr(owl2.RDFXMLParser, "parse")

    def test_parse_from_file_method_exists(self):
        """Test that parse_from_file method exists."""
        assert hasattr(owl2.RDFXMLParser, "parse_from_file")

    def test_parse_empty_returns_ontology(self):
        """Test that parsing empty string returns an Ontology."""
        # Note: May throw exception for invalid RDF/XML, but should return Ontology type
        try:
            result = owl2.RDFXMLParser.parse("")
            assert isinstance(result, owl2.Ontology)
        except owl2.RDFXMLParseException:
            # Expected for invalid XML
            pass


class TestTurtleParser:
    """Tests for TurtleParser (stub implementation)."""

    def test_parser_exists(self):
        """Test that TurtleParser class exists."""
        assert hasattr(owl2, "TurtleParser")

    def test_parse_method_exists(self):
        """Test that parse method exists."""
        assert hasattr(owl2.TurtleParser, "parse")

    def test_parse_from_file_method_exists(self):
        """Test that parse_from_file method exists."""
        assert hasattr(owl2.TurtleParser, "parse_from_file")

    def test_parse_returns_ontology(self):
        """Test that parsing returns an Ontology (currently empty stub)."""
        result = owl2.TurtleParser.parse("")
        assert isinstance(result, owl2.Ontology)
        # Stub implementation returns empty ontology
        assert result.get_axiom_count() == 0

    def test_exception_type_exists(self):
        """Test that TurtleParseException exists."""
        assert hasattr(owl2, "TurtleParseException")


class TestFunctionalParser:
    """Tests for FunctionalParser (stub implementation)."""

    def test_parser_exists(self):
        """Test that FunctionalParser class exists."""
        assert hasattr(owl2, "FunctionalParser")

    def test_parse_method_exists(self):
        """Test that parse method exists."""
        assert hasattr(owl2.FunctionalParser, "parse")

    def test_parse_from_file_method_exists(self):
        """Test that parse_from_file method exists."""
        assert hasattr(owl2.FunctionalParser, "parse_from_file")

    def test_parse_returns_ontology(self):
        """Test that parsing returns an Ontology (currently empty stub)."""
        result = owl2.FunctionalParser.parse("")
        assert isinstance(result, owl2.Ontology)
        # Stub implementation returns empty ontology
        assert result.get_axiom_count() == 0

    def test_exception_type_exists(self):
        """Test that FunctionalParseException exists."""
        assert hasattr(owl2, "FunctionalParseException")


class TestManchesterParser:
    """Tests for ManchesterParser (stub implementation)."""

    def test_parser_exists(self):
        """Test that ManchesterParser class exists."""
        assert hasattr(owl2, "ManchesterParser")

    def test_parse_method_exists(self):
        """Test that parse method exists."""
        assert hasattr(owl2.ManchesterParser, "parse")

    def test_parse_from_file_method_exists(self):
        """Test that parse_from_file method exists."""
        assert hasattr(owl2.ManchesterParser, "parse_from_file")

    def test_parse_returns_ontology(self):
        """Test that parsing returns an Ontology (currently empty stub)."""
        result = owl2.ManchesterParser.parse("")
        assert isinstance(result, owl2.Ontology)
        # Stub implementation returns empty ontology
        assert result.get_axiom_count() == 0

    def test_exception_type_exists(self):
        """Test that ManchesterParseException exists."""
        assert hasattr(owl2, "ManchesterParseException")


class TestOWLXMLParser:
    """Tests for OWLXMLParser (stub implementation)."""

    def test_parser_exists(self):
        """Test that OWLXMLParser class exists."""
        assert hasattr(owl2, "OWLXMLParser")

    def test_parse_method_exists(self):
        """Test that parse method exists."""
        assert hasattr(owl2.OWLXMLParser, "parse")

    def test_parse_from_file_method_exists(self):
        """Test that parse_from_file method exists."""
        assert hasattr(owl2.OWLXMLParser, "parse_from_file")

    def test_parse_returns_ontology(self):
        """Test that parsing returns an Ontology (currently empty stub)."""
        result = owl2.OWLXMLParser.parse("")
        assert isinstance(result, owl2.Ontology)
        # Stub implementation returns empty ontology
        assert result.get_axiom_count() == 0

    def test_exception_type_exists(self):
        """Test that OWLXMLParseException exists."""
        assert hasattr(owl2, "OWLXMLParseException")


class TestCSVParser:
    """Tests for CSVParser."""

    def test_parser_exists(self):
        """Test that CSVParser class exists."""
        assert hasattr(owl2, "CSVParser")

    def test_config_classes_exist(self):
        """Test that configuration classes exist."""
        assert hasattr(owl2, "NodeTypeConfig")
        assert hasattr(owl2, "RelationshipTypeConfig")

    def test_csv_parser_instantiation(self):
        """Test that CSVParser can be instantiated."""
        onto = owl2.Ontology()
        parser = owl2.CSVParser(onto, "http://example.org/")
        assert parser is not None

    def test_node_type_config_instantiation(self):
        """Test that NodeTypeConfig can be instantiated."""
        config = owl2.NodeTypeConfig()
        assert config is not None
        # Test setting attributes
        config.iri_column_name = "id"
        config.has_headers = True
        assert config.iri_column_name == "id"
        assert config.has_headers == True

    def test_relationship_type_config_instantiation(self):
        """Test that RelationshipTypeConfig can be instantiated."""
        config = owl2.RelationshipTypeConfig()
        assert config is not None
        # Test setting attributes
        config.subject_column_name = "subject"
        config.object_column_name = "object"
        config.has_headers = True
        assert config.subject_column_name == "subject"
        assert config.object_column_name == "object"
        assert config.has_headers == True

    def test_exception_type_exists(self):
        """Test that CSVParseException exists."""
        assert hasattr(owl2, "CSVParseException")


class TestParserExceptions:
    """Tests for parser exception types."""

    def test_all_exceptions_exist(self):
        """Test that all parser exception types are accessible."""
        exceptions = [
            "RDFXMLParseException",
            "TurtleParseException",
            "FunctionalParseException",
            "ManchesterParseException",
            "OWLXMLParseException",
            "CSVParseException",
        ]
        for exc_name in exceptions:
            assert hasattr(owl2, exc_name), f"Missing exception: {exc_name}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
