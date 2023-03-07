from typing import List

import numpy as np

from .node import Node
from .edge import Edge

class Graph:
    def __init__(self, nodes: List[Node] = list(), edges: List[Edge] = list()):
        """Basic implementation of a directed graph."""
        # We use lists/arrays for now, but will switch to something more high performance
        # for large graphs once we find an adequate solution. Probably move to C/C++ extensions.
        self.nodes = nodes
        self.edges = edges

    def add_node(self, node_class: str = None, node_properties: dict = dict()):
        n = Node(node_class, node_properties)
        self.nodes.append(n)

        return n

    def add_edge(self, from_node: Node, to_node: Node, weight = 1, edge_properties: dict = dict()):
        self.edges.append((from_node, to_node, weight, edge_properties))

    def delete_edge(self, from_node: Node, to_node: Node, fail_on_multiple_match: bool = True):
        """Delete an edge from the graph, given start and end nodes and returns
        the deleted edge.
        
        Fails if multiple matching edges are found (e.g., in the case of a
        multigraph), unless `fail_on_multiple_match` is set to `False`."""
        match_idxs = []
        for e, i in enumerate(self.edges):
            if ((from_node == e[0]) and (to_node == e[1])):
                match_idxs.append(i)
        
        if (len(match_idxs) > 1) and (fail_on_multiple_match):
            raise RuntimeError("Multiple matching edges found. If you want to delete both, retry with `fail_on_multiple_match=False`.")
        
        if len(match_idxs) == 0:
            return False
        
        match = match_idxs[0]
        del self.edges[match_idxs[0]]

        return match

    def get_adjacency(self, format="matrix"):
        """Get a representation of the graph's node adjacency.
        
        Notes
        -----
        Currently, only adjacency matrices are supported. Future support will be
        added for adjacency lists, etc.
        """
        if format != "matrix":
            raise NotImplementedError("Only adjacency matrices are supported at this time.")
        
        num_nodes = len(self.nodes)
        adj = np.ndarray((num_nodes, num_nodes))

        for e in self.edges:
            n1 = e.from_node.node_idx
            n2 = e.to_node.node_idx
            adj[n1, n2] = e.weight

        return adj