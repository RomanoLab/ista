# Memgraph Graph Database Integration

This guide explains how to populate Memgraph graph databases from OWL2 ontologies using ISTA.

Memgraph is a high-performance, in-memory graph database compatible with Neo4j's Cypher query language, designed for real-time analytics, streaming graph data, and ACID transactions.

## Overview

The integration maps OWL2 ontology structures to Memgraph's property graph model:

| OWL2 Concept | Memgraph Representation |
|--------------|------------------------|
| **Individuals** | Nodes |
| **Classes** | Node Labels (types) |
| **Data Properties** | Node Properties |
| **Annotation Properties** | Node Properties |
| **Object Properties** | Relationships between Nodes |

## Quick Start

### 1. Install Memgraph

#### Option A: Docker (Recommended)
```bash
# Pull and run Memgraph Platform (includes Lab UI)
docker run -p 7687:7687 -p 7444:7444 memgraph/memgraph-platform

# Or just the database
docker run -p 7687:7687 memgraph/memgraph
```

#### Option B: Local Installation
```bash
# Ubuntu/Debian
wget https://download.memgraph.com/memgraph/v2.11.0/ubuntu-22.04/memgraph_2.11.0-1_amd64.deb
sudo dpkg -i memgraph_2.11.0-1_amd64.deb

# macOS
brew install memgraph

# Windows
# Download installer from https://memgraph.com/download
```

### 2. Install Python Dependencies
```bash
pip install neo4j  # Memgraph uses Neo4j driver
```

### 3. Run Example
```bash
cd examples/
python memgraph_integration_example.py
```

### 4. Explore in Memgraph Lab
Open http://localhost:7444 in your browser

## Usage

### Basic Example

```python
from ista import owl2
from ista.memgraph_loader import MemgraphLoader

# Create or load ontology
onto = owl2.Ontology(owl2.IRI("http://example.org/medical"))
# ... populate with individuals, classes, properties ...

# Connect to Memgraph
loader = MemgraphLoader("bolt://localhost:7687")
loader.connect()

# Load ontology
stats = loader.load_ontology(onto)
print(f"Loaded {stats['individuals_loaded']} individuals")
print(f"Created {stats['relationship_count']} relationships")

# Clean up
loader.close()
```

### Context Manager (Recommended)

```python
from ista.memgraph_loader import MemgraphLoader

with MemgraphLoader("bolt://localhost:7687") as loader:
    stats = loader.load_ontology(onto)
    # Connection automatically closed
```

### Convenience Function

```python
from ista.memgraph_loader import load_ontology_to_memgraph

# One-liner to load ontology
stats = load_ontology_to_memgraph(
    onto,
    uri="bolt://localhost:7687",
    clear_existing=True
)
```

## Mapping Details

### Individuals → Nodes

Each OWL individual becomes a node with:
- **Base Label**: `Individual`
- **Class Labels**: One label per OWL class the individual belongs to
- **Properties**:
  - `iri`: Full IRI of the individual
  - `label`: Local name extracted from IRI
  - Plus all data property values

**Example OWL**:
```turtle
:Patient1 rdf:type :Patient ;
          :name "Alice Johnson" ;
          :age 45 .
```

**Memgraph Node**:
```cypher
(:Individual:Patient {
  iri: "http://example.org/medical#Patient1",
  label: "Patient1",
  name: "Alice Johnson",
  age: "45"
})
```

### Classes → Node Labels

OWL classes become node labels (types):
- Sanitized to be valid Cypher identifiers
- Multiple labels if individual belongs to multiple classes
- Label names are extracted from class IRIs

**Example**:
- `http://example.org/medical#Patient` → Label: `Patient`
- `http://example.org/medical#CardiacPatient` → Label: `CardiacPatient`

### Data Properties → Node Properties

Data property assertions become node properties:
- Property name extracted from IRI
- Value stored as string (Memgraph handles type conversion)
- Multiple values possible (stored as list)

**Example**:
```turtle
:Patient1 :name "Alice" ;
          :age 45 ;
          :bloodType "A+" .
```

Becomes:
```cypher
{name: "Alice", age: "45", bloodType: "A+"}
```

### Object Properties → Relationships

Object property assertions become directed relationships:
- Relationship type from property IRI
- Source: subject individual
- Target: object individual
- Property IRI stored in relationship properties

**Example**:
```turtle
:Patient1 :diagnoses :Disease1 .
```

Becomes:
```cypher
(:Individual {iri: "...#Patient1"})-[:diagnoses {property_iri: "...#diagnoses"}]->(:Individual {iri: "...#Disease1"})
```

## Configuration Options

### MemgraphLoader Parameters

```python
loader = MemgraphLoader(
    uri="bolt://localhost:7687",    # Memgraph connection URI
    username="",                      # Username (empty for Memgraph default)
    password="",                      # Password (empty for Memgraph default)
    database="memgraph"               # Database name
)
```

### load_ontology() Parameters

```python
stats = loader.load_ontology(
    ontology,                    # OWL2 ontology object
    clear_existing=True,         # Clear database before loading
    create_indexes=True,         # Create indexes on IRI property
    batch_size=1000             # Nodes/relationships per batch
)
```

## Querying the Graph

Once loaded, you can query using Cypher:

### Find All Nodes of a Type

```cypher
MATCH (p:Patient)
RETURN p.label as name, p.age as age
ORDER BY p.age DESC
```

### Find Relationships

```cypher
MATCH (p:Patient)-[r:diagnoses]->(d:Disease)
RETURN p.label as patient, d.label as disease
```

### Pattern Matching

```cypher
MATCH (doc:Doctor)-[:treats]->(p:Patient)-[:diagnoses]->(d:Disease)
RETURN doc.label as doctor, 
       p.label as patient, 
       d.label as disease
```

### Aggregations

```cypher
MATCH (d:Doctor)-[:treats]->(p:Patient)
RETURN d.label as doctor, 
       count(p) as patient_count
ORDER BY patient_count DESC
```

### Path Finding

```cypher
MATCH path = (a:Patient)-[*1..3]-(b:Disease)
RETURN path
LIMIT 10
```

## Programmatic Querying

### Execute Custom Queries

```python
with MemgraphLoader("bolt://localhost:7687") as loader:
    # Execute query
    results = loader.execute_query("""
        MATCH (p:Patient)-[:diagnoses]->(d:Disease)
        RETURN p.label as patient, d.label as disease
    """)
    
    # Process results
    for record in results:
        print(f"{record['patient']} has {record['disease']}")
```

### With Parameters

```python
results = loader.execute_query(
    """
    MATCH (p:Patient {iri: $patient_iri})
    RETURN p.label as name, p.age as age
    """,
    parameters={"patient_iri": "http://example.org/medical#Patient1"}
)
```

## Database Statistics

```python
with MemgraphLoader("bolt://localhost:7687") as loader:
    stats = loader.get_database_statistics()
    
    print(f"Nodes: {stats['node_count']}")
    print(f"Relationships: {stats['relationship_count']}")
    print(f"Labels: {stats['labels']}")
    print(f"Relationship Types: {stats['relationship_types']}")
```

## Performance Optimization

### Batch Loading

The loader uses batching for efficiency:
- Default batch size: 1000 nodes/relationships
- Adjust based on your data size and available memory

```python
# Larger batches for big datasets
loader.load_ontology(onto, batch_size=5000)

# Smaller batches for memory-constrained environments
loader.load_ontology(onto, batch_size=100)
```

### Indexes

Indexes are created automatically on the `iri` property:
```cypher
CREATE INDEX ON :Individual(iri)
```

For frequent queries on other properties, create additional indexes:
```python
with loader.driver.session() as session:
    session.run("CREATE INDEX ON :Patient(age)")
    session.run("CREATE INDEX ON :Disease(severity)")
```

### Memory Settings

For large ontologies, configure Memgraph's memory:
```bash
# In memgraph.conf
--memory-limit=8192  # 8GB limit
```

Or with Docker:
```bash
docker run -p 7687:7687 \
  -e MEMGRAPH="--memory-limit=8192" \
  memgraph/memgraph
```

## Advanced Features

### Incremental Loading

Load multiple ontologies incrementally:
```python
with MemgraphLoader("bolt://localhost:7687") as loader:
    # First ontology - clear database
    loader.load_ontology(onto1, clear_existing=True)
    
    # Additional ontologies - append
    loader.load_ontology(onto2, clear_existing=False)
    loader.load_ontology(onto3, clear_existing=False)
```

### Filtering During Load

Currently, all individuals are loaded. To filter:

```python
# Option 1: Filter ontology before loading
filtered_onto = filter_ontology_by_class(onto, target_classes)
loader.load_ontology(filtered_onto)

# Option 2: Delete unwanted nodes after loading
with loader.driver.session() as session:
    session.run("""
        MATCH (n:Individual)
        WHERE NOT n:Patient AND NOT n:Doctor
        DETACH DELETE n
    """)
```

### Data Type Handling

Memgraph automatically handles common data types:
- Strings: Stored as-is
- Numbers: Converted from string literals
- Booleans: "true"/"false" strings
- Dates: ISO 8601 strings

For complex types, pre-process in Python:
```python
# Custom property transformation
for individual in individuals:
    if 'birthDate' in individual['properties']:
        date_str = individual['properties']['birthDate']
        # Convert to Memgraph-compatible format
        individual['properties']['birthDate'] = parse_date(date_str)
```

### Streaming Updates

Memgraph supports streaming - update the graph in real-time:
```python
import time

with MemgraphLoader("bolt://localhost:7687") as loader:
    # Initial load
    loader.load_ontology(onto)
    
    # Stream updates
    while True:
        new_data = get_ontology_updates()
        loader.load_ontology(new_data, clear_existing=False)
        time.sleep(60)  # Update every minute
```

## Integration with Memgraph Lab

### Visualizing the Graph

1. Open Memgraph Lab: http://localhost:7444
2. Connect to database (usually automatic)
3. Run query:
   ```cypher
   MATCH (n)
   RETURN n
   LIMIT 100
   ```
4. Switch to Graph view to see visualization

### Query Profiling

Profile query performance:
```cypher
PROFILE
MATCH (p:Patient)-[:diagnoses]->(d:Disease)
RETURN p, d
```

### Graph Style

Customize node colors and styles in Memgraph Lab:
```css
@NodeStyle Patient {
  color: #3498db;
  size: 50;
  label: Property(name);
}

@NodeStyle Disease {
  color: #e74c3c;
  size: 40;
  label: Property(label);
}

@EdgeStyle diagnoses {
  color: #95a5a6;
  width: 2;
}
```

## Comparison with Neo4j

| Feature | Memgraph | Neo4j |
|---------|----------|-------|
| **Performance** | In-memory, very fast | Disk-based, fast |
| **License** | Free (Community) | Free/Commercial |
| **Query Language** | Cypher (compatible) | Cypher (original) |
| **Use Case** | Real-time analytics | General purpose |
| **Streaming** | Built-in support | Via plugins |
| **Memory** | RAM-first | Disk with caching |
| **Setup** | Very simple | More complex |

### When to Use Memgraph vs Neo4j

**Use Memgraph when:**
- Need real-time analytics
- Working with streaming data
- Have sufficient RAM for full graph
- Want simpler setup/deployment
- Need maximum query speed

**Use Neo4j when:**
- Graph won't fit in RAM
- Need enterprise features
- Require mature ecosystem
- Want extensive documentation
- Need production support

## Troubleshooting

### Connection Failed

```
Error: Could not connect to Memgraph
```

**Solutions:**
1. Check Memgraph is running:
   ```bash
   docker ps | grep memgraph
   ```
2. Verify port 7687 is open
3. Check connection URI: `bolt://localhost:7687`

### Out of Memory

```
Error: Memgraph out of memory
```

**Solutions:**
1. Increase memory limit:
   ```bash
   docker run -e MEMGRAPH="--memory-limit=16384" memgraph/memgraph
   ```
2. Reduce batch size:
   ```python
   loader.load_ontology(onto, batch_size=100)
   ```
3. Filter ontology before loading

### Slow Queries

**Solutions:**
1. Create indexes on frequently queried properties
2. Use PROFILE to identify bottlenecks
3. Optimize Cypher queries (use WHERE early, limit results)
4. Consider query caching

### Invalid Labels

```
Error: Invalid label name
```

Labels are automatically sanitized, but if issues persist:
```python
# Check label sanitization
from ista.memgraph_loader import MemgraphLoader
loader = MemgraphLoader()
clean_label = loader._sanitize_label("Problem-Label!")
print(clean_label)  # Should be valid
```

## Example Queries

### Healthcare Analytics

```cypher
// Find most common diseases
MATCH (p:Patient)-[:diagnoses]->(d:Disease)
RETURN d.label as disease, count(p) as patient_count
ORDER BY patient_count DESC

// Find patients with multiple conditions
MATCH (p:Patient)-[:diagnoses]->(d:Disease)
WITH p, collect(d.label) as diseases
WHERE size(diseases) > 1
RETURN p.label as patient, diseases

// Find treatment efficacy (requires outcome data)
MATCH (doc:Doctor)-[:treats]->(p:Patient)-[:diagnoses]->(d:Disease)
WHERE d.severity = 'severe'
RETURN doc.label as doctor, count(DISTINCT p) as severe_cases
```

### Network Analysis

```cypher
// Find central doctors (most connected)
MATCH (doc:Doctor)-[:treats]->(p:Patient)
RETURN doc.label, count(p) as degree
ORDER BY degree DESC
LIMIT 5

// Find shortest path between entities
MATCH path = shortestPath((a:Patient)-[*]-(b:Drug))
WHERE a.iri = '...' AND b.iri = '...'
RETURN path

// Community detection (requires GDS library)
CALL algo.louvain.stream('Patient', 'diagnoses')
YIELD nodeId, community
RETURN community, count(*) as size
ORDER BY size DESC
```

## Resources

- **Memgraph Documentation**: https://memgraph.com/docs
- **Memgraph Lab**: https://memgraph.com/docs/memgraph-lab
- **Cypher Query Language**: https://memgraph.com/docs/cypher-manual
- **Neo4j Driver Docs**: https://neo4j.com/docs/python-manual/current/
- **ISTA Converters**: See `ista/converters/README.md`

## Next Steps

1. Try the example: `python memgraph_integration_example.py`
2. Explore your data in Memgraph Lab
3. Write custom Cypher queries
4. Integrate with your OWL2 ontologies
5. Build real-time analytics dashboards

## See Also

- `native_csv_population_example.py` - Loading ontologies from CSV
- `ista/converters/` - NetworkX and igraph conversion
- `ista/load_kb.py` - Neo4j integration (similar approach)
