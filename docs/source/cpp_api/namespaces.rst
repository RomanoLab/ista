Namespaces
==========

The libista library uses a hierarchical namespace structure to organize its components.

Main Namespace
--------------

ista
~~~~

The top-level namespace for all ista components.

ista::owl2
~~~~~~~~~~

The main namespace for OWL 2 functionality. All core classes, parsers, and serializers are in this namespace.

**Usage:**

.. code-block:: cpp

   using namespace ista::owl2;

   Ontology onto;
   Class person(IRI("http://example.org/Person"));

Sub-namespaces
--------------

xsd
~~~

Contains constants for XSD datatype IRIs.

**Members:**

* ``xsd::STRING`` - ``http://www.w3.org/2001/XMLSchema#string``
* ``xsd::INTEGER`` - ``http://www.w3.org/2001/XMLSchema#integer``
* ``xsd::INT`` - ``http://www.w3.org/2001/XMLSchema#int``
* ``xsd::LONG`` - ``http://www.w3.org/2001/XMLSchema#long``
* ``xsd::DOUBLE`` - ``http://www.w3.org/2001/XMLSchema#double``
* ``xsd::FLOAT`` - ``http://www.w3.org/2001/XMLSchema#float``
* ``xsd::BOOLEAN`` - ``http://www.w3.org/2001/XMLSchema#boolean``
* ``xsd::DATE_TIME`` - ``http://www.w3.org/2001/XMLSchema#dateTime``
* ``xsd::DATE`` - ``http://www.w3.org/2001/XMLSchema#date``

**Example:**

.. code-block:: cpp

   Literal age("30", xsd::INTEGER);
   Literal height("1.75", xsd::DOUBLE);

facets
~~~~~~

Contains constants for XSD facet IRIs used in datatype restrictions.

**Members:**

* ``facets::MIN_INCLUSIVE`` - Minimum inclusive value
* ``facets::MAX_INCLUSIVE`` - Maximum inclusive value
* ``facets::MIN_EXCLUSIVE`` - Minimum exclusive value
* ``facets::MAX_EXCLUSIVE`` - Maximum exclusive value
* ``facets::LENGTH`` - Exact length
* ``facets::MIN_LENGTH`` - Minimum length
* ``facets::MAX_LENGTH`` - Maximum length
* ``facets::PATTERN`` - Regular expression pattern

**Example:**

.. code-block:: cpp

   std::vector<std::pair<IRI, Literal>> restrictions;
   restrictions.push_back({facets::MIN_INCLUSIVE, Literal("0", xsd::INTEGER)});
   restrictions.push_back({facets::MAX_INCLUSIVE, Literal("120", xsd::INTEGER)});

   auto ageRange = std::make_shared<DatatypeRestriction>(
       Datatype(xsd::INTEGER), restrictions);

Type Aliases
------------

The library provides several type aliases for commonly used types:

.. code-block:: cpp

   // Shared pointers for class expressions and data ranges
   using ClassExpressionPtr = std::shared_ptr<ClassExpression>;
   using DataRangePtr = std::shared_ptr<DataRange>;

   // Variant types for polymorphic entities
   using Individual = std::variant<NamedIndividual, AnonymousIndividual>;
   using ObjectPropertyExpression = std::variant<ObjectProperty, InverseObjectProperty>;
   using AnnotationSubject = std::variant<IRI, AnonymousIndividual>;
   using AnnotationValue = std::variant<IRI, Literal, AnonymousIndividual>;

**Example:**

.. code-block:: cpp

   // Using ClassExpressionPtr
   ClassExpressionPtr personClass = std::make_shared<NamedClass>(
       Class(IRI("http://example.org/Person")));

   // Using Individual variant
   Individual alice = NamedIndividual(IRI("http://example.org/Alice"));
   Individual blankNode = AnonymousIndividual("_:b1");

Include Headers
---------------

Primary Header
~~~~~~~~~~~~~~

For most use cases, include the main header:

.. code-block:: cpp

   #include "owl2/owl2.hpp"

This includes all core functionality, axioms, class expressions, and data ranges.

Specific Components
~~~~~~~~~~~~~~~~~~~

For specific components, include their headers directly:

.. code-block:: cpp

   // Parsers
   #include "owl2/parser/rdfxml_parser.hpp"
   #include "owl2/parser/csv_parser.hpp"
   #include "owl2/parser/turtle_parser.hpp"
   #include "owl2/parser/functional_parser.hpp"
   #include "owl2/parser/manchester_parser.hpp"
   #include "owl2/parser/owlxml_parser.hpp"

   // Serializers
   #include "owl2/serializer/rdfxml_serializer.hpp"
   #include "owl2/serializer/functional_serializer.hpp"
   #include "owl2/serializer/turtle_serializer.hpp"
   #include "owl2/serializer/manchester_serializer.hpp"
   #include "owl2/serializer/owlxml_serializer.hpp"

   // Subgraph extraction
   #include "owl2/core/ontology_filter.hpp"

Best Practices
--------------

Using Declarations
~~~~~~~~~~~~~~~~~~

For cleaner code, use namespace declarations:

.. code-block:: cpp

   // Option 1: Using directive (imports all names)
   using namespace ista::owl2;

   Ontology onto;
   Class person(IRI("http://example.org/Person"));

.. code-block:: cpp

   // Option 2: Using declarations (imports specific names)
   using ista::owl2::Ontology;
   using ista::owl2::Class;
   using ista::owl2::IRI;

   Ontology onto;
   Class person(IRI("http://example.org/Person"));

.. code-block:: cpp

   // Option 3: Namespace alias
   namespace owl2 = ista::owl2;

   owl2::Ontology onto;
   owl2::Class person(owl2::IRI("http://example.org/Person"));

See Also
--------

* :doc:`core` - Core classes documentation
* :doc:`parsers` - Parser documentation
* :doc:`serializers` - Serializer documentation
* :doc:`../user_guide/cpp_library` - C++ library user guide
