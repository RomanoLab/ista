from typing import List

import numpy as np

from .node import Node
from .edge import Edge

class Graph:
    def __init__(self, nodes: List[Node] = None, edges: List[Edge] = None):
        """Basic implementation of a directed graph."""
        # We use lists/arrays for now, but will switch to something more high performance
        # for large graphs once we find an adequate solution. Probably move to C/C++ extensions.
        self.nodes = nodes if nodes is not None else []
        self.edges = edges if edges is not None else []

    def add_node(self, node_class: str = None, node_properties: dict = None):
        n = Node(node_class, properties=node_properties)
        self.nodes.append(n)

        return n

    def add_edge(self, from_node: Node, to_node: Node, weight = 1, edge_properties: dict = None):
        if edge_properties is None:
            edge_properties = {}
        self.edges.append((from_node, to_node, weight, edge_properties))

    def delete_edge(self, from_node: Node, to_node: Node, fail_on_multiple_match: bool = True):
        """Delete an edge from the graph, given start and end nodes.

        Parameters
        ----------
        from_node : Node
            Source node of the edge to delete.
        to_node : Node
            Target node of the edge to delete.
        fail_on_multiple_match : bool, optional
            If True, raise an error when multiple matching edges exist.
            If False, delete all matching edges. Default is True.

        Returns
        -------
        list or bool
            If successful, returns list of deleted edges (tuples).
            Returns False if no matching edges found.

        Raises
        ------
        RuntimeError
            If multiple matching edges found and fail_on_multiple_match is True.
        """
        match_idxs = []
        for idx, edge in enumerate(self.edges):
            if (from_node == edge[0]) and (to_node == edge[1]):
                match_idxs.append(idx)

        if len(match_idxs) == 0:
            return False

        if (len(match_idxs) > 1) and fail_on_multiple_match:
            raise RuntimeError(
                f"Multiple matching edges found ({len(match_idxs)}). "
                "Set fail_on_multiple_match=False to delete all matches."
            )

        # Delete in reverse order to maintain valid indices
        deleted_edges = []
        for idx in reversed(match_idxs):
            deleted_edges.append(self.edges[idx])
            del self.edges[idx]

        return list(reversed(deleted_edges))

    def get_adjacency(self, format="matrix"):
        """Get a representation of the graph's node adjacency.

        Parameters
        ----------
        format : str, optional
            Format of the adjacency representation. Currently only 'matrix' is
            supported. Default is 'matrix'.

        Returns
        -------
        numpy.ndarray
            Adjacency matrix where entry (i, j) is the weight of the edge from
            node i to node j. Zero indicates no edge exists.

        Raises
        ------
        NotImplementedError
            If format is not 'matrix'.

        Notes
        -----
        Node indices are assigned based on their order in self.nodes.
        Multiple edges between the same nodes will use the last edge's weight.
        """
        if format != "matrix":
            raise NotImplementedError("Only adjacency matrices are supported at this time.")

        num_nodes = len(self.nodes)
        # Initialize with zeros (no edges)
        adj = np.zeros((num_nodes, num_nodes), dtype=np.float64)

        # Build node-to-index mapping
        node_to_idx = {id(node): idx for idx, node in enumerate(self.nodes)}

        # Populate adjacency matrix
        # Edge tuple structure: (from_node, to_node, weight, edge_properties)
        for edge in self.edges:
            from_node, to_node, weight, _ = edge
            from_idx = node_to_idx.get(id(from_node))
            to_idx = node_to_idx.get(id(to_node))

            if from_idx is not None and to_idx is not None:
                adj[from_idx, to_idx] = weight

        return adj