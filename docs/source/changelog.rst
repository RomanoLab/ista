Changelog
=========

All notable changes to the ista project will be documented in this file.

The format is based on `Keep a Changelog <https://keepachangelog.com/en/1.0.0/>`_,
and this project adheres to `Semantic Versioning <https://semver.org/spec/v2.0.0.html>`_.

[Unreleased]
------------

Added
~~~~~
- Complete Sphinx documentation with Furo theme
- C++ API documentation with Doxygen and Breathe
- Python API documentation with numpydoc
- Comprehensive user guides and examples
- Documentation build scripts (shell, batch, Makefile)

Changed
~~~~~~~
- Updated requirements.txt with documentation dependencies

[0.1.0] - 2024-XX-XX
--------------------

Added
~~~~~
- Initial OWL2 interface implementation in C++
- Python bindings for OWL2 library
- Core entity types: IRI, Literal, Class, ObjectProperty, DataProperty, NamedIndividual
- Ontology container class for managing axioms
- Declaration axioms
- Class axioms: SubClassOf, EquivalentClasses, DisjointClasses
- Property axioms: SubObjectPropertyOf, EquivalentObjectProperties, etc.
- Assertion axioms: ClassAssertion, ObjectPropertyAssertion, DataPropertyAssertion
- Class expressions: intersection, union, complement, restrictions, cardinality
- Annotation support: AnnotationAssertion, AnnotationProperty
- Functional syntax serializer
- Functional syntax parser
- OntologyFilter for subgraph extraction
- FilterCriteria for flexible filtering
- Neighborhood extraction with configurable depth
- Graph converters (NetworkX, pandas DataFrame)
- Database parser for Excel/CSV to OWL2 conversion
- Example projects: AlzKB, NeuroKB
- Test suite for core functionality

Fixed
~~~~~
- Memory management issues with smart pointers
- IRI comparison and hashing
- Parser error handling
- Serialization of complex class expressions

Changed
~~~~~~~
- Reorganized project structure (lib/ and src/ separation)
- Updated C++ code to use C++20 features
- Improved error messages and exception handling

Deprecated
~~~~~~~~~~
- None

Removed
~~~~~~~
- Duplicate struct definitions
- Legacy parsing code

Security
~~~~~~~~
- None

Version History
---------------

Development Milestones
~~~~~~~~~~~~~~~~~~~~~~

The ista project follows these development phases:

**Phase 1: Core Infrastructure** (Completed)
  - C++ OWL2 implementation
  - Python bindings
  - Basic serialization/parsing

**Phase 2: Advanced Features** (Completed)
  - Subgraph extraction
  - Graph converters
  - Database parsing

**Phase 3: Documentation & Testing** (In Progress)
  - Comprehensive documentation
  - Extended test coverage
  - Example projects

**Phase 4: Performance & Optimization** (Planned)
  - Performance benchmarks
  - Memory optimization
  - Parallel processing

**Phase 5: Extended Features** (Planned)
  - Reasoning support
  - Additional serialization formats
  - Query language support

Compatibility Notes
-------------------

Python Compatibility
~~~~~~~~~~~~~~~~~~~~
- Python 3.7+: Full support
- Python 3.6: Not supported (EOL)
- Python 3.11+: Tested and supported

C++ Compatibility
~~~~~~~~~~~~~~~~~
- C++20: Required
- C++17: Not supported (missing required features)
- Compilers:

  - GCC 10+: Supported
  - Clang 11+: Supported
  - MSVC 2019+: Supported

Platform Support
~~~~~~~~~~~~~~~~
- Linux: Fully supported
- macOS: Fully supported
- Windows: Fully supported (MSYS2, MinGW, MSVC)

Breaking Changes
----------------

None yet (pre-1.0.0 release)

Migration Guides
----------------

Future migration guides will be added here when breaking changes occur.

Contributing
------------

See :doc:`contributing` for information on how to contribute to ista.

Links
-----

- Repository: https://github.com/JDRomano2/ista
- Issue Tracker: https://github.com/JDRomano2/ista/issues
- Documentation: https://ista.readthedocs.io/ (if hosted)
