# OWL2 Library Implementation

Technical documentation for the libista OWL2 library implementation.

## Architecture Overview

The OWL2 library is structured around the OWL2 structural specification, providing C++ classes that directly model the abstract syntax of OWL2. The implementation follows modern C++20 practices with a focus on type safety, performance, and maintainability.

## Module Organization

### Core Module (`core/`)

Contains the fundamental OWL2 structures as defined in the W3C specification.

#### `iri.hpp/cpp` - IRI Implementation

**Purpose**: Represents Internationalized Resource Identifiers, the foundation of OWL2's naming system.

**Key Features**:
- Full IRI storage and manipulation
- Prefix/namespace decomposition
- Abbreviated form support (prefix:localName)
- Hash function for use in unordered containers
- Comparison operators for ordering

**Design Notes**:
- IRIs are immutable after construction
- Both full and abbreviated forms are stored when available
- Namespace extraction follows standard IRI parsing rules
- Hash implementation enables efficient use in sets and maps

**Usage Pattern**:
```cpp
// Full IRI
IRI full("http://example.org/ontology#MyClass");

// Abbreviated with prefix resolution
IRI abbrev("ex", "MyClass", "http://example.org/ontology#");
```

#### `entity.hpp` - Entity Type Hierarchy

**Purpose**: Defines the six entity types in OWL2.

**Entity Types**:
1. `Class` - OWL classes
2. `Datatype` - XSD and custom datatypes
3. `ObjectProperty` - Relations between individuals
4. `DataProperty` - Relations from individuals to literals
5. `AnnotationProperty` - Metadata properties
6. `NamedIndividual` - Named instances
7. `AnonymousIndividual` - Blank nodes (not an Entity subclass)

**Design Notes**:
- All entities (except anonymous individuals) inherit from base `Entity` class
- Entities are lightweight wrappers around IRIs
- Hash functions provided for all entity types
- Virtual `getEntityType()` method for runtime type identification
- Shared pointer typedefs for memory management

**Memory Management**:
- Entity objects are copyable (IRI is copied)
- Smart pointers (`EntityPtr` typedefs) for polymorphic use
- No dynamic allocation required for simple entity usage

#### `literal.hpp/cpp` - Literal Values

**Purpose**: Represents data values with optional language tags or datatypes.

**Features**:
- Plain literals with language tags (`"Hello"@en`)
- Typed literals (`"42"^^xsd:integer`)
- Predefined XSD datatype constants
- String conversion and formatting

**XSD Namespace**:
Provides constants for common XSD datatypes:
- `xsd::STRING`, `xsd::INTEGER`, `xsd::DOUBLE`, `xsd::FLOAT`
- `xsd::BOOLEAN`, `xsd::DATE_TIME`, `xsd::DATE`
- `xsd::INT`, `xsd::LONG`

**Design Notes**:
- Language tags and datatypes are mutually exclusive
- Lexical form stored as string (no automatic parsing)
- Comparison based on lexical form only
- Immutable after construction

#### `annotation.hpp/cpp` - Annotation System

**Purpose**: Implements OWL2's annotation mechanism for metadata.

**Key Types**:
- `AnnotationValue`: Variant type holding IRI, Literal, or AnonymousIndividual
- `Annotation`: Property-value pair with optional nested annotations

**Features**:
- Nested annotations (annotations on annotations)
- Three value types: IRI, Literal, AnonymousIndividual
- Helper functions for common annotation patterns
- Functional syntax serialization

**Design Notes**:
- Uses `std::variant` for type-safe value storage
- Supports arbitrary nesting depth
- Annotations are independent objects (not axioms)
- Helper functions (`makeAnnotation`) for convenience

#### `class_expression.hpp/cpp` - Class Expressions

**Purpose**: Represents complex class descriptions in OWL2.

**Expression Types**:
- `NamedClass`: Wrapper for a Class entity
- `ObjectIntersectionOf`: C1 ⊓ C2 ⊓ ... ⊓ Cn
- `ObjectUnionOf`: C1 ⊔ C2 ⊔ ... ⊔ Cn
- `ObjectSomeValuesFrom`: ∃R.C (existential quantification)
- `ObjectAllValuesFrom`: ∀R.C (universal quantification)

**Design Notes**:
- Base class `ClassExpression` with virtual interface
- Shared pointers (`ClassExpressionPtr`) for tree structures
- Vector storage for n-ary expressions
- Recursive functional syntax generation
- Virtual `getExpressionType()` for runtime identification

**Extension Points**:
The current implementation covers the most common expressions. Additional expressions can be added:
- `ObjectComplementOf`, `ObjectOneOf`
- `ObjectHasValue`, `ObjectHasSelf`
- `ObjectMinCardinality`, `ObjectMaxCardinality`, `ObjectExactCardinality`
- Data property restrictions

#### `data_range.hpp/cpp` - Data Ranges

**Purpose**: Represents sets of data values (the data property equivalent of class expressions).

**Range Types**:
- `NamedDatatype`: Reference to a datatype
- `DataIntersectionOf`: Intersection of ranges
- `DataUnionOf`: Union of ranges
- `DataComplementOf`: Complement of a range
- `DataOneOf`: Enumeration of literal values
- `DatatypeRestriction`: Facet-based restrictions

**Facet Support**:
Predefined constants in `facets` namespace:
- `MIN_INCLUSIVE`, `MAX_INCLUSIVE`
- `MIN_EXCLUSIVE`, `MAX_EXCLUSIVE`
- `LENGTH`, `MIN_LENGTH`, `MAX_LENGTH`
- `PATTERN`

**Design Notes**:
- Similar structure to class expressions
- Base class with virtual interface
- Shared pointers for tree structures
- Facets represented as (IRI, Literal) pairs

**Example Usage**:
```cpp
// Integer range [18, 65]
auto restriction = std::make_shared<DatatypeRestriction>(
    Datatype(xsd::INTEGER),
    std::vector<DatatypeRestriction::FacetRestriction>{
        {facets::MIN_INCLUSIVE, Literal("18", xsd::INTEGER)},
        {facets::MAX_INCLUSIVE, Literal("65", xsd::INTEGER)}
    });
```

#### `axiom.hpp/cpp` - Axiom Hierarchy

**Purpose**: Implements all OWL2 axiom types as defined in the structural specification.

**Axiom Categories**:

1. **Declaration Axioms** (1 type)
   - `Declaration`: Entity existence declaration

2. **Class Axioms** (4 types)
   - `SubClassOf`: Class subsumption
   - `EquivalentClasses`: Class equivalence
   - `DisjointClasses`: Pairwise disjointness
   - `DisjointUnion`: Disjoint union decomposition

3. **Object Property Axioms** (13 types)
   - Hierarchy: `SubObjectPropertyOf` (including property chains)
   - Equivalence: `EquivalentObjectProperties`
   - Disjointness: `DisjointObjectProperties`
   - Inverse: `InverseObjectProperties`
   - Domain/Range: `ObjectPropertyDomain`, `ObjectPropertyRange`
   - Characteristics: `FunctionalObjectProperty`, `InverseFunctionalObjectProperty`,
     `ReflexiveObjectProperty`, `IrreflexiveObjectProperty`,
     `SymmetricObjectProperty`, `AsymmetricObjectProperty`,
     `TransitiveObjectProperty`

4. **Data Property Axioms** (7 types)
   - Hierarchy: `SubDataPropertyOf`
   - Equivalence: `EquivalentDataProperties`
   - Disjointness: `DisjointDataProperties`
   - Domain/Range: `DataPropertyDomain`, `DataPropertyRange`
   - Characteristics: `FunctionalDataProperty`

5. **Assertion Axioms** (8 types)
   - Individual facts: `SameIndividual`, `DifferentIndividuals`
   - Type assertions: `ClassAssertion`
   - Property assertions: `ObjectPropertyAssertion`, `DataPropertyAssertion`
   - Negative assertions: `NegativeObjectPropertyAssertion`, `NegativeDataPropertyAssertion`

6. **Annotation Axioms** (4 types)
   - `AnnotationAssertion`: Attach metadata
   - `SubAnnotationPropertyOf`: Annotation property hierarchy
   - `AnnotationPropertyDomain`: Domain constraints
   - `AnnotationPropertyRange`: Range constraints

7. **Other Axioms** (2 types)
   - `DatatypeDefinition`: Custom datatype definitions
   - `HasKey`: Key constraints for classes

**Design Notes**:
- Base `Axiom` class with virtual interface
- All axioms support annotations
- Shared pointers (`AxiomPtr`) for polymorphic storage
- Virtual `getAxiomType()` returns string identifier
- Virtual `toFunctionalSyntax()` for serialization
- Helper functions for formatting complex structures

**Type Safety Features**:
- `ObjectPropertyExpression` variant for properties and inverses
- `Individual` variant for named and anonymous individuals
- `AnnotationSubject` variant for IRI and anonymous individuals
- Strong typing prevents incorrect axiom construction

**Property Chains**:
`SubObjectPropertyOf` supports property chain axioms:
```cpp
// r1 ∘ r2 ⊑ r3
SubObjectPropertyOf(
    std::vector<ObjectPropertyExpression>{r1, r2},
    r3
);
```

#### `ontology.hpp/cpp` - Ontology Container

**Purpose**: Main container class managing ontology metadata, axioms, and entities.

**Components**:

**Metadata Management**:
- Ontology IRI (optional)
- Version IRI (optional)
- Import declarations (set of IRIs)
- Ontology annotations

**Prefix Management**:
- Bidirectional prefix-namespace mapping
- Registration and lookup
- Standard prefixes (owl, rdf, rdfs, xsd) pre-registered
- Removal and clearing operations

**Axiom Management**:
- Add, remove, contains operations
- Full axiom retrieval
- Query by axiom type
- Query by specific entity references
- Clear all axioms

**Entity Queries**:
- Extract all entities of each type
- Count entities by type
- Check entity existence
- Overall statistics generation

**Serialization**:
- Functional syntax generation
- Configurable indentation
- Organized output (declarations, then axioms by type)

**Design Notes**:
- Axioms stored in vector (insertion order preserved)
- Prefixes stored in bidirectional hash maps
- Standard prefixes initialized in constructor
- Query methods build results on demand (no caching)
- Statistics computed dynamically

**Performance Considerations**:
- Linear search for axiom queries (suitable for most ontologies)
- Entity extraction builds unordered sets
- Hash-based prefix lookup (O(1))
- No indexing structures (future optimization opportunity)

**Memory Management**:
- Shared pointers for axioms
- Copy operations are shallow (shared axiom ownership)
- Clear operations release axiom references

### Serializer Module (`serializer/`)

#### `functional_serializer.hpp/cpp` - Functional Syntax Serializer

**Purpose**: Converts ontologies to OWL2 Functional Syntax format.

**Features**:
- Complete ontology serialization
- Prefix declarations
- Organized axiom output
- Configurable indentation
- File and string output

**Output Organization**:
1. Prefix declarations
2. Ontology header (IRI, version, imports, annotations)
3. Declaration axioms
4. Class axioms
5. Object property axioms
6. Data property axioms
7. Annotation property axioms
8. Individual assertions
9. Other axioms

**Design Notes**:
- Static methods (stateless serializer)
- Delegates to `Ontology::toFunctionalSyntax()`
- File operations with error handling
- UTF-8 output encoding
- Consistent indentation and formatting

**Format Compliance**:
Generates valid OWL2 Functional Syntax as specified in:
https://www.w3.org/TR/owl2-syntax/#Functional-Style_Syntax

### Parser Module (`parser/`)

**Status**: Planned but not yet implemented.

**Future Parsers**:
- RDF/XML parser (requires XML library integration)
- Turtle parser
- Functional syntax parser
- Manchester syntax parser

## Design Patterns

### Entity Storage

Entities are value types that can be stored directly or via shared pointers:
```cpp
// Direct storage (copy semantics)
Class myClass(IRI("http://example.org#MyClass"));

// Shared pointer (for polymorphism)
std::shared_ptr<Entity> entity = std::make_shared<Class>(myClass);
```

### Expression Trees

Class expressions and data ranges form tree structures:
```cpp
auto leaf1 = std::make_shared<NamedClass>(class1);
auto leaf2 = std::make_shared<NamedClass>(class2);
auto node = std::make_shared<ObjectIntersectionOf>(
    std::vector<ClassExpressionPtr>{leaf1, leaf2}
);
```

### Variant Types

Type-safe unions for heterogeneous values:
```cpp
// Individual can be named or anonymous
Individual ind1 = NamedIndividual(IRI("ex:John"));
Individual ind2 = AnonymousIndividual("_:b1");

// Annotation value can be IRI, Literal, or AnonymousIndividual
AnnotationValue val1 = IRI("http://example.org");
AnnotationValue val2 = Literal("label", "en");
```

### Optional Values

`std::optional` for nullable fields:
```cpp
std::optional<IRI> ontoIRI = ontology.getOntologyIRI();
if (ontoIRI) {
    std::cout << "IRI: " << ontoIRI->toString() << std::endl;
}
```

## Implementation Details

### Memory Management Strategy

- **Value Types**: IRIs, Literals, Entities (copyable, no dynamic allocation required)
- **Shared Ownership**: Axioms, ClassExpressions, DataRanges (shared_ptr)
- **Containers**: Standard library containers (vector, unordered_set, unordered_map)
- **No Raw Pointers**: All dynamic memory managed via smart pointers

### Type Safety

- Virtual base classes for polymorphic types
- `std::variant` for type-safe unions
- `std::optional` for nullable values
- Strong typing prevents incorrect constructions
- Template-free design (easier debugging and compilation)

### String Handling

- UTF-8 encoding throughout
- `std::string` for all text
- No custom string classes
- Functional syntax output is UTF-8

### Error Handling

Current implementation uses:
- Return values (bool for success/failure)
- `std::optional` for nullable results
- Standard exceptions not currently used (future enhancement)

### Serialization Strategy

- Visitor pattern via virtual methods
- Each class knows how to serialize itself
- Recursive serialization for nested structures
- Indentation passed as string parameter
- Formatted output with proper nesting

## Extension Points

### Adding New Axiom Types

1. Define class inheriting from `Axiom`
2. Implement `getAxiomType()` and `toFunctionalSyntax()`
3. Add to appropriate query methods in `Ontology`
4. Update serializer organization if needed

### Adding New Expression Types

1. Define class inheriting from `ClassExpression` or `DataRange`
2. Implement virtual methods
3. Add to expression tree construction patterns

### Adding New Serializers

1. Create new serializer class in `serializer/`
2. Implement static `serialize()` methods
3. Follow format-specific generation rules
4. Handle prefixes and abbreviation

### Adding Parsers

1. Create parser class in `parser/`
2. Implement parsing for specific format
3. Build ontology incrementally via `Ontology::addAxiom()`
4. Handle prefix declarations
5. Error reporting and recovery

## Testing Strategy

**Current State**: No formal test suite (future work)

**Recommended Testing Approach**:
- Unit tests for each core class
- Axiom construction and serialization tests
- Ontology query tests
- Round-trip serialization tests
- OWL2 profile compliance tests
- Performance benchmarks for large ontologies

**Test Framework Suggestions**:
- Google Test (gtest)
- Catch2
- Boost.Test

## Performance Characteristics

### Time Complexity

- Axiom addition: O(1) amortized (vector push_back)
- Axiom queries: O(n) linear scan
- Entity queries: O(n) linear scan with set construction
- Prefix lookup: O(1) hash table
- Serialization: O(n) where n is axiom count

### Space Complexity

- Axiom storage: O(n) where n is axiom count
- Entity sets: O(e) where e is entity count
- Prefix maps: O(p) where p is prefix count
- Shared axioms: Single copy regardless of query count

### Optimization Opportunities

**For Future Work**:
- Axiom indexing by type (avoid linear scans)
- Entity caching (avoid rebuilding sets)
- Axiom hash set (faster contains checks)
- Lazy serialization (generate on demand)
- Memory-mapped files for large ontologies

## Compliance Notes

### OWL2 Specification Compliance

**Covered**:
- Full entity type support
- Most common class expressions
- Complete axiom coverage
- Functional syntax serialization
- Annotation mechanism

**Not Yet Covered**:
- Full class expression set (cardinality, oneOf, etc.)
- Data property restrictions in class expressions
- OWL2 profiles (EL, QL, RL)
- Structural validation
- RDF mapping

### Standard Namespaces

Pre-registered in every ontology:
- `owl`: http://www.w3.org/2002/07/owl#
- `rdf`: http://www.w3.org/1999/02/22-rdf-syntax-ns#
- `rdfs`: http://www.w3.org/2000/01/rdf-schema#
- `xsd`: http://www.w3.org/2001/XMLSchema#

## Known Limitations

1. **Expression Coverage**: Not all OWL2 class expressions implemented yet
2. **No Parser**: Only serialization currently supported
3. **No Validation**: No checking for OWL2 structural constraints
4. **Linear Queries**: No indexing for fast axiom retrieval
5. **No Reasoner**: No inference or consistency checking
6. **Single Format**: Only Functional Syntax serialization

## Future Enhancements

### Short Term
- Complete class expression types
- Functional syntax parser
- Basic validation (detect duplicate declarations, etc.)
- Test suite

### Medium Term
- RDF/XML parser and serializer
- Turtle parser and serializer
- Axiom indexing for performance
- OWL2 profile checkers

### Long Term
- Manchester syntax support
- Reasoner integration
- Python bindings
- Ontology merging utilities
- SPARQL integration

## References

### W3C Specifications
- [OWL2 Structural Specification](https://www.w3.org/TR/owl2-syntax/)
- [OWL2 Functional Syntax](https://www.w3.org/TR/owl2-syntax/#Functional-Style_Syntax)
- [OWL2 RDF Mapping](https://www.w3.org/TR/owl2-mapping-to-rdf/)
- [OWL2 Profiles](https://www.w3.org/TR/owl2-profiles/)

### Implementation Resources
- [OWL API](https://github.com/owlcs/owlapi) - Java reference implementation
- [Owlready2](https://github.com/pwin/owlready2) - Python ontology library
- Modern C++ patterns for ontology manipulation

## Development Notes

### Coding Conventions

- C++20 standard
- 4-space indentation
- Header guards (not `#pragma once`)
- Extensive comments in headers
- Doxygen-style documentation
- Namespace: `ista::owl2`

### File Organization

- Header/implementation split for all classes
- One class per file (with related helpers)
- Headers are self-contained (include dependencies)
- Forward declarations where possible

### Naming Conventions

- Classes: PascalCase
- Methods: camelCase
- Members: snake_case with trailing underscore
- Constants: UPPER_SNAKE_CASE (in namespaces)
- Namespaces: lowercase

### Git Workflow

Repository structure:
```
lib/
├── owl2/
│   ├── core/           # Core implementation
│   ├── serializer/     # Serializers
│   └── parser/         # Parsers (future)
src/                    # Example applications
```

Recent commits show active development on axiom types and entity structures.
