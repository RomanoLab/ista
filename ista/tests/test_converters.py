"""
Tests for ista.converters module.

These tests cover:
- ConversionOptions and ConversionStrategy
- IRI manipulation utilities
- Base converter functionality
"""

import pytest
from unittest.mock import Mock, MagicMock, patch


def _has_networkx():
    """Check if NetworkX is available."""
    try:
        import networkx

        return True
    except ImportError:
        return False


def _has_igraph():
    """Check if igraph is available."""
    try:
        import igraph

        return True
    except ImportError:
        return False


class TestConversionStrategy:
    """Tests for ConversionStrategy enum."""

    def test_strategy_values(self):
        """Test that all strategy values are defined."""
        from ista.converters.ontology_to_graph import ConversionStrategy

        assert ConversionStrategy.INDIVIDUALS_ONLY.value == "individuals_only"
        assert ConversionStrategy.INCLUDE_CLASSES.value == "include_classes"
        assert ConversionStrategy.INCLUDE_PROPERTIES.value == "include_properties"

    def test_strategy_iteration(self):
        """Test that strategies can be iterated."""
        from ista.converters.ontology_to_graph import ConversionStrategy

        strategies = list(ConversionStrategy)
        assert len(strategies) == 3


class TestConversionOptions:
    """Tests for ConversionOptions dataclass."""

    def test_default_options(self):
        """Test default option values."""
        from ista.converters.ontology_to_graph import (
            ConversionOptions,
            ConversionStrategy,
        )

        opts = ConversionOptions()
        assert opts.strategy == ConversionStrategy.INDIVIDUALS_ONLY
        assert opts.include_data_properties is True
        assert opts.include_annotations is False
        assert opts.filter_classes is None
        assert opts.include_inferred is False
        assert opts.simplify_iris is True
        assert opts.preserve_namespaces is False

    def test_custom_options(self):
        """Test custom option values."""
        from ista.converters.ontology_to_graph import (
            ConversionOptions,
            ConversionStrategy,
        )

        opts = ConversionOptions(
            strategy=ConversionStrategy.INCLUDE_CLASSES,
            include_data_properties=False,
            include_annotations=True,
            filter_classes={"http://example.org/Class1"},
            data_property_prefix="prop_",
            simplify_iris=False,
        )

        assert opts.strategy == ConversionStrategy.INCLUDE_CLASSES
        assert opts.include_data_properties is False
        assert opts.include_annotations is True
        assert "http://example.org/Class1" in opts.filter_classes
        assert opts.data_property_prefix == "prop_"
        assert opts.simplify_iris is False


class TestConverterUtilities:
    """Tests for converter utility methods."""

    @pytest.fixture
    def mock_converter(self):
        """Create a mock converter for testing utility methods."""
        from ista.converters.ontology_to_graph import (
            OntologyToGraphConverter,
            ConversionOptions,
        )

        # Create a concrete subclass for testing
        class TestConverter(OntologyToGraphConverter):
            def convert(self):
                return None

            def reverse_convert(self, graph, ontology_iri):
                return None

        # Mock the HAS_OWL2 check and owl2 module
        with patch("ista.converters.ontology_to_graph.HAS_OWL2", True):
            mock_ontology = MagicMock()
            mock_ontology.axioms = []
            converter = TestConverter(mock_ontology)
            yield converter

    def test_simplify_iri_with_hash(self, mock_converter):
        """Test IRI simplification with hash fragment."""
        result = mock_converter._simplify_iri("http://example.org/onto#Person")
        assert result == "Person"

    def test_simplify_iri_with_slash(self, mock_converter):
        """Test IRI simplification with slash."""
        result = mock_converter._simplify_iri("http://example.org/onto/Person")
        assert result == "Person"

    def test_simplify_iri_no_delimiter(self, mock_converter):
        """Test IRI simplification with no delimiter."""
        result = mock_converter._simplify_iri("Person")
        assert result == "Person"

    def test_simplify_iri_disabled(self, mock_converter):
        """Test IRI simplification when disabled."""
        mock_converter.options.simplify_iris = False
        full_iri = "http://example.org/onto#Person"
        result = mock_converter._simplify_iri(full_iri)
        assert result == full_iri

    def test_get_namespace_with_hash(self, mock_converter):
        """Test namespace extraction with hash."""
        result = mock_converter._get_namespace("http://example.org/onto#Person")
        assert result == "http://example.org/onto#"

    def test_get_namespace_with_slash(self, mock_converter):
        """Test namespace extraction with slash."""
        result = mock_converter._get_namespace("http://example.org/onto/Person")
        assert result == "http://example.org/onto/"

    def test_get_namespace_no_delimiter(self, mock_converter):
        """Test namespace extraction with no delimiter."""
        result = mock_converter._get_namespace("Person")
        assert result == "Person"


class TestNetworkXConverter:
    """Tests for NetworkXConverter."""

    def test_import_error_without_networkx(self):
        """Test that ImportError is raised when NetworkX is not available."""
        with patch("ista.converters.networkx_converter.HAS_NETWORKX", False):
            with patch("ista.converters.networkx_converter.HAS_OWL2", True):
                from ista.converters.networkx_converter import NetworkXConverter

                mock_ontology = MagicMock()
                mock_ontology.axioms = []

                converter = NetworkXConverter(mock_ontology)
                with pytest.raises(ImportError) as exc_info:
                    converter.convert()

                assert "networkx" in str(exc_info.value).lower()

    @pytest.mark.skipif(not _has_networkx(), reason="NetworkX not installed")
    def test_convert_empty_ontology(self):
        """Test converting an empty ontology."""
        with patch("ista.converters.networkx_converter.HAS_OWL2", True):
            from ista.converters.networkx_converter import NetworkXConverter

            mock_ontology = MagicMock()
            mock_ontology.axioms = []

            converter = NetworkXConverter(mock_ontology)
            graph = converter.convert()

            assert len(graph.nodes()) == 0
            assert len(graph.edges()) == 0


class TestIGraphConverter:
    """Tests for IGraphConverter."""

    def test_import_error_without_igraph(self):
        """Test that ImportError is raised when igraph is not available."""
        with patch("ista.converters.igraph_converter.HAS_IGRAPH", False):
            with patch("ista.converters.igraph_converter.HAS_OWL2", True):
                from ista.converters.igraph_converter import IGraphConverter

                mock_ontology = MagicMock()
                mock_ontology.axioms = []

                converter = IGraphConverter(mock_ontology)
                with pytest.raises(ImportError) as exc_info:
                    converter.convert()

                assert "igraph" in str(exc_info.value).lower()


class TestIstaGraphConverter:
    """Tests for IstaGraphConverter."""

    def test_convert_empty_ontology(self):
        """Test converting an empty ontology to ista.graph."""
        with patch("ista.converters.ista_graph_converter.HAS_OWL2", True):
            from ista.converters.ista_graph_converter import IstaGraphConverter

            mock_ontology = MagicMock()
            mock_ontology.axioms = []

            converter = IstaGraphConverter(mock_ontology)
            graph = converter.convert()

            # ista.graph.Graph uses nodes and edges lists
            assert len(graph.nodes) == 0
            assert len(graph.edges) == 0


class TestModuleExports:
    """Tests for module exports and imports."""

    def test_converters_init_exports(self):
        """Test that main classes are exported from converters package."""
        from ista.converters import (
            ConversionOptions,
            ConversionStrategy,
            OntologyToGraphConverter,
        )

        assert ConversionOptions is not None
        assert ConversionStrategy is not None
        assert OntologyToGraphConverter is not None

    def test_networkx_converter_import(self):
        """Test NetworkXConverter can be imported."""
        from ista.converters.networkx_converter import NetworkXConverter

        assert NetworkXConverter is not None

    def test_igraph_converter_import(self):
        """Test IGraphConverter can be imported."""
        from ista.converters.igraph_converter import IGraphConverter

        assert IGraphConverter is not None

    def test_ista_graph_converter_import(self):
        """Test IstaGraphConverter can be imported."""
        from ista.converters.ista_graph_converter import IstaGraphConverter

        assert IstaGraphConverter is not None
