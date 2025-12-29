# Quick Start: Adding All DrugBank Relationships to NeuroKB

## The Fast Way (Recommended)

```bash
cd D:\projects\ista\examples

# 1. Extract all mappings from DrugBank (takes a few minutes)
python indication_map.py
python contraindication_map.py
python adverse_event_map.py
python drug_interaction_map.py

# 2. Filter to only entities in NeuroKB (fast)
python filter_mappings_by_ontology.py
python filter_contraindication_mappings_by_ontology.py
python filter_adverse_event_mappings_by_ontology.py
python filter_drug_interaction_mappings_by_ontology.py

# 3. Add all relationships to ontology (takes 1-2 minutes)
python add_all_drug_relationships_direct.py
```

**Output:** `kg_projects/neurokb/neurokb-with-all-drug-relationships.rdf` (267 MB)

## What Gets Added

| Relationship Type | Property Name | Count | Type |
|------------------|---------------|--------|------|
| Indications | drugTreatsDisease | 185 | Drug → Disease |
| Contraindications | drugContraindicatedForDisease | 166 | Drug → Disease |
| Adverse Events | drugCausesAdverseEvent | 142 | Drug → Disease |
| Drug Interactions | drugInteractsWithDrug | 152,780 | Drug → Drug |
| **TOTAL** | | **153,273** | |

## Individual Workflows

If you only want specific relationship types:

### Indications Only
```bash
python indication_map.py
python filter_mappings_by_ontology.py
python add_drug_disease_relationships_direct.py
```

### Contraindications Only
```bash
python contraindication_map.py
python filter_contraindication_mappings_by_ontology.py
python add_drug_contraindication_relationships_direct.py
```

### Adverse Events Only
```bash
python adverse_event_map.py
python filter_adverse_event_mappings_by_ontology.py
python add_drug_adverse_event_relationships_direct.py
```

### Drug Interactions Only
```bash
python drug_interaction_map.py
python filter_drug_interaction_mappings_by_ontology.py
python add_drug_interaction_relationships_direct.py
```

## Key Points

- **Drug interactions dominate** - 152,780 out of 153,273 total relationships (99.7%)
- **Drug-disease relationships are limited** by NeuroKB's 274 diseases (neurological focus)
- **All scripts preserve original content** - no data loss (direct RDF modification)
- **Major severity only** - drug interactions filtered to severity = 2 (most serious)

## Verification

Check the output file was created successfully:
```bash
ls -lh kg_projects/neurokb/neurokb-with-all-drug-relationships.rdf
# Should show ~267 MB
```

Count relationships added:
```bash
grep -c "drugTreatsDisease" kg_projects/neurokb/neurokb-with-all-drug-relationships.rdf
grep -c "drugContraindicatedForDisease" kg_projects/neurokb/neurokb-with-all-drug-relationships.rdf
grep -c "drugCausesAdverseEvent" kg_projects/neurokb/neurokb-with-all-drug-relationships.rdf
grep -c "drugInteractsWithDrug" kg_projects/neurokb/neurokb-with-all-drug-relationships.rdf
```

## Next Steps

### Option 1: Analyze the RDF Ontology Directly

Use the enriched ontology for:
- OWL reasoning with tools like Konclude
- SPARQL querying
- Semantic web applications
- Ontology-based data integration

### Option 2: Load into Memgraph for Graph Analytics

```bash
# Install neo4j driver
pip install neo4j

# Start Memgraph
docker run -p 7687:7687 -p 7444:7444 memgraph/memgraph-platform

# Load the ontology (takes ~35-70 minutes)
python load_neurokb_to_memgraph.py
```

Access Memgraph Lab at http://localhost:7444 to query and visualize the graph.

**What gets loaded:**
- 252,021 nodes (drugs, genes, diseases, pathways, etc.)
- 1,791,486 relationships (drug interactions, gene regulations, etc.)
- Full Cypher query support for graph analytics

See:
- `MEMGRAPH_QUICK_START.md` - Quick reference for Memgraph loading
- `MEMGRAPH_LOADING_README.md` - Complete guide with queries and troubleshooting
- `DRUGBANK_INTEGRATION_README.md` - Full DrugBank integration documentation
