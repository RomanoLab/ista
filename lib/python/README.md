# Python Bindings for libista OWL2

This directory contains comprehensive pybind11 bindings for the libista OWL2 library, enabling full OWL2 ontology manipulation from Python.

## Overview

The bindings expose the complete C++ API to Python, including:

- **Core OWL2 Classes**: IRI, Entity types (Class, ObjectProperty, DataProperty, NamedIndividual, etc.)
- **Literals**: Typed and plain literals with language tags
- **Class Expressions**: NamedClass, ObjectIntersectionOf, ObjectUnionOf, ObjectSomeValuesFrom, ObjectAllValuesFrom
- **Data Ranges**: NamedDatatype, DataIntersectionOf, DataUnionOf, DataComplementOf, DataOneOf, DatatypeRestriction
- **Axioms**: All OWL2 axiom types including:
  - Declaration axioms
  - Class axioms (SubClassOf, EquivalentClasses, DisjointClasses, etc.)
  - Object property axioms (SubObjectPropertyOf, domain, range, characteristics)
  - Data property axioms (SubDataPropertyOf, domain, range, functional)
  - Assertion axioms (ClassAssertion, PropertyAssertion, etc.)
  - Annotation axioms
- **Ontology**: Complete ontology management with prefix handling, axiom queries, and statistics
- **Serialization**: FunctionalSyntaxSerializer for OWL2 Functional Syntax output

## Building

### Prerequisites

1. **CMake** 3.15 or later
2. **C++20 compatible compiler** (GCC 10+, Clang 10+, MSVC 2019+)
3. **Python** 3.7 or later with development headers
4. **pybind11**

### Installing pybind11

You have several options to install pybind11:

#### Option 1: System-wide installation via pip
```bash
pip install pybind11
```

#### Option 2: As a git submodule in the project
```bash
# From the project root
git submodule add https://github.com/pybind/pybind11.git external/pybind11
git submodule update --init --recursive
```

#### Option 3: Clone locally in lib/python
```bash
cd lib/python
git clone https://github.com/pybind/pybind11.git
```

### Building the bindings

From the project root:

```bash
# Create build directory
mkdir build
cd build

# Configure
cmake ..

# Build
cmake --build .

# Install (optional)
cmake --install .
```

The Python module will be built as `_libista_owl2.so` (Linux/Mac) or `_libista_owl2.pyd` (Windows).

### Building with tests

```bash
cmake .. -DBUILD_PYTHON_TESTS=ON
cmake --build .
ctest
```

## Usage

### Basic Example

```python
from libista_owl2 import IRI, Class, Ontology, Declaration, EntityType
from libista_owl2 import SubClassOf, NamedClass, FunctionalSyntaxSerializer

# Create an ontology
onto = Ontology(IRI("http://example.org/myontology"))
onto.register_prefix("ex", "http://example.org/myontology#")

# Create classes
person_iri = IRI("ex", "Person", "http://example.org/myontology#")
student_iri = IRI("ex", "Student", "http://example.org/myontology#")

person_cls = Class(person_iri)
student_cls = Class(student_iri)

# Add declarations
onto.add_axiom(Declaration(EntityType.CLASS, person_iri))
onto.add_axiom(Declaration(EntityType.CLASS, student_iri))

# Add SubClassOf axiom: Student ⊑ Person
subclass_axiom = SubClassOf(
    NamedClass(student_cls),
    NamedClass(person_cls)
)
onto.add_axiom(subclass_axiom)

# Print statistics
print(onto.get_statistics())

# Serialize to functional syntax
print(onto.to_functional_syntax())

# Save to file
FunctionalSyntaxSerializer.serialize_to_file(onto, "myontology.ofn")
```

### Working with Individuals and Properties

```python
from libista_owl2 import (
    IRI, NamedIndividual, ObjectProperty, DataProperty,
    ClassAssertion, ObjectPropertyAssertion, DataPropertyAssertion,
    Literal, xsd
)

# Create individuals
john = NamedIndividual(IRI("ex", "John", "http://example.org/myontology#"))
mary = NamedIndividual(IRI("ex", "Mary", "http://example.org/myontology#"))

# Create properties
knows = ObjectProperty(IRI("ex", "knows", "http://example.org/myontology#"))
age = DataProperty(IRI("ex", "age", "http://example.org/myontology#"))

# Declare entities
onto.add_axiom(Declaration(EntityType.NAMED_INDIVIDUAL, john.get_iri()))
onto.add_axiom(Declaration(EntityType.NAMED_INDIVIDUAL, mary.get_iri()))
onto.add_axiom(Declaration(EntityType.OBJECT_PROPERTY, knows.get_iri()))
onto.add_axiom(Declaration(EntityType.DATA_PROPERTY, age.get_iri()))

# Add assertions
onto.add_axiom(ClassAssertion(NamedClass(person_cls), john))
onto.add_axiom(ClassAssertion(NamedClass(person_cls), mary))
onto.add_axiom(ObjectPropertyAssertion(knows, john, mary))
onto.add_axiom(DataPropertyAssertion(age, john, Literal("30", xsd.INTEGER)))
```

### Querying the Ontology

```python
# Get all classes
classes = onto.get_classes()
for cls in classes:
    print(f"Class: {cls.get_iri().get_abbreviated()}")

# Get subclass axioms for a specific class
subclass_axioms = onto.get_sub_class_axioms_for_super_class(person_cls)
for axiom in subclass_axioms:
    print(axiom.to_functional_syntax())

# Get all assertions for an individual
class_assertions = onto.get_class_assertions(john)
for assertion in class_assertions:
    print(assertion.to_functional_syntax())
```

### Using Annotations

```python
from libista_owl2 import AnnotationProperty, Annotation, Literal

# Create annotation properties
rdfs_label = AnnotationProperty(IRI("http://www.w3.org/2000/01/rdf-schema#label"))
rdfs_comment = AnnotationProperty(IRI("http://www.w3.org/2000/01/rdf-schema#comment"))

# Create annotations
label = Annotation(rdfs_label, Literal("Person", "en"))
comment = Annotation(rdfs_comment, Literal("A human being", "en"))

# Add annotations to axioms
decl = Declaration(EntityType.CLASS, person_iri)
decl.add_annotation(label)
decl.add_annotation(comment)
onto.add_axiom(decl)
```

## API Documentation

### Core Classes

#### IRI
```python
IRI(iri_string: str)  # Full IRI
IRI(prefix: str, local_name: str, namespace_uri: str)  # Abbreviated IRI

iri.get_full_iri() -> str
iri.get_prefix() -> Optional[str]
iri.get_local_name() -> Optional[str]
iri.get_namespace() -> str
iri.get_abbreviated() -> str
iri.is_abbreviated() -> bool
```

#### Ontology
```python
Ontology()
Ontology(ontology_iri: IRI)
Ontology(ontology_iri: IRI, version_iri: IRI)

# Prefix management
onto.register_prefix(prefix: str, namespace_uri: str)
onto.get_prefix_map() -> Dict[str, str]

# Axiom management
onto.add_axiom(axiom: Axiom) -> bool
onto.remove_axiom(axiom: Axiom) -> bool
onto.get_axioms() -> List[Axiom]

# Entity queries
onto.get_classes() -> Set[Class]
onto.get_object_properties() -> Set[ObjectProperty]
onto.get_data_properties() -> Set[DataProperty]
onto.get_individuals() -> Set[NamedIndividual]

# Statistics
onto.get_axiom_count() -> int
onto.get_entity_count() -> int
onto.get_statistics() -> str

# Serialization
onto.to_functional_syntax() -> str
onto.to_functional_syntax(indent: str) -> str
```

### Constants

The module provides XSD datatype constants:
```python
from libista_owl2 import xsd

xsd.STRING
xsd.INTEGER
xsd.INT
xsd.LONG
xsd.DOUBLE
xsd.FLOAT
xsd.BOOLEAN
xsd.DATE_TIME
xsd.DATE
```

And XSD facet constants:
```python
from libista_owl2 import facets

facets.MIN_INCLUSIVE
facets.MAX_INCLUSIVE
facets.MIN_EXCLUSIVE
facets.MAX_EXCLUSIVE
facets.LENGTH
facets.MIN_LENGTH
facets.MAX_LENGTH
facets.PATTERN
```

## File Structure

```
lib/python/
├── bindings.cpp        # Main pybind11 bindings implementation
├── CMakeLists.txt      # Build configuration
├── __init__.py         # Python package initialization
└── README.md           # This file
```

## Implementation Details

### Memory Management

The bindings use pybind11's smart pointer support to manage C++ object lifetimes:
- Entity types use `std::shared_ptr<T>` to ensure proper reference counting
- Python objects automatically manage the underlying C++ object lifetime
- No manual memory management required from Python

### Type Conversions

The bindings automatically handle conversions between C++ and Python types:
- `std::string` ↔ `str`
- `std::vector<T>` ↔ `List[T]`
- `std::unordered_set<T>` ↔ `Set[T]`
- `std::unordered_map<K,V>` ↔ `Dict[K,V]`
- `std::optional<T>` ↔ `Optional[T]`
- `std::variant<T...>` ↔ Python union types

### Return Value Policies

The bindings use appropriate return value policies:
- By value for simple types (IRI, Literal, etc.)
- By reference for containers
- Smart pointers for polymorphic types (Axiom, ClassExpression, etc.)

## Troubleshooting

### Import Error: No module named '_libista_owl2'

Make sure the module is in your Python path:
```python
import sys
sys.path.insert(0, '/path/to/build/lib/python')
import _libista_owl2
```

Or install the module:
```bash
cd build
cmake --install .
```

### CMake cannot find pybind11

Install pybind11 using one of the methods described in the Building section above.

### Compilation errors related to C++20

Ensure your compiler supports C++20:
- GCC 10 or later
- Clang 10 or later
- MSVC 2019 (16.8) or later

## License

The bindings follow the same license as the libista library.

## Contributing

Contributions are welcome! Please ensure:
1. New bindings follow the existing patterns
2. All exposed functions have docstrings
3. Memory management is handled correctly
4. Type conversions work as expected

## Version History

- **0.1.0** (2025-10-25): Initial release with comprehensive OWL2 bindings
