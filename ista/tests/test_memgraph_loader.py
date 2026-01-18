"""
Tests for ista.memgraph_loader module.

These tests cover:
- MemgraphLoader class initialization and connection handling
- Utility methods (label sanitization, IRI extraction)
- Ontology to Memgraph conversion logic
"""

import pytest
from unittest.mock import Mock, MagicMock, patch


class TestMemgraphLoaderInit:
    """Tests for MemgraphLoader initialization."""

    def test_import_error_without_neo4j(self):
        """Test that ImportError is raised when neo4j is not installed."""
        with patch("ista.memgraph_loader.HAS_NEO4J_DRIVER", False):
            from ista.memgraph_loader import MemgraphLoader

            with pytest.raises(ImportError) as exc_info:
                MemgraphLoader()

            assert "neo4j" in str(exc_info.value).lower()

    def test_default_connection_params(self):
        """Test default connection parameters."""
        with patch("ista.memgraph_loader.HAS_NEO4J_DRIVER", True):
            from ista.memgraph_loader import MemgraphLoader

            loader = MemgraphLoader()
            assert loader.uri == "bolt://localhost:7687"
            assert loader.username == ""
            assert loader.password == ""
            assert loader.database == "memgraph"

    def test_custom_connection_params(self):
        """Test custom connection parameters."""
        with patch("ista.memgraph_loader.HAS_NEO4J_DRIVER", True):
            from ista.memgraph_loader import MemgraphLoader

            loader = MemgraphLoader(
                uri="bolt://custom:7687",
                username="admin",
                password="secret",
                database="mydb",
            )
            assert loader.uri == "bolt://custom:7687"
            assert loader.username == "admin"
            assert loader.password == "secret"
            assert loader.database == "mydb"


class TestMemgraphLoaderUtilities:
    """Tests for MemgraphLoader utility methods."""

    @pytest.fixture
    def loader(self):
        """Create a loader instance without connecting."""
        with patch("ista.memgraph_loader.HAS_NEO4J_DRIVER", True):
            from ista.memgraph_loader import MemgraphLoader

            loader = MemgraphLoader()
            yield loader

    def test_sanitize_label_valid(self, loader):
        """Test label sanitization with valid input."""
        assert loader._sanitize_label("Person") == "Person"
        assert loader._sanitize_label("DrugTarget") == "DrugTarget"
        assert loader._sanitize_label("Gene_123") == "Gene_123"

    def test_sanitize_label_special_chars(self, loader):
        """Test label sanitization removes special characters."""
        assert loader._sanitize_label("Drug-Target") == "Drug_Target"
        assert loader._sanitize_label("has value") == "has_value"
        assert loader._sanitize_label("class@type") == "class_type"

    def test_sanitize_label_starts_with_number(self, loader):
        """Test label sanitization when starting with number."""
        result = loader._sanitize_label("123Class")
        assert result.startswith("C_")
        assert "123Class" in result

    def test_sanitize_label_empty(self, loader):
        """Test label sanitization with empty input."""
        assert loader._sanitize_label("") == "Entity"

    def test_extract_local_name_with_hash(self, loader):
        """Test local name extraction with hash."""
        result = loader._extract_local_name("http://example.org/onto#Person")
        assert result == "Person"

    def test_extract_local_name_with_slash(self, loader):
        """Test local name extraction with slash."""
        result = loader._extract_local_name("http://example.org/onto/Person")
        assert result == "Person"

    def test_extract_local_name_no_delimiter(self, loader):
        """Test local name extraction with no delimiter."""
        result = loader._extract_local_name("Person")
        assert result == "Person"


class TestMemgraphLoaderContextManager:
    """Tests for MemgraphLoader context manager behavior."""

    def test_context_manager_connects(self):
        """Test that context manager establishes connection."""
        with patch("ista.memgraph_loader.HAS_NEO4J_DRIVER", True):
            mock_driver = MagicMock()
            with patch("ista.memgraph_loader.GraphDatabase") as MockGD:
                MockGD.driver.return_value = mock_driver

                from ista.memgraph_loader import MemgraphLoader

                with MemgraphLoader() as loader:
                    assert loader.driver is mock_driver

                MockGD.driver.assert_called_once()

    def test_context_manager_closes(self):
        """Test that context manager closes connection on exit."""
        with patch("ista.memgraph_loader.HAS_NEO4J_DRIVER", True):
            mock_driver = MagicMock()
            with patch("ista.memgraph_loader.GraphDatabase") as MockGD:
                MockGD.driver.return_value = mock_driver

                from ista.memgraph_loader import MemgraphLoader

                with MemgraphLoader() as loader:
                    pass

                mock_driver.close.assert_called_once()

    def test_context_manager_closes_on_exception(self):
        """Test that context manager closes connection on exception."""
        with patch("ista.memgraph_loader.HAS_NEO4J_DRIVER", True):
            mock_driver = MagicMock()
            with patch("ista.memgraph_loader.GraphDatabase") as MockGD:
                MockGD.driver.return_value = mock_driver

                from ista.memgraph_loader import MemgraphLoader

                try:
                    with MemgraphLoader() as loader:
                        raise ValueError("Test error")
                except ValueError:
                    pass

                mock_driver.close.assert_called_once()


class TestMemgraphLoaderDatabaseOps:
    """Tests for MemgraphLoader database operations."""

    def test_clear_database(self):
        """Test database clear operation."""
        with patch("ista.memgraph_loader.HAS_NEO4J_DRIVER", True):
            mock_driver = MagicMock()
            mock_session = MagicMock()
            mock_driver.session.return_value.__enter__ = Mock(
                return_value=mock_session
            )
            mock_driver.session.return_value.__exit__ = Mock(return_value=False)

            with patch("ista.memgraph_loader.GraphDatabase") as MockGD:
                MockGD.driver.return_value = mock_driver

                from ista.memgraph_loader import MemgraphLoader

                loader = MemgraphLoader()
                loader.connect()
                loader.clear_database()

                mock_session.run.assert_called_once()
                call_args = mock_session.run.call_args[0][0]
                assert "DETACH DELETE" in call_args

    def test_create_indexes(self):
        """Test index creation."""
        with patch("ista.memgraph_loader.HAS_NEO4J_DRIVER", True):
            mock_driver = MagicMock()
            mock_session = MagicMock()
            mock_driver.session.return_value.__enter__ = Mock(
                return_value=mock_session
            )
            mock_driver.session.return_value.__exit__ = Mock(return_value=False)

            with patch("ista.memgraph_loader.GraphDatabase") as MockGD:
                MockGD.driver.return_value = mock_driver

                from ista.memgraph_loader import MemgraphLoader

                loader = MemgraphLoader()
                loader.connect()
                loader.create_indexes()

                mock_session.run.assert_called_once()
                call_args = mock_session.run.call_args[0][0]
                assert "CREATE INDEX" in call_args
                assert "iri" in call_args


class TestMemgraphLoaderStatistics:
    """Tests for MemgraphLoader statistics methods."""

    def test_get_database_statistics(self):
        """Test retrieving database statistics."""
        with patch("ista.memgraph_loader.HAS_NEO4J_DRIVER", True):
            mock_driver = MagicMock()
            mock_session = MagicMock()

            # Mock the results for different queries
            mock_results = [
                MagicMock(single=Mock(return_value={"count": 100})),  # node count
                MagicMock(single=Mock(return_value={"count": 50})),  # rel count
                MagicMock(__iter__=Mock(return_value=iter([{"labels": ["Drug", "Entity"]}]))),  # labels
                MagicMock(__iter__=Mock(return_value=iter([{"type": "TREATS"}]))),  # rel types
            ]
            mock_session.run.side_effect = mock_results

            mock_driver.session.return_value.__enter__ = Mock(
                return_value=mock_session
            )
            mock_driver.session.return_value.__exit__ = Mock(return_value=False)

            with patch("ista.memgraph_loader.GraphDatabase") as MockGD:
                MockGD.driver.return_value = mock_driver

                from ista.memgraph_loader import MemgraphLoader

                loader = MemgraphLoader()
                loader.connect()
                stats = loader.get_database_statistics()

                assert stats["node_count"] == 100
                assert stats["relationship_count"] == 50
                assert "Drug" in stats["labels"]
                assert "Entity" in stats["labels"]
                assert "TREATS" in stats["relationship_types"]


class TestConvenienceFunctions:
    """Tests for convenience functions."""

    def test_load_ontology_to_memgraph_function_exists(self):
        """Test that load_ontology_to_memgraph function exists."""
        from ista.memgraph_loader import load_ontology_to_memgraph

        assert callable(load_ontology_to_memgraph)

    def test_load_rdf_to_memgraph_function_exists(self):
        """Test that load_rdf_to_memgraph function exists."""
        from ista.memgraph_loader import load_rdf_to_memgraph

        assert callable(load_rdf_to_memgraph)


class TestModuleExports:
    """Tests for module exports."""

    def test_memgraph_loader_exported_from_ista(self):
        """Test that MemgraphLoader is exported from ista package."""
        from ista import MemgraphLoader

        assert MemgraphLoader is not None

    def test_convenience_functions_exported(self):
        """Test that convenience functions are exported from ista package."""
        from ista import load_ontology_to_memgraph, load_rdf_to_memgraph

        assert callable(load_ontology_to_memgraph)
        assert callable(load_rdf_to_memgraph)
