from typing import Dict

from .node import Node

class Edge:
    def __init__(self, from_node: Node, to_node: Node, weight: float = 0, edge_properties: Dict = dict()):
        """Directed edge in a knowledge graph."""
        self.from_node = from_node
        self.to_node = to_node
        self.weight = weight
        self.edge_properties = edge_properties