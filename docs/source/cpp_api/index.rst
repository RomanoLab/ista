C++ API Reference
=================

This section documents the C++ API for the libista library.

.. note::
   C++ documentation is generated from source code using Doxygen and Breathe.
   To build the C++ documentation, you need to have Doxygen installed and run:

   .. code-block:: bash

      cd docs
      doxygen Doxyfile

Overview
--------

The libista C++ library provides a complete implementation of the OWL2 structural specification
with modern C++20 features for type safety and performance.

.. toctree::
   :maxdepth: 2
   :caption: C++ API Sections:

   core
   serializers
   parsers
   namespaces

Library Structure
-----------------

The library is organized into several namespaces:

* ``ista::owl2`` - Main namespace for OWL2 functionality
* ``ista::owl2::core`` - Core data structures
* ``ista::owl2::serializer`` - Serialization formats
* ``ista::owl2::parser`` - Parsing functionality

Key Classes
-----------

Core Types
~~~~~~~~~~

.. doxygenclass:: ista::owl2::IRI
   :project: ista
   :members:

.. doxygenclass:: ista::owl2::Literal
   :project: ista
   :members:

Entity Types
~~~~~~~~~~~~

.. doxygenclass:: ista::owl2::Entity
   :project: ista
   :members:

.. doxygenclass:: ista::owl2::Class
   :project: ista
   :members:

.. doxygenclass:: ista::owl2::ObjectProperty
   :project: ista
   :members:

.. doxygenclass:: ista::owl2::DataProperty
   :project: ista
   :members:

.. doxygenclass:: ista::owl2::NamedIndividual
   :project: ista
   :members:

Ontology Container
~~~~~~~~~~~~~~~~~~

.. doxygenclass:: ista::owl2::Ontology
   :project: ista
   :members:

Subgraph Extraction
~~~~~~~~~~~~~~~~~~~

.. doxygenclass:: ista::owl2::OntologyFilter
   :project: ista
   :members:

.. doxygenclass:: ista::owl2::FilterCriteria
   :project: ista
   :members:

.. doxygenclass:: ista::owl2::FilterResult
   :project: ista
   :members:

Usage Example
-------------

.. code-block:: cpp

   #include "owl2/owl2.hpp"
   using namespace ista::owl2;

   int main() {
       // Create ontology
       Ontology onto(IRI("http://example.org/myonto"));
       onto.registerPrefix("ex", "http://example.org/myonto#");

       // Create entities
       Class person(IRI("ex", "Person", "http://example.org/myonto#"));
       NamedIndividual alice(IRI("ex", "Alice", "http://example.org/myonto#"));

       // Add axioms
       onto.addAxiom(std::make_shared<Declaration>(
           Declaration::EntityType::CLASS, person.getIRI()));
       onto.addAxiom(std::make_shared<ClassAssertion>(
           std::make_shared<NamedClass>(person),
           Individual(alice)));

       // Serialize
       FunctionalSyntaxSerializer::serializeToFile(onto, "output.ofn");

       return 0;
   }

Building the Documentation
---------------------------

To generate the C++ API documentation:

.. code-block:: bash

   # Install Doxygen (platform-specific)
   # Ubuntu/Debian:
   sudo apt install doxygen

   # macOS:
   brew install doxygen

   # Windows: Download from doxygen.org

   # Generate XML documentation
   cd docs
   doxygen Doxyfile

   # Build HTML documentation with Sphinx
   cd ..
   sphinx-build -b html docs/source docs/build/html

See Also
--------

* :doc:`../user_guide/cpp_library` - C++ library user guide
* :doc:`../examples` - Example programs
