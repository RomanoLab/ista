# Owlready2 Migration Analysis

This document catalogs all owlready2 functionality currently used in the ista codebase and maps it to equivalent ista.owl2 features. The goal is to eliminate the owlready2 dependency entirely.

## Executive Summary

**Files using owlready2:**
- `ista/__init__.py` - Basic ontology loading
- `ista/util.py` - Utility functions for property manipulation and ontology queries
- `ista/database_parser.py` - Core database parsing functionality
- `ista/ista.py` - CLI tool
- `examples/kg_projects/neurokb/neurokb.py` - Example knowledge base
- `examples/kg_projects/alzkb/alzkb.py` - Example knowledge base

## Detailed Feature Analysis

### 1. Ontology Loading and Saving

#### Owlready2 Usage
```python
# Loading
onto = owlready2.get_ontology("file://path/to/file.rdf").load()

# Saving
with open("output.rdf", 'wb') as fp:
    onto.save(file=fp, format="rdfxml")
```

#### ista.owl2 Equivalent
```python
# Loading
onto = ista.owl2.RDFXMLParser.parse_from_file("path/to/file.rdf")

# Saving
serializer = ista.owl2.RDFXMLSerializer()
rdf_content = serializer.serialize(onto)
with open("output.rdf", 'w') as fp:
    fp.write(rdf_content)
```

**Status:** ✅ **IMPLEMENTED** - RDFXMLParser and RDFXMLSerializer exist with Python bindings

---

### 2. Ontology Metadata Access

#### Owlready2 Usage
```python
_OWL = owlready2.get_ontology("http://www.w3.org/2002/07/owl#")
```

#### ista.owl2 Equivalent
**Status:** ❌ **MISSING** - Need built-in OWL vocabulary constants

**Required Implementation:**
- C++ constants for standard OWL IRIs
- Python bindings for OWL vocabulary
- Similar for RDF, RDFS, XSD vocabularies

---

### 3. Class Retrieval by Name

#### Owlready2 Usage
```python
def get_onto_class_by_node_type(ont: owlready2.namespace.Ontology, node_label: str):
    matches = [c for c in ont.classes() if str(c).split(".")[-1] == node_label]
    if len(matches) == 1:
        return matches[0]
    elif len(matches) == 0:
        return None
    else:
        raise ValueError("Duplicate classes found")
```

#### ista.owl2 Equivalent
```python
def get_onto_class_by_node_type(ont: ista.owl2.Ontology, node_label: str):
    classes = ont.get_classes()
    matches = [c for c in classes if c.get_iri().get_local_name() == node_label]
    if len(matches) == 1:
        return matches[0]
    elif len(matches) == 0:
        return None
    else:
        raise ValueError("Duplicate classes found")
```

**Status:** ✅ **IMPLEMENTED** - `get_classes()` exists with Python bindings

---

### 4. Individual Creation

#### Owlready2 Usage
```python
cl = get_onto_class_by_node_type(ont, "Drug")
individual_name = "drug_aspirin"
new_individual = cl(individual_name)
```

#### ista.owl2 Equivalent
**Status:** ❌ **MISSING** - No convenient individual creation API

**Required Implementation:**
- Method to create individuals: `Ontology::createIndividual(Class, IRI)`
- Automatic ClassAssertion axiom creation
- Python bindings for individual creation

---

### 5. Property Value Setting (Functional Properties)

#### Owlready2 Usage
```python
def safe_add_property(entity, prop, value):
    if _OWL.FunctionalProperty in prop.is_a:
        setattr(entity, prop._python_name, value)
    else:
        # ... handle non-functional properties
```

#### ista.owl2 Equivalent
**Status:** ❌ **MISSING** - No property assertion API

**Required Implementation:**
- `Ontology::addDataPropertyAssertion(NamedIndividual, DataProperty, Literal)`
- `Ontology::addObjectPropertyAssertion(NamedIndividual, ObjectProperty, NamedIndividual)`
- Check if property is functional
- Python bindings for property assertions

---

### 6. Property Value Setting (Non-Functional Properties)

#### Owlready2 Usage
```python
def safe_add_property(entity, prop, value):
    # ...
    else:
        if len(getattr(entity, prop._python_name)) == 0:
            setattr(entity, prop._python_name, [value])
        else:
            if value not in getattr(entity, prop._python_name):
                getattr(entity, prop._python_name).append(value)
```

#### ista.owl2 Equivalent
**Status:** ❌ **MISSING** - Same as above

---

### 7. Entity Search by Property Value

#### Owlready2 Usage
```python
# Search for individuals with specific property value
match = ont.search(**{property_name: property_value})
```

#### ista.owl2 Equivalent
**Status:** ❌ **MISSING** - No search functionality

**Required Implementation:**
- `Ontology::searchByDataProperty(DataProperty, Literal) -> std::vector<NamedIndividual>`
- `Ontology::searchByObjectProperty(ObjectProperty, NamedIndividual) -> std::vector<NamedIndividual>`
- Python bindings for search methods

---

### 8. Iterating Over Classes

#### Owlready2 Usage
```python
for cl in onto.classes():
    # Process class
```

#### ista.owl2 Equivalent
```python
for cl in onto.get_classes():
    # Process class
```

**Status:** ✅ **IMPLEMENTED** - `get_classes()` exists

---

### 9. Iterating Over Object Properties

#### Owlready2 Usage
```python
for op in onto.object_properties():
    # Process object property
```

#### ista.owl2 Equivalent
```python
for op in onto.get_object_properties():
    # Process object property
```

**Status:** ✅ **IMPLEMENTED** - `get_object_properties()` exists

---

### 10. Getting Instances of a Class

#### Owlready2 Usage
```python
instances = onto.get_instances_of(cl)
```

#### ista.owl2 Equivalent
```python
instances = onto.get_individuals_of_class(cl)
```

**Status:** ✅ **IMPLEMENTED** - `get_individuals_of_class()` exists (needs Python binding verification)

---

### 11. Getting Relations for Object Property

#### Owlready2 Usage
```python
relations = op.get_relations()
```

#### ista.owl2 Equivalent
**Status:** ❌ **MISSING** - No method to query all assertions for a property

**Required Implementation:**
- `Ontology::getObjectPropertyAssertions(ObjectProperty) -> std::vector<std::pair<NamedIndividual, NamedIndividual>>`
- `Ontology::getDataPropertyAssertions(DataProperty) -> std::vector<std::pair<NamedIndividual, Literal>>`
- Python bindings

---

### 12. Individual Class Membership Check

#### Owlready2 Usage
```python
# Check if individual is instance of class
if some_class in individual.is_a:
    # ...
```

#### ista.owl2 Equivalent
**Status:** ❌ **MISSING** - No convenience method

**Required Implementation:**
- `Ontology::isInstanceOf(NamedIndividual, Class) -> bool`
- Check ClassAssertion axioms
- Python bindings

---

### 13. Getting Individual's Classes

#### Owlready2 Usage
```python
classes = individual.is_a
```

#### ista.owl2 Equivalent
**Status:** ❌ **MISSING**

**Required Implementation:**
- `Ontology::getClassesForIndividual(NamedIndividual) -> std::vector<Class>`
- Python bindings

---

### 14. Adding Class to Individual

#### Owlready2 Usage
```python
individual.is_a.append(new_class)
```

#### ista.owl2 Equivalent
**Status:** ❌ **MISSING**

**Required Implementation:**
- Same as individual creation - adds ClassAssertion axiom

---

### 15. Ontology Statistics

#### Owlready2 Usage
```python
def print_onto_stats(onto: owlready2.Ontology):
    # Count individuals per class
    for cl in onto.classes():
        count = len(onto.get_instances_of(cl))
        print(f"{cl.name}: {count}")
    
    # Count relationships per property
    for op in onto.object_properties():
        count = len(list(op.get_relations()))
        print(f"{op.name}: {count}")
```

#### ista.owl2 Equivalent
```python
def print_onto_stats(onto: ista.owl2.Ontology):
    # Count individuals per class
    for cl in onto.get_classes():
        count = len(onto.get_individuals_of_class(cl))
        print(f"{cl.get_iri().get_local_name()}: {count}")
    
    # Count relationships per property (NEEDS IMPLEMENTATION)
    for op in onto.get_object_properties():
        assertions = onto.get_object_property_assertions(op)  # MISSING
        count = len(assertions)
        print(f"{op.get_iri().get_local_name()}: {count}")
```

**Status:** ⚠️ **PARTIALLY IMPLEMENTED** - Stats exist but missing property assertion queries

---

## Summary of Missing Features

### High Priority (Core Functionality)

1. **Individual Creation API**
   - C++: `Ontology::createIndividual(const Class&, const IRI&) -> NamedIndividual`
   - Automatically creates ClassAssertion axiom
   - Python bindings

2. **Property Assertion APIs**
   - C++: `Ontology::addDataPropertyAssertion(const NamedIndividual&, const DataProperty&, const Literal&)`
   - C++: `Ontology::addObjectPropertyAssertion(const NamedIndividual&, const ObjectProperty&, const NamedIndividual&)`
   - Python bindings

3. **Search/Query APIs**
   - C++: `Ontology::searchByDataProperty(const DataProperty&, const Literal&) -> std::vector<NamedIndividual>`
   - C++: `Ontology::searchByObjectProperty(const ObjectProperty&, const NamedIndividual&) -> std::vector<NamedIndividual>`
   - Python bindings

4. **Property Assertion Queries**
   - C++: `Ontology::getObjectPropertyAssertions(const ObjectProperty&) -> std::vector<std::pair<NamedIndividual, NamedIndividual>>`
   - C++: `Ontology::getDataPropertyAssertions(const DataProperty&) -> std::vector<std::pair<NamedIndividual, Literal>>`
   - Python bindings

5. **Individual Class Queries**
   - C++: `Ontology::getClassesForIndividual(const NamedIndividual&) -> std::vector<Class>`
   - C++: `Ontology::isInstanceOf(const NamedIndividual&, const Class&) -> bool`
   - Python bindings (verify `get_individuals_of_class` is bound)

### Medium Priority (Convenience Features)

6. **Standard Vocabulary Constants**
   - C++ namespace with OWL, RDF, RDFS, XSD IRIs
   - Python bindings as module-level constants

7. **Property Characteristic Queries**
   - C++: `Ontology::isFunctionalProperty(const ObjectProperty&) -> bool`
   - C++: `Ontology::isFunctionalProperty(const DataProperty&) -> bool`
   - Check for FunctionalObjectProperty/FunctionalDataProperty axioms
   - Python bindings

### Low Priority (Nice to Have)

8. **Dynamic Property Access**
   - Python-style attribute access for properties
   - Similar to owlready2's `individual.property_name` syntax
   - Would require Python-side implementation

---

## Implementation Status

### ✅ Phase 1: Core Individual and Property APIs - **COMPLETED**
- ✅ Implemented individual creation in C++ (`Ontology::createIndividual`)
- ✅ Implemented property assertion APIs in C++ (`addDataPropertyAssertion`, `addObjectPropertyAssertion`, `addClassAssertion`)
- ✅ Added Python bindings for all methods
- ✅ Created and validated test suite (`examples/test_new_api.py`)

### ✅ Phase 2: Search and Query APIs - **COMPLETED**
- ✅ Implemented search by property value in C++ (`searchByDataProperty`, `searchByObjectProperty`)
- ✅ Implemented property assertion queries in C++ (`getObjectPropertyAssertions`, `getDataPropertyAssertions`)
- ✅ Added Python bindings with proper overload disambiguation
- ✅ Validated with test suite

### ✅ Phase 3: Individual Class Queries - **COMPLETED**
- ✅ Implemented class membership queries in C++ (`getClassesForIndividual`, `isInstanceOf`)
- ✅ Added Python bindings
- ✅ Validated with test suite

### ✅ Phase 4: Property Characteristics - **COMPLETED**
- ✅ Implemented property characteristic queries (`isFunctionalObjectProperty`, `isFunctionalDataProperty`)
- ✅ Added Python bindings
- ✅ Ready for use

### ⏳ Phase 5: Vocabulary Constants - **PENDING**
- ⏳ Standard vocabulary constants (OWL, RDF, RDFS, XSD IRIs) - recommended for convenience but not blocking

### 🚀 Phase 6: Migration - **READY TO BEGIN**
1. Update `ista/util.py` to use ista.owl2 APIs
2. Update `ista/database_parser.py` to use ista.owl2 APIs
3. Update examples to use ista.owl2 APIs
4. Remove owlready2 dependency
5. Update documentation

All core functionality required to replace owlready2 has been implemented and tested!

---

## Files Requiring Modification During Migration

1. **`ista/__init__.py`**
   - Replace `owlready2.get_ontology()` with `ista.owl2.RDFXMLParser`
   - Remove `_OWL` variable

2. **`ista/util.py`**
   - Rewrite `safe_add_property()` using ista.owl2 property assertion APIs
   - Rewrite `get_onto_class_by_node_type()` using ista.owl2 class queries
   - Rewrite `print_onto_stats()` using ista.owl2 statistics APIs

3. **`ista/database_parser.py`**
   - Update all ontology type hints from `owlready2.namespace.Ontology` to `ista.owl2.Ontology`
   - Rewrite `_merge_node()` using ista.owl2 search and property APIs
   - Rewrite `_write_new_node()` using ista.owl2 individual creation APIs
   - Update all property assertion code

4. **`ista/ista.py`**
   - Replace `owlready2.get_ontology()` with ista.owl2 parser
   - Replace `onto.save()` with ista.owl2 serializer

5. **`examples/kg_projects/neurokb/neurokb.py`**
   - Update imports
   - Replace ontology loading/saving
   - Update property assertions

6. **`examples/kg_projects/alzkb/alzkb.py`**
   - Same as neurokb.py

7. **`setup.py` and `pyproject.toml`**
   - Remove owlready2 from dependencies

---

## Testing Strategy

1. **Unit Tests**: Create tests for each new C++ API
2. **Integration Tests**: Test Python bindings for all new features
3. **Migration Tests**: Run existing examples with new APIs
4. **Regression Tests**: Ensure ontology outputs match owlready2 versions

---

## Benefits of Migration

1. **Single Library**: Reduces dependency complexity
2. **Performance**: Native C++ implementation is faster
3. **Consistency**: Single ontology model throughout codebase
4. **Control**: Full control over features and bug fixes
5. **Extensibility**: Easier to add biomedical-specific features
6. **Documentation**: Better aligned with project goals
