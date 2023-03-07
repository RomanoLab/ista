from typing import Dict

class Node:
    def __init__(self, node_class: str, node_idx: int = None, name: str = None, properties: Dict = {}, weight_prop: str = None):
        """Node in a graph.

        Attributes
        ----------
        node_class : str
            Class describing the modality of entity this node represents. For
            example, a node describing a chemical would be of the class
            `'Chemical'`.
        node_idx : int
            Integer index of the node in a graph. Users should generally not
            manipulate this directly.
        
        Notes
        -----
        In this implementation, nodes basically function as containers for
        data, with extra abilities to perform computations or logic. For
        example, nodes are not aware of incident edges. Things like this are
        handled entirely by the Graph object that the node is a part of.
        """
        self.properties = properties
        if node_class:
            self.node_class = node_class.capitalize()
        else:
            self.node_class = None

        self.name = name
        if self.name:
            self.is_named = True
        else:
            self.is_named = False
        
        self.node_idx = node_idx
        

    def __str__(self):
        if (self.node_class and self.name):
            return f"{self.node_class} node with name {self.name}: {id(self)}"
        elif self.node_class:
            return f"{self.node_class} node (no name specified): {id(self)}"
        elif self.name:
            return f"Node with name {self.name}: {id(self)}"
        else:
            return f"Anonymous node: {id(self)}"

    @property
    def label(self):
        """'Label' is a synonym for a node class.
        
        E.g., they are called labels in Neo4j. Neo4j also allows for multiple
        labels on one node, but this is currently unsupported by ista."""
        return self.node_class
