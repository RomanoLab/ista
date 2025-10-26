Python API Reference
====================

This section documents the Python API for ista.

.. toctree::
   :maxdepth: 2
   :caption: Python Modules:

   owl2
   converters
   database_parser
   graph

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
