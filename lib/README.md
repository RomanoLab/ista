# libista - OWL2 Ontology Library

A modern C++20 library for working with OWL2 (Web Ontology Language 2) ontologies. Part of the **ista** toolkit for manipulating and building knowledge graphs.

> **ista** _N._ [ˈistɑ] — (Sindarin) Knowledge

## Overview

**libista** is a high-performance C++ library for creating, manipulating, and serializing OWL2 ontologies. It provides a clean, type-safe API that closely follows the OWL2 specification, making it suitable for both research and production use cases in semantic web applications, knowledge representation, and ontology engineering.

The library is designed with the following principles:

- **Type Safety**: Strong typing throughout the API to catch errors at compile time
- **Performance**: Efficient C++20 implementation suitable for large-scale ontologies
- **Completeness**: Comprehensive coverage of OWL2 constructs including all axiom types
- **Ease of Use**: Intuitive API that mirrors the OWL2 specification
- **Extensibility**: Modular design allowing for custom parsers and serializers

## Features

- **Complete OWL2 Support**
  - All entity types (Classes, ObjectProperty, DataProperty, AnnotationProperty, NamedIndividual)
  - Full class expression support (intersection, union, restrictions, etc.)
  - Data ranges with facet restrictions
  - All axiom types (declarations, class axioms, property axioms, assertions, etc.)
  - Annotations with nested annotation support

- **IRI Management**
  - Full and abbreviated IRI forms
  - Prefix registration and resolution
  - Automatic namespace handling

- **Ontology Management**
  - Ontology metadata (IRI, version IRI, imports)
  - Axiom queries by type and entity
  - Entity extraction and counting
  - Statistics generation

- **Serialization**
  - OWL2 Functional Syntax output
  - Pretty-printed format with configurable indentation
  - File and string serialization

- **Modern C++ Design**
  - C++20 standard
  - Smart pointers for memory safety
  - STL containers for efficiency
  - Optional and variant types for clarity

## Project Structure

```
lib/
├── CMakeLists.txt          # Build configuration
├── README.md               # This file
└── owl2/                   # OWL2 library implementation
    ├── README.md           # Technical implementation details
    ├── owl2.hpp            # Main include file
    ├── entity.hpp          # Entity type shortcuts (deprecated)
    ├── core/               # Core OWL2 structures
    │   ├── iri.hpp/cpp             # IRI implementation
    │   ├── entity.hpp/cpp          # Entity types (Class, Property, etc.)
    │   ├── literal.hpp/cpp         # Literal values and XSD datatypes
    │   ├── annotation.hpp/cpp      # Annotations
    │   ├── class_expression.hpp/cpp # Class expressions
    │   ├── data_range.hpp/cpp      # Data ranges
    │   ├── axiom.hpp/cpp           # All axiom types
    │   └── ontology.hpp/cpp        # Ontology container
    ├── serializer/         # Serialization implementations
    │   └── functional_serializer.hpp/cpp
    └── parser/             # Parser implementations (planned)
```

## Building

### Prerequisites

- C++20 compatible compiler (GCC 10+, Clang 12+, MSVC 2019+)
- CMake 3.15 or higher

### Build Instructions

```bash
# From the project root directory
mkdir build
cd build
cmake ..
cmake --build .
```

The library will be built as a static library that can be linked into your applications.

### Integration into Your Project

#### Using CMake

Add the following to your `CMakeLists.txt`:

```cmake
add_subdirectory(path/to/ista/lib)
target_link_libraries(your_target owl2)
```

#### Manual Integration

Include the library headers and link against the built library:

```cpp
#include "owl2/owl2.hpp"
```

## Quick Start

Here's a simple example that creates an ontology with classes, properties, and individuals:

```cpp
#include <iostream>
#include "owl2/owl2.hpp"

using namespace ista::owl2;

int main() {
    // Create an ontology
    IRI ontology_iri("http://example.org/university");
    IRI version_iri("http://example.org/university/1.0");
    Ontology onto(ontology_iri, version_iri);
    
    // Register prefixes for convenience
    onto.registerPrefix("uni", "http://example.org/university#");
    
    // Create and declare classes
    Class person(IRI("uni", "Person", "http://example.org/university#"));
    Class student(IRI("uni", "Student", "http://example.org/university#"));
    
    onto.addAxiom(std::make_shared<Declaration>(
        Declaration::EntityType::CLASS, person.getIRI()));
    onto.addAxiom(std::make_shared<Declaration>(
        Declaration::EntityType::CLASS, student.getIRI()));
    
    // Add subclass relationship
    auto student_expr = std::make_shared<NamedClass>(student);
    auto person_expr = std::make_shared<NamedClass>(person);
    onto.addAxiom(std::make_shared<SubClassOf>(student_expr, person_expr));
    
    // Create object property
    ObjectProperty teaches(IRI("uni", "teaches", "http://example.org/university#"));
    onto.addAxiom(std::make_shared<Declaration>(
        Declaration::EntityType::OBJECT_PROPERTY, teaches.getIRI()));
    
    // Create individuals
    NamedIndividual john(IRI("uni", "John", "http://example.org/university#"));
    NamedIndividual mary(IRI("uni", "Mary", "http://example.org/university#"));
    
    onto.addAxiom(std::make_shared<Declaration>(
        Declaration::EntityType::NAMED_INDIVIDUAL, john.getIRI()));
    onto.addAxiom(std::make_shared<Declaration>(
        Declaration::EntityType::NAMED_INDIVIDUAL, mary.getIRI()));
    
    // Assert types and relationships
    onto.addAxiom(std::make_shared<ClassAssertion>(person_expr, john));
    onto.addAxiom(std::make_shared<ClassAssertion>(student_expr, mary));
    onto.addAxiom(std::make_shared<ObjectPropertyAssertion>(teaches, john, mary));
    
    // Print statistics
    std::cout << onto.getStatistics() << std::endl;
    
    // Serialize to Functional Syntax
    std::string output = onto.toFunctionalSyntax();
    std::cout << output << std::endl;
    
    // Save to file
    FunctionalSyntaxSerializer::serializeToFile(onto, "university.ofn");
    
    return 0;
}
```

For a more complete example, see `src/ista.cpp`.

## API Overview

### Core Classes

#### IRI

Represents Internationalized Resource Identifiers used throughout OWL2:

```cpp
// Full IRI
IRI full("http://example.org/ontology#Class1");

// Abbreviated IRI with prefix
IRI abbrev("ex", "Class1", "http://example.org/ontology#");

// Access components
std::string full_iri = iri.getFullIRI();
std::optional<std::string> prefix = iri.getPrefix();
std::string abbreviated = iri.getAbbreviated();
```

#### Entity Types

All OWL2 entities inherit from the base `Entity` class:

- **Class**: Represents OWL classes
- **Datatype**: Represents XSD and custom datatypes
- **ObjectProperty**: Properties relating individuals to individuals
- **DataProperty**: Properties relating individuals to literals
- **AnnotationProperty**: Properties for metadata annotations
- **NamedIndividual**: Named instances in the ontology
- **AnonymousIndividual**: Blank nodes

```cpp
Class person(IRI("http://example.org#Person"));
ObjectProperty knows(IRI("http://example.org#knows"));
DataProperty age(IRI("http://example.org#age"));
NamedIndividual john(IRI("http://example.org#John"));
```

#### Literal

Represents data values with optional language tags or datatypes:

```cpp
// Plain literal with language tag
Literal label("Hello", "en");

// Typed literal
Literal age("25", xsd::INTEGER);
Literal pi("3.14159", xsd::DOUBLE);
Literal active("true", xsd::BOOLEAN);
```

Common XSD datatypes are available in the `xsd` namespace: `STRING`, `INTEGER`, `INT`, `LONG`, `DOUBLE`, `FLOAT`, `BOOLEAN`, `DATE_TIME`, `DATE`.

#### ClassExpression

Represents complex class descriptions:

- **NamedClass**: Wrapper for a Class entity
- **ObjectIntersectionOf**: Intersection of class expressions (AND)
- **ObjectUnionOf**: Union of class expressions (OR)
- **ObjectSomeValuesFrom**: Existential restriction (∃)
- **ObjectAllValuesFrom**: Universal restriction (∀)

```cpp
auto person = std::make_shared<NamedClass>(Class(IRI("ex:Person")));
auto student = std::make_shared<NamedClass>(Class(IRI("ex:Student")));

// Person AND Student
auto intersection = std::make_shared<ObjectIntersectionOf>(
    std::vector<ClassExpressionPtr>{person, student});

// ∃ teaches.Student (things that teach some student)
auto restriction = std::make_shared<ObjectSomeValuesFrom>(
    ObjectProperty(IRI("ex:teaches")), student);
```

#### DataRange

Represents sets of data values:

- **NamedDatatype**: Reference to a datatype
- **DataIntersectionOf**: Intersection of data ranges
- **DataUnionOf**: Union of data ranges
- **DataComplementOf**: Complement of a data range
- **DataOneOf**: Enumeration of specific values
- **DatatypeRestriction**: Datatype with facet constraints

```cpp
// Integers between 18 and 65
auto intType = std::make_shared<NamedDatatype>(Datatype(xsd::INTEGER));
auto restriction = std::make_shared<DatatypeRestriction>(
    Datatype(xsd::INTEGER),
    std::vector<DatatypeRestriction::FacetRestriction>{
        {facets::MIN_INCLUSIVE, Literal("18", xsd::INTEGER)},
        {facets::MAX_INCLUSIVE, Literal("65", xsd::INTEGER)}
    });
```

#### Axiom Hierarchy

The library supports all OWL2 axiom types organized into categories:

**Declaration Axioms**
- `Declaration`: Declares an entity exists

**Class Axioms**
- `SubClassOf`: Class hierarchy
- `EquivalentClasses`: Class equivalence
- `DisjointClasses`: Pairwise disjoint classes
- `DisjointUnion`: Disjoint union definition

**Object Property Axioms**
- `SubObjectPropertyOf`: Property hierarchy (including chains)
- `EquivalentObjectProperties`: Property equivalence
- `DisjointObjectProperties`: Pairwise disjoint properties
- `InverseObjectProperties`: Inverse property relationships
- `ObjectPropertyDomain`: Domain restrictions
- `ObjectPropertyRange`: Range restrictions
- `FunctionalObjectProperty`: Functional characteristic
- `InverseFunctionalObjectProperty`: Inverse functional characteristic
- `ReflexiveObjectProperty`, `IrreflexiveObjectProperty`: Reflexivity
- `SymmetricObjectProperty`, `AsymmetricObjectProperty`: Symmetry
- `TransitiveObjectProperty`: Transitivity

**Data Property Axioms**
- `SubDataPropertyOf`: Property hierarchy
- `EquivalentDataProperties`: Property equivalence
- `DisjointDataProperties`: Pairwise disjoint properties
- `DataPropertyDomain`: Domain restrictions
- `DataPropertyRange`: Range restrictions
- `FunctionalDataProperty`: Functional characteristic

**Assertion Axioms**
- `ClassAssertion`: Type assertions for individuals
- `ObjectPropertyAssertion`: Object property facts
- `DataPropertyAssertion`: Data property facts
- `NegativeObjectPropertyAssertion`: Negative object property facts
- `NegativeDataPropertyAssertion`: Negative data property facts
- `SameIndividual`: Individual equality
- `DifferentIndividuals`: Individual inequality

**Annotation Axioms**
- `AnnotationAssertion`: Attach annotations to entities
- `SubAnnotationPropertyOf`: Annotation property hierarchy
- `AnnotationPropertyDomain`: Domain for annotation properties
- `AnnotationPropertyRange`: Range for annotation properties

**Other Axioms**
- `DatatypeDefinition`: Define custom datatypes
- `HasKey`: Define keys for classes

#### Ontology

The main container for ontology data:

```cpp
// Create ontology
Ontology onto(IRI("http://example.org/onto"), IRI("http://example.org/onto/v1.0"));

// Metadata
onto.setOntologyIRI(IRI("http://example.org/new"));
onto.addImport(IRI("http://other.org/imported"));
onto.addOntologyAnnotation(Annotation(rdfsLabel, Literal("My Ontology")));

// Prefix management
onto.registerPrefix("ex", "http://example.org#");
auto ns = onto.getNamespaceForPrefix("ex");

// Axiom management
onto.addAxiom(axiom);
onto.removeAxiom(axiom);
bool has = onto.containsAxiom(axiom);

// Query axioms
auto declarations = onto.getDeclarationAxioms();
auto classAxioms = onto.getClassAxioms();
auto subClassAxioms = onto.getSubClassAxiomsForSubClass(myClass);

// Entity queries
auto classes = onto.getClasses();
auto properties = onto.getObjectProperties();
bool hasClass = onto.containsClass(myClass);

// Statistics
size_t axiomCount = onto.getAxiomCount();
size_t classCount = onto.getClassCount();
std::string stats = onto.getStatistics();

// Serialization
std::string functional = onto.toFunctionalSyntax();
```

## Examples

The `src/ista.cpp` file contains a comprehensive example demonstrating:

- Creating an ontology with metadata
- Declaring classes, properties, and individuals
- Building class hierarchies with subclass relationships
- Defining property domains and ranges
- Creating functional properties
- Asserting individual types and property values
- Working with literals and datatypes
- Serializing to Functional Syntax
- Saving to files

To run the example:

```bash
cd build
./ista
```

This will create a university ontology and save it to `university.ofn`.

## Serialization

### OWL2 Functional Syntax

The library currently supports serialization to OWL2 Functional Syntax, a human-readable text format that directly represents the abstract syntax of OWL2.

```cpp
// Serialize entire ontology
std::string output = onto.toFunctionalSyntax();

// Serialize with custom indentation
std::string output = onto.toFunctionalSyntax("    ");

// Save to file
FunctionalSyntaxSerializer::serializeToFile(onto, "output.ofn");

// Using the serializer directly
std::string output = FunctionalSyntaxSerializer::serialize(onto);
```

The output follows the OWL2 Functional Syntax specification and includes:
- Prefix declarations
- Ontology metadata (IRI, version, imports, annotations)
- All axioms organized by type
- Proper nesting and indentation

Example output:
```
Prefix(ex:=<http://example.org/university#>)

Ontology(<http://example.org/university> <http://example.org/university/1.0>

Declaration(Class(ex:Person))
Declaration(Class(ex:Student))
SubClassOf(ex:Student ex:Person)

Declaration(ObjectProperty(ex:teaches))
ObjectPropertyDomain(ex:teaches ex:Professor)
ObjectPropertyRange(ex:teaches ex:Student)

Declaration(NamedIndividual(ex:John))
ClassAssertion(ex:Professor ex:John)
)
```

## Future Work

### Planned Features

- **RDF/XML Parser**: Read ontologies from RDF/XML files
  - Requires integration with XML library (libxml2, pugixml, or rapidxml)
  - Full OWL2 RDF mapping support

- **Turtle Parser/Serializer**: Support for the popular Turtle format
  - More concise than RDF/XML
  - Better suited for version control

- **Manchester Syntax**: Support for the user-friendly Manchester Syntax
  - Parser for reading .omn files
  - Serializer for writing human-readable ontologies

- **Python Bindings**: PyBind11-based Python interface
  - Pythonic API wrapping the C++ library
  - Integration with popular Python ontology tools
  - NumPy/Pandas integration for analysis

- **Reasoner Integration**: Interfaces for OWL2 reasoners
  - HermiT, Pellet, or custom reasoner integration
  - Classification and consistency checking
  - Query answering

- **Performance Optimizations**
  - Ontology indexing for faster queries
  - Memory-mapped file support for large ontologies
  - Parallel axiom processing

- **Additional Serialization Formats**
  - OWL/XML
  - JSON-LD
  - OBO format

- **Validation and Linting**
  - OWL2 profile checking (EL, QL, RL)
  - Best practice recommendations
  - Structural validation

## Contributing

Contributions are welcome! The library is part of the larger **ista** project for knowledge graph manipulation.

### Development Guidelines

- Follow the existing code style (C++20 standard library patterns)
- Add tests for new features
- Update documentation for API changes
- Ensure backward compatibility where possible

## License

This library is released under the MIT License. See the `LICENSE` file in the project root for details.

```
MIT License

Copyright (c) 2022 Joseph D. Romano

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## References

- [OWL2 Web Ontology Language Document Overview](https://www.w3.org/TR/owl2-overview/)
- [OWL2 Structural Specification](https://www.w3.org/TR/owl2-syntax/)
- [OWL2 Functional Syntax](https://www.w3.org/TR/owl2-syntax/#Functional-Style_Syntax)
- [OWL2 Primer](https://www.w3.org/TR/owl2-primer/)

## Support

For questions, issues, or feature requests, please file an issue on the project repository.
