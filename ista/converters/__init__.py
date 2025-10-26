"""
OWL2 Ontology to Graph Converters

This module provides utilities for converting between OWL2 ontologies and various
graph representations (NetworkX, igraph, and ista's native graph format).

Available Converters
--------------------
- NetworkX: to_networkx(), from_networkx()
- igraph: to_igraph(), from_igraph() (if igraph is installed)
- ista.graph: to_ista_graph(), from_ista_graph()

Conversion Strategies
---------------------
- individuals_only: Only individuals as nodes, object properties as edges
- include_classes: Include classes as nodes in the graph
- include_properties: Include properties as nodes in the graph

Examples
--------
>>> from ista import owl2
>>> from ista.converters import to_networkx, to_ista_graph
>>>
>>> # Load an ontology
>>> ontology = owl2.Ontology("http://example.org/ontology")
>>>
>>> # Convert to NetworkX with individuals only
>>> nx_graph = to_networkx(ontology, strategy='individuals_only')
>>>
>>> # Convert to ista.graph including classes
>>> ista_graph = to_ista_graph(ontology, strategy='include_classes')
"""

from .ontology_to_graph import (
    OntologyToGraphConverter,
    ConversionStrategy,
    ConversionOptions,
)

# Import converters if dependencies are available
try:
    from .networkx_converter import to_networkx, from_networkx

    HAS_NETWORKX = True
except ImportError:
    HAS_NETWORKX = False
    to_networkx = None
    from_networkx = None

try:
    from .igraph_converter import to_igraph, from_igraph

    HAS_IGRAPH = True
except ImportError:
    HAS_IGRAPH = False
    to_igraph = None
    from_igraph = None

# Native ista.graph converter is always available
from .ista_graph_converter import to_ista_graph, from_ista_graph

__all__ = [
    # Base classes
    "OntologyToGraphConverter",
    "ConversionStrategy",
    "ConversionOptions",
    # NetworkX converters
    "to_networkx",
    "from_networkx",
    "HAS_NETWORKX",
    # igraph converters
    "to_igraph",
    "from_igraph",
    "HAS_IGRAPH",
    # ista.graph converters
    "to_ista_graph",
    "from_ista_graph",
]
