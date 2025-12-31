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

See `drugbank_examples/README.md` and `DRUGBANK_INTEGRATION_README.md` for details.

### Memgraph Integration
See `memgraph_examples/` for graph database integration:
- Loading ontologies into Memgraph
- Querying with Cypher

See `memgraph_examples/MEMGRAPH_QUICK_START.md` for details.

## Complete Workflows

- **COMPLETE_WORKFLOW.md** - Step-by-step guide for building complete knowledge graphs from multiple data sources
- **QUICK_START.md** - Quick reference for common tasks

## Data Directories

- **csv_data/** - Sample CSV data for population examples
- **flatfile_data/** - Sample flat files for data import
- **kg_projects/** - Knowledge graph projects (e.g., NeuroKB)
  - `neurokb/` - Neuroscience knowledge base example

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
├── QUICK_START.md                      # Quick reference guide
├── COMPLETE_WORKFLOW.md                # Complete workflow guide
├── DRUGBANK_INTEGRATION_README.md      # DrugBank integration details
│
├── Core examples (*.py)                # Main example scripts
│
├── drugbank_examples/                  # DrugBank integration
│   ├── README.md
│   ├── add_drug_relationships.py       # Consolidated drug data script
│   ├── filter_drug_mappings.py         # Filter mappings by ontology
│   ├── check_severity_levels.py
│   └── *.csv                           # Drug mapping data files
│
├── memgraph_examples/                  # Graph database integration
│   ├── MEMGRAPH_QUICK_START.md
│   ├── MEMGRAPH_LOADING_README.md
│   ├── load_neurokb_to_memgraph.py
│   └── memgraph_integration_example.py
│
├── tests/                              # Test scripts
│   ├── test_turtle_roundtrip.py
│   └── test_turtle_serializer.py
│
├── csv_data/                           # Sample CSV data
├── flatfile_data/                      # Sample flat files
├── kg_projects/                        # Knowledge graph projects
│   └── neurokb/
│
└── archived_scripts/                   # Legacy scripts (reference only)
```

## Getting Help

- Main documentation: `../docs/`
- API reference: See `../docs/source/api/`
- Installation: See `../docs/source/installation.rst`

For issues or questions, see the project repository.
