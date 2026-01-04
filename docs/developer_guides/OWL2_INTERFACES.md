# OWL2 Interface in ista

The ista package provides a **native C++ OWL2 ontology manipulation library** with Python bindings for high-performance knowledge graph operations.

## Overview

ista.owl2 is a modern C++20 library with Python bindings that provides complete OWL 2 ontology manipulation capabilities without any external dependencies.

| Feature | Details |
|---------|---------|
| **Language** | C++ with Python bindings (pybind11) |
| **Performance** | High (optimized C++) |
| **Main Use Cases** | - Create/manipulate ontologies programmatically<br>- Parse/serialize RDF/XML & Functional Syntax<br>- Individual and property management<br>- Search and query operations<br>- Subgraph extraction<br>- Graph analysis |
| **Module** | `ista.owl2` (built-in) |
| **Dependencies** | None (fully native) |

---

## Core Functionality

### 1. Ontology Creation and Management

```python
from ista import owl2

# Create a new ontology
onto = owl2.Ontology(owl2.IRI("http://example.org/biomedical"))

# Or with version IRI
onto = owl2.Ontology(
    owl2.IRI("http://example.org/biomedical"),
    owl2.IRI("http://example.org/biomedical/v1.0")
)

# Manage prefixes
onto.register_prefix("bio", "http://example.org/biomedical#")
onto.register_prefix("gene", "http://example.org/genes#")

# Get statistics
print(f"Axioms: {onto.get_axiom_count()}")
print(f"Classes: {onto.get_class_count()}")
print(f"Individuals: {onto.get_individual_count()}")
```

### 2. Classes and Properties

```python
from ista import owl2

# Create classes
disease_cls = owl2.Class(owl2.IRI("http://example.org/Disease"))
gene_cls = owl2.Class(owl2.IRI("http://example.org/Gene"))
drug_cls = owl2.Class(owl2.IRI("http://example.org/Drug"))

# Create object properties
targets = owl2.ObjectProperty(owl2.IRI("http://example.org/targets"))
treats = owl2.ObjectProperty(owl2.IRI("http://example.org/treats"))

# Create data properties
has_name = owl2.DataProperty(owl2.IRI("http://example.org/hasName"))
drugbank_id = owl2.DataProperty(owl2.IRI("http://example.org/drugbankId"))
```

### 3. Individual Creation and Management

```python
from ista import owl2

# Create individuals with automatic class assertion
aspirin = onto.create_individual(
    drug_cls,
    owl2.IRI("http://example.org/aspirin")
)

cox1 = onto.create_individual(
    gene_cls,
    owl2.IRI("http://example.org/COX1")
)

alzheimers = onto.create_individual(
    disease_cls,
    owl2.IRI("http://example.org/Alzheimers")
)

# Add additional class memberships
onto.add_class_assertion(aspirin, owl2.Class(owl2.IRI("http://example.org/NSAID")))
```

### 4. Property Assertions

```python
from ista import owl2

# Data property assertions
onto.add_data_property_assertion(
    aspirin,
    has_name,
    owl2.Literal("Aspirin")
)

onto.add_data_property_assertion(
    aspirin,
    drugbank_id,
    owl2.Literal("DB00945")
)

# Object property assertions
onto.add_object_property_assertion(
    aspirin,  # subject
    targets,  # property
    cox1      # object
)

onto.add_object_property_assertion(
    aspirin,
    treats,
    alzheimers
)
```

### 5. Search and Query Operations

```python
from ista import owl2

# Search by data property value
results = onto.search_by_data_property(
    drugbank_id,
    owl2.Literal("DB00945")
)
print(f"Found {len(results)} drugs with ID DB00945")

# Search by object property
drugs_targeting_cox1 = onto.search_by_object_property(targets, cox1)
for drug in drugs_targeting_cox1:
    print(f"Drug: {drug.get_iri().get_local_name()}")

# Get all assertions for a property
relationships = onto.get_object_property_assertions_for_property(targets)
for subject, object in relationships:
    print(f"{subject.get_iri().get_local_name()} -> {object.get_iri().get_local_name()}")

# Get classes for an individual
classes = onto.get_classes_for_individual(aspirin)
for cls in classes:
    print(f"Aspirin is a: {cls.get_iri().get_local_name()}")

# Check instance membership
if onto.is_instance_of(aspirin, drug_cls):
    print("Aspirin is a drug")

# Get all individuals of a class
all_drugs = onto.get_individuals_of_class(drug_cls)
print(f"Found {len(all_drugs)} drugs in ontology")
```

### 6. Property Characteristics

```python
from ista import owl2

# Check if a property is functional
if onto.is_functional_data_property(drugbank_id):
    print("drugbank_id is functional (unique per individual)")

if onto.is_functional_object_property(targets):
    print("targets is functional")
```

### 7. Serialization and Parsing

```python
from ista import owl2

# Parse from RDF/XML file
onto = owl2.RDFXMLParser.parse_from_file("input.owl")

# Serialize to RDF/XML
serializer = owl2.RDFXMLSerializer()
rdf_content = serializer.serialize(onto)

# Save to file
with open("output.owl", "w") as f:
    f.write(rdf_content)

# Serialize to Functional Syntax
functional = onto.to_functional_syntax()
print(functional)
```

### 8. High-Performance Subgraph Extraction

```python
from ista import owl2

# Create filter
filter_obj = owl2.OntologyFilter(onto)

# Extract k-hop neighborhood (BFS, O(V+E))
result = filter_obj.extract_neighborhood(
    owl2.IRI("http://example.org/Alzheimers"),
    depth=2
)

# Filter by class membership
result = filter_obj.filter_by_classes({
    owl2.IRI("http://example.org/Disease"),
    owl2.IRI("http://example.org/Gene")
})

# Extract specific individuals
result = filter_obj.filter_by_individuals({
    owl2.IRI("http://example.org/aspirin"),
    owl2.IRI("http://example.org/ibuprofen")
})

# Access filtered results
print(f"Original: {result.original_axiom_count} axioms")
print(f"Filtered: {result.filtered_axiom_count} axioms")
subgraph = result.ontology  # The filtered ontology
```

### 9. Graph Analysis

```python
from ista import owl2

# Get k-hop neighbors of an individual
neighbors = onto.get_neighbors(
    owl2.NamedIndividual(owl2.IRI("http://example.org/aspirin")),
    depth=2
)

# Check if path exists between two individuals
has_path = onto.has_path(
    owl2.NamedIndividual(owl2.IRI("http://example.org/aspirin")),
    owl2.NamedIndividual(owl2.IRI("http://example.org/Alzheimers"))
)
```

---

## Database Parsing Integration

ista provides database parsers that integrate seamlessly with ista.owl2:

```python
from ista import FlatFileDatabaseParser, owl2

# Create ontology
onto = owl2.Ontology(owl2.IRI("http://example.org/mydata"))

# Define classes and properties
drug_cls = owl2.Class(owl2.IRI("http://example.org/Drug"))
has_name = owl2.DataProperty(owl2.IRI("http://example.org/hasName"))
drugbank_id = owl2.DataProperty(owl2.IRI("http://example.org/drugbankId"))

# Parse CSV files into ontology
parser = FlatFileDatabaseParser("DrugData", onto, "./data")

parser.parse_node_type(
    node_type="Drug",
    source_filename="drugs.csv",
    fmt="csv",
    parse_config={
        "iri_column_name": "drug_id",
        "headers": True,
        "data_property_map": {
            "name": has_name,
            "drugbank_id": drugbank_id,
        },
        "merge_column": {
            "source_column_name": "drugbank_id",
            "data_property": drugbank_id,
        },
    }
)

# Save populated ontology
serializer = owl2.RDFXMLSerializer()
with open("drugs.owl", "w") as f:
    f.write(serializer.serialize(onto))
```

---

## Complete API Reference

### Core Types

**IRI Management**
- `IRI(iri_string)` - Create IRI from string
- `IRI(prefix, local_name, namespace)` - Create from components
- `.get_full_iri()`, `.get_local_name()`, `.get_namespace()`

**Literals**
- `Literal(value)` - Create literal value
- `Literal(value, datatype_iri)` - Typed literal
- `Literal(value, language_tag)` - Language-tagged literal

### Entities

- `Class(iri)` - OWL class
- `ObjectProperty(iri)` - Object property
- `DataProperty(iri)` - Data property
- `AnnotationProperty(iri)` - Annotation property
- `NamedIndividual(iri)` - Individual/instance
- `Datatype(iri)` - Datatype

### Ontology Methods

**Individual Management**
- `create_individual(cls, iri)` → Creates individual with class assertion
- `add_class_assertion(individual, cls)` → Add class membership

**Property Assertions**
- `add_data_property_assertion(individual, property, literal)` → Add data property
- `add_object_property_assertion(subject, property, object)` → Add object property

**Search & Query**
- `search_by_data_property(property, value)` → Find individuals by data property
- `search_by_object_property(property, object)` → Find subjects by object property
- `get_object_property_assertions_for_property(property)` → All assertions for property
- `get_data_property_assertions_for_property(property)` → All data assertions
- `get_classes_for_individual(individual)` → Classes individual belongs to
- `is_instance_of(individual, cls)` → Check class membership
- `get_individuals_of_class(cls)` → All instances of a class

**Property Characteristics**
- `is_functional_object_property(property)` → Check if functional
- `is_functional_data_property(property)` → Check if functional

**Graph Operations**
- `get_neighbors(individual, depth)` → K-hop neighborhood
- `has_path(from_individual, to_individual)` → Path existence check

**Statistics**
- `get_axiom_count()`, `get_class_count()`, `get_individual_count()`
- `get_statistics()` → Formatted statistics string

### Serialization

**RDF/XML**
- `RDFXMLParser.parse_from_file(filename)` → Load ontology
- `RDFXMLSerializer().serialize(ontology)` → Save as RDF/XML

**Functional Syntax**
- `ontology.to_functional_syntax()` → Convert to OWL Functional Syntax

### Filtering

**OntologyFilter**
- `OntologyFilter(ontology)` - Create filter
- `.filter_by_individuals(iri_set)` → Extract specific individuals
- `.filter_by_classes(class_iri_set)` → Filter by class membership
- `.extract_neighborhood(individual_iri, depth)` → K-hop neighborhood
- `.extract_path(from_iri, to_iri)` → Path between individuals
- `.random_sample(n, seed)` → Random sample

**FilterResult**
- `.ontology` - The filtered ontology
- `.original_axiom_count`, `.filtered_axiom_count`
- `.original_individual_count`, `.filtered_individual_count`
- `.included_individuals` - Set of included IRIs

---

## Performance Characteristics

All operations are implemented in optimized C++:

| Operation | Time Complexity | Space Complexity |
|-----------|----------------|------------------|
| `create_individual()` | O(1) | O(1) |
| `add_*_property_assertion()` | O(1) | O(1) |
| `search_by_*_property()` | O(A) | O(k) |
| `get_individuals_of_class()` | O(A) | O(k) |
| `extract_neighborhood(k)` | O(V + E) | O(V) |
| `extract_path()` | O(V + E) | O(V) |
| `filter_by_individuals()` | O(A) | O(V + A) |

Where:
- V = number of individuals (vertices)
- E = number of object property assertions (edges)
- A = number of axioms
- k = number of results

---

## Utility Functions

ista provides several utility functions that work with ista.owl2:

```python
from ista.util import (
    safe_add_property,           # Add property with duplicate checking
    get_onto_class_by_node_type, # Find class by local name
    safe_make_individual_name,   # Generate unique individual names
    print_onto_stats,            # Print ontology statistics
)

# Safe property addition (checks for duplicates)
safe_add_property(onto, individual, property, value)

# Find class by name
drug_class = get_onto_class_by_node_type(onto, "Drug")

# Print statistics
print_onto_stats(onto)
```

---

## Examples

### Complete Workflow Example

```python
from ista import owl2

# 1. Create ontology
onto = owl2.Ontology(owl2.IRI("http://example.org/pharma"))
onto.register_prefix("pharma", "http://example.org/pharma#")

# 2. Define schema
drug = owl2.Class(owl2.IRI("http://example.org/pharma#Drug"))
gene = owl2.Class(owl2.IRI("http://example.org/pharma#Gene"))
targets = owl2.ObjectProperty(owl2.IRI("http://example.org/pharma#targets"))
has_name = owl2.DataProperty(owl2.IRI("http://example.org/pharma#hasName"))

# 3. Create individuals
aspirin = onto.create_individual(drug, owl2.IRI("http://example.org/pharma#aspirin"))
cox1 = onto.create_individual(gene, owl2.IRI("http://example.org/pharma#COX1"))

# 4. Add properties
onto.add_data_property_assertion(aspirin, has_name, owl2.Literal("Aspirin"))
onto.add_object_property_assertion(aspirin, targets, cox1)

# 5. Query
drugs = onto.get_individuals_of_class(drug)
print(f"Total drugs: {len(drugs)}")

# 6. Save
serializer = owl2.RDFXMLSerializer()
with open("pharma.owl", "w") as f:
    f.write(serializer.serialize(onto))
```

### More Examples

- `examples/test_new_api.py` - Comprehensive API demonstration
- `examples/kg_projects/neurokb/neurokb.py` - Neuroscience knowledge base
- `examples/kg_projects/alzkb/alzkb.py` - Alzheimer's knowledge base

---

## Installation

The ista.owl2 library is built automatically when you install ista:

```bash
# Install in development mode (builds C++ extension)
pip install -e .

# Or install from PyPI (when available)
pip install ista
```

### Build Requirements

- C++20 compatible compiler (GCC 10+, Clang 10+, MSVC 2019+)
- CMake 3.15+
- Python 3.7+
- pybind11 (automatically downloaded)

---

## Migration from owlready2

ista previously used owlready2 for OWL ontology manipulation. As of version 0.2.0, we've migrated entirely to the native ista.owl2 implementation for better performance and control.

**Key differences:**

| Operation | owlready2 (Old) | ista.owl2 (New) |
|-----------|----------------|-----------------|
| Load ontology | `owlready2.get_ontology("file://...").load()` | `owl2.RDFXMLParser.parse_from_file(...)` |
| Create individual | `SomeClass("name")` | `onto.create_individual(cls, iri)` |
| Add property | `individual.property = value` | `onto.add_data_property_assertion(...)` |
| Search | `onto.search(property=value)` | `onto.search_by_data_property(property, value)` |
| Save | `onto.save(file=f, format="rdfxml")` | `serializer.serialize(onto)` |

See `docs/OWLREADY2_MIGRATION_ANALYSIS.md` for complete migration guide.

---

## Getting Help

- **API Documentation**: See Python docstrings and this guide
- **C++ Documentation**: See `lib/README.md` and Doxygen docs
- **Examples**: `examples/` directory
- **Issues**: https://github.com/JDRomano2/ista/issues

---

*Last Updated: 2025-12-30*  
*ista Version: 0.2.0*
