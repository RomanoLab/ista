from typing import Dict

class Node:
    def __init__(self, node_class: str, properties: Dict = {}):
        """Node in a graph.
        
        Notes
        -----
        In this implementation, nodes basically function as containers for
        data, with extra abilities to perform computations or logic. For
        example, nodes are not aware of incident edges. Things like this are
        handled entirely by the Graph object that the node is a part of.
        """
        self.properties = dict()
        self.node_class = node_class

    @property
    def label(self):
        return self.node_class
