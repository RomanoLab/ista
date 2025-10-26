# ista

> **ista** _N._ — (Sindarin) Knowledge

A hybrid Python/C++ toolkit for manipulating and building knowledge graphs with support for OWL2 ontologies.

## Overview

**ista** combines Python flexibility for data integration with C++ performance for knowledge graph manipulation. The project consists of:

- **Python Package (`ista/`)**: Tools for building knowledge graphs from third-party data sources
- **C++ Library (`lib/`)**: High-performance OWL2 ontology manipulation library (`libista`)

## Components

### Python Package

The Python package provides tools for:
- Parsing flat files (CSV, TSV, XLSX) and MySQL databases
- Converting structured data into OWL2 ontologies
- Loading knowledge graphs into Neo4j graph databases
- Custom graph data structures
- **Python bindings to high-performance C++ OWL2 library**

**Key Features:**
- Integration with `owlready2` for OWL2 manipulation
- **Native C++ OWL2 library bindings via pybind11**
- Database parsers for MySQL and flat files
- Neo4j loader via Neosemantics (n10s)
- Example knowledge bases (AlzKB, NeuroKB)
- **RDF/XML and Functional Syntax serialization**

### C++ Library (libista)

A modern C++20 library for parsing, creating, and manipulating OWL2 ontologies.

**Key Features:**
- Complete OWL2 structural specification implementation
- 40+ axiom types (classes, properties, individuals, assertions)
- Complex class expressions and data ranges
- IRI management with prefix support
- Ontology container with rich query API
- **RDF/XML serialization (.owl/.rdf files)**
- **Functional Syntax serialization (.ofn files)**
- **Python bindings via pybind11**
- No external dependencies for core functionality

See [lib/README.md](lib/README.md) for detailed C++ library documentation.

## Project Status

### Completed Features

- [x] Python tools for building semantic graph databases from public sources
- [x] C++ library for high-performance OWL2 ontology manipulation
- [x] **Python bindings to C++ library (pybind11)**
- [x] **RDF/XML serialization (.owl/.rdf files)**
- [x] OWL2 Functional Syntax serialization (.ofn files)
- [x] Comprehensive entity, axiom, and expression support
- [x] Example programs and documentation

### In Progress / Planned

- [ ] RDF/XML parser for reading OWL2 files
- [ ] Turtle parser and serializer
- [ ] Manchester Syntax support
- [ ] Graph summarization and characterization tools
- [ ] Conversion tools between graph representations
- [ ] Fast subgraph generators
- [ ] Performance optimizations for large graphs

## Installation

### Python Package

```bash
pip install -r requirements.txt
pip install -e .
```

### C++ Library

```bash
mkdir build && cd build
cmake ..
cmake --build .
```

The library will be built as `libista` (or `ista.lib` on Windows).

## Quick Start

### Python Example with C++ OWL2 Library

```python
from ista import owl2

# Create an ontology using the high-performance C++ library
onto = owl2.Ontology(owl2.IRI("http://example.org/myonto"))
onto.register_prefix("ex", "http://example.org/myonto#")

# Create and declare a class
person = owl2.Class(owl2.IRI("ex", "Person", "http://example.org/myonto#"))
onto.add_axiom(owl2.Declaration(owl2.EntityType.CLASS, person.get_iri()))

# Create a subclass
student = owl2.Class(owl2.IRI("ex", "Student", "http://example.org/myonto#"))
onto.add_axiom(owl2.Declaration(owl2.EntityType.CLASS, student.get_iri()))
onto.add_axiom(owl2.SubClassOf(owl2.NamedClass(student), owl2.NamedClass(person)))

# Save to RDF/XML (.owl) and Functional Syntax (.ofn)
owl2.RDFXMLSerializer.serialize_to_file(onto, "output.owl")
owl2.FunctionalSyntaxSerializer.serialize_to_file(onto, "output.ofn")
```

### Python Example with Database Parser

```python
import owlready2
from ista import FlatFileDatabaseParser

# Load or create an ontology
onto = owlready2.get_ontology("http://example.org/myonto").load()

# Parse data from CSV file
parser = FlatFileDatabaseParser("drugbank", onto, "./data")
parser.parse_node_type(
    node_type="Drug",
    source_filename="drugs.csv",
    fmt="csv",
    parse_config={
        "iri_column_name": "DrugID",
        "data_property_map": {
            "DrugID": onto.drugID,
            "Name": onto.commonName,
        }
    }
)

# Save ontology
with open("output.rdf", "wb") as f:
    onto.save(file=f, format="rdfxml")
```

### C++ Example

```cpp
#include "owl2/owl2.hpp"
using namespace ista::owl2;

int main() {
    // Create ontology
    Ontology onto(IRI("http://example.org/myonto"));
    onto.registerPrefix("ex", "http://example.org/myonto#");
    
    // Create a class
    Class person(IRI("ex", "Person", "http://example.org/myonto#"));
    onto.addAxiom(std::make_shared<Declaration>(
        Declaration::EntityType::CLASS, person.getIRI()));
    
    // Serialize
    FunctionalSyntaxSerializer::serializeToFile(onto, "output.ofn");
    return 0;
}
```

See [src/ista.cpp](src/ista.cpp) for a complete working example.

## Directory Structure

```
ista/
├── ista/                      # Python package
│   ├── __init__.py
│   ├── ista.py                # CLI interface
│   ├── database_parser.py      # Data source parsers
│   ├── load_kb.py             # Neo4j loader
│   ├── graph/                 # Graph data structures
│   └── tests/                 # Python tests
├── lib/                       # C++ library (libista)
│   ├── owl2/                  # OWL2 sub-library
│   │   ├── core/              # Core OWL2 structures
│   │   ├── serializer/        # Output formats
│   │   └── parser/            # Input parsers (planned)
│   └── CMakeLists.txt
├── src/                       # C++ example executable
│   └── ista.cpp
├── examples/                  # Example knowledge bases
│   └── projects/
│       ├── alzkb/             # Alzheimer KB
│       └── neurokb/           # Neurology KB
├── CMakeLists.txt             # Root build config
├── setup.py                   # Python package setup
└── README.md                  # This file
```

## Documentation

- **C++ Library**: See [lib/README.md](lib/README.md) for API documentation
- **OWL2 Implementation**: See [lib/owl2/README.md](lib/owl2/README.md) for technical details

## Examples

### Python Knowledge Bases

- **AlzKB** ([examples/projects/alzkb/](examples/projects/alzkb/)): Alzheimer disease knowledge graph
- **NeuroKB** ([examples/projects/neurokb/](examples/projects/neurokb/)): Neurology knowledge graph

### C++ Examples

- **University Ontology** ([src/ista.cpp](src/ista.cpp)): Complete example with classes, properties, individuals

## Requirements

### Python
- Python 3.7+
- owlready2
- pandas
- neo4j (optional, for database loading)
- networkx (optional, for graph algorithms)

See [requirements.txt](requirements.txt) for full list.

### C++
- C++20 compatible compiler (GCC 10+, Clang 12+, MSVC 2019+)
- CMake 3.15+
- No external dependencies for core library

## Contributing

Contributions are welcome! Areas of interest:
- RDF/XML and Turtle parsers
- Python bindings (pybind11)
- Additional serialization formats
- Performance optimizations
- Graph algorithms
- Documentation improvements

## License

MIT License - See LICENSE file for details.

## References

- [OWL 2 Web Ontology Language Structural Specification](https://www.w3.org/TR/owl2-syntax/)
- [OWL 2 Web Ontology Language Primer](https://www.w3.org/TR/owl2-primer/)
- [Owlready2 Documentation](https://owlready2.readthedocs.io/)
