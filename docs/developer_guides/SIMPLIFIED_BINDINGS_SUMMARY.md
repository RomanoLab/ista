# Simplified Python Bindings for libista OWL2

## Summary

Successfully created a simplified version of the Python bindings that exposes essential OWL2 classes without variant types. The simplified bindings compile successfully and provide practical functionality for creating ontologies, declaring entities, adding simple axioms, and serializing to OWL/RDF files.

## Files Created/Modified

### New Files
- **`lib/python/bindings_simple.cpp`** - Simplified Python bindings implementation
- **`test_simple_bindings.py`** - Comprehensive test script demonstrating all features
- **`test_family_simple.ofn`** - Generated OWL Functional Syntax output
- **`test_family_simple.rdf`** - Generated RDF/XML output

### Modified Files
- **`lib/python/CMakeLists.txt`** - Updated to use `bindings_simple.cpp` instead of `bindings.cpp`

## What's Exposed

### 1. Core Classes (Full Implementation)

#### IRI
- Full IRI construction from string or prefix/local name/namespace
- Methods: `get_full_iri()`, `get_prefix()`, `get_local_name()`, `get_namespace()`, `get_abbreviated()`, `is_abbreviated()`, `to_string()`
- Supports comparison operators and hashing

#### Literal
- Plain literals with optional language tags
- Typed literals with XSD datatypes
- Methods: `get_lexical_form()`, `get_datatype()`, `get_language_tag()`, `is_typed()`, `has_language_tag()`, `to_string()`
- Supports comparison operators

#### Entity Types (No Variant Wrappers)
- **Class** - OWL2 classes
- **ObjectProperty** - Object properties
- **DataProperty** - Data properties
- **NamedIndividual** - Named individuals (no AnonymousIndividual support)

All entity types inherit from `Entity` base class with:
- `get_iri()` - Get the entity's IRI
- `get_entity_type()` - Get type as string
- Comparison operators

### 2. Simple Class Expressions

#### NamedClass
- Wraps a `Class` entity as a class expression
- Constructor: `NamedClass(cls: Class)`
- Methods: `get_class()`, `to_functional_syntax()`, `get_expression_type()`

### 3. Simple Axioms (No Variants)

#### Declaration
- Declares entities in the ontology
- Constructor: `Declaration(entity_type: EntityType, iri: IRI)`
- EntityType enum: `CLASS`, `DATATYPE`, `OBJECT_PROPERTY`, `DATA_PROPERTY`, `ANNOTATION_PROPERTY`, `NAMED_INDIVIDUAL`
- Methods: `get_entity_type()`, `get_iri()`

#### SubClassOf
- Subclass relationships
- Constructor: `SubClassOf(subclass: ClassExpressionPtr, superclass: ClassExpressionPtr)`
- Methods: `get_sub_class()`, `get_super_class()`

#### ClassAssertion
- **Simplified**: Accepts `NamedIndividual` directly (no Individual variant)
- Constructor: `ClassAssertion(class_expression: ClassExpressionPtr, individual: NamedIndividual)`
- Methods: `get_class_expression()`
- Note: Uses lambda wrapper to convert NamedIndividual to Individual variant internally

#### ObjectPropertyDomain
- **Simplified**: Accepts `ObjectProperty` directly (no ObjectPropertyExpression variant)
- Constructor: `ObjectPropertyDomain(property: ObjectProperty, domain: ClassExpressionPtr)`
- Methods: `get_domain()`
- Note: Uses lambda wrapper to convert ObjectProperty to ObjectPropertyExpression variant internally

#### ObjectPropertyRange
- **Simplified**: Accepts `ObjectProperty` directly
- Constructor: `ObjectPropertyRange(property: ObjectProperty, range: ClassExpressionPtr)`
- Methods: `get_range()`

#### DataPropertyDomain
- Standard implementation (DataProperty is not a variant)
- Constructor: `DataPropertyDomain(property: DataProperty, domain: ClassExpressionPtr)`
- Methods: `get_property()`, `get_domain()`

#### DataPropertyRange
- **Note**: Exposed but constructor skipped (requires DataRangePtr which is complex)

#### FunctionalObjectProperty
- **Simplified**: Accepts `ObjectProperty` directly
- Constructor: `FunctionalObjectProperty(property: ObjectProperty)`
- Note: Uses lambda wrapper

#### FunctionalDataProperty
- Standard implementation
- Constructor: `FunctionalDataProperty(property: DataProperty)`
- Methods: `get_property()`

### 4. Ontology Class (Full Implementation)

#### Metadata Management
- `get_ontology_iri()`, `set_ontology_iri(iri)`
- `get_version_iri()`, `set_version_iri(iri)`
- `get_imports()`, `add_import(iri)`, `remove_import(iri)`, `has_import(iri)`

#### Prefix Management
- `register_prefix(prefix, namespace_uri)`
- `get_namespace_for_prefix(prefix)`
- `get_prefix_for_namespace(namespace_uri)`
- `get_prefix_map()`, `remove_prefix(prefix)`, `clear_prefixes()`

#### Axiom Management
- `add_axiom(axiom)`, `remove_axiom(axiom)`, `contains_axiom(axiom)`
- `get_axioms()`, `clear_axioms()`

#### Entity Queries
- `get_classes()`, `get_object_properties()`, `get_data_properties()`, `get_individuals()`
- `contains_class(cls)`, `contains_object_property(prop)`, `contains_data_property(prop)`, `contains_individual(ind)`

#### Statistics
- `get_axiom_count()`, `get_entity_count()`
- `get_class_count()`, `get_object_property_count()`, `get_data_property_count()`, `get_individual_count()`
- `get_statistics()` - Returns formatted statistics string

#### Serialization
- `to_functional_syntax()` - With optional indent parameter

### 5. Serializers

#### FunctionalSyntaxSerializer
- Static methods:
  - `serialize(ontology)` - Serialize to string
  - `serialize(ontology, indent)` - Serialize with custom indentation
  - `serialize_to_file(ontology, filename)` - Save to file

#### RDFXMLSerializer
- Static methods:
  - `serialize(ontology)` - Serialize to RDF/XML string
  - `serialize_to_file(ontology, filename)` - Save to RDF/XML file

### 6. XSD Constants Module

Accessible as `owl2.xsd.*`:
- `STRING`, `INTEGER`, `INT`, `LONG`, `DOUBLE`, `FLOAT`, `BOOLEAN`, `DATE_TIME`, `DATE`

## Design Decisions

### Lambda Wrappers for Variant Types
The simplified bindings use lambda wrappers to hide variant types from Python users:

```cpp
// Instead of exposing ObjectPropertyExpression variant:
.def(py::init([](const ObjectProperty& property, const ClassExpressionPtr& domain) {
     return std::make_shared<ObjectPropertyDomain>(ObjectPropertyExpression(property), domain);
 }))
```

This allows Python users to pass simple `ObjectProperty` objects directly without dealing with variants.

### What's NOT Included

To keep the bindings simple, the following are omitted:
- **AnonymousIndividual** - Only NamedIndividual is exposed
- **Annotation support** - Annotation, AnnotationProperty, annotation axioms
- **Complex class expressions** - ObjectIntersectionOf, ObjectUnionOf, ObjectSomeValuesFrom, ObjectAllValuesFrom, etc.
- **Data ranges** - DataRange and its subclasses
- **Datatype** - Datatype entity and DatatypeDefinition axiom
- **Complex property axioms** - EquivalentClasses, DisjointClasses, property chains, inverse properties, etc.
- **Assertion axioms** - ObjectPropertyAssertion, DataPropertyAssertion (requires Individual/Literal handling)
- **Helper functions** - formatObjectPropertyExpression, formatIndividual, etc. (all use variants)

### Benefits of Simplification

1. **Easier to use** - No need to understand C++ variants in Python
2. **Cleaner API** - Direct use of entity types without wrappers
3. **Faster compilation** - Fewer template instantiations
4. **Good for learning** - Focuses on core OWL2 concepts
5. **Practical** - Covers common use cases: entity declaration, basic axioms, serialization

## Compilation Results

**Status**: ✅ Successfully compiled

```
Building Custom Rule D:/projects/ista/lib/python/CMakeLists.txt
bindings_simple.cpp
Creating library D:/projects/ista/build/lib/python/Release/_libista_owl2.lib
_libista_owl2.vcxproj -> D:\projects\ista\build\lib\python\Release\_libista_owl2.cp38-win_amd64.pyd
```

## Test Results

**Status**: ✅ All tests passed

The test script (`test_simple_bindings.py`) successfully demonstrates:
1. Ontology creation with IRI
2. Prefix registration
3. Entity creation (classes, properties, individuals)
4. Declaration axioms
5. SubClassOf axioms
6. ClassAssertion axioms
7. Property domain/range axioms
8. Functional property axioms
9. Ontology statistics
10. Functional Syntax serialization
11. File saving (both .ofn and .rdf formats)
12. IRI functionality (abbreviated forms, prefix extraction)
13. Literal functionality (plain and typed literals, language tags)
14. XSD constant access

### Example Output

**Functional Syntax** (test_family_simple.ofn):
```
Ontology(<http://example.org/family>
    Prefix(owl:=<http://www.w3.org/2002/07/owl#>)
    Prefix(fam:=<http://example.org/family#>)
    ...
    Declaration(Class(<http://example.org/family#Person>))
    Declaration(Class(<http://example.org/family#Parent>))
    SubClassOf(<http://example.org/family#Parent> <http://example.org/family#Person>)
    ClassAssertion(<http://example.org/family#Person> <http://example.org/family#John>)
    ...
)
```

**RDF/XML** (test_family_simple.rdf):
```xml
<?xml version="1.0" encoding="UTF-8"?>
<rdf:RDF xmlns:fam="http://example.org/family#" ...>
    <owl:Ontology rdf:about="http://example.org/family"/>
    <owl:Class rdf:about="http://example.org/family#Person"/>
    <owl:Class rdf:about="http://example.org/family#Parent">
        <rdfs:subClassOf rdf:resource="http://example.org/family#Person"/>
    </owl:Class>
    ...
</rdf:RDF>
```

## Usage Example

```python
import ista.owl2 as owl2

# Create ontology
onto = owl2.Ontology(owl2.IRI("http://example.org/myonto"))
onto.register_prefix("ex", "http://example.org/myonto#")

# Create entities
person_cls = owl2.Class(owl2.IRI("ex", "Person", "http://example.org/myonto#"))
john = owl2.NamedIndividual(owl2.IRI("ex", "John", "http://example.org/myonto#"))

# Add axioms
onto.add_axiom(owl2.Declaration(owl2.EntityType.CLASS, person_cls.get_iri()))
onto.add_axiom(owl2.Declaration(owl2.EntityType.NAMED_INDIVIDUAL, john.get_iri()))
onto.add_axiom(owl2.ClassAssertion(owl2.NamedClass(person_cls), john))

# Serialize
owl2.FunctionalSyntaxSerializer.serialize_to_file(onto, "output.ofn")
owl2.RDFXMLSerializer.serialize_to_file(onto, "output.rdf")
```

## Next Steps

If you need more advanced features, you can:
1. **Extend the simplified bindings** - Add more axiom types using the same lambda wrapper pattern
2. **Use the full bindings** - Switch back to `bindings.cpp` for complete OWL2 support
3. **Create hybrid bindings** - Mix simple and advanced features based on your needs

## Conclusion

The simplified bindings provide a clean, easy-to-use Python interface for basic OWL2 ontology manipulation. They compile successfully, work correctly, and demonstrate practical functionality for common use cases while avoiding the complexity of variant types.
