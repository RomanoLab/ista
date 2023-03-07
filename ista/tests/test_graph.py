import pytest

from ista.graph import Graph, Node, Edge

def test_empty_graph():
    try:
        G = Graph()
    except:
        assert False, "Couldn't instantiate Graph."
    
def test_simple_nodes():
    G = Graph()
    try:
        G.add_node()
    except:
        assert False, "Couldn't create a simple (anonymous) node."

def test_nodes_with_classes():
    G = Graph()
    try:
        G.add_node("Chemical", {'name': 'Benzene', 'casrn': '71-43-2'})
    except:
        assert False, "Couldn't create a node with a class and attributes."

def test_simple_edges():
    G = Graph()
    n1 = G.add_node()
    n2 = G.add_node()
    try:
        G.add_edge(n1, n2)
    except:
        assert False, "Couldn't create an edge between two nodes"

def test_edge_attributes():
    pass

def test_weighted_edges():
    pass