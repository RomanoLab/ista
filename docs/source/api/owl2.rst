ista.owl2 Module
================

The ``ista.owl2`` module provides the main Python interface to the high-performance C++ OWL2 library.

.. note::
   This is the recommended interface for all new OWL2 ontology work in ista.
   See :doc:`../user_guide/owl2_interfaces` for comparison with owlready2.

Module Overview
---------------

.. automodule:: ista.owl2
   :members:
   :undoc-members:
   :show-inheritance:

Core Types
----------

IRI
~~~

.. autoclass:: ista.owl2.IRI
   :members:
   :special-members: __init__, __str__, __eq__, __hash__

Literal
~~~~~~~

.. autoclass:: ista.owl2.Literal
   :members:
   :special-members: __init__

Entity Types
------------

Entity
~~~~~~

.. autoclass:: ista.owl2.Entity
   :members:
   :show-inheritance:

Class
~~~~~

.. autoclass:: ista.owl2.Class
   :members:
   :show-inheritance:
   :special-members: __init__

ObjectProperty
~~~~~~~~~~~~~~

.. autoclass:: ista.owl2.ObjectProperty
   :members:
   :show-inheritance:
   :special-members: __init__

DataProperty
~~~~~~~~~~~~

.. autoclass:: ista.owl2.DataProperty
   :members:
   :show-inheritance:
   :special-members: __init__

NamedIndividual
~~~~~~~~~~~~~~~

.. autoclass:: ista.owl2.NamedIndividual
   :members:
   :show-inheritance:
   :special-members: __init__, __hash__

Class Expressions
-----------------

ClassExpression
~~~~~~~~~~~~~~~

.. autoclass:: ista.owl2.ClassExpression
   :members:
   :show-inheritance:

NamedClass
~~~~~~~~~~

.. autoclass:: ista.owl2.NamedClass
   :members:
   :show-inheritance:
   :special-members: __init__

Axiom Types
-----------

Axiom
~~~~~

.. autoclass:: ista.owl2.Axiom
   :members:
   :show-inheritance:

Declaration
~~~~~~~~~~~

.. autoclass:: ista.owl2.Declaration
   :members:
   :show-inheritance:
   :special-members: __init__

SubClassOf
~~~~~~~~~~

.. autoclass:: ista.owl2.SubClassOf
   :members:
   :show-inheritance:
   :special-members: __init__

ClassAssertion
~~~~~~~~~~~~~~

.. autoclass:: ista.owl2.ClassAssertion
   :members:
   :show-inheritance:
   :special-members: __init__

ObjectPropertyAssertion
~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: ista.owl2.ObjectPropertyAssertion
   :members:
   :show-inheritance:
   :special-members: __init__

DataPropertyAssertion
~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: ista.owl2.DataPropertyAssertion
   :members:
   :show-inheritance:
   :special-members: __init__

Ontology Container
------------------

Ontology
~~~~~~~~

.. autoclass:: ista.owl2.Ontology
   :members:
   :special-members: __init__

   Core Methods
   ^^^^^^^^^^^^

   .. automethod:: add_axiom
   .. automethod:: remove_axiom
   .. automethod:: contains_axiom
   .. automethod:: get_axiom_count
   .. automethod:: get_axioms

   Entity Queries
   ^^^^^^^^^^^^^^

   .. automethod:: get_classes
   .. automethod:: get_object_properties
   .. automethod:: get_data_properties
   .. automethod:: get_individuals
   .. automethod:: get_class_count

   Subgraph Operations
   ^^^^^^^^^^^^^^^^^^^

   .. automethod:: create_subgraph
   .. automethod:: get_individuals_of_class
   .. automethod:: get_neighbors
   .. automethod:: has_path

   IRI Management
   ^^^^^^^^^^^^^^

   .. automethod:: get_ontology_iri
   .. automethod:: register_prefix
   .. automethod:: get_prefix_map

Serialization and Parsing
--------------------------

RDFXMLSerializer
~~~~~~~~~~~~~~~~

.. autoclass:: ista.owl2.RDFXMLSerializer
   :members:
   :undoc-members:

FunctionalSyntaxSerializer
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: ista.owl2.FunctionalSyntaxSerializer
   :members:
   :undoc-members:

RDFXMLParser
~~~~~~~~~~~~

.. autoclass:: ista.owl2.RDFXMLParser
   :members:
   :undoc-members:

RDFXMLParseException
~~~~~~~~~~~~~~~~~~~~

.. autoexception:: ista.owl2.RDFXMLParseException
   :members:
   :show-inheritance:

Subgraph Extraction
-------------------

OntologyFilter
~~~~~~~~~~~~~~

.. autoclass:: ista.owl2.OntologyFilter
   :members:
   :special-members: __init__

   Filtering Methods
   ^^^^^^^^^^^^^^^^^

   .. automethod:: filter_by_individuals
   .. automethod:: filter_by_classes
   .. automethod:: extract_neighborhood
   .. automethod:: extract_path
   .. automethod:: random_sample
   .. automethod:: apply_filter

   Builder Pattern
   ^^^^^^^^^^^^^^^

   .. automethod:: with_individuals
   .. automethod:: with_classes
   .. automethod:: with_max_depth
   .. automethod:: execute

FilterCriteria
~~~~~~~~~~~~~~

.. autoclass:: ista.owl2.FilterCriteria
   :members:
   :undoc-members:

FilterResult
~~~~~~~~~~~~

.. autoclass:: ista.owl2.FilterResult
   :members:
   :undoc-members:

Constants
---------

Entity Type Constants
~~~~~~~~~~~~~~~~~~~~~

.. autodata:: ista.owl2.CLASS
.. autodata:: ista.owl2.OBJECT_PROPERTY
.. autodata:: ista.owl2.DATA_PROPERTY
.. autodata:: ista.owl2.NAMED_INDIVIDUAL
.. autodata:: ista.owl2.DATATYPE
.. autodata:: ista.owl2.ANNOTATION_PROPERTY

XSD Datatypes
~~~~~~~~~~~~~

.. autodata:: ista.owl2.xsd

Utility Functions
-----------------

.. autofunction:: ista.owl2.is_available
