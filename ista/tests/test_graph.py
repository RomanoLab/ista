import pytest

from ista.graph import Graph, Node, Edge

def test_empty_graph():
    try:
        G = Graph()
    except:
        assert False, "Couldn't instantiate Graph."
    