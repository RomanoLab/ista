ista.owl2 Module
================

The ``ista.owl2`` module provides the main Python interface to the high-performance C++ OWL2 library.

.. note::
   This is the recommended interface for all OWL2 ontology work in ista.
   See :doc:`../user_guide/owl2_interfaces` for detailed documentation.

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
   :undoc-members:
   :special-members: __init__

Serialization and Parsing
--------------------------

Serializers
~~~~~~~~~~~

RDFXMLSerializer
^^^^^^^^^^^^^^^^

.. autoclass:: ista.owl2.RDFXMLSerializer
   :members:
   :undoc-members:

FunctionalSyntaxSerializer
^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: ista.owl2.FunctionalSyntaxSerializer
   :members:
   :undoc-members:

TurtleSerializer
^^^^^^^^^^^^^^^^

.. autoclass:: ista.owl2.TurtleSerializer
   :members:
   :undoc-members:

   .. note::
      Turtle is a compact, human-readable RDF serialization format that is particularly
      efficient for large ontologies with many individuals. It produces significantly
      smaller files than RDF/XML (typically 30-50% smaller).

      The current implementation supports the most common axiom types including:
      declarations, class assertions, property assertions, subclass/subproperty axioms,
      and annotations. Complex class expressions are simplified to named classes.

Parsers
~~~~~~~

RDFXMLParser
^^^^^^^^^^^^

.. autoclass:: ista.owl2.RDFXMLParser
   :members:
   :undoc-members:

TurtleParser
^^^^^^^^^^^^

.. autoclass:: ista.owl2.TurtleParser
   :members:
   :undoc-members:

   .. note::
      The Turtle parser provides basic support for the most common Turtle syntax patterns.
      It successfully handles:

      - Prefix declarations (@prefix and @base)
      - IRI references (full IRIs in <> and prefixed names including default prefix :)
      - Literals (plain strings, typed with ^^, language-tagged with @)
      - Basic triples (subject predicate object .)
      - Comments (# to end of line)
      - Class and property declarations
      - Individual assertions and property values

      Current limitations (marked with BREADCRUMB comments in source):

      - No semicolon grouping (;) or comma lists (,)
      - No blank node property lists []
      - No RDF collections ()
      - Simplified numeric literal handling
      - No IRI escape sequences (\u, \U)
      - No triple-quoted strings
      - Simplified RDF-to-OWL conversion

      The parser achieves approximately 80% coverage of common use cases and is suitable
      for most standard ontology files. Complex RDF patterns may not parse correctly.

FunctionalSyntaxParser
^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: ista.owl2.FunctionalSyntaxParser
   :members:
   :undoc-members:

CSV Parser
~~~~~~~~~~

CSVParser
^^^^^^^^^

.. autoclass:: ista.owl2.CSVParser
   :members:
   :special-members: __init__

NodeTypeConfig
^^^^^^^^^^^^^^

.. autoclass:: ista.owl2.NodeTypeConfig
   :members:
   :undoc-members:

RelationshipTypeConfig
^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: ista.owl2.RelationshipTypeConfig
   :members:
   :undoc-members:

Parser Exceptions
~~~~~~~~~~~~~~~~~

RDFXMLParseException
^^^^^^^^^^^^^^^^^^^^

.. autoexception:: ista.owl2.RDFXMLParseException
   :members:
   :show-inheritance:

Subgraph Extraction
-------------------

OntologyFilter
~~~~~~~~~~~~~~

.. autoclass:: ista.owl2.OntologyFilter
   :members:
   :undoc-members:
   :special-members: __init__

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
