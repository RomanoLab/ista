# Simplified Python Bindings - Quick Reference

## Overview

The simplified bindings (`bindings_simple.cpp`) provide an easy-to-use Python interface for OWL2 ontology manipulation without the complexity of variant types.

## Installation

Build the bindings:
```bash
cd /path/to/ista
mkdir -p build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Release
cmake --build . --target _libista_owl2
```

The compiled module will be at: `build/lib/python/Release/_libista_owl2.cp38-win_amd64.pyd`

## Quick Start

```python
import _libista_owl2 as owl2

# Create an ontology
onto = owl2.Ontology(owl2.IRI("http://example.org/myonto"))

# Register a prefix
onto.register_prefix("ex", "http://example.org/myonto#")

# Create a class
person = owl2.Class(owl2.IRI("ex", "Person", "http://example.org/myonto#"))

# Declare the class
onto.add_axiom(owl2.Declaration(owl2.EntityType.CLASS, person.get_iri()))

# Save to file
owl2.FunctionalSyntaxSerializer.serialize_to_file(onto, "myonto.ofn")
```

## API Reference

### IRI - Internationalized Resource Identifier

```python
# Construction
iri1 = owl2.IRI("http://example.org/test#Something")
iri2 = owl2.IRI("ex", "Something", "http://example.org/test#")

# Methods
iri.get_full_iri()      # Full IRI string
iri.get_abbreviated()   # Prefix:localName form
iri.get_prefix()        # Namespace prefix
iri.get_local_name()    # Local name part
iri.get_namespace()     # Namespace URI
iri.is_abbreviated()    # True if abbreviated form available
iri.to_string()         # Convert to string
```

### Entities

#### Class
```python
cls = owl2.Class(owl2.IRI("http://example.org/Person"))
iri = cls.get_iri()
entity_type = cls.get_entity_type()  # Returns "Class"
```

#### ObjectProperty
```python
prop = owl2.ObjectProperty(owl2.IRI("http://example.org/hasChild"))
```

#### DataProperty
```python
prop = owl2.DataProperty(owl2.IRI("http://example.org/age"))
```

#### NamedIndividual
```python
ind = owl2.NamedIndividual(owl2.IRI("http://example.org/John"))
```

### Literal - Literal Values

```python
# Plain literal with language tag
lit1 = owl2.Literal("Hello", "en")

# Typed literal
lit2 = owl2.Literal("42", owl2.xsd.INTEGER)
lit3 = owl2.Literal("3.14", owl2.xsd.DOUBLE)
lit4 = owl2.Literal("true", owl2.xsd.BOOLEAN)

# Methods
lit.get_lexical_form()    # String representation
lit.get_datatype()        # Datatype IRI
lit.get_language_tag()    # Language tag (or None)
lit.is_typed()            # True if typed
lit.has_language_tag()    # True if has language tag
```

### XSD Datatypes

```python
owl2.xsd.STRING      # xsd:string
owl2.xsd.INTEGER     # xsd:integer
owl2.xsd.INT         # xsd:int
owl2.xsd.LONG        # xsd:long
owl2.xsd.DOUBLE      # xsd:double
owl2.xsd.FLOAT       # xsd:float
owl2.xsd.BOOLEAN     # xsd:boolean
owl2.xsd.DATE_TIME   # xsd:dateTime
owl2.xsd.DATE        # xsd:date
```

### Class Expressions

#### NamedClass
```python
person_cls = owl2.Class(owl2.IRI("http://example.org/Person"))
person_expr = owl2.NamedClass(person_cls)
```

### Axioms

All axioms inherit from `Axiom` base class with:
- `to_functional_syntax()` - Convert to OWL Functional Syntax string
- `get_axiom_type()` - Get axiom type name

#### Declaration
```python
# Entity types
owl2.EntityType.CLASS
owl2.EntityType.OBJECT_PROPERTY
owl2.EntityType.DATA_PROPERTY
owl2.EntityType.NAMED_INDIVIDUAL
owl2.EntityType.ANNOTATION_PROPERTY
owl2.EntityType.DATATYPE

# Create declaration
decl = owl2.Declaration(owl2.EntityType.CLASS, owl2.IRI("http://example.org/Person"))
```

#### SubClassOf
```python
parent_expr = owl2.NamedClass(parent_cls)
person_expr = owl2.NamedClass(person_cls)
axiom = owl2.SubClassOf(parent_expr, person_expr)
```

#### ClassAssertion
```python
john = owl2.NamedIndividual(owl2.IRI("http://example.org/John"))
person_expr = owl2.NamedClass(person_cls)
axiom = owl2.ClassAssertion(person_expr, john)
```

#### ObjectPropertyDomain
```python
has_child = owl2.ObjectProperty(owl2.IRI("http://example.org/hasChild"))
person_expr = owl2.NamedClass(person_cls)
axiom = owl2.ObjectPropertyDomain(has_child, person_expr)
```

#### ObjectPropertyRange
```python
axiom = owl2.ObjectPropertyRange(has_child, person_expr)
```

#### DataPropertyDomain
```python
age = owl2.DataProperty(owl2.IRI("http://example.org/age"))
axiom = owl2.DataPropertyDomain(age, person_expr)
```

#### FunctionalObjectProperty
```python
axiom = owl2.FunctionalObjectProperty(has_child)
```

#### FunctionalDataProperty
```python
axiom = owl2.FunctionalDataProperty(age)
```

### Ontology

#### Construction
```python
# Empty ontology
onto = owl2.Ontology()

# With IRI
onto = owl2.Ontology(owl2.IRI("http://example.org/myonto"))

# With IRI and version
onto = owl2.Ontology(
    owl2.IRI("http://example.org/myonto"),
    owl2.IRI("http://example.org/myonto/v1.0")
)
```

#### Metadata
```python
onto.get_ontology_iri()
onto.set_ontology_iri(iri)
onto.get_version_iri()
onto.set_version_iri(iri)
onto.get_imports()
onto.add_import(iri)
onto.remove_import(iri)
onto.has_import(iri)
```

#### Prefix Management
```python
onto.register_prefix("ex", "http://example.org/test#")
onto.get_namespace_for_prefix("ex")
onto.get_prefix_for_namespace("http://example.org/test#")
onto.get_prefix_map()  # Returns dict
onto.remove_prefix("ex")
onto.clear_prefixes()
```

#### Axiom Management
```python
onto.add_axiom(axiom)
onto.remove_axiom(axiom)
onto.contains_axiom(axiom)
onto.get_axioms()  # Returns list of all axioms
onto.clear_axioms()
```

#### Entity Queries
```python
onto.get_classes()             # List of Class objects
onto.get_object_properties()   # List of ObjectProperty objects
onto.get_data_properties()     # List of DataProperty objects
onto.get_individuals()         # List of NamedIndividual objects

onto.contains_class(cls)
onto.contains_object_property(prop)
onto.contains_data_property(prop)
onto.contains_individual(ind)
```

#### Statistics
```python
onto.get_axiom_count()
onto.get_entity_count()
onto.get_class_count()
onto.get_object_property_count()
onto.get_data_property_count()
onto.get_individual_count()
onto.get_statistics()  # Returns formatted string
```

#### Serialization
```python
# To string
fs = onto.to_functional_syntax()
fs_indented = onto.to_functional_syntax("    ")
```

### Serializers

#### FunctionalSyntaxSerializer
```python
# To string
output = owl2.FunctionalSyntaxSerializer.serialize(onto)
output = owl2.FunctionalSyntaxSerializer.serialize(onto, "  ")  # Custom indent

# To file
owl2.FunctionalSyntaxSerializer.serialize_to_file(onto, "output.ofn")
```

#### RDFXMLSerializer
```python
# To string
rdf = owl2.RDFXMLSerializer.serialize(onto)

# To file
owl2.RDFXMLSerializer.serialize_to_file(onto, "output.rdf")
```

## Complete Example

```python
import _libista_owl2 as owl2

# Create ontology
onto = owl2.Ontology(owl2.IRI("http://example.org/family"))

# Register prefixes
onto.register_prefix("fam", "http://example.org/family#")
onto.register_prefix("xsd", "http://www.w3.org/2001/XMLSchema#")

# Create classes
person = owl2.Class(owl2.IRI("fam", "Person", "http://example.org/family#"))
parent = owl2.Class(owl2.IRI("fam", "Parent", "http://example.org/family#"))

# Create properties
has_child = owl2.ObjectProperty(owl2.IRI("fam", "hasChild", "http://example.org/family#"))
age = owl2.DataProperty(owl2.IRI("fam", "age", "http://example.org/family#"))

# Create individuals
john = owl2.NamedIndividual(owl2.IRI("fam", "John", "http://example.org/family#"))

# Declare entities
onto.add_axiom(owl2.Declaration(owl2.EntityType.CLASS, person.get_iri()))
onto.add_axiom(owl2.Declaration(owl2.EntityType.CLASS, parent.get_iri()))
onto.add_axiom(owl2.Declaration(owl2.EntityType.OBJECT_PROPERTY, has_child.get_iri()))
onto.add_axiom(owl2.Declaration(owl2.EntityType.DATA_PROPERTY, age.get_iri()))
onto.add_axiom(owl2.Declaration(owl2.EntityType.NAMED_INDIVIDUAL, john.get_iri()))

# Add axioms
person_expr = owl2.NamedClass(person)
parent_expr = owl2.NamedClass(parent)

onto.add_axiom(owl2.SubClassOf(parent_expr, person_expr))  # Parent ⊑ Person
onto.add_axiom(owl2.ClassAssertion(person_expr, john))     # john : Person
onto.add_axiom(owl2.ObjectPropertyDomain(has_child, person_expr))
onto.add_axiom(owl2.ObjectPropertyRange(has_child, person_expr))
onto.add_axiom(owl2.DataPropertyDomain(age, person_expr))
onto.add_axiom(owl2.FunctionalDataProperty(age))

# Print statistics
print(f"Axioms: {onto.get_axiom_count()}")
print(f"Classes: {onto.get_class_count()}")
print(onto.get_statistics())

# Save to files
owl2.FunctionalSyntaxSerializer.serialize_to_file(onto, "family.ofn")
owl2.RDFXMLSerializer.serialize_to_file(onto, "family.rdf")
```

## Limitations

The simplified bindings intentionally omit:
- Anonymous individuals
- Annotations
- Complex class expressions (intersections, unions, restrictions)
- Data ranges
- Complex property axioms (equivalence, disjointness, chains, inverses)
- Property assertions

For these features, use the full bindings in `bindings.cpp`.

## Version

Version: 0.1.0-simple

## See Also

- Full test: `test_simple_bindings.py`
- Documentation: `SIMPLIFIED_BINDINGS_SUMMARY.md`
- Original bindings: `bindings.cpp`
