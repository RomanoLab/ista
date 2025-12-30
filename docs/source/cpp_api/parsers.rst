Parsers
=======

The libista library provides parsers for multiple OWL 2 serialization formats.

Overview
--------

All parsers follow a consistent interface with static methods for parsing from strings and files.

Available Parsers
-----------------

RDF/XML Parser
~~~~~~~~~~~~~~

.. doxygenclass:: ista::owl2::RDFXMLParser
   :project: ista
   :members:

**Status**: ✅ Fully implemented

The RDF/XML parser provides complete support for parsing OWL 2 ontologies serialized in RDF/XML format.

**Example:**

.. code-block:: cpp

   #include "owl2/parser/rdfxml_parser.hpp"

   // Parse from file
   Ontology onto = RDFXMLParser::parseFromFile("myonto.rdf");

   // Parse from string
   std::string rdfxml_content = "...";
   Ontology onto2 = RDFXMLParser::parse(rdfxml_content);

Turtle Parser
~~~~~~~~~~~~~

.. doxygenclass:: ista::owl2::TurtleParser
   :project: ista
   :members:

**Status**: 🚧 Stub implementation (returns empty ontology)

The Turtle parser will provide support for parsing Turtle format RDF files.

**Example:**

.. code-block:: cpp

   #include "owl2/parser/turtle_parser.hpp"

   // Note: Currently returns empty ontology
   Ontology onto = TurtleParser::parseFromFile("myonto.ttl");

Functional Syntax Parser
~~~~~~~~~~~~~~~~~~~~~~~~~

.. doxygenclass:: ista::owl2::FunctionalParser
   :project: ista
   :members:

**Status**: 🚧 Stub implementation (returns empty ontology)

The Functional Syntax parser will provide support for parsing OWL 2 Functional Syntax files.

**Example:**

.. code-block:: cpp

   #include "owl2/parser/functional_parser.hpp"

   // Note: Currently returns empty ontology
   Ontology onto = FunctionalParser::parseFromFile("myonto.ofn");

Manchester Syntax Parser
~~~~~~~~~~~~~~~~~~~~~~~~~

.. doxygenclass:: ista::owl2::ManchesterParser
   :project: ista
   :members:

**Status**: 🚧 Stub implementation (returns empty ontology)

The Manchester Syntax parser will provide support for parsing Manchester Syntax OWL files.

**Example:**

.. code-block:: cpp

   #include "owl2/parser/manchester_parser.hpp"

   // Note: Currently returns empty ontology
   Ontology onto = ManchesterParser::parseFromFile("myonto.omn");

OWL/XML Parser
~~~~~~~~~~~~~~

.. doxygenclass:: ista::owl2::OWLXMLParser
   :project: ista
   :members:

**Status**: 🚧 Stub implementation (returns empty ontology)

The OWL/XML parser will provide support for parsing OWL/XML format files.

**Example:**

.. code-block:: cpp

   #include "owl2/parser/owlxml_parser.hpp"

   // Note: Currently returns empty ontology
   Ontology onto = OWLXMLParser::parseFromFile("myonto.owx");

CSV Parser
~~~~~~~~~~

.. doxygenclass:: ista::owl2::CSVParser
   :project: ista
   :members:

**Status**: ✅ Fully implemented

The CSV parser provides high-performance parsing of large CSV files to dynamically populate ontologies with individuals and relationships.

**Example:**

.. code-block:: cpp

   #include "owl2/parser/csv_parser.hpp"

   Ontology onto;
   CSVParser parser(onto, "http://example.org/");

   // Parse node types (create individuals)
   NodeTypeConfig nodeConfig;
   nodeConfig.iri_column_name = "id";
   nodeConfig.has_headers = true;
   nodeConfig.data_property_map["name"] = IRI("http://example.org/hasName");

   parser.parse_node_type("people.csv",
                          IRI("http://example.org/Person"),
                          nodeConfig);

   // Parse relationships
   RelationshipTypeConfig relConfig;
   relConfig.subject_column_name = "person_id";
   relConfig.object_column_name = "friend_id";

   parser.parse_relationship_type("friendships.csv",
                                  IRI("http://example.org/knows"),
                                  relConfig);

Parser Exceptions
-----------------

All parsers throw specific exception types derived from ``std::runtime_error``:

.. doxygenclass:: ista::owl2::RDFXMLParseException
   :project: ista
   :members:

.. doxygenclass:: ista::owl2::TurtleParseException
   :project: ista
   :members:

.. doxygenclass:: ista::owl2::FunctionalParseException
   :project: ista
   :members:

.. doxygenclass:: ista::owl2::ManchesterParseException
   :project: ista
   :members:

.. doxygenclass:: ista::owl2::OWLXMLParseException
   :project: ista
   :members:

.. doxygenclass:: ista::owl2::CSVParseException
   :project: ista
   :members:

See Also
--------

* :doc:`serializers` - Serializer documentation
* :doc:`../user_guide/cpp_library` - C++ library user guide
