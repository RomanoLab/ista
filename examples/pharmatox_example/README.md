# PharmaTox: Synthetic Biomedical Knowledge Graph Example

## Overview

PharmaTox is a **toy example** demonstrating ISTA's knowledge graph building capabilities. It showcases how to integrate multimodal data from various sources (CSV, TSV, SQLite) into an OWL2 ontology representing drug-gene-disease-pathway relationships.

**IMPORTANT**: This example uses **entirely synthetic data** for testing and demonstration purposes only. The relationships between drugs, genes, diseases, and other entities are **fictitious** and should **NOT** be used for any real biomedical research or clinical decision-making.

## Features Demonstrated

| Feature | Description |
|---------|-------------|
| Multi-format data sources | CSV, TSV, and SQLite database integration |
| Primary/Enrichment pattern | Drug entities enriched with toxicity data via CAS number matching |
| Cross-reference identifiers | DrugBank, NCBI Gene, UMLS, Reactome, MedDRA, Cell Ontology |
| Relationship mapping | 7 different relationship types connecting entities |
| Ontology formats | Both RDF/XML and Turtle format ontology files |
| YAML configuration | Declarative mapping specification |

## Directory Structure

```
pharmatox_example/
├── README.md                      # This file
├── ontology/
│   ├── pharmatox.owl              # Ontology in RDF/XML format
│   └── pharmatox.ttl              # Ontology in Turtle format
├── data/
│   ├── drugs.csv                  # Primary drug data (10 drugs)
│   ├── drug_toxicity.csv          # Toxicity enrichment data
│   ├── genes.tsv                  # Gene data (12 genes)
│   ├── diseases.tsv               # Disease data (8 diseases)
│   ├── pathways.tsv               # Pathway data (6 pathways)
│   └── pharmatox.db               # SQLite database with relationships
├── config/
│   └── pharmatox_mapping.yaml     # YAML mapping configuration
└── scripts/
    ├── create_sqlite_db.py        # Script to create SQLite database
    └── build_pharmatox.py         # Script to build the knowledge graph
```

## Entity Types

| Entity | Count | Source | Identifiers |
|--------|-------|--------|-------------|
| Drug | 10 | CSV | DrugBank ID, CAS RN, PubChem CID |
| Gene | 12 | TSV | NCBI Gene ID, Gene Symbol |
| Disease | 8 | TSV | UMLS CUI, MeSH ID |
| Pathway | 6 | TSV | Reactome ID |
| AdverseEvent | 8 | SQLite | MedDRA ID |
| DrugClass | 6 | Derived | Name |
| CellType | 5 | SQLite | Cell Ontology ID |

**Total: ~55 individuals**

## Relationships

| Relationship | Count | Description |
|--------------|-------|-------------|
| drugTreatsDisease | 15 | Drug therapeutic indications |
| drugTargetsGene | 18 | Drug-gene target interactions |
| geneAssociatesWithDisease | 20 | Gene-disease associations |
| geneInPathway | 15 | Gene pathway memberships |
| drugCausesAdverseEvent | 20 | Drug side effects |
| drugInClass | 10 | Drug pharmacological classes |
| geneExpressedInCellType | 12 | Gene expression locations |

**Total: ~110 relationships**

## Quick Start

### 1. Create the SQLite Database

```bash
cd examples/pharmatox_example/scripts
python create_sqlite_db.py
```

### 2. Build the Knowledge Graph

```bash
python build_pharmatox.py
```

This will create `pharmatox_populated.owl` in the example directory.

### 3. Explore the Result

The populated ontology can be:
- Loaded into ISTA's GUI for visualization
- Queried using SPARQL
- Converted to graph formats (NetworkX, igraph)
- Loaded into graph databases (Neo4j, Memgraph)

## YAML Configuration

The `config/pharmatox_mapping.yaml` file demonstrates ISTA's declarative mapping specification:

```yaml
version: "1.0"
base_iri: "http://example.org/pharmatox#"

sources:
  drugs_csv:
    type: csv
    path: "./data/drugs.csv"
  
  pharmatox_db:
    type: sqlite
    path: "./data/pharmatox.db"

entity_types:
  Drug:
    primary:
      source: drugs_csv
      iri_column: drugbank_id
      properties:
        - { column: drugbank_id, property: xrefDrugbank }
        - { column: common_name, property: commonName }
    enrichments:
      - name: "Drug Toxicity Data"
        source: drug_toxicity_csv
        match:
          source_column: cas_number
          target_property: xrefCasRN
        properties:
          - { column: ld50_value, property: ld50Value, datatype: float }

relationship_mappings:
  - name: "Drug Treats Disease"
    source: pharmatox_db
    table: drug_treats_disease
    relationship: drugTreatsDisease
    subject:
      class_name: Drug
      column: drugbank_id
      match_property: xrefDrugbank
    object:
      class_name: Disease
      column: umls_cui
      match_property: xrefUmlsCUI
```

## Data Sources

### CSV Files (Comma-Separated)
- `drugs.csv`: Primary drug information with DrugBank IDs
- `drug_toxicity.csv`: LD50 values for enriching drug entities

### TSV Files (Tab-Separated)
- `genes.tsv`: Human genes with NCBI Gene IDs
- `diseases.tsv`: Medical conditions with UMLS CUIs
- `pathways.tsv`: Biological pathways with Reactome IDs

### SQLite Database
Contains relationship tables and additional entity types:
- `adverse_events`: Side effect entities
- `cell_types`: Cell type entities
- `drug_treats_disease`: Treatment relationships
- `drug_targets_gene`: Drug-gene interactions
- `gene_disease_association`: Gene-disease links
- `gene_pathway`: Pathway memberships
- `drug_adverse_event`: Side effect associations
- `gene_expression`: Cell type expression

## Ontology Namespaces

| Prefix | Namespace |
|--------|-----------|
| ptox | http://example.org/pharmatox# |
| owl | http://www.w3.org/2002/07/owl# |
| rdfs | http://www.w3.org/2000/01/rdf-schema# |
| xsd | http://www.w3.org/2001/XMLSchema# |

## Disclaimer

This example is provided for **educational and testing purposes only**. The data is:

- **Synthetic**: All relationships are artificially generated
- **Incomplete**: Does not represent real biomedical knowledge
- **Not validated**: Should not be used for research or clinical purposes

For real biomedical knowledge graphs, please use validated data sources such as:
- DrugBank (https://go.drugbank.com/)
- NCBI Gene (https://www.ncbi.nlm.nih.gov/gene/)
- DisGeNET (https://www.disgenet.org/)
- Reactome (https://reactome.org/)

## License

This example is part of the ISTA project and is provided under the same license terms.
