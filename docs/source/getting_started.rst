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
* Reasoning support via integration with reasoners like Konclude

Installation
------------

Install ista using pip:

.. code-block:: bash

   pip install ista

For development installation:

.. code-block:: bash

   git clone https://github.com/yourusername/ista.git
   cd ista
   pip install -e .

Basic Workflow
--------------

Create an Ontology
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from ista import owl2

   # Create ontology with IRI
   base_iri = "http://example.org/biomedical#"
   ont = owl2.Ontology(owl2.IRI(base_iri + "ontology"))

Define Classes and Properties
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Helper function for creating IRIs
   def make_iri(name):
       return owl2.IRI("bio", name, base_iri)

   # Define classes
   disease_iri = make_iri("Disease")
   disease = owl2.Class(disease_iri)

   gene_iri = make_iri("Gene")
   gene = owl2.Class(gene_iri)

   # Declare classes in ontology
   ont.add_axiom(owl2.Declaration(owl2.Declaration.EntityType.CLASS, disease_iri))
   ont.add_axiom(owl2.Declaration(owl2.Declaration.EntityType.CLASS, gene_iri))

   # Define object property
   associated_with_iri = make_iri("associatedWith")
   associated_with = owl2.ObjectProperty(associated_with_iri)
   ont.add_axiom(owl2.Declaration(
       owl2.Declaration.EntityType.OBJECT_PROPERTY,
       associated_with_iri
   ))

Add Individuals and Assertions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Create individuals with automatic class assertion
   alzheimers_iri = make_iri("Alzheimers")
   alzheimers = ont.create_individual(disease, alzheimers_iri)

   apoe_iri = make_iri("APOE")
   apoe = ont.create_individual(gene, apoe_iri)

   # Add property assertion
   ont.add_object_property_assertion(apoe, associated_with, alzheimers)

   # Add data property
   has_name_iri = make_iri("hasName")
   has_name = owl2.DataProperty(has_name_iri)
   ont.add_axiom(owl2.Declaration(
       owl2.Declaration.EntityType.DATA_PROPERTY,
       has_name_iri
   ))

   name_value = owl2.Literal("APOE Gene")
   ont.add_data_property_assertion(apoe, has_name, name_value)

Query Individuals
~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Search by data property value
   search_value = owl2.Literal("APOE Gene")
   results = ont.search_by_data_property(has_name, search_value)

   # Get all properties for an individual
   data_props = ont.get_data_property_assertions_for_individual(apoe)
   obj_props = ont.get_object_property_assertions_for_individual(apoe)

   # Check class membership
   is_gene = ont.is_instance_of(apoe, gene)

   # Get all classes for an individual
   classes = ont.get_classes_for_individual(apoe)

Serialize and Parse
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from ista.owl2 import RDFXMLSerializer, RDFXMLParser

   # Serialize to RDF/XML
   serializer = RDFXMLSerializer()
   rdf_content = serializer.serialize(ont)
   with open("biomedical.rdf", "w") as f:
       f.write(rdf_content)

   # Parse from file
   parser = RDFXMLParser()
   ont2 = parser.parse_from_file("biomedical.rdf")

   print(f"Loaded ontology with {ont2.get_axiom_count()} axioms")

Functional Syntax
~~~~~~~~~~~~~~~~~

.. code-block:: python

   from ista.owl2 import FunctionalSyntaxSerializer, FunctionalSyntaxParser

   # Serialize to Functional Syntax
   serializer = FunctionalSyntaxSerializer()
   ofn_content = serializer.serialize(ont)
   with open("biomedical.ofn", "w") as f:
       f.write(ofn_content)

   # Parse Functional Syntax
   parser = FunctionalSyntaxParser()
   ont3 = parser.parse_from_file("biomedical.ofn")

Extract Subgraphs
~~~~~~~~~~~~~~~~~

.. code-block:: python

   from ista.owl2 import OntologyFilter

   # Create filter
   filter_obj = OntologyFilter(ont)

   # Extract 2-hop neighborhood around Alzheimer's
   result = filter_obj.extract_neighborhood(
       seed_iri=alzheimers_iri,
       depth=2,
       include_superclasses=True,
       include_subclasses=True
   )

   # Get filtered ontology
   subgraph = result.get_ontology()
   included_iris = result.get_included_iris()

   print(f"Subgraph contains {subgraph.get_axiom_count()} axioms")
   print(f"Included {len(included_iris)} IRIs")

Convert to Graphs
~~~~~~~~~~~~~~~~~

.. code-block:: python

   from ista.converters import ontology_to_networkx
   import networkx as nx

   # Convert to NetworkX graph
   G = ontology_to_networkx(ont)

   # Analyze graph structure
   print(f"Nodes: {G.number_of_nodes()}")
   print(f"Edges: {G.number_of_edges()}")

   # Calculate centrality
   centrality = nx.betweenness_centrality(G)
   most_central = max(centrality, key=centrality.get)
   print(f"Most central node: {most_central}")

Parse Databases
~~~~~~~~~~~~~~~

.. code-block:: python

   from ista.database_parser import FlatFileDatabaseParser

   # Load base ontology
   ont = owl2.RDFXMLParser().parse_from_file("base_ontology.rdf")

   # Parse CSV file into ontology
   parser = FlatFileDatabaseParser(ont)

   parse_config = {
       "file_path": "diseases.csv",
       "entity_class_iri": "http://example.org/Disease",
       "id_column": "DiseaseID",
       "property_mappings": {
           "Name": {
               "property_iri": "http://example.org/hasName",
               "is_data_property": True
           },
           "Symptom": {
               "property_iri": "http://example.org/hasSymptom",
               "is_data_property": True
           }
       }
   }

   parser.parse(parse_config)

   # Save populated ontology
   serializer = owl2.RDFXMLSerializer()
   rdf_content = serializer.serialize(ont)
   with open("populated_ontology.rdf", "w") as f:
       f.write(rdf_content)

Working with Complex Class Expressions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Define some classes
   neurodegenerative_iri = make_iri("NeurodegenerativeDisease")
   neurodegenerative = owl2.Class(neurodegenerative_iri)
   ont.add_axiom(owl2.Declaration(
       owl2.Declaration.EntityType.CLASS,
       neurodegenerative_iri
   ))

   genetic_iri = make_iri("GeneticDisease")
   genetic = owl2.Class(genetic_iri)
   ont.add_axiom(owl2.Declaration(
       owl2.Declaration.EntityType.CLASS,
       genetic_iri
   ))

   # Create intersection (neurodegenerative AND genetic)
   neuro_named = owl2.NamedClass(neurodegenerative)
   genetic_named = owl2.NamedClass(genetic)
   intersection = owl2.ObjectIntersectionOf([neuro_named, genetic_named])

   # Make Alzheimer's a subclass of this intersection
   alzheimers_disease_iri = make_iri("AlzheimersDisease")
   alzheimers_disease = owl2.Class(alzheimers_disease_iri)
   ont.add_axiom(owl2.Declaration(
       owl2.Declaration.EntityType.CLASS,
       alzheimers_disease_iri
   ))

   alzheimers_named = owl2.NamedClass(alzheimers_disease)
   subclass_axiom = owl2.SubClassOf(alzheimers_named, intersection)
   ont.add_axiom(subclass_axiom)

Reasoning with Konclude
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from ista.reasoners import KoncludeReasoner

   # Initialize reasoner
   reasoner = KoncludeReasoner(konclude_path="/path/to/Konclude")

   # Classify ontology
   reasoner.classify(ont, output_file="classified.owl")

   # Check consistency
   is_consistent = reasoner.is_consistent(ont)
   print(f"Ontology is consistent: {is_consistent}")

Key Concepts
------------

**IRI (Internationalized Resource Identifier)**
   Unique identifier for entities in OWL2. Every class, property, and individual has an IRI.

**Ontology**
   Container for axioms (statements about classes, properties, and individuals).

**Axiom**
   A logical statement in the ontology (e.g., "Class A is a subclass of Class B").

**Individual**
   An instance of a class (e.g., "APOE" is an instance of "Gene").

**Property Assertion**
   Statement that an individual has a property value (data or object property).

**Class Expression**
   Complex class definition using logical operators (intersection, union, restrictions).

Next Steps
----------

* :doc:`installation` - Detailed installation instructions
* :doc:`user_guide/index` - Complete user guide
* :doc:`user_guide/owl2_interfaces` - OWL2 interface documentation
* :doc:`user_guide/database_parsing` - Database parsing guide
* :doc:`api/index` - Python API reference
* :doc:`cpp_api/index` - C++ API reference
* :doc:`examples` - Example programs and tutorials
