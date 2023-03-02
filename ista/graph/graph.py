from typing import List, Dict

from .node import Node
from .edge import Edge

class Graph:
    def __init__(self, nodes: List[Node] = list(), edges: List[Edge] = list()):
        # We use lists/arrays for now, but will switch to something more high performance
        # for large graphs once we find an adequate solution. Probably move to C/C++ extensions.
        self.nodes = nodes
        self.edges = edges

    def.add_edge(self, from_node: Node, to_node: Node, weight = 1, edge_properties: Dict = dict()):
        self.edge.append((from_node, to_node, weight, edge_properties))

    def.delete_edge(self, from_node: Node, to_node: Node):
        matches = []
        for e in self.edges:
            if ((from_node == e[0]) and (to_node == e[1]))
