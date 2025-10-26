Getting Started
===============

This guide will help you get started with ista quickly.

What is ista?
-------------

**ista** (Sindarin for "knowledge") is a toolkit for working with knowledge graphs and OWL2 ontologies. It provides:

* A high-performance C++ library for OWL2 ontology manipulation
* Python bindings for easy access to C++ functionality
* Tools for building knowledge graphs from databases
* Converters between ontologies and popular graph formats

Two OWL2 Interfaces
-------------------

ista provides two ways to work with OWL2 ontologies:

1. **ista.owl2** (New C++ Library) - Recommended for new projects

   * High-performance C++ implementation
   * Complete OWL2 support with modern API
   * Subgraph extraction and filtering
   * RDF/XML parsing and serialization

2. **owlready2** (Legacy) - For database parsing workflows

   * Pure Python library
   * Used by database parsers
   * Mature and feature-complete

See :doc:`user_guide/owl2_interfaces` for detailed comparison.

Basic Workflow
--------------

Create an Ontology
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from ista import owl2

   # Create ontology with IRI
   ont = owl2.Ontology(owl2.IRI("http://example.org/biomedical"))

   # Register prefixes for convenience
   ont.register_prefix("bio", "http://example.org/biomedical#")

Define Classes and Properties
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Define classes
   disease = owl2.Class(owl2.IRI("bio", "Disease", "http://example.org/biomedical#"))
   gene = owl2.Class(owl2.IRI("bio", "Gene", "http://example.org/biomedical#"))

   # Define properties
   associated_with = owl2.ObjectProperty(
       owl2.IRI("bio", "associatedWith", "http://example.org/biomedical#")
   )

   # Declare entities
   ont.add_axiom(owl2.Declaration(owl2.CLASS, disease.get_iri()))
   ont.add_axiom(owl2.Declaration(owl2.CLASS, gene.get_iri()))

Add Individuals and Assertions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Create individuals
   alzheimers = owl2.NamedIndividual(owl2.IRI("bio", "Alzheimers", "..."))
   apoe = owl2.NamedIndividual(owl2.IRI("bio", "APOE", "..."))

   # Add class assertions
   ont.add_axiom(owl2.ClassAssertion(disease, alzheimers))
   ont.add_axiom(owl2.ClassAssertion(gene, apoe))

   # Add property assertions
   ont.add_axiom(owl2.ObjectPropertyAssertion(associated_with, apoe, alzheimers))

Serialize and Parse
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Serialize to RDF/XML
   owl2.RDFXMLSerializer.serialize_to_file(ont, "biomedical.owl")

   # Parse from file
   ont2 = owl2.RDFXMLParser.parse_from_file("biomedical.owl")

Extract Subgraphs
~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Create filter
   filter_obj = owl2.OntologyFilter(ont)

   # Extract 2-hop neighborhood
   result = filter_obj.extract_neighborhood(
       owl2.IRI("bio", "Alzheimers", "..."),
       depth=2
   )

   # Get filtered ontology
   subgraph = result.ontology
   print(f"Filtered: {result.filtered_axiom_count} axioms")

Convert to Graphs
~~~~~~~~~~~~~~~~~

.. code-block:: python

   from ista.converters import to_networkx
   import networkx as nx

   # Convert to NetworkX
   G = to_networkx(ont, strategy='individuals_only')

   # Analyze
   centrality = nx.betweenness_centrality(G)
   communities = nx.community.greedy_modularity_communities(G)

Next Steps
----------

* :doc:`installation` - Detailed installation instructions
* :doc:`user_guide/index` - Complete user guide
* :doc:`api/index` - Python API reference
* :doc:`cpp_api/index` - C++ API reference
* :doc:`examples` - Example programs and tutorials
