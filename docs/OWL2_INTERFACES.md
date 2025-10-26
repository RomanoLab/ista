# OWL2 Interfaces in ista

The ista package provides **two OWL2 ontology manipulation interfaces** that serve different purposes and use cases.

## Overview

| Feature | owlready2 (Legacy) | ista.owl2 (New C++ Library) |
|---------|-------------------|---------------------------|
| **Purpose** | Database parsing & KB building | High-performance ontology manipulation |
| **Language** | Pure Python | C++ with Python bindings |
| **Performance** | Moderate | High (optimized C++) |
| **Main Use Cases** | - Parse CSV/Excel/MySQL to ontologies<br>- Build knowledge graphs from databases | - Create ontologies programmatically<br>- Parse/serialize RDF/XML<br>- Subgraph extraction<br>- Graph analysis |
| **Module** | `owlready2` (external) | `ista.owl2` (built-in) |
| **Status** | Maintained (legacy workflows) | Active development |

---

## 1. owlready2 (Legacy Database Parsing)

### What is it?
[owlready2](https://pypi.org/project/Owlready2/) is an external Python library for manipulating OWL 2.0 ontologies. It was the original ontology library used by ista for building knowledge graphs from structured data sources.

### When to use it?
- **Database to Ontology**: Converting CSV files, Excel spreadsheets, or MySQL databases into OWL ontologies
- **Legacy Projects**: Working with existing ista projects (e.g., `examples/projects/alzkb/`, `examples/projects/neurokb/`)
- **Compatibility**: When you need features specific to owlready2's ecosystem

### Core Components Using owlready2

#### Database Parsers (`ista/database_parser.py`)
```python
from ista import FlatFileDatabaseParser, MySQLDatabaseParser
import owlready2

# Create an ontology using owlready2
onto = owlready2.get_ontology("http://example.org/myonto")

# Parse CSV/Excel files into the ontology
parser = FlatFileDatabaseParser(
    name="MyData",
    destination=onto,
    data_dir="./data"
)

# The parser populates the ontology with individuals and relationships
parser.parse_node_type(...)
```

#### Utility Functions (`ista/util.py`)
```python
from ista.util import (
    safe_add_property,           # Handle functional/non-functional properties
    get_onto_class_by_node_type, # Dynamic class lookup
    print_onto_stats,            # Print ontology statistics
)
```

#### Command-Line Tool (`ista/ista.py`)
```bash
ista -i input.owl -o output.owl -c config/ -d data/
```

### Example Workflow
```python
import owlready2
from ista import FlatFileDatabaseParser

# 1. Create or load an ontology with owlready2
onto = owlready2.get_ontology("http://example.org/biomedical")
onto.load()

# 2. Define classes
with onto:
    class Disease(owlready2.Thing): pass
    class Gene(owlready2.Thing): pass

# 3. Parse database into ontology
parser = FlatFileDatabaseParser("GeneDB", onto, "./data")
# ... parser populates ontology ...

# 4. Save
onto.save(file="output.owl", format="rdfxml")
```

### Limitations
- **Performance**: Pure Python, slower for large ontologies
- **Memory**: Can be memory-intensive for very large graphs
- **Subgraph Extraction**: No built-in high-performance filtering

---

## 2. ista.owl2 (New C++ Library)

### What is it?
`ista.owl2` is a high-performance C++ library with Python bindings (via pybind11) for OWL 2 ontology manipulation. It provides the same core functionality as owlready2 but with significantly better performance, plus advanced features like subgraph extraction.

### When to use it?
- **New Projects**: All new ontology manipulation code
- **Performance-Critical**: Large ontologies, frequent operations
- **Subgraph Extraction**: Filtering, neighborhood extraction, path finding
- **Serialization**: Fast RDF/XML parsing and generation
- **Graph Analysis**: Converting ontologies to graph formats (NetworkX, igraph)

### Core Components

#### Core Ontology Types
```python
from ista import owl2

# Create ontology
ont = owl2.Ontology(owl2.IRI("http://example.org/biomedical"))

# Create entities
disease_cls = owl2.Class(owl2.IRI("http://example.org/Disease"))
gene_cls = owl2.Class(owl2.IRI("http://example.org/Gene"))
associated_with = owl2.ObjectProperty(owl2.IRI("http://example.org/associatedWith"))

# Create individuals
alzheimers = owl2.NamedIndividual(owl2.IRI("http://example.org/Alzheimers"))
apoe = owl2.NamedIndividual(owl2.IRI("http://example.org/APOE"))

# Add axioms
ont.add_axiom(owl2.ClassAssertion(disease_cls, alzheimers))
ont.add_axiom(owl2.ClassAssertion(gene_cls, apoe))
ont.add_axiom(owl2.ObjectPropertyAssertion(associated_with, apoe, alzheimers))
```

#### Serialization & Parsing
```python
from ista import owl2

# Serialize to RDF/XML
rdf_xml = owl2.RDFXMLSerializer.serialize(ont)
with open("output.owl", "w") as f:
    f.write(rdf_xml)

# Serialize to Functional Syntax
functional = owl2.FunctionalSyntaxSerializer.serialize(ont)

# Parse from RDF/XML
ont = owl2.RDFXMLParser.parse_from_file("input.owl")
```

#### High-Performance Subgraph Extraction
```python
from ista import owl2

# Create filter
filter_obj = owl2.OntologyFilter(ont)

# Extract k-hop neighborhood (BFS, O(V+E))
result = filter_obj.extract_neighborhood(
    owl2.IRI("http://example.org/Alzheimers"),
    depth=2
)

# Find shortest path between entities
result = filter_obj.extract_path(
    owl2.IRI("http://example.org/Disease1"),
    owl2.IRI("http://example.org/Drug1")
)

# Filter by class membership
result = filter_obj.filter_by_classes({
    owl2.IRI("http://example.org/Disease"),
    owl2.IRI("http://example.org/Gene")
})

# Random sampling
result = filter_obj.random_sample(n=100, seed=42)

# Access results
print(f"Original: {result.original_axiom_count} axioms")
print(f"Filtered: {result.filtered_axiom_count} axioms")
print(f"Individuals: {result.filtered_individual_count}")
subgraph = result.ontology  # The filtered ontology
```

#### Builder Pattern for Complex Filters
```python
from ista import owl2

# Chain filter operations
result = (owl2.OntologyFilter(ont)
          .with_classes({owl2.IRI("http://example.org/Gene")})
          .with_max_depth(2)
          .execute())
```

#### Convenience Methods on Ontology
```python
from ista import owl2

# Get all individuals of a class
persons = ont.get_individuals_of_class(
    owl2.Class(owl2.IRI("http://example.org/Person"))
)

# Get k-hop neighbors
neighbors = ont.get_neighbors(
    owl2.NamedIndividual(owl2.IRI("http://example.org/Alice")),
    depth=2
)

# Check if path exists
has_path = ont.has_path(
    owl2.NamedIndividual(owl2.IRI("http://example.org/Alice")),
    owl2.NamedIndividual(owl2.IRI("http://example.org/Bob"))
)
```

### Complete API Reference

See the [module docstring](../ista/owl2.py) for the complete API, including:

**Core Types**: `IRI`, `Literal`  
**Entities**: `Entity`, `Class`, `ObjectProperty`, `DataProperty`, `NamedIndividual`  
**Axioms**: `ClassAssertion`, `ObjectPropertyAssertion`, `DataPropertyAssertion`, `SubClassOf`, `Declaration`, etc.  
**Ontology**: `Ontology` (main container)  
**Serialization**: `RDFXMLSerializer`, `FunctionalSyntaxSerializer`, `RDFXMLParser`  
**Filtering**: `OntologyFilter`, `FilterCriteria`, `FilterResult`  

### Performance Characteristics

All filtering operations are implemented in optimized C++:

| Operation | Time Complexity | Space Complexity |
|-----------|----------------|------------------|
| `extract_neighborhood(k)` | O(V + E) | O(V) |
| `extract_path()` | O(V + E) | O(V) |
| `filter_by_individuals()` | O(A) | O(V + A) |
| `filter_by_classes()` | O(V + A) | O(V + A) |
| `random_sample()` | O(n) | O(n) |

Where:
- V = number of individuals (vertices)
- E = number of object property assertions (edges)
- A = number of axioms
- n = sample size

---

## Comparison: Which Should I Use?

### Use **owlready2** when:
- ✓ Parsing databases (CSV, Excel, MySQL) into ontologies
- ✓ Working with existing ista projects (alzkb, neurokb, etc.)
- ✓ You need owlready2-specific features (reasoning, SWRL rules, etc.)
- ✓ Compatibility with existing owlready2 code is required

### Use **ista.owl2** when:
- ✓ Building new ontology manipulation code
- ✓ Performance is critical (large ontologies, frequent operations)
- ✓ You need subgraph extraction or filtering
- ✓ Converting between ontologies and graph formats (NetworkX, igraph)
- ✓ You want type safety and C++ performance

### Can I use both?
Yes! You can use both in the same project. For example:
1. Use owlready2 database parsers to build an ontology from data
2. Export to RDF/XML
3. Load into ista.owl2 for high-performance filtering and analysis

---

## Migration Path (Future Development)

### Phase 1: Coexistence (Current)
- Both libraries available
- Use each for their strengths
- Document best practices (this document)

### Phase 2: Interoperability (Planned)
Add converters between the two libraries:

```python
# Future API (not yet implemented)
from ista.converters import owlready2_to_ista_owl2, ista_owl2_to_owlready2

# Parse database with owlready2
owlready2_ont = owlready2.get_ontology("...")
parser.parse_into(owlready2_ont)

# Convert to ista.owl2 for filtering
ista_ont = owlready2_to_ista_owl2(owlready2_ont)
result = owl2.OntologyFilter(ista_ont).extract_neighborhood(...)

# Convert back if needed
final_ont = ista_owl2_to_owlready2(result.ontology)
```

### Phase 3: Full Migration (Long-term)
Once ista.owl2 is feature-complete:
- Rewrite database parsers to use ista.owl2
- Deprecate owlready2 dependency (make it optional)
- Maintain backward compatibility via conversion utilities

---

## Installation & Setup

### Installing owlready2
```bash
pip install owlready2
```

### Building ista.owl2
```bash
# Install in development mode (builds C++ extension)
pip install -e .

# Or build manually
mkdir build && cd build
cmake .. -DBUILD_PYTHON_BINDINGS=ON
cmake --build . --config Release
```

### Checking Availability
```python
from ista import owl2

if owl2.is_available():
    print("ista.owl2 C++ library is available!")
else:
    print("C++ library not built. Please run: pip install -e .")
```

---

## Examples

### owlready2 Examples
- `examples/projects/alzkb/alzkb.py` - Alzheimer's knowledge base
- `examples/projects/neurokb/neurokb.py` - Neuroscience knowledge base

### ista.owl2 Examples
- `examples/subgraph_extraction_example.py` - Biomedical subgraph extraction
- `examples/graph_conversion_example.py` - Convert to NetworkX/igraph
- `examples/owl2_roundtrip_example.py` - Create, serialize, parse
- `test_subgraph.py` - Test suite for filtering features

---

## FAQ

**Q: Why have two OWL2 libraries?**  
A: owlready2 was the original library used for database parsing. ista.owl2 is a new C++ library that provides better performance and advanced features. We maintain both during the transition period.

**Q: Will owlready2 be removed?**  
A: Not in the near future. It will remain for database parsing workflows until ista.owl2 provides equivalent functionality.

**Q: Can I convert between the two formats?**  
A: Not directly yet, but you can serialize with one and parse with the other via RDF/XML. Direct converters are planned for Phase 2.

**Q: Which is faster?**  
A: ista.owl2 is significantly faster due to optimized C++ implementation, especially for large ontologies and filtering operations.

**Q: Do they use the same file formats?**  
A: Yes, both work with standard OWL2 formats (RDF/XML, Functional Syntax, etc.).

---

## Getting Help

- **ista.owl2 Documentation**: See module docstrings in `ista/owl2.py`
- **owlready2 Documentation**: https://owlready2.readthedocs.io/
- **Issues**: https://github.com/JDRomano2/ista/issues (update with your actual repo)
- **Examples**: See `examples/` directory

---

*Last Updated: 2025-01-XX*  
*ista Version: 0.x.x*
