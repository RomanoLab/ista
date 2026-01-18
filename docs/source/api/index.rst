Python API Reference
====================

This section documents the Python API for ista.

.. toctree::
   :maxdepth: 2
   :caption: Python Modules:

   owl2

Core Modules
------------

ista.owl2
~~~~~~~~~

The main module for OWL2 ontology manipulation using the high-performance C++ library.

.. autosummary::
   :toctree: generated
   :recursive:

   ista.owl2

ista.converters
~~~~~~~~~~~~~~~

Converters between ontologies and graph representations (NetworkX, igraph, ista.graph).

.. autosummary::
   :toctree: generated
   :recursive:

   ista.converters

ista.database_parser
~~~~~~~~~~~~~~~~~~~~

Tools for parsing databases and flat files into ontologies.

.. autosummary::
   :toctree: generated
   :recursive:

   ista.database_parser

ista.graph
~~~~~~~~~~

Native graph data structures.

.. autosummary::
   :toctree: generated
   :recursive:

   ista.graph

Graph Database Integration
--------------------------

ista.owl2memgraph
~~~~~~~~~~~~~~~~~

CLI tool and Python API for loading OWL2 ontologies into Memgraph graph database.
Supports multiple ontology formats (RDF/XML, Turtle, Functional Syntax, Manchester, OWL/XML).

.. autosummary::
   :toctree: generated
   :recursive:

   ista.owl2memgraph

ista.memgraph_loader
~~~~~~~~~~~~~~~~~~~~

Low-level Memgraph loading utilities for programmatic ontology-to-graph conversion.

.. autosummary::
   :toctree: generated
   :recursive:

   ista.memgraph_loader
