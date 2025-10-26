# Graph Converter Module

The `ista.converters` module provides powerful utilities for converting between OWL2 ontologies and popular graph representations. This enables you to leverage the rich ecosystem of graph analysis tools while working with semantic knowledge bases.

## Table of Contents

- [Overview](#overview)
- [Supported Graph Formats](#supported-graph-formats)
- [Conversion Strategies](#conversion-strategies)
- [Configuration Options](#configuration-options)
- [Quick Start](#quick-start)
- [Detailed Usage](#detailed-usage)
- [Round-Trip Conversion](#round-trip-conversion)
- [Use Cases](#use-cases)
- [API Reference](#api-reference)
- [Comparison Table](#comparison-table)
- [Examples](#examples)

## Overview

The converter module bridges the gap between OWL2 ontologies (semantic web) and graph data structures (network analysis). It allows you to:

- **Convert ontologies to graphs** for network analysis, visualization, and machine learning
- **Preserve semantic information** including classes, properties, and data values
- **Choose conversion strategies** based on your needs (individuals only, include classes, or full ontology)
- **Support multiple backends** to leverage the best tools for each task
- **Perform round-trip conversions** to maintain data integrity

The module is designed with a unified API across all graph formats, making it easy to switch between them or use multiple formats in the same workflow.

## Supported Graph Formats

### NetworkX

**Best for:** General-purpose graph analysis, prototyping, integration with Python scientific stack

- Pure Python implementation
- Rich ecosystem of algorithms (centrality, community detection, paths)
- Excellent documentation and community support
- Easy visualization with matplotlib
- Extensive import/export capabilities (GraphML, GML, pickle, etc.)

**Installation:**
```bash
pip install networkx
```

### igraph

**Best for:** High-performance analysis, large graphs, advanced algorithms

- High-performance C library with Python bindings
- Fast community detection algorithms (Leiden, Louvain)
- Efficient memory usage
- Comprehensive statistical analysis tools
- Strong performance on large-scale networks

**Installation:**
```bash
pip install igraph
```

### ista.graph

**Best for:** Native integration, custom operations, lightweight graphs

- Native ista format (always available)
- Custom graph operations
- Direct integration with other ista modules
- Lightweight representation
- No external dependencies

## Conversion Strategies

The converter supports three conversion strategies that determine what elements from the ontology are included as nodes in the graph:

### 1. individuals_only (Default)

**What it includes:**
- Nodes: Named individuals only
- Edges: Object property assertions between individuals
- Attributes: Classes, data properties, annotations (optional)

**Use this when:**
- You want to analyze the instance-level knowledge graph
- Working with domain data (patients, products, documents, etc.)
- Performing entity-centric analysis

**Example:**
```python
graph = to_networkx(ontology, strategy='individuals_only')
```

### 2. include_classes

**What it includes:**
- Nodes: Named individuals + classes
- Edges: Object properties + class hierarchy (subClassOf) + class membership (rdf:type)
- Attributes: All available metadata

**Use this when:**
- You need the class hierarchy structure
- Analyzing relationships between instances and types
- Working with taxonomies or ontology structure

**Example:**
```python
graph = to_networkx(ontology, strategy='include_classes')
```

### 3. include_properties

**What it includes:**
- Nodes: Named individuals + classes + properties
- Edges: All relationships including property hierarchies (subPropertyOf)
- Attributes: Complete ontology metadata

**Use this when:**
- You need a complete ontology representation
- Analyzing the meta-model structure
- Working with ontology engineering tasks

**Example:**
```python
graph = to_networkx(ontology, strategy='include_properties')
```

## Configuration Options

The `ConversionOptions` class provides fine-grained control over the conversion process:

```python
from ista.converters import ConversionOptions, ConversionStrategy

options = ConversionOptions(
    strategy=ConversionStrategy.INDIVIDUALS_ONLY,
    include_data_properties=True,
    include_annotations=False,
    filter_classes=None,
    include_inferred=False,
    data_property_prefix='data_',
    annotation_property_prefix='annot_',
    simplify_iris=True,
    preserve_namespaces=False
)
```

### Option Details

#### `strategy` : ConversionStrategy
The conversion strategy to use (see [Conversion Strategies](#conversion-strategies)).

**Default:** `ConversionStrategy.INDIVIDUALS_ONLY`

#### `include_data_properties` : bool
If `True`, include data property values as node attributes. Data properties represent literal values like age, name, date, etc.

**Default:** `True`

**Example:** Node attributes might include `data_age=30`, `data_name="John Doe"`

#### `include_annotations` : bool
If `True`, include annotation property values as node attributes. Annotations are metadata like labels, comments, or documentation.

**Default:** `False`

**Note:** Annotations can add significant overhead; enable only when needed.

#### `filter_classes` : Optional[Set[str]]
If provided, only include individuals belonging to these classes. Classes should be specified as full IRIs.

**Default:** `None` (include all individuals)

**Example:**
```python
filter_classes={'http://example.org/ontology#Patient', 'http://example.org/ontology#Doctor'}
```

#### `include_inferred` : bool
If `True`, include inferred relationships from reasoning. Requires a reasoner to be configured.

**Default:** `False`

**Note:** Not yet fully implemented; reserved for future reasoning support.

#### `data_property_prefix` : str
Prefix to add to data property names when storing as node attributes.

**Default:** `"data_"`

**Example:** Property `age` becomes node attribute `data_age`

#### `annotation_property_prefix` : str
Prefix to add to annotation property names when storing as node attributes.

**Default:** `"annot_"`

**Example:** Annotation `rdfs:label` becomes node attribute `annot_label`

#### `simplify_iris` : bool
If `True`, simplify IRIs to local names where possible. Extracts the fragment after `#` or the last path component after `/`.

**Default:** `True`

**Example:**
- `http://example.org/ontology#Patient1` becomes `Patient1`
- `http://example.org/ontology/Patient1` becomes `Patient1`

#### `preserve_namespaces` : bool
If `True`, preserve namespace information in node and edge attributes. Adds `namespace` attributes to nodes and `property_namespace` to edges.

**Default:** `False`

**Use when:** You need to reconstruct full IRIs or work with multiple ontologies.

## Quick Start

### Basic Conversion

```python
from ista import owl2
from ista.converters import to_networkx, to_igraph, to_ista_graph

# Load an ontology
ontology = owl2.Ontology("http://example.org/myontology")

# Convert to NetworkX (most common case)
nx_graph = to_networkx(ontology)

# Convert to igraph (for performance)
ig_graph = to_igraph(ontology)

# Convert to ista.graph (native format)
ista_graph = to_ista_graph(ontology)
```

### With Custom Options

```python
from ista.converters import to_networkx

# Convert with custom options
graph = to_networkx(
    ontology,
    strategy='include_classes',
    include_annotations=True,
    simplify_iris=False,
    preserve_namespaces=True
)

# Access node data
for node, attrs in graph.nodes(data=True):
    print(f"Node: {attrs['label']}")
    print(f"  Type: {attrs['type']}")
    print(f"  IRI: {attrs['iri']}")
    if 'classes' in attrs:
        print(f"  Classes: {attrs['classes']}")
```

### Reverse Conversion

```python
from ista.converters import from_networkx

# Convert graph back to ontology
reconstructed_ontology = from_networkx(
    graph,
    ontology_iri='http://example.org/reconstructed'
)

# Save the reconstructed ontology
owl2.FunctionalSyntaxSerializer.serialize_to_file(
    reconstructed_ontology,
    'reconstructed.ofn'
)
```

## Detailed Usage

### NetworkX Converter

NetworkX creates a directed graph (`DiGraph`) where nodes represent ontology entities and edges represent relationships.

#### Converting to NetworkX

```python
from ista.converters import to_networkx
import networkx as nx

# Basic conversion
graph = to_networkx(ontology)

# With options
graph = to_networkx(
    ontology,
    strategy='individuals_only',
    include_data_properties=True,
    include_annotations=False,
    simplify_iris=True
)

# Explore the graph
print(f"Nodes: {graph.number_of_nodes()}")
print(f"Edges: {graph.number_of_edges()}")

# Access node attributes
for node in graph.nodes():
    attrs = graph.nodes[node]
    print(f"{attrs['label']}: {attrs['type']}")

# Access edge attributes
for u, v, data in graph.edges(data=True):
    print(f"{graph.nodes[u]['label']} --[{data['property_label']}]--> {graph.nodes[v]['label']}")
```

#### Node Attributes (NetworkX)

Each node has the following attributes:

- `iri`: Full IRI of the entity
- `type`: Entity type (`'individual'`, `'class'`, `'object_property'`, etc.)
- `label`: Simplified name (if `simplify_iris=True`)
- `classes`: List of class IRIs (for individuals)
- `namespace`: Namespace part of IRI (if `preserve_namespaces=True`)
- `data_*`: Data property values (if `include_data_properties=True`)
- `annot_*`: Annotation values (if `include_annotations=True`)

#### Edge Attributes (NetworkX)

Each edge has the following attributes:

- `property_iri`: Full IRI of the property
- `property_label`: Simplified property name
- `property_type`: Type of relationship (`'object_property'`, `'class_hierarchy'`, `'class_membership'`, `'property_hierarchy'`)
- `property_namespace`: Namespace of property (if `preserve_namespaces=True`)

#### NetworkX Analysis Examples

```python
import networkx as nx

# Centrality analysis
degree_centrality = nx.degree_centrality(graph)
betweenness = nx.betweenness_centrality(graph)
pagerank = nx.pagerank(graph)

# Find most central nodes
top_nodes = sorted(degree_centrality.items(), key=lambda x: x[1], reverse=True)[:5]
for node, score in top_nodes:
    print(f"{graph.nodes[node]['label']}: {score:.3f}")

# Find shortest paths
if nx.has_path(graph, source_node, target_node):
    path = nx.shortest_path(graph, source_node, target_node)
    print(f"Path length: {len(path) - 1}")

# Community detection
communities = list(nx.community.greedy_modularity_communities(graph.to_undirected()))
print(f"Found {len(communities)} communities")

# Connected components
num_components = nx.number_weakly_connected_components(graph)
print(f"Weakly connected components: {num_components}")
```

#### Converting from NetworkX

```python
from ista.converters import from_networkx

# Reconstruct ontology from graph
ontology = from_networkx(graph, 'http://example.org/reconstructed')

# The reconstructed ontology contains:
# - All individuals with their class assertions
# - All object property assertions (edges)
# - All data property assertions (from node attributes)
# - Classes (if included in the graph)
# - Properties (if included in the graph)
```

### igraph Converter

igraph creates a directed `Graph` object optimized for performance. Unlike NetworkX, igraph uses numeric vertex IDs internally, with a mapping maintained to IRIs.

#### Converting to igraph

```python
from ista.converters import to_igraph
import igraph as ig

# Basic conversion
graph = to_igraph(ontology)

# With options
graph = to_igraph(
    ontology,
    strategy='include_classes',
    include_data_properties=True
)

# Explore the graph
print(f"Vertices: {graph.vcount()}")
print(f"Edges: {graph.ecount()}")
print(f"Density: {graph.density():.4f}")

# Access vertex attributes
for v in graph.vs:
    print(f"{v['label']}: {v['type']}")

# Access edge attributes
for e in graph.es:
    source = graph.vs[e.source]
    target = graph.vs[e.target]
    print(f"{source['label']} --[{e['property_label']}]--> {target['label']}")
```

#### Vertex Attributes (igraph)

Each vertex has the following attributes (same as NetworkX nodes):

- `name`: The IRI (used for vertex lookup)
- `iri`: Full IRI of the entity
- `type`: Entity type
- `label`: Simplified name
- `classes`: List of class IRIs (for individuals)
- Plus data properties and annotations if enabled

#### Edge Attributes (igraph)

Each edge has the following attributes (same as NetworkX edges):

- `property_iri`: Full IRI of the property
- `property_label`: Simplified property name
- `property_type`: Type of relationship

#### igraph Analysis Examples

```python
import igraph as ig

# Degree distribution
in_degrees = graph.indegree()
out_degrees = graph.outdegree()
print(f"Avg in-degree: {sum(in_degrees) / len(in_degrees):.2f}")
print(f"Avg out-degree: {sum(out_degrees) / len(out_degrees):.2f}")

# Centrality measures
betweenness = graph.betweenness()
closeness = graph.closeness()
eigenvector = graph.eigenvector_centrality()

# Find top nodes by betweenness
top_indices = sorted(range(len(betweenness)), key=lambda i: betweenness[i], reverse=True)[:5]
for idx in top_indices:
    print(f"{graph.vs[idx]['label']}: {betweenness[idx]:.3f}")

# Community detection (Leiden algorithm - very fast)
communities = graph.community_leiden()
print(f"Communities: {len(communities)}")
print(f"Modularity: {communities.modularity:.4f}")

# Clustering coefficient
transitivity = graph.transitivity_undirected()
print(f"Clustering coefficient: {transitivity:.4f}")

# Graph diameter
if graph.is_connected(mode='weak'):
    diameter = graph.diameter(directed=True)
    print(f"Diameter: {diameter}")
```

#### Converting from igraph

```python
from ista.converters import from_igraph

# Reconstruct ontology from igraph
ontology = from_igraph(graph, 'http://example.org/reconstructed')

# Same reconstruction capabilities as NetworkX
```

### ista.graph Converter

The native ista.graph format provides a lightweight, flexible representation integrated with the ista ecosystem.

#### Converting to ista.graph

```python
from ista.converters import to_ista_graph

# Basic conversion
graph = to_ista_graph(ontology)

# With options
graph = to_ista_graph(
    ontology,
    strategy='individuals_only',
    include_data_properties=True
)

# Explore the graph
print(f"Nodes: {len(graph.nodes)}")
print(f"Edges: {len(graph.edges)}")

# Access nodes
for node in graph.nodes:
    print(f"Node: {node.name}")
    print(f"  Class: {node.node_class}")
    print(f"  Index: {node.node_idx}")
    print(f"  Properties: {node.properties}")

# Access edges
for edge in graph.edges:
    print(f"{edge.from_node.name} --> {edge.to_node.name}")
    print(f"  Weight: {edge.weight}")
    print(f"  Properties: {edge.edge_properties}")
```

#### Node Structure (ista.graph)

Each `Node` object has:

- `node_class`: The node's primary class
- `node_idx`: Numeric index
- `name`: Display name
- `properties`: Dictionary of all attributes (IRI, type, classes, data properties, etc.)

#### Edge Structure (ista.graph)

Each `Edge` object has:

- `from_node`: Source node object
- `to_node`: Target node object
- `weight`: Edge weight (default 1.0)
- `edge_properties`: Dictionary of edge attributes

#### ista.graph Operations

```python
# Get adjacency matrix
adj_matrix = graph.get_adjacency(format='matrix')
print(f"Shape: {adj_matrix.shape}")

# Filter nodes by class
patients = [node for node in graph.nodes if node.node_class == 'Patient']

# Find edges by property
diagnoses = [edge for edge in graph.edges 
             if edge.edge_properties.get('property_label') == 'diagnoses']

# Count node types
from collections import Counter
node_types = Counter(node.node_class for node in graph.nodes)
for node_type, count in node_types.items():
    print(f"{node_type}: {count}")
```

#### Converting from ista.graph

```python
from ista.converters import from_ista_graph

# Reconstruct ontology from ista.graph
ontology = from_ista_graph(graph, 'http://example.org/reconstructed')

# Full reconstruction support
```

## Round-Trip Conversion

Round-trip conversion allows you to convert an ontology to a graph, manipulate it, and convert it back while preserving semantic information.

### Basic Round-Trip

```python
from ista import owl2
from ista.converters import to_networkx, from_networkx

# Load original ontology
original = owl2.Ontology("http://example.org/medical")
print(f"Original: {original.get_individual_count()} individuals")

# Convert to NetworkX
graph = to_networkx(original, strategy='individuals_only')
print(f"Graph: {graph.number_of_nodes()} nodes")

# Manipulate graph (optional)
# ... perform graph operations ...

# Convert back to ontology
reconstructed = from_networkx(graph, "http://example.org/medical-reconstructed")
print(f"Reconstructed: {reconstructed.get_individual_count()} individuals")

# Save reconstructed ontology
owl2.FunctionalSyntaxSerializer.serialize_to_file(reconstructed, 'output.ofn')
```

### What is Preserved?

Round-trip conversion preserves:

- **Individuals**: All named individuals with their declarations
- **Class Assertions**: Individual class membership (`rdf:type`)
- **Object Properties**: Relationships between individuals
- **Data Properties**: Literal values attached to individuals
- **Classes**: If `include_classes` strategy is used
- **Properties**: If `include_properties` strategy is used
- **Class Hierarchy**: SubClassOf relationships (with appropriate strategy)
- **Property Hierarchy**: SubPropertyOf relationships (with appropriate strategy)

### What is Not Preserved?

- **Complex Class Expressions**: Unions, intersections, restrictions (simplified to class names)
- **Property Characteristics**: Transitivity, symmetry, functionality
- **Axiom Annotations**: Metadata on axioms themselves
- **SWRL Rules**: Semantic Web Rule Language rules
- **General Class Axioms**: Axioms not tied to specific individuals

### Round-Trip Best Practices

1. **Use appropriate strategy**: Choose based on what you need to preserve
2. **Enable namespace preservation**: If working with multiple ontologies
3. **Keep IRIs intact**: Set `simplify_iris=False` for exact reconstruction
4. **Document transformations**: Track any graph manipulations performed
5. **Validate results**: Compare axiom counts and spot-check entities

### Example: Full Preservation

```python
from ista.converters import to_networkx, from_networkx, ConversionOptions, ConversionStrategy

# Configure for maximum preservation
options = ConversionOptions(
    strategy=ConversionStrategy.INCLUDE_CLASSES,
    include_data_properties=True,
    include_annotations=True,
    simplify_iris=False,
    preserve_namespaces=True
)

# Convert with options
graph = to_networkx(ontology, **vars(options))

# Reconstruct
reconstructed = from_networkx(graph, ontology.iri.iri_string, **vars(options))

# Compare
print(f"Original axioms: {ontology.get_axiom_count()}")
print(f"Reconstructed axioms: {reconstructed.get_axiom_count()}")
```

## Use Cases

### 1. Knowledge Graph Analysis

**Goal:** Analyze network structure of domain knowledge

```python
import networkx as nx
from ista.converters import to_networkx

# Convert ontology to graph
graph = to_networkx(ontology, strategy='individuals_only')

# Find central entities
pagerank = nx.pagerank(graph)
top_entities = sorted(pagerank.items(), key=lambda x: x[1], reverse=True)[:10]

# Find communities
communities = list(nx.community.greedy_modularity_communities(graph.to_undirected()))

# Analyze paths
for u in graph.nodes():
    for v in graph.nodes():
        if u != v and nx.has_path(graph, u, v):
            path_length = nx.shortest_path_length(graph, u, v)
            if path_length > 5:
                print(f"Long path: {graph.nodes[u]['label']} -> {graph.nodes[v]['label']}: {path_length}")
```

### 2. Visualization

**Goal:** Create visual representations of ontology structure

```python
import networkx as nx
import matplotlib.pyplot as plt
from ista.converters import to_networkx

# Convert to NetworkX
graph = to_networkx(ontology, strategy='include_classes')

# Color nodes by type
colors = []
for node in graph.nodes():
    node_type = graph.nodes[node]['type']
    if node_type == 'individual':
        colors.append('lightblue')
    elif node_type == 'class':
        colors.append('lightgreen')
    else:
        colors.append('gray')

# Create layout
pos = nx.spring_layout(graph, k=2, iterations=50)

# Draw graph
plt.figure(figsize=(12, 8))
nx.draw(graph, pos, node_color=colors, with_labels=True, 
        labels={n: graph.nodes[n]['label'] for n in graph.nodes()},
        node_size=1000, font_size=8, arrows=True)

plt.savefig('ontology_visualization.png', dpi=300)
```

### 3. Machine Learning on Graphs

**Goal:** Apply graph neural networks or embeddings

```python
from ista.converters import to_networkx
import networkx as nx

# Convert to graph
graph = to_networkx(ontology, strategy='individuals_only')

# Generate node embeddings using Node2Vec
from node2vec import Node2Vec

node2vec = Node2Vec(graph, dimensions=64, walk_length=30, num_walks=200)
model = node2vec.fit()

# Get embeddings
embeddings = {node: model.wv[node] for node in graph.nodes()}

# Use embeddings for downstream tasks
# (classification, clustering, similarity, etc.)
```

### 4. Performance Analysis with igraph

**Goal:** Analyze large ontologies efficiently

```python
from ista.converters import to_igraph
import igraph as ig

# Convert to igraph (much faster for large graphs)
graph = to_igraph(ontology, strategy='individuals_only')

# Fast community detection
communities = graph.community_leiden(objective_function='modularity', n_iterations=10)

# Fast centrality computation
betweenness = graph.betweenness()
closeness = graph.closeness()

# Efficient path analysis
shortest_paths = graph.shortest_paths()

# Statistical analysis
print(f"Density: {graph.density():.4f}")
print(f"Average path length: {graph.average_path_length():.2f}")
print(f"Clustering coefficient: {graph.transitivity_undirected():.4f}")
```

### 5. Data Integration

**Goal:** Merge multiple knowledge sources

```python
from ista.converters import to_networkx, from_networkx
import networkx as nx

# Convert multiple ontologies to graphs
graph1 = to_networkx(ontology1, strategy='individuals_only')
graph2 = to_networkx(ontology2, strategy='individuals_only')

# Merge graphs (compose creates union)
merged_graph = nx.compose(graph1, graph2)

# Optionally: resolve conflicts, merge nodes, add cross-references
# ... custom merging logic ...

# Convert back to ontology
merged_ontology = from_networkx(merged_graph, 'http://example.org/merged')
```

### 6. Quality Analysis

**Goal:** Detect ontology quality issues

```python
from ista.converters import to_networkx
import networkx as nx

# Convert with class hierarchy
graph = to_networkx(ontology, strategy='include_classes')

# Find isolated nodes (potential orphans)
isolated = list(nx.isolates(graph))
print(f"Isolated entities: {len(isolated)}")

# Find cycles in class hierarchy
class_nodes = [n for n, d in graph.nodes(data=True) if d['type'] == 'class']
class_subgraph = graph.subgraph(class_nodes)
try:
    cycles = list(nx.simple_cycles(class_subgraph))
    if cycles:
        print(f"WARNING: Found {len(cycles)} cycles in class hierarchy")
except:
    pass

# Find densely connected regions (may indicate over-specification)
density = nx.density(graph)
if density > 0.3:
    print(f"WARNING: High graph density ({density:.3f}) may indicate over-specification")
```

### 7. Export for External Tools

**Goal:** Use ontology data in graph databases or visualization tools

```python
from ista.converters import to_networkx
import networkx as nx

# Convert to NetworkX
graph = to_networkx(ontology, strategy='individuals_only')

# Export to various formats
nx.write_graphml(graph, 'output.graphml')  # For Gephi, Cytoscape
nx.write_gml(graph, 'output.gml')          # For graph tools
nx.write_gexf(graph, 'output.gexf')        # For Gephi

# Export to Neo4j-compatible format
with open('output.cypher', 'w') as f:
    for node, attrs in graph.nodes(data=True):
        f.write(f"CREATE (:{attrs['type']} {{iri: '{attrs['iri']}', label: '{attrs['label']}'}})\n")
    for u, v, attrs in graph.edges(data=True):
        f.write(f"MATCH (a {{iri: '{u}'}}), (b {{iri: '{v}'}}) CREATE (a)-[:{attrs['property_label']}]->(b)\n")
```

## API Reference

### Conversion Functions

#### `to_networkx(ontology, strategy='individuals_only', **options)`

Convert an OWL2 ontology to a NetworkX directed graph.

**Parameters:**
- `ontology` : `owl2.Ontology` - The ontology to convert
- `strategy` : `str` - Conversion strategy (`'individuals_only'`, `'include_classes'`, `'include_properties'`)
- `**options` - Additional options (see `ConversionOptions`)

**Returns:**
- `networkx.DiGraph` - The converted graph

**Raises:**
- `ImportError` - If NetworkX is not installed

---

#### `from_networkx(graph, ontology_iri, **options)`

Convert a NetworkX directed graph to an OWL2 ontology.

**Parameters:**
- `graph` : `networkx.DiGraph` - The graph to convert
- `ontology_iri` : `str` - IRI for the new ontology
- `**options` - Additional options (see `ConversionOptions`)

**Returns:**
- `owl2.Ontology` - The converted ontology

**Raises:**
- `ImportError` - If OWL2 library is not available

---

#### `to_igraph(ontology, strategy='individuals_only', **options)`

Convert an OWL2 ontology to an igraph Graph.

**Parameters:**
- `ontology` : `owl2.Ontology` - The ontology to convert
- `strategy` : `str` - Conversion strategy
- `**options` - Additional options

**Returns:**
- `igraph.Graph` - The converted graph

**Raises:**
- `ImportError` - If igraph is not installed

---

#### `from_igraph(graph, ontology_iri, **options)`

Convert an igraph Graph to an OWL2 ontology.

**Parameters:**
- `graph` : `igraph.Graph` - The graph to convert
- `ontology_iri` : `str` - IRI for the new ontology
- `**options` - Additional options

**Returns:**
- `owl2.Ontology` - The converted ontology

---

#### `to_ista_graph(ontology, strategy='individuals_only', **options)`

Convert an OWL2 ontology to an ista.graph.Graph.

**Parameters:**
- `ontology` : `owl2.Ontology` - The ontology to convert
- `strategy` : `str` - Conversion strategy
- `**options` - Additional options

**Returns:**
- `ista.graph.Graph` - The converted graph

---

#### `from_ista_graph(graph, ontology_iri, **options)`

Convert an ista.graph.Graph to an OWL2 ontology.

**Parameters:**
- `graph` : `ista.graph.Graph` - The graph to convert
- `ontology_iri` : `str` - IRI for the new ontology
- `**options` - Additional options

**Returns:**
- `owl2.Ontology` - The converted ontology

### Configuration Classes

#### `ConversionStrategy` (Enum)

Defines the conversion strategy.

**Values:**
- `INDIVIDUALS_ONLY` - Only individuals as nodes
- `INCLUDE_CLASSES` - Include classes as nodes
- `INCLUDE_PROPERTIES` - Include properties as nodes

---

#### `ConversionOptions` (Dataclass)

Configuration options for conversion.

**Attributes:**
- `strategy` : `ConversionStrategy` - Conversion strategy
- `include_data_properties` : `bool` - Include data property values
- `include_annotations` : `bool` - Include annotation property values
- `filter_classes` : `Optional[Set[str]]` - Filter to specific classes
- `include_inferred` : `bool` - Include inferred relationships
- `data_property_prefix` : `str` - Prefix for data properties
- `annotation_property_prefix` : `str` - Prefix for annotations
- `simplify_iris` : `bool` - Simplify IRIs to local names
- `preserve_namespaces` : `bool` - Preserve namespace information

---

#### `OntologyToGraphConverter` (Abstract Base Class)

Base class for all converters. Not typically used directly.

**Methods:**
- `convert()` - Convert ontology to graph
- `reverse_convert(graph, ontology_iri)` - Convert graph to ontology

## Comparison Table

| Feature | NetworkX | igraph | ista.graph |
|---------|----------|--------|------------|
| **Installation** | `pip install networkx` | `pip install igraph` | Built-in |
| **Performance** | Medium (Pure Python) | High (C library) | Medium |
| **Memory Usage** | Medium | Low (efficient) | Low |
| **Algorithms** | Extensive | Very extensive | Basic |
| **Ease of Use** | Very easy | Easy | Very easy |
| **Documentation** | Excellent | Good | Good |
| **Visualization** | Easy (matplotlib) | Built-in | Basic |
| **Community** | Very large | Large | Growing |
| **Export Formats** | Many | Many | Limited |
| **Custom Operations** | Easy | Moderate | Very easy |
| **Integration** | Python ecosystem | Multi-language | ista ecosystem |

### When to Use Each Format

**Use NetworkX when:**
- You're prototyping or learning
- You need rich Python integration
- You want easy visualization
- Graph size is small to medium (<10,000 nodes)
- You need extensive documentation and examples
- You're already using other NetworkX-based tools

**Use igraph when:**
- You have large graphs (>10,000 nodes)
- Performance is critical
- You need advanced community detection
- You're doing statistical network analysis
- Memory efficiency matters
- You need production-level performance

**Use ista.graph when:**
- You want zero external dependencies
- You're building custom graph operations
- You need tight integration with ista modules
- You want a lightweight solution
- You're prototyping new algorithms
- You need simple graph representation

## Examples

The `examples/` directory contains comprehensive examples demonstrating the converter module:

### Complete Workflow Example

**File:** `examples/graph_conversion_example.py`

A complete workflow demonstrating:
- Creating a medical ontology with patients, diseases, treatments, and symptoms
- Converting to all three graph formats
- Performing format-specific analyses
- Round-trip conversions
- Visualization

**Run with:**
```bash
python examples/graph_conversion_example.py
```

### Knowledge Graph Analysis

**File:** `examples/knowledge_graph_analysis.py`

Advanced analysis demonstrating:
- Creating a multi-domain knowledge graph (scientific, geographic, conceptual)
- Comparing graph representations
- Format-specific algorithms and performance
- Exporting to multiple file formats
- Performance benchmarking
- Memory usage comparison

**Run with:**
```bash
python examples/knowledge_graph_analysis.py
```

### Simple Examples

#### Example 1: Basic Conversion

```python
from ista import owl2
from ista.converters import to_networkx

# Load ontology
ontology = owl2.Ontology("http://example.org/myont")

# Convert to NetworkX
graph = to_networkx(ontology)

# Analyze
print(f"Nodes: {graph.number_of_nodes()}")
print(f"Edges: {graph.number_of_edges()}")
```

#### Example 2: With Class Hierarchy

```python
from ista.converters import to_networkx
import networkx as nx

# Convert including classes
graph = to_networkx(ontology, strategy='include_classes')

# Find class nodes
classes = [n for n, d in graph.nodes(data=True) if d['type'] == 'class']
print(f"Classes in graph: {len(classes)}")

# Analyze class hierarchy
class_subgraph = graph.subgraph(classes)
print(f"Class hierarchy depth: {nx.dag_longest_path_length(class_subgraph)}")
```

#### Example 3: Round-Trip with Validation

```python
from ista.converters import to_networkx, from_networkx

# Original ontology
print(f"Original: {ontology.get_individual_count()} individuals")

# Convert to graph and back
graph = to_networkx(ontology)
reconstructed = from_networkx(graph, "http://example.org/reconstructed")

# Validate
print(f"Reconstructed: {reconstructed.get_individual_count()} individuals")
print(f"Preservation rate: {reconstructed.get_individual_count() / ontology.get_individual_count() * 100:.1f}%")
```

#### Example 4: Performance Comparison

```python
import time
from ista.converters import to_networkx, to_igraph

# NetworkX timing
start = time.time()
nx_graph = to_networkx(ontology)
nx_time = time.time() - start

# igraph timing
start = time.time()
ig_graph = to_igraph(ontology)
ig_time = time.time() - start

print(f"NetworkX: {nx_time:.4f}s")
print(f"igraph: {ig_time:.4f}s")
print(f"Speedup: {nx_time / ig_time:.2f}x")
```

---

## Additional Resources

- **NetworkX Documentation:** https://networkx.org/documentation/stable/
- **igraph Documentation:** https://igraph.org/python/
- **OWL2 Specification:** https://www.w3.org/TR/owl2-overview/
- **Graph Theory Basics:** https://en.wikipedia.org/wiki/Graph_theory

## Contributing

Contributions to the converter module are welcome! Areas for improvement:

- Additional graph backends (graph-tool, PyTorch Geometric)
- Performance optimizations
- Advanced conversion options
- More comprehensive round-trip preservation
- Additional examples and use cases

## License

See the main ista project LICENSE file.
