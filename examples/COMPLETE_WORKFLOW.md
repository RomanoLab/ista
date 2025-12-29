# Complete Workflow: DrugBank → NeuroKB → Memgraph

This document shows the complete end-to-end workflow for enriching the NeuroKB ontology with DrugBank data and loading it into Memgraph for graph analytics.

## Overview

```
DrugBank CSV Files
       ↓
  Extract & Map (Python)
       ↓
  Filter by NeuroKB (Python)
       ↓
  Add to RDF (Direct XML modification)
       ↓
  Enriched RDF Ontology
       ↓
  Parse & Load (Python + Memgraph)
       ↓
  Knowledge Graph (Memgraph)
```

## Phase 1: DrugBank Integration (2-3 minutes)

### Extract Drug Relationships from DrugBank

```bash
cd D:\projects\ista\examples

# Extract all four relationship types
python indication_map.py           # Drug indications (treats disease)
python contraindication_map.py     # Drug contraindications
python adverse_event_map.py        # Adverse events (side effects)
python drug_interaction_map.py     # Drug-drug interactions (major severity)
```

**Output:**
- `drug_disease_mappings.csv` (15,753 pairs)
- `drug_contraindication_mappings.csv` (9,294 pairs)
- `drug_adverse_event_mappings.csv` (314,458 pairs)
- `drug_interaction_mappings.csv` (154,684 pairs - major severity only)

### Filter by NeuroKB Content

```bash
# Filter to only include drugs/diseases that exist in NeuroKB
python filter_mappings_by_ontology.py
python filter_contraindication_mappings_by_ontology.py
python filter_adverse_event_mappings_by_ontology.py
python filter_drug_interaction_mappings_by_ontology.py
```

**Output:**
- `drug_disease_mappings_filtered.csv` (185 pairs)
- `drug_contraindication_mappings_filtered.csv` (166 pairs)
- `drug_adverse_event_mappings_filtered.csv` (142 pairs)
- `drug_interaction_mappings_filtered.csv` (152,780 pairs)

**Why fewer?** NeuroKB has comprehensive drug coverage (37K drugs) but limited disease coverage (274 neurological diseases), so drug-disease relationships are heavily filtered. Drug-drug interactions preserve 98.8% of data.

## Phase 2: RDF Ontology Enrichment (1-2 minutes)

### Add All Relationships to NeuroKB

```bash
# All-in-one: adds all four relationship types
python add_all_drug_relationships_direct.py
```

**What it does:**
1. Reads `neurokb-populated.rdf` (243 MB)
2. Adds 3 new object properties:
   - `drugContraindicatedForDisease`
   - `drugCausesAdverseEvent`
   - `drugInteractsWithDrug`
3. Adds 153,273 relationships:
   - 185 indications (uses existing `drugTreatsDisease`)
   - 166 contraindications
   - 142 adverse events
   - 152,780 drug-drug interactions
4. Saves to `neurokb-with-all-drug-relationships.rdf` (267 MB)

**Key:** Uses direct XML modification to preserve ALL original content (no data loss).

### Alternative: Add Relationships Individually

```bash
# Add only indications
python add_drug_disease_relationships_direct.py

# Add only contraindications
python add_drug_contraindication_relationships_direct.py

# Add only adverse events
python add_drug_adverse_event_relationships_direct.py

# Add only drug interactions
python add_drug_interaction_relationships_direct.py
```

## Phase 3: Memgraph Loading (35-70 minutes)

### Prerequisites

```bash
# Install neo4j driver
pip install neo4j

# Start Memgraph (Docker)
docker run -p 7687:7687 -p 7444:7444 memgraph/memgraph-platform
```

### Load into Memgraph

```bash
# Load the enriched ontology
python load_neurokb_to_memgraph.py
```

**What it does:**
1. Parses RDF/XML file (~20 seconds)
2. Extracts 252,021 individuals (nodes)
3. Extracts 1,791,486 object properties (relationships)
4. Creates indexes in Memgraph
5. Loads nodes (~5 minutes)
6. Loads relationships (~30-60 minutes)

**Output:** Knowledge graph in Memgraph with 252K nodes and 1.8M edges

### Verify Loading

Open Memgraph Lab: http://localhost:7444

Run a test query:
```cypher
MATCH (n) RETURN labels(n) as type, count(*) as count ORDER BY count DESC;
```

You should see:
- Gene: 193,313
- Drug: 36,959
- BiologicalProcess: 11,381
- Disease: 274
- etc.

## Phase 4: Graph Analytics

### Using Memgraph Lab (Web UI)

Open http://localhost:7444 and explore:

#### Find drugs treating Alzheimer's
```cypher
MATCH (drug:Drug)-[:drugTreatsDisease]->(disease:Disease)
WHERE disease.commonName CONTAINS 'Alzheimer'
RETURN drug.commonName as drug, disease.commonName as disease;
```

#### Explore drug-drug interactions
```cypher
MATCH (d1:Drug)-[:drugInteractsWithDrug]->(d2:Drug)
WHERE d1.commonName = 'Etanercept'
RETURN d1.commonName, d2.commonName LIMIT 20;
```

#### Find pathways with most genes
```cypher
MATCH (gene:Gene)-[:geneInPathway]->(pathway:Pathway)
RETURN pathway.commonName, count(gene) as gene_count
ORDER BY gene_count DESC LIMIT 10;
```

#### Complex: Drug repurposing candidates
```cypher
// Find drugs treating disease A that might work for disease B
// based on shared gene associations
MATCH (drug:Drug)-[:drugTreatsDisease]->(diseaseA:Disease)
MATCH (geneA:Gene)-[:geneAssociatesWithDisease]->(diseaseA)
MATCH (geneB:Gene)-[:geneAssociatesWithDisease]->(diseaseB:Disease)
WHERE diseaseA <> diseaseB
  AND geneA = geneB
RETURN drug.commonName,
       diseaseA.commonName as treats,
       diseaseB.commonName as potential_target,
       count(DISTINCT geneA) as shared_genes
ORDER BY shared_genes DESC
LIMIT 10;
```

### Using Python

```python
from neo4j import GraphDatabase

driver = GraphDatabase.driver("bolt://localhost:7687")

with driver.session() as session:
    # Query for drugs and their interactions
    result = session.run("""
        MATCH (d1:Drug)-[:drugInteractsWithDrug]->(d2:Drug)
        RETURN d1.commonName as drug1,
               d2.commonName as drug2
        LIMIT 100
    """)

    interactions = [(r['drug1'], r['drug2']) for r in result]
    print(f"Found {len(interactions)} drug interactions")

driver.close()
```

## Complete Statistics

### Data at Each Stage

| Stage | Drugs | Diseases | Relationships |
|-------|-------|----------|---------------|
| DrugBank (extracted) | 2,638 | 10,480 | 493,989 |
| Filtered by NeuroKB | 88-3,017 | 16-111 | 493 (drug-disease) + 152,780 (drug-drug) |
| NeuroKB RDF | 36,959 | 274 | 153,273 (added) |
| Memgraph Graph | 36,959 | 274 | 1,791,486 (total) |

### Relationship Breakdown in Memgraph

| Relationship Type | Count | Source |
|-------------------|-------|--------|
| geneParticipatesInBiologicalProcess | 559,385 | Original NeuroKB |
| geneRegulatesGene | 265,667 | Original NeuroKB |
| geneInPathway | 179,433 | Original NeuroKB |
| **drugInteractsWithDrug** | **152,780** | **DrugBank** |
| geneInteractsWithGene | 147,001 | Original NeuroKB |
| bodyPartUnderexpressesGene | 102,185 | Original NeuroKB |
| bodyPartOverexpressesGene | 97,772 | Original NeuroKB |
| **drugTreatsDisease** | **185** | **DrugBank** |
| **drugContraindicatedForDisease** | **166** | **DrugBank** |
| **drugCausesAdverseEvent** | **142** | **DrugBank** |

## Time Estimates

| Phase | Task | Time |
|-------|------|------|
| 1 | Extract from DrugBank | 2-3 minutes |
| 1 | Filter by NeuroKB | < 1 minute |
| 2 | Add to RDF | 1-2 minutes |
| 3 | Parse RDF | 20 seconds |
| 3 | Load to Memgraph | 35-70 minutes |
| **Total** | | **~40-80 minutes** |

## Disk Space Requirements

| File | Size | Description |
|------|------|-------------|
| DrugBank CSVs | ~3.4 GB | Original DrugBank data |
| Mapping CSVs | ~50 MB | Intermediate mapping files |
| neurokb-populated.rdf | 243 MB | Original NeuroKB |
| neurokb-with-all-drug-relationships.rdf | 267 MB | Enriched NeuroKB |
| Memgraph database | ~500 MB | In-memory + disk storage |
| **Total** | **~4.5 GB** | |

## Troubleshooting

### Phase 1 Issues

**"File not found: D:/data/drugbank/..."**
- Download DrugBank CSV files to `D:/data/drugbank/2025-11-19/`

**"No mappings found"**
- Check that UMLS CUI mappings exist in `condition_external_identifiers.csv`

### Phase 2 Issues

**"Output file is 125 KB (should be 267 MB)"**
- You're using the wrong script (uses ista parser which loses data)
- Use `add_all_drug_relationships_direct.py` instead

### Phase 3 Issues

**"Connection refused"**
- Start Memgraph: `docker run -p 7687:7687 -p 7444:7444 memgraph/memgraph-platform`

**"Out of memory"**
- Reduce batch size in script: `batch_size=1000`
- Increase Docker memory limit

**"Too slow"**
- This is normal for 1.8M relationships (~30-60 minutes)
- Increase batch size if you have RAM: `batch_size=10000`

## Quick Reference

### All Scripts
```bash
# Phase 1: Extract & Filter
python indication_map.py && python filter_mappings_by_ontology.py
python contraindication_map.py && python filter_contraindication_mappings_by_ontology.py
python adverse_event_map.py && python filter_adverse_event_mappings_by_ontology.py
python drug_interaction_map.py && python filter_drug_interaction_mappings_by_ontology.py

# Phase 2: Enrich RDF
python add_all_drug_relationships_direct.py

# Phase 3: Load Memgraph
python load_neurokb_to_memgraph.py
```

### Key Files
- `QUICK_START.md` - Fast track guide
- `DRUGBANK_INTEGRATION_README.md` - DrugBank integration details
- `MEMGRAPH_LOADING_README.md` - Memgraph loading guide
- `MEMGRAPH_QUICK_START.md` - Memgraph quick reference

## Use Cases

### Drug Repurposing
Identify new indications for existing drugs based on:
- Shared gene associations between diseases
- Pathway overlap
- Mechanism of action similarity

### Safety Analysis
Evaluate drug safety profiles:
- Identify contraindication patterns
- Analyze adverse event clustering
- Map drug-drug interaction networks

### Pathway Analysis
Understand biological mechanisms:
- Gene regulatory networks
- Disease pathway associations
- Drug mechanism pathways

### Precision Medicine
Patient-specific analysis:
- Gene-drug interaction predictions
- Personalized risk assessment
- Treatment optimization

## Next Steps

1. **Explore the graph** using Memgraph Lab
2. **Build applications** using the neo4j Python driver
3. **Run analytics** using Cypher queries
4. **Export subgraphs** for machine learning
5. **Integrate with other data** sources (clinical, genomic, etc.)

## Resources

- [Memgraph Documentation](https://memgraph.com/docs)
- [DrugBank](https://go.drugbank.com/)
- [NeuroKB Paper](https://doi.org/10.1093/database/baac107)
- [Cypher Query Language](https://neo4j.com/docs/cypher-manual/current/)
