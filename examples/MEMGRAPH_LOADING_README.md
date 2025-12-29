# Loading NeuroKB into Memgraph

This guide explains how to load the enriched NeuroKB ontology (with DrugBank relationships) into Memgraph for graph analytics and querying.

## Overview

The loader transforms the RDF/XML ontology into Memgraph's property graph model:

- **RDF Individuals** → Memgraph Nodes
- **RDF Types (rdf:type)** → Node Labels
- **Data Properties** → Node Properties
- **Object Properties** → Relationships (edges)

## What Gets Loaded

From `neurokb-with-all-drug-relationships.rdf`:

| Component | Count | Description |
|-----------|-------|-------------|
| **Nodes** | 252,021 | Individuals in the ontology |
| **Relationships** | 1,791,486 | Object property assertions |
| **Node Types** | 12 | Gene, Drug, Disease, BiologicalProcess, etc. |
| **Relationship Types** | 22 | drugInteractsWithDrug, geneRegulatesGene, etc. |

### Top Node Types

| Label | Count | Description |
|-------|-------|-------------|
| Gene | 193,313 | Human genes |
| Drug | 36,959 | Drugs from DrugBank |
| BiologicalProcess | 11,381 | GO biological processes |
| Pathway | 4,570 | Biological pathways |
| MolecularFunction | 2,884 | GO molecular functions |
| CellularComponent | 1,391 | GO cellular components |
| Disease | 274 | Neurological diseases |
| Symptom | 438 | Clinical symptoms |
| BodyPart | 402 | Anatomical structures |

### Top Relationship Types

| Relationship | Count | Description |
|--------------|-------|-------------|
| geneParticipatesInBiologicalProcess | 559,385 | Gene-process associations |
| geneRegulatesGene | 265,667 | Gene regulatory interactions |
| geneInPathway | 179,433 | Gene-pathway memberships |
| **drugInteractsWithDrug** | **152,780** | Drug-drug interactions (major severity) |
| geneInteractsWithGene | 147,001 | Protein-protein interactions |
| bodyPartUnderexpressesGene | 102,185 | Tissue-specific underexpression |
| bodyPartOverexpressesGene | 97,772 | Tissue-specific overexpression |
| geneHasMolecularFunction | 97,191 | Gene-function annotations |
| **drugTreatsDisease** | **185** | Drug indications |
| **drugContraindicatedForDisease** | **166** | Drug contraindications |
| **drugCausesAdverseEvent** | **142** | Drug adverse events |

## Prerequisites

### 1. Install Neo4j Driver

```bash
pip install neo4j
```

### 2. Start Memgraph

Using Docker:

```bash
docker run -p 7687:7687 -p 7444:7444 memgraph/memgraph-platform
```

This starts:
- Memgraph database on port 7687 (Bolt protocol)
- Memgraph Lab UI on port 7444 (web interface)

Access Memgraph Lab at: http://localhost:7444

### 3. Verify Memgraph is Running

Open http://localhost:7444 in your browser. You should see the Memgraph Lab interface.

## Loading the Data

### Quick Start

```bash
cd D:\projects\ista\examples
python load_neurokb_to_memgraph.py
```

This will:
1. Parse the RDF file (takes ~20 seconds)
2. Clear the existing Memgraph database
3. Create indexes for performance
4. Load 252,021 nodes (~5 minutes)
5. Load 1,791,486 relationships (~30-60 minutes depending on hardware)

**Total time:** Approximately 35-70 minutes for the full dataset

### Loading Different Files

Specify a different RDF file:

```bash
python load_neurokb_to_memgraph.py kg_projects/neurokb/neurokb-populated.rdf
```

## Performance Tips

### Batch Size

Adjust batch size for your hardware:

```python
# In load_neurokb_to_memgraph.py, line ~456:
stats = loader.load_rdf_file(rdf_file, batch_size=5000)  # Default

# For faster loading (more memory):
stats = loader.load_rdf_file(rdf_file, batch_size=10000)

# For less memory:
stats = loader.load_rdf_file(rdf_file, batch_size=1000)
```

## Querying the Graph

### Using Memgraph Lab

Open http://localhost:7444 and try these queries:

#### Count nodes by type
```cypher
MATCH (n)
RETURN labels(n) as type, count(*) as count
ORDER BY count DESC;
```

#### Find a specific drug
```cypher
MATCH (d:Drug)
WHERE d.commonName CONTAINS 'Lepirudin'
RETURN d;
```

#### Find drugs that treat Alzheimer's
```cypher
MATCH (drug:Drug)-[:drugTreatsDisease]->(disease:Disease)
WHERE disease.commonName CONTAINS 'Alzheimer'
RETURN drug.commonName, disease.commonName;
```

#### Find drug-drug interactions for a specific drug
```cypher
MATCH (d1:Drug)-[:drugInteractsWithDrug]->(d2:Drug)
WHERE d1.commonName = 'Etanercept'
RETURN d1.commonName, d2.commonName
LIMIT 20;
```

#### Find genes in Alzheimer's-related pathways
```cypher
MATCH (gene:Gene)-[:geneInPathway]->(pathway:Pathway)
WHERE pathway.commonName CONTAINS 'Alzheimer'
RETURN gene.commonName, pathway.commonName
LIMIT 20;
```

#### Complex: Drugs, their interactions, and diseases they treat
```cypher
MATCH (d1:Drug)-[:drugInteractsWithDrug]->(d2:Drug)
MATCH (d1)-[:drugTreatsDisease]->(disease:Disease)
RETURN d1.commonName as drug1,
       d2.commonName as drug2,
       disease.commonName as treats
LIMIT 10;
```

#### Find genes associated with diseases that have treatments
```cypher
MATCH (gene:Gene)-[:geneAssociatesWithDisease]->(disease:Disease)
MATCH (drug:Drug)-[:drugTreatsDisease]->(disease)
RETURN disease.commonName,
       count(DISTINCT gene) as gene_count,
       count(DISTINCT drug) as drug_count
ORDER BY drug_count DESC
LIMIT 10;
```

### Using Python (neo4j driver)

```python
from neo4j import GraphDatabase

driver = GraphDatabase.driver("bolt://localhost:7687")

with driver.session() as session:
    # Run a query
    result = session.run("""
        MATCH (d:Drug)-[:drugTreatsDisease]->(dis:Disease)
        RETURN d.commonName as drug, dis.commonName as disease
        LIMIT 10
    """)

    for record in result:
        print(f"{record['drug']} treats {record['disease']}")

driver.close()
```

## Troubleshooting

### Connection Refused

**Problem:** `neo4j.exceptions.ServiceUnavailable: Failed to establish connection`

**Solution:** Ensure Memgraph is running:
```bash
docker ps  # Check if memgraph container is running
docker run -p 7687:7687 -p 7444:7444 memgraph/memgraph-platform
```

### Out of Memory During Loading

**Problem:** System runs out of memory

**Solutions:**
1. Reduce batch size (edit script, set `batch_size=1000`)
2. Increase Docker memory limit
3. Use a machine with more RAM

### Loading Takes Too Long

**Problem:** Loading relationships is very slow

**Explanation:** Creating 1.8 million relationships takes time. This is normal.

**Solutions:**
1. Increase batch size if you have RAM: `batch_size=10000`
2. Use SSD storage for better I/O performance
3. Consider loading a subset first (smaller RDF file)

### Database Already Has Data

**Problem:** Want to reload without duplicates

**Solution:** The loader clears the database by default. To preserve existing data:

```python
# Edit load_neurokb_to_memgraph.py
stats = loader.load_rdf_file(rdf_file, clear_existing=False)
```

## Advanced Usage

### Programmatic Loading

```python
from load_neurokb_to_memgraph import RDFMemgraphLoader

# Custom connection
loader = RDFMemgraphLoader(
    uri="bolt://your-server:7687",
    username="your-user",
    password="your-pass"
)

# Load with custom settings
stats = loader.load_rdf_file(
    "path/to/your/ontology.rdf",
    clear_existing=True,
    create_indexes=True,
    batch_size=5000
)

print(f"Loaded {stats['nodes']:,} nodes")
print(f"Loaded {stats['relationships']:,} relationships")

loader.close()
```

### Incremental Loading

To add more data without clearing:

```python
with RDFMemgraphLoader() as loader:
    # Load base ontology
    loader.load_rdf_file("neurokb-populated.rdf", clear_existing=True)

    # Add enriched relationships (without clearing)
    loader.load_rdf_file("neurokb-with-all-drug-relationships.rdf",
                        clear_existing=False)
```

## Performance Benchmarks

Approximate loading times on a typical workstation (16GB RAM, SSD):

| Stage | Items | Time |
|-------|-------|------|
| RDF Parsing | 252K nodes + 1.8M rels | 20 seconds |
| Node Creation | 252,021 nodes | 5 minutes |
| Relationship Creation | 1,791,486 relationships | 30-60 minutes |
| **Total** | | **35-70 minutes** |

Factors affecting performance:
- Hardware (CPU, RAM, disk I/O)
- Batch size setting
- Memgraph configuration
- System load

## Next Steps

Once loaded, you can:

1. **Run analytics** in Memgraph Lab
2. **Build applications** using the neo4j driver
3. **Export subgraphs** for specific analyses
4. **Visualize relationships** using Memgraph Lab's graph view
5. **Stream data** using Memgraph's streaming capabilities

## Additional Resources

- [Memgraph Documentation](https://memgraph.com/docs)
- [Cypher Query Language Guide](https://memgraph.com/docs/cypher-manual)
- [Neo4j Python Driver](https://neo4j.com/docs/api/python-driver/current/)
- [Memgraph Lab User Guide](https://memgraph.com/docs/memgraph-lab)
