# ISTA Examples

This directory contains examples demonstrating the core functionality of the ISTA library for OWL ontology manipulation and knowledge graph construction.

## Quick Start

New users should start with these examples in order:

1. **owl2_example.py** - Basic OWL2 ontology creation and manipulation
2. **native_csv_population_example.py** - Populate ontologies from CSV data using native parser
3. **subgraph_extraction_example.py** - Extract subgraphs around entities of interest
4. **owl2_roundtrip_example.py** - Serialize and parse ontologies in different formats

## Core Examples

### Ontology Creation and Manipulation

- **owl2_example.py** - Demonstrates basic OWL2 API usage: creating classes, individuals, properties, and axioms
- **social_network_ontology.py** - Build a small social network ontology from scratch

### Data Population

- **native_csv_population_example.py** - Populate ontology individuals from CSV using native C++ parser (recommended)
- **flatfile_population_example.py** - Populate from flat file data sources
- **graph_conversion_example.py** - Convert between graph representations

### Analysis and Extraction

- **subgraph_extraction_example.py** - High-performance subgraph extraction using OntologyFilter
- **knowledge_graph_analysis.py** - Analyze knowledge graph structure and statistics

### Reasoning

- **konclude_reasoning_example.py** - OWL reasoning using Konclude reasoner integration

### Serialization

- **owl2_roundtrip_example.py** - Serialize and deserialize ontologies (RDF/XML, Turtle, Functional Syntax)

## Specialized Examples

### DrugBank Integration

See `drugbank_examples/` for scripts to integrate DrugBank drug data:
- Drug-disease indications
- Drug-drug interactions
- Adverse events
- Contraindications

**Key scripts:**
- `add_drug_relationships.py` - Consolidated script for all relationship types
- `filter_drug_mappings.py` - Filter mappings to entities in your ontology

See `drugbank_examples/README.md` for details.

### Memgraph Graph Database Integration

See `memgraph_examples/` for loading ontologies into Memgraph:
- **memgraph_integration_example.py** - Build and load an ontology via the OWL2 API
- **load_neurokb_to_memgraph.py** - Example loading NeuroKB RDF file

**CLI Tool:** Use `owl2memgraph` to load any OWL2 ontology into Memgraph:
```bash
# Install
pip install -e .[neo4j]

# Load an ontology (auto-detects format from extension)
owl2memgraph -i ontology.rdf
owl2memgraph -i ontology.ttl
owl2memgraph -i ontology.ofn

# With options
owl2memgraph -i ontology.rdf --uri bolt://localhost:7687 --batch-size 2000
```

Supported formats: RDF/XML (.rdf, .owl), Turtle (.ttl), Functional Syntax (.ofn), Manchester (.omn), OWL/XML (.owx)

## Knowledge Graph Projects

### pharmatox_example/
Synthetic biomedical example demonstrating the complete data loading workflow with YAML mapping specifications.

### kg_projects/
Real knowledge graph projects:
- **neurokb/** - Neuroscience knowledge base with drug, gene, disease, and pathway data
- **alzkb/** - Alzheimer's disease knowledge base

## Data Directories

- **csv_data/** - Sample CSV data for population examples
- **flatfile_data/** - Sample flat files for data import

## Test Scripts

See `tests/` for validation scripts:
- Turtle format round-trip tests
- Serialization tests

## Archived Scripts

`archived_scripts/` contains older iteration scripts that have been superseded by consolidated versions. These are kept for reference but are not maintained.

## Directory Structure

```
examples/
├── README.md                           # This file
│
├── Core examples (*.py)                # Main example scripts
│
├── drugbank_examples/                  # DrugBank integration
│   ├── README.md
│   ├── add_drug_relationships.py       # Consolidated drug data script
│   └── filter_drug_mappings.py         # Filter mappings by ontology
│
├── memgraph_examples/                  # Graph database integration
│   ├── load_neurokb_to_memgraph.py     # NeuroKB loading example
│   └── memgraph_integration_example.py # OWL2 API integration example
│
├── pharmatox_example/                  # Synthetic biomedical example
│   ├── README.md
│   └── config/                         # YAML mapping specifications
│
├── kg_projects/                        # Knowledge graph projects
│   ├── neurokb/                        # Neuroscience KB
│   └── alzkb/                          # Alzheimer's KB
│
├── tests/                              # Test scripts
│
├── csv_data/                           # Sample CSV data
├── flatfile_data/                      # Sample flat files
│
└── archived_scripts/                   # Legacy scripts (reference only)
```

## Getting Help

- Main documentation: `../docs/`
- API reference: See `../docs/source/api/`
- Installation: See `../docs/source/installation.rst`

For issues or questions, see the project repository.
