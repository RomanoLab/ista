ista Documentation
==================

.. image:: https://img.shields.io/badge/license-MIT-blue.svg
   :target: https://opensource.org/licenses/MIT
   :alt: License: MIT

**ista** (*Sindarin:* Knowledge) is a hybrid Python/C++ toolkit for manipulating and building knowledge graphs with support for OWL2 ontologies.

The project combines Python's flexibility for data integration with C++'s performance for knowledge graph manipulation.

Features
--------

**Python Package**

* Parse flat files (CSV, TSV, XLSX) and MySQL databases
* Convert structured data into OWL2 ontologies
* Load knowledge graphs into Neo4j graph databases
* Custom graph data structures
* Python bindings to high-performance C++ OWL2 library
* Graph converters for NetworkX, igraph, and native graphs

**C++ Library (libista)**

* Complete OWL2 structural specification implementation
* 40+ axiom types (classes, properties, individuals, assertions)
* Complex class expressions and data ranges
* IRI management with prefix support
* RDF/XML and Functional Syntax serialization
* High-performance subgraph extraction with O(V+E) algorithms
* Python bindings via pybind11

Quick Start
-----------

Installation
~~~~~~~~~~~~

.. code-block:: bash

   # Install Python package with C++ extension
   pip install -e .

Python Example
~~~~~~~~~~~~~~

.. code-block:: python

   from ista import owl2

   # Create an ontology
   ont = owl2.Ontology(owl2.IRI("http://example.org/myonto"))

   # Add classes and individuals
   person = owl2.Class(owl2.IRI("http://example.org/Person"))
   alice = owl2.NamedIndividual(owl2.IRI("http://example.org/Alice"))
   ont.add_axiom(owl2.ClassAssertion(person, alice))

   # Serialize to RDF/XML
   owl2.RDFXMLSerializer.serialize_to_file(ont, "output.owl")

   # Extract subgraphs
   filter_obj = owl2.OntologyFilter(ont)
   result = filter_obj.extract_neighborhood(alice.get_iri(), depth=2)

Documentation Contents
======================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   getting_started
   installation
   user_guide/index
   api/index
   cpp_api/index
   examples
   contributing
   changelog

Indices and Tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
