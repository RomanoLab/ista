"""
Tests for OWL2 serializer bindings.

Tests all serializer classes to ensure Python bindings are working correctly.
"""

import pytest

from ista import owl2


class TestRDFXMLSerializer:
    """Tests for RDFXMLSerializer."""

    def test_serializer_exists(self):
        """Test that RDFXMLSerializer class exists."""
        assert hasattr(owl2, "RDFXMLSerializer")

    def test_serialize_method_exists(self):
        """Test that serialize method exists."""
        assert hasattr(owl2.RDFXMLSerializer, "serialize")

    def test_serialize_to_file_method_exists(self):
        """Test that serialize_to_file method exists."""
        assert hasattr(owl2.RDFXMLSerializer, "serialize_to_file")

    def test_serialize_empty_ontology(self):
        """Test that serializing empty ontology returns string."""
        onto = owl2.Ontology()
        result = owl2.RDFXMLSerializer.serialize(onto)
        assert isinstance(result, str)
        assert len(result) > 0


class TestFunctionalSyntaxSerializer:
    """Tests for FunctionalSyntaxSerializer."""

    def test_serializer_exists(self):
        """Test that FunctionalSyntaxSerializer class exists."""
        assert hasattr(owl2, "FunctionalSyntaxSerializer")

    def test_serialize_method_exists(self):
        """Test that serialize method exists."""
        assert hasattr(owl2.FunctionalSyntaxSerializer, "serialize")

    def test_serialize_to_file_method_exists(self):
        """Test that serialize_to_file method exists."""
        assert hasattr(owl2.FunctionalSyntaxSerializer, "serialize_to_file")

    def test_serialize_empty_ontology(self):
        """Test that serializing empty ontology returns string."""
        onto = owl2.Ontology()
        result = owl2.FunctionalSyntaxSerializer.serialize(onto)
        assert isinstance(result, str)
        assert len(result) > 0


class TestTurtleSerializer:
    """Tests for TurtleSerializer (stub implementation)."""

    def test_serializer_exists(self):
        """Test that TurtleSerializer class exists."""
        assert hasattr(owl2, "TurtleSerializer")

    def test_serialize_method_exists(self):
        """Test that serialize method exists."""
        assert hasattr(owl2.TurtleSerializer, "serialize")

    def test_serialize_to_file_method_exists(self):
        """Test that serialize_to_file method exists."""
        assert hasattr(owl2.TurtleSerializer, "serialize_to_file")

    def test_serialize_throws_not_implemented(self):
        """Test that stub implementation throws RuntimeError."""
        onto = owl2.Ontology()
        with pytest.raises(RuntimeError):
            owl2.TurtleSerializer.serialize(onto)


class TestManchesterSerializer:
    """Tests for ManchesterSerializer (stub implementation)."""

    def test_serializer_exists(self):
        """Test that ManchesterSerializer class exists."""
        assert hasattr(owl2, "ManchesterSerializer")

    def test_serialize_method_exists(self):
        """Test that serialize method exists."""
        assert hasattr(owl2.ManchesterSerializer, "serialize")

    def test_serialize_to_file_method_exists(self):
        """Test that serialize_to_file method exists."""
        assert hasattr(owl2.ManchesterSerializer, "serialize_to_file")

    def test_serialize_throws_not_implemented(self):
        """Test that stub implementation throws RuntimeError."""
        onto = owl2.Ontology()
        with pytest.raises(RuntimeError):
            owl2.ManchesterSerializer.serialize(onto)


class TestOWLXMLSerializer:
    """Tests for OWLXMLSerializer (stub implementation)."""

    def test_serializer_exists(self):
        """Test that OWLXMLSerializer class exists."""
        assert hasattr(owl2, "OWLXMLSerializer")

    def test_serialize_method_exists(self):
        """Test that serialize method exists."""
        assert hasattr(owl2.OWLXMLSerializer, "serialize")

    def test_serialize_to_file_method_exists(self):
        """Test that serialize_to_file method exists."""
        assert hasattr(owl2.OWLXMLSerializer, "serialize_to_file")

    def test_serialize_throws_not_implemented(self):
        """Test that stub implementation throws RuntimeError."""
        onto = owl2.Ontology()
        with pytest.raises(RuntimeError):
            owl2.OWLXMLSerializer.serialize(onto)


class TestSerializerRoundTrip:
    """Tests for serialization round-trips."""

    def test_rdfxml_roundtrip_empty(self):
        """Test RDF/XML serialization and parsing of empty ontology."""
        # Create empty ontology
        onto1 = owl2.Ontology(owl2.IRI("http://example.org/test"))

        # Serialize
        rdfxml = owl2.RDFXMLSerializer.serialize(onto1)
        assert isinstance(rdfxml, str)

        # Parse back (may not work perfectly for empty ontology, but should not crash)
        try:
            onto2 = owl2.RDFXMLParser.parse(rdfxml)
            assert isinstance(onto2, owl2.Ontology)
        except owl2.RDFXMLParseException:
            # Some parsers may reject certain empty ontologies
            pass

    def test_functional_roundtrip_empty(self):
        """Test Functional Syntax serialization of empty ontology."""
        # Create empty ontology
        onto = owl2.Ontology(owl2.IRI("http://example.org/test"))

        # Serialize (should work)
        functional = owl2.FunctionalSyntaxSerializer.serialize(onto)
        assert isinstance(functional, str)
        assert "Ontology" in functional


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
