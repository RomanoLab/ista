Core Classes
============

This section documents the core data structures that form the foundation of the libista OWL 2 library.

IRI - Internationalized Resource Identifier
--------------------------------------------

.. doxygenclass:: ista::owl2::IRI
   :project: ista
   :members:

The IRI class represents Internationalized Resource Identifiers, the fundamental naming mechanism in OWL 2.

**Example:**

.. code-block:: cpp

   // Full IRI
   IRI person("http://example.org/Person");

   // Abbreviated IRI with prefix
   IRI name("ex", "hasName", "http://example.org/");

   // Get string representations
   std::string full = person.getFullIRI();  // "http://example.org/Person"
   std::string abbrev = name.getAbbreviated();  // "ex:hasName"

Literal - Data Values
---------------------

.. doxygenclass:: ista::owl2::Literal
   :project: ista
   :members:

The Literal class represents typed or language-tagged data values.

**Example:**

.. code-block:: cpp

   // Plain literal with language tag
   Literal label("Alice", "en");

   // Typed literal
   Literal age("30", xsd::INTEGER);

   // Check properties
   bool hasLang = label.hasLanguageTag();  // true
   bool isTyped = age.isTyped();  // true

Entity Types
------------

Base Entity Class
~~~~~~~~~~~~~~~~~

.. doxygenclass:: ista::owl2::Entity
   :project: ista
   :members:

Class
~~~~~

.. doxygenclass:: ista::owl2::Class
   :project: ista
   :members:

**Example:**

.. code-block:: cpp

   Class person(IRI("http://example.org/Person"));
   IRI classIRI = person.getIRI();
   std::string type = person.getEntityType();  // "Class"

ObjectProperty
~~~~~~~~~~~~~~

.. doxygenclass:: ista::owl2::ObjectProperty
   :project: ista
   :members:

**Example:**

.. code-block:: cpp

   ObjectProperty knows(IRI("http://example.org/knows"));

DataProperty
~~~~~~~~~~~~

.. doxygenclass:: ista::owl2::DataProperty
   :project: ista
   :members:

**Example:**

.. code-block:: cpp

   DataProperty hasAge(IRI("http://example.org/hasAge"));

AnnotationProperty
~~~~~~~~~~~~~~~~~~

.. doxygenclass:: ista::owl2::AnnotationProperty
   :project: ista
   :members:

**Example:**

.. code-block:: cpp

   AnnotationProperty label(IRI("http://www.w3.org/2000/01/rdf-schema#label"));

NamedIndividual
~~~~~~~~~~~~~~~

.. doxygenclass:: ista::owl2::NamedIndividual
   :project: ista
   :members:

**Example:**

.. code-block:: cpp

   NamedIndividual alice(IRI("http://example.org/Alice"));

AnonymousIndividual
~~~~~~~~~~~~~~~~~~~

.. doxygenclass:: ista::owl2::AnonymousIndividual
   :project: ista
   :members:

**Example:**

.. code-block:: cpp

   AnonymousIndividual blank("_:b1");

Datatype
~~~~~~~~

.. doxygenclass:: ista::owl2::Datatype
   :project: ista
   :members:

**Example:**

.. code-block:: cpp

   Datatype intType(xsd::INTEGER);

Annotation
----------

.. doxygenclass:: ista::owl2::Annotation
   :project: ista
   :members:

**Example:**

.. code-block:: cpp

   AnnotationProperty rdfsLabel(IRI("http://www.w3.org/2000/01/rdf-schema#label"));
   Literal labelValue("Person", "en");
   Annotation ann(rdfsLabel, AnnotationValue(labelValue));

Ontology Container
------------------

.. doxygenclass:: ista::owl2::Ontology
   :project: ista
   :members:

The Ontology class is the main container for OWL 2 axioms and provides comprehensive query and manipulation capabilities.

**Example:**

.. code-block:: cpp

   // Create ontology with IRI
   Ontology onto(IRI("http://example.org/myonto"));

   // Register prefixes
   onto.registerPrefix("ex", "http://example.org/");
   onto.registerPrefix("foaf", "http://xmlns.com/foaf/0.1/");

   // Create and add axioms
   Class person(IRI("ex", "Person", "http://example.org/"));
   auto decl = std::make_shared<Declaration>(
       Declaration::EntityType::CLASS, person.getIRI());
   onto.addAxiom(decl);

   // Query
   auto classes = onto.getClasses();
   size_t axiomCount = onto.getAxiomCount();

   // Statistics
   std::string stats = onto.getStatistics();

XSD Datatypes
-------------

The library provides constants for standard XSD datatypes:

.. code-block:: cpp

   namespace xsd {
       extern const IRI STRING;
       extern const IRI INTEGER;
       extern const IRI INT;
       extern const IRI LONG;
       extern const IRI DOUBLE;
       extern const IRI FLOAT;
       extern const IRI BOOLEAN;
       extern const IRI DATE_TIME;
       extern const IRI DATE;
   }

**Example:**

.. code-block:: cpp

   Literal name("Alice", xsd::STRING);
   Literal age("30", xsd::INTEGER);
   Literal height("1.75", xsd::DOUBLE);
   Literal active("true", xsd::BOOLEAN);

See Also
--------

* :doc:`../user_guide/cpp_library` - C++ library user guide
* :doc:`index` - C++ API overview
