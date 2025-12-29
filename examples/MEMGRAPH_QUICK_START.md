# Memgraph Loading - Quick Start

## Setup (One Time)

```bash
# Install neo4j driver
pip install neo4j

# Start Memgraph
docker run -p 7687:7687 -p 7444:7444 memgraph/memgraph-platform
```

## Load Data

```bash
cd D:\projects\ista\examples
python load_neurokb_to_memgraph.py
```

**Time:** ~35-70 minutes for full neurokb (252K nodes, 1.8M relationships)

## Access

- **Memgraph Lab UI:** http://localhost:7444
- **Bolt Protocol:** bolt://localhost:7687

## Quick Queries (paste in Memgraph Lab)

### Count Everything
```cypher
MATCH (n) RETURN labels(n) as type, count(*) as count ORDER BY count DESC;
```

### Find Drugs Treating Alzheimer's
```cypher
MATCH (drug:Drug)-[:drugTreatsDisease]->(disease:Disease)
WHERE disease.commonName CONTAINS 'Alzheimer'
RETURN drug.commonName, disease.commonName;
```

### Drug-Drug Interactions
```cypher
MATCH (d1:Drug)-[:drugInteractsWithDrug]->(d2:Drug)
RETURN d1.commonName, d2.commonName LIMIT 10;
```

### Genes in Alzheimer's Pathways
```cypher
MATCH (gene:Gene)-[:geneInPathway]->(pathway:Pathway)
WHERE pathway.commonName CONTAINS 'Alzheimer'
RETURN gene.commonName, pathway.commonName LIMIT 10;
```

## What's in the Graph

| Component | Count |
|-----------|-------|
| Nodes | 252,021 |
| Relationships | 1,791,486 |
| Drugs | 36,959 |
| Genes | 193,313 |
| Diseases | 274 |
| Drug Interactions | 152,780 |
| Drug-Disease (treats) | 185 |
| Drug-Disease (contraindicated) | 166 |
| Drug-Disease (adverse events) | 142 |

## Common Issues

**"Connection refused"** → Start Memgraph: `docker run -p 7687:7687 -p 7444:7444 memgraph/memgraph-platform`

**"Too slow"** → Edit script, increase batch_size to 10000

**"Out of memory"** → Edit script, decrease batch_size to 1000

## Full Documentation

See `MEMGRAPH_LOADING_README.md` for complete guide.
