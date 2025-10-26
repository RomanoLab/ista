Examples
========

This page provides links to example programs demonstrating various ista features.

Python Examples
---------------

Subgraph Extraction
~~~~~~~~~~~~~~~~~~~

**File**: ``examples/subgraph_extraction_example.py``

Demonstrates high-performance subgraph extraction from a biomedical knowledge graph:

* Creating a biomedical ontology (diseases, genes, proteins, drugs)
* Filtering by disease to extract relevant subgraphs
* Extracting drug-target networks
* Finding paths between entities
* Comparing multiple diseases
* Random sampling
* Builder pattern for complex filters
* Performance benchmarking

.. literalinclude:: ../../examples/subgraph_extraction_example.py
   :language: python
   :lines: 1-50
   :caption: Subgraph Extraction Example (excerpt)

Run with:

.. code-block:: bash

   python examples/subgraph_extraction_example.py

Graph Conversion
~~~~~~~~~~~~~~~~

**File**: ``examples/graph_conversion_example.py``

Shows how to convert between OWL2 ontologies and graph representations:

* Creating a medical ontology
* Converting to NetworkX graphs
* Converting to igraph graphs
* Converting to ista.graph native format
* Performing graph analysis (centrality, communities, clustering)
* Round-trip testing (ontology → graph → ontology)

Run with:

.. code-block:: bash

   python examples/graph_conversion_example.py

OWL2 Round-Trip
~~~~~~~~~~~~~~~

**File**: ``examples/owl2_roundtrip_example.py``

Demonstrates complete OWL2 workflow:

* Creating ontologies from scratch
* Adding various axiom types
* Serializing to RDF/XML and Functional Syntax
* Parsing ontologies from files
* Modifying parsed ontologies
* Round-trip verification

Run with:

.. code-block:: bash

   python examples/owl2_roundtrip_example.py

C++ Examples
------------

University Ontology
~~~~~~~~~~~~~~~~~~~

**File**: ``src/ista.cpp``

Complete C++ example showing:

* Creating an ontology with IRI
* Defining classes (Person, Student, Professor)
* Creating object and data properties
* Adding individuals
* Making assertions
* Serializing to Functional Syntax

Build and run:

.. code-block:: bash

   mkdir build && cd build
   cmake ..
   cmake --build .
   ./ista

Project Examples
----------------

Alzheimer's Knowledge Base (AlzKB)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Directory**: ``examples/projects/alzkb/``

A knowledge graph for Alzheimer's disease research built from public databases.

Features:

* Parsing structured data into OWL2
* Integration of multiple data sources
* Disease-gene-drug relationships

Neuroscience Knowledge Base (NeuroKB)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Directory**: ``examples/projects/neurokb/``

A neuroscience-focused knowledge graph.

Features:

* Neurological conditions
* Treatments and medications
* Research data integration

Test Examples
-------------

The ``tests/`` directory contains additional examples:

Simple Bindings Test
~~~~~~~~~~~~~~~~~~~~

**File**: ``tests/test_simple_bindings.py``

Basic example of using Python bindings:

* Creating ontologies
* Defining entities
* Adding axioms
* Serialization

Parser Test
~~~~~~~~~~~

**File**: ``tests/test_parser.py``

RDF/XML parsing examples:

* Parsing OWL files
* Round-trip testing
* Verifying axiom preservation

Subgraph Extraction Test
~~~~~~~~~~~~~~~~~~~~~~~~~

**File**: ``tests/test_subgraph.py``

Complete subgraph extraction test suite showing all filtering capabilities.

Example Workflow
----------------

Here's a complete workflow combining multiple features:

.. code-block:: python

   from ista import owl2
   from ista.converters import to_networkx
   import networkx as nx

   # 1. Create an ontology
   ont = owl2.Ontology(owl2.IRI("http://example.org/bio"))

   # 2. Add content
   disease = owl2.Class(owl2.IRI("http://example.org/bio#Disease"))
   gene = owl2.Class(owl2.IRI("http://example.org/bio#Gene"))
   alzheimers = owl2.NamedIndividual(owl2.IRI("http://example.org/bio#Alzheimers"))
   apoe = owl2.NamedIndividual(owl2.IRI("http://example.org/bio#APOE"))

   ont.add_axiom(owl2.ClassAssertion(disease, alzheimers))
   ont.add_axiom(owl2.ClassAssertion(gene, apoe))

   # 3. Save to file
   owl2.RDFXMLSerializer.serialize_to_file(ont, "biomedical.owl")

   # 4. Extract subgraph
   filter_obj = owl2.OntologyFilter(ont)
   result = filter_obj.extract_neighborhood(alzheimers.get_iri(), depth=2)

   # 5. Convert to NetworkX for analysis
   G = to_networkx(result.ontology)

   # 6. Analyze
   print(f"Nodes: {G.number_of_nodes()}")
   print(f"Edges: {G.number_of_edges()}")
   centrality = nx.betweenness_centrality(G)
   print(f"Most central: {max(centrality, key=centrality.get)}")

Running Examples
----------------

All examples can be run directly after installing ista:

.. code-block:: bash

   # Install ista
   pip install -e .

   # Run Python examples
   python examples/subgraph_extraction_example.py
   python examples/graph_conversion_example.py
   python examples/owl2_roundtrip_example.py

   # Run tests (also serve as examples)
   python tests/test_simple_bindings.py
   python tests/test_parser.py
   python tests/test_subgraph.py

See Also
--------

* :doc:`api/index` - Python API reference
* :doc:`cpp_api/index` - C++ API reference
* :doc:`user_guide/index` - User guide
