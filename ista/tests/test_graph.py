import pytest
import numpy as np

from ista.graph import Graph, Node, Edge


class TestGraphCreation:
    """Tests for Graph instantiation."""

    def test_empty_graph(self):
        """Test creating an empty graph."""
        G = Graph()
        assert G.nodes == []
        assert G.edges == []

    def test_graph_with_initial_nodes(self):
        """Test creating a graph with initial nodes."""
        n1 = Node("Chemical")
        n2 = Node("Disease")
        G = Graph(nodes=[n1, n2])
        assert len(G.nodes) == 2
        assert n1 in G.nodes
        assert n2 in G.nodes

    def test_mutable_default_isolation(self):
        """Test that mutable defaults are not shared between instances."""
        G1 = Graph()
        G2 = Graph()
        G1.add_node("Test")
        # G2 should not be affected by G1's modification
        assert len(G1.nodes) == 1
        assert len(G2.nodes) == 0


class TestNodeOperations:
    """Tests for node creation and manipulation."""

    def test_simple_node(self):
        """Test creating a simple anonymous node."""
        G = Graph()
        node = G.add_node()
        assert node is not None
        assert node in G.nodes

    def test_node_with_class(self):
        """Test creating a node with a class."""
        G = Graph()
        node = G.add_node("Chemical")
        assert node.node_class == "Chemical"

    def test_node_with_properties(self):
        """Test creating a node with properties."""
        G = Graph()
        props = {'name': 'Benzene', 'casrn': '71-43-2'}
        node = G.add_node("Chemical", props)
        assert node.properties['name'] == 'Benzene'
        assert node.properties['casrn'] == '71-43-2'

    def test_node_properties_mutable_default_isolation(self):
        """Test that node properties are not shared between instances."""
        n1 = Node("Chemical")
        n2 = Node("Disease")
        n1.properties['test'] = 'value'
        assert 'test' not in n2.properties


class TestEdgeOperations:
    """Tests for edge creation and manipulation."""

    def test_simple_edge(self):
        """Test creating a simple edge between two nodes."""
        G = Graph()
        n1 = G.add_node()
        n2 = G.add_node()
        G.add_edge(n1, n2)
        assert len(G.edges) == 1
        edge = G.edges[0]
        assert edge[0] == n1
        assert edge[1] == n2

    def test_edge_attributes(self):
        """Test that edges can store and retrieve custom attributes."""
        G = Graph()
        n1 = G.add_node("Gene", {"name": "TP53"})
        n2 = G.add_node("Disease", {"name": "Cancer"})

        edge_attrs = {
            "relationship": "associated_with",
            "evidence": "experimental",
            "confidence": 0.95
        }
        G.add_edge(n1, n2, edge_properties=edge_attrs)

        assert len(G.edges) == 1
        edge = G.edges[0]
        assert edge[0] == n1
        assert edge[1] == n2
        assert edge[3]["relationship"] == "associated_with"
        assert edge[3]["evidence"] == "experimental"
        assert edge[3]["confidence"] == 0.95

    def test_weighted_edges(self):
        """Test that edges support weight values."""
        G = Graph()
        n1 = G.add_node()
        n2 = G.add_node()
        n3 = G.add_node()

        # Add edges with different weights
        G.add_edge(n1, n2, weight=0.5)
        G.add_edge(n2, n3, weight=1.0)
        G.add_edge(n1, n3, weight=0.25)

        assert len(G.edges) == 3

        # Verify weights (edge tuple structure: from, to, weight, props)
        weights = [edge[2] for edge in G.edges]
        assert 0.5 in weights
        assert 1.0 in weights
        assert 0.25 in weights

    def test_default_weight(self):
        """Test that edges have default weight of 1."""
        G = Graph()
        n1 = G.add_node()
        n2 = G.add_node()
        G.add_edge(n1, n2)
        assert G.edges[0][2] == 1

    def test_edge_properties_mutable_default_isolation(self):
        """Test that edge properties are not shared between edges."""
        G = Graph()
        n1 = G.add_node()
        n2 = G.add_node()
        n3 = G.add_node()

        G.add_edge(n1, n2)
        G.add_edge(n2, n3)

        # Modify first edge's properties
        G.edges[0][3]['test'] = 'value'

        # Second edge should not be affected
        assert 'test' not in G.edges[1][3]


class TestEdgeDeletion:
    """Tests for edge deletion."""

    def test_delete_single_edge(self):
        """Test deleting a single edge."""
        G = Graph()
        n1 = G.add_node()
        n2 = G.add_node()
        G.add_edge(n1, n2, weight=5)

        result = G.delete_edge(n1, n2)
        assert result is not False
        assert len(G.edges) == 0
        # Check returned deleted edge
        assert len(result) == 1
        assert result[0][2] == 5

    def test_delete_nonexistent_edge(self):
        """Test deleting an edge that doesn't exist."""
        G = Graph()
        n1 = G.add_node()
        n2 = G.add_node()

        result = G.delete_edge(n1, n2)
        assert result is False

    def test_delete_multiple_edges_fails_by_default(self):
        """Test that deleting multiple edges fails by default."""
        G = Graph()
        n1 = G.add_node()
        n2 = G.add_node()

        # Create multigraph scenario
        G.add_edge(n1, n2, weight=1)
        G.add_edge(n1, n2, weight=2)

        with pytest.raises(RuntimeError) as excinfo:
            G.delete_edge(n1, n2)
        assert "Multiple matching edges" in str(excinfo.value)

    def test_delete_multiple_edges_allowed(self):
        """Test deleting multiple edges when allowed."""
        G = Graph()
        n1 = G.add_node()
        n2 = G.add_node()

        G.add_edge(n1, n2, weight=1)
        G.add_edge(n1, n2, weight=2)

        result = G.delete_edge(n1, n2, fail_on_multiple_match=False)
        assert len(result) == 2
        assert len(G.edges) == 0

    def test_delete_preserves_other_edges(self):
        """Test that deleting an edge preserves other edges."""
        G = Graph()
        n1 = G.add_node()
        n2 = G.add_node()
        n3 = G.add_node()

        G.add_edge(n1, n2)
        G.add_edge(n2, n3)
        G.add_edge(n1, n3)

        G.delete_edge(n1, n2)

        assert len(G.edges) == 2
        # Verify remaining edges
        from_nodes = [e[0] for e in G.edges]
        assert n2 in from_nodes
        assert n1 in from_nodes


class TestAdjacencyMatrix:
    """Tests for adjacency matrix generation."""

    def test_empty_graph_adjacency(self):
        """Test adjacency matrix for empty graph."""
        G = Graph()
        adj = G.get_adjacency()
        assert adj.shape == (0, 0)

    def test_simple_adjacency(self):
        """Test adjacency matrix for simple graph."""
        G = Graph()
        n1 = G.add_node()
        n2 = G.add_node()
        G.add_edge(n1, n2, weight=1)

        adj = G.get_adjacency()
        assert adj.shape == (2, 2)
        assert adj[0, 1] == 1
        assert adj[1, 0] == 0  # Directed graph
        assert adj[0, 0] == 0
        assert adj[1, 1] == 0

    def test_weighted_adjacency(self):
        """Test adjacency matrix preserves weights."""
        G = Graph()
        n1 = G.add_node()
        n2 = G.add_node()
        n3 = G.add_node()

        G.add_edge(n1, n2, weight=0.5)
        G.add_edge(n2, n3, weight=2.0)
        G.add_edge(n1, n3, weight=0.75)

        adj = G.get_adjacency()
        assert adj.shape == (3, 3)
        assert adj[0, 1] == 0.5
        assert adj[1, 2] == 2.0
        assert adj[0, 2] == 0.75

    def test_adjacency_no_self_loops(self):
        """Test adjacency matrix with no self-loops."""
        G = Graph()
        n1 = G.add_node()
        n2 = G.add_node()
        G.add_edge(n1, n2)

        adj = G.get_adjacency()
        # Diagonal should be zero (no self-loops added)
        assert adj[0, 0] == 0
        assert adj[1, 1] == 0

    def test_adjacency_unsupported_format(self):
        """Test that unsupported format raises NotImplementedError."""
        G = Graph()
        with pytest.raises(NotImplementedError):
            G.get_adjacency(format="list")

    def test_adjacency_dtype(self):
        """Test that adjacency matrix has float64 dtype."""
        G = Graph()
        n1 = G.add_node()
        n2 = G.add_node()
        G.add_edge(n1, n2)

        adj = G.get_adjacency()
        assert adj.dtype == np.float64


class TestEdgeClass:
    """Tests for the Edge class."""

    def test_edge_creation(self):
        """Test creating an Edge object."""
        n1 = Node("Gene")
        n2 = Node("Disease")
        edge = Edge(n1, n2, weight=0.8)

        assert edge.from_node == n1
        assert edge.to_node == n2
        assert edge.weight == 0.8

    def test_edge_default_weight(self):
        """Test Edge default weight is 0."""
        n1 = Node("Gene")
        n2 = Node("Disease")
        edge = Edge(n1, n2)

        assert edge.weight == 0

    def test_edge_properties(self):
        """Test Edge with custom properties."""
        n1 = Node("Gene")
        n2 = Node("Disease")
        props = {"type": "causes", "source": "literature"}
        edge = Edge(n1, n2, edge_properties=props)

        assert edge.edge_properties["type"] == "causes"
        assert edge.edge_properties["source"] == "literature"

    def test_edge_properties_mutable_default(self):
        """Test that Edge properties don't share mutable defaults."""
        n1 = Node("Gene")
        n2 = Node("Disease")

        e1 = Edge(n1, n2)
        e2 = Edge(n1, n2)

        e1.edge_properties['test'] = 'value'
        assert 'test' not in e2.edge_properties


class TestNodeClass:
    """Tests for the Node class."""

    def test_node_str_with_class_and_name(self):
        """Test Node string representation with class and name."""
        node = Node("Chemical", name="Aspirin")
        s = str(node)
        assert "Chemical" in s
        assert "Aspirin" in s

    def test_node_str_with_class_only(self):
        """Test Node string representation with class only."""
        node = Node("Chemical")
        s = str(node)
        assert "Chemical" in s
        assert "no name" in s

    def test_node_str_anonymous(self):
        """Test Node string representation for anonymous node."""
        node = Node(None)
        s = str(node)
        assert "Anonymous" in s

    def test_node_label_property(self):
        """Test that label is a synonym for node_class."""
        node = Node("Disease")
        assert node.label == node.node_class
        assert node.label == "Disease"

    def test_node_class_capitalization(self):
        """Test that node_class is capitalized."""
        node = Node("gene")
        assert node.node_class == "Gene"

    def test_node_is_named(self):
        """Test is_named property."""
        named_node = Node("Chemical", name="Benzene")
        unnamed_node = Node("Chemical")

        assert named_node.is_named is True
        assert unnamed_node.is_named is False
