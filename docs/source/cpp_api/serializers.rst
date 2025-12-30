Serializers
===========

The libista library provides serializers for multiple OWL 2 serialization formats.

Overview
--------

All serializers follow a consistent interface with static methods for serializing to strings and files.

Available Serializers
---------------------

RDF/XML Serializer
~~~~~~~~~~~~~~~~~~

.. doxygenclass:: ista::owl2::RDFXMLSerializer
   :project: ista
   :members:

**Status**: ✅ Fully implemented

The RDF/XML serializer provides complete support for serializing OWL 2 ontologies to RDF/XML format.

**Example:**

.. code-block:: cpp

   #include "owl2/serializer/rdfxml_serializer.hpp"

   Ontology onto;
   // ... populate ontology ...

   // Serialize to file
   RDFXMLSerializer::serializeToFile(onto, "output.rdf");

   // Serialize to string
   std::string rdfxml = RDFXMLSerializer::serialize(onto);

Functional Syntax Serializer
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. doxygenclass:: ista::owl2::FunctionalSyntaxSerializer
   :project: ista
   :members:

**Status**: ✅ Fully implemented

The Functional Syntax serializer provides complete support for serializing OWL 2 ontologies to Functional Syntax format.

**Example:**

.. code-block:: cpp

   #include "owl2/serializer/functional_serializer.hpp"

   Ontology onto;
   // ... populate ontology ...

   // Serialize to file
   FunctionalSyntaxSerializer::serializeToFile(onto, "output.ofn");

   // Serialize to string with custom indentation
   std::string functional = FunctionalSyntaxSerializer::serialize(onto, "  ");

Turtle Serializer
~~~~~~~~~~~~~~~~~

.. doxygenclass:: ista::owl2::TurtleSerializer
   :project: ista
   :members:

**Status**: 🚧 Stub implementation (throws exception)

The Turtle serializer will provide support for serializing ontologies to Turtle format RDF.

**Example:**

.. code-block:: cpp

   #include "owl2/serializer/turtle_serializer.hpp"

   Ontology onto;
   // ... populate ontology ...

   // Note: Currently throws std::runtime_error
   // std::string turtle = TurtleSerializer::serialize(onto);

   // With custom prefixes (also throws)
   // std::map<std::string, std::string> prefixes;
   // prefixes["ex"] = "http://example.org/";
   // std::string turtle = TurtleSerializer::serialize(onto, prefixes);

Manchester Syntax Serializer
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. doxygenclass:: ista::owl2::ManchesterSerializer
   :project: ista
   :members:

**Status**: 🚧 Stub implementation (throws exception)

The Manchester Syntax serializer will provide support for serializing ontologies to Manchester Syntax.

**Example:**

.. code-block:: cpp

   #include "owl2/serializer/manchester_serializer.hpp"

   Ontology onto;
   // ... populate ontology ...

   // Note: Currently throws std::runtime_error
   // std::string manchester = ManchesterSerializer::serialize(onto);

OWL/XML Serializer
~~~~~~~~~~~~~~~~~~

.. doxygenclass:: ista::owl2::OWLXMLSerializer
   :project: ista
   :members:

**Status**: 🚧 Stub implementation (throws exception)

The OWL/XML serializer will provide support for serializing ontologies to OWL/XML format.

**Example:**

.. code-block:: cpp

   #include "owl2/serializer/owlxml_serializer.hpp"

   Ontology onto;
   // ... populate ontology ...

   // Note: Currently throws std::runtime_error
   // std::string owlxml = OWLXMLSerializer::serialize(onto);

Serializer Best Practices
--------------------------

Choosing a Format
~~~~~~~~~~~~~~~~~

* **RDF/XML**: Best for interoperability with RDF tools and triple stores
* **Functional Syntax**: Most readable for humans, good for version control
* **Turtle**: Compact RDF format (coming soon)
* **Manchester Syntax**: Domain-specific, very readable (coming soon)
* **OWL/XML**: XML-based, good for XML toolchains (coming soon)

Performance Considerations
~~~~~~~~~~~~~~~~~~~~~~~~~~~

All serializers are optimized for performance:

* **Streaming**: Serializers write directly to output streams
* **Memory efficient**: No intermediate representations
* **Prefix optimization**: Automatic prefix management for compact output

Error Handling
~~~~~~~~~~~~~~

Serializers may throw exceptions during serialization:

.. code-block:: cpp

   try {
       RDFXMLSerializer::serializeToFile(onto, "output.rdf");
   } catch (const std::runtime_error& e) {
       std::cerr << "Serialization failed: " << e.what() << std::endl;
   }

Custom Prefixes
~~~~~~~~~~~~~~~

Some serializers support custom prefix mappings:

.. code-block:: cpp

   // Register prefixes in ontology
   onto.registerPrefix("foaf", "http://xmlns.com/foaf/0.1/");
   onto.registerPrefix("dc", "http://purl.org/dc/elements/1.1/");

   // Serializers will use registered prefixes
   std::string output = FunctionalSyntaxSerializer::serialize(onto);

See Also
--------

* :doc:`parsers` - Parser documentation
* :doc:`../user_guide/cpp_library` - C++ library user guide
