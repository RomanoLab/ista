from typing import Dict

class Edge:
    def __init__(self, from_node: Node, to_node: Node, edge_properties: Dict = dict()):
        """Directed edge in a knowledge graph."""
        self.from_node = from_node
        self.to_node = to_node
        self.edge_properties = edge_properties