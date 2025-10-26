Graph Converters
================

The ista library provides utilities to convert OWL2 ontologies into various graph
representations for analysis, visualization, and integration with other tools.

Overview
--------

Graph conversion enables:

- **Network Analysis**: Use NetworkX, igraph, or other graph libraries
- **Visualization**: Export to formats for Gephi, Cytoscape, etc.
- **Machine Learning**: Convert to graph embeddings for ML pipelines
- **Data Analysis**: Work with ontologies as tabular data (pandas)

Available Converters
--------------------

ista provides converters to several popular formats:

- **NetworkX** - Python graph library for analysis
- **pandas DataFrame** - Tabular representation
- **RDF Graph** - RDF/XML, Turtle, N-Triples
- **Edge List** - Simple source-target pairs
- **Adjacency Matrix** - Matrix representation

NetworkX Converter
------------------

Convert ontologies to NetworkX directed graphs.

Basic Usage
~~~~~~~~~~~

.. code-block:: python

    from ista import owl2
    from ista.converters import ontology_to_networkx
    import networkx as nx

    # Load ontology
    parser = owl2.FunctionalSyntaxParser()
    ont = parser.parse("biomedical.ofn")

    # Convert to NetworkX
    G = ontology_to_networkx(ont)

    # Basic statistics
    print(f"Nodes: {G.number_of_nodes()}")
    print(f"Edges: {G.number_of_edges()}")
    print(f"Density: {nx.density(G):.4f}")

Node and Edge Attributes
~~~~~~~~~~~~~~~~~~~~~~~~~

The converter preserves ontology information as graph attributes:

.. code-block:: python

    # Node attributes
    for node, data in G.nodes(data=True):
        print(f"Node: {node}")
        print(f"  Type: {data.get('entity_type')}")  # CLASS, PROPERTY, etc.
        print(f"  Label: {data.get('label')}")
        print(f"  IRI: {data.get('iri')}")

    # Edge attributes
    for source, target, data in G.edges(data=True):
        print(f"Edge: {source} -> {target}")
        print(f"  Relation: {data.get('relation_type')}")  # subClassOf, etc.
        print(f"  Property: {data.get('property')}")

Conversion Options
~~~~~~~~~~~~~~~~~~

Customize the conversion process:

.. code-block:: python

    G = ontology_to_networkx(
        ont,
        include_individuals=True,      # Include named individuals
        include_literals=False,         # Exclude literal nodes
        simplify_iris=True,             # Use short forms for node labels
        include_annotations=True,       # Include annotation properties
        property_edges_only=False,      # Include all axiom types
    )

Graph Analysis
~~~~~~~~~~~~~~

Leverage NetworkX for powerful graph analysis:

.. code-block:: python

    import networkx as nx

    # Centrality measures
    degree_cent = nx.degree_centrality(G)
    betweenness = nx.betweenness_centrality(G)
    closeness = nx.closeness_centrality(G)

    # Find most central nodes
    top_nodes = sorted(degree_cent.items(), key=lambda x: x[1], reverse=True)[:10]
    print("Top 10 most connected entities:")
    for node, centrality in top_nodes:
        print(f"  {node}: {centrality:.4f}")

    # Community detection
    G_undirected = G.to_undirected()
    communities = nx.community.greedy_modularity_communities(G_undirected)
    print(f"Found {len(communities)} communities")

    # Shortest paths
    if nx.is_weakly_connected(G):
        avg_path_length = nx.average_shortest_path_length(G)
        diameter = nx.diameter(G)
        print(f"Average path length: {avg_path_length:.2f}")
        print(f"Diameter: {diameter}")

    # Find hierarchy depth
    # Assume we have a root class
    root = "owl:Thing"
    if root in G:
        depths = nx.single_source_shortest_path_length(G, root)
        max_depth = max(depths.values())
        print(f"Maximum hierarchy depth: {max_depth}")

Visualization
~~~~~~~~~~~~~

Create visualizations using NetworkX and matplotlib:

.. code-block:: python

    import matplotlib.pyplot as plt

    # Simple visualization
    plt.figure(figsize=(12, 8))
    pos = nx.spring_layout(G, k=0.5, iterations=50)
    nx.draw(G, pos, with_labels=True, node_size=500,
            node_color='lightblue', font_size=8,
            arrows=True, edge_color='gray')
    plt.title("Ontology Graph")
    plt.tight_layout()
    plt.savefig("ontology_graph.png", dpi=300)

    # Color by entity type
    color_map = {
        'CLASS': 'lightblue',
        'OBJECT_PROPERTY': 'lightgreen',
        'DATA_PROPERTY': 'lightyellow',
        'NAMED_INDIVIDUAL': 'lightcoral'
    }
    colors = [color_map.get(G.nodes[n].get('entity_type'), 'gray')
              for n in G.nodes()]

    plt.figure(figsize=(12, 8))
    nx.draw(G, pos, node_color=colors, with_labels=True,
            node_size=500, font_size=8)
    plt.title("Ontology Graph (colored by entity type)")
    plt.savefig("ontology_graph_colored.png", dpi=300)

Export to Other Tools
~~~~~~~~~~~~~~~~~~~~~

Export NetworkX graphs to formats for other visualization tools:

.. code-block:: python

    # Export to GEXF (for Gephi)
    nx.write_gexf(G, "ontology.gexf")

    # Export to GraphML (for Cytoscape, yEd)
    nx.write_graphml(G, "ontology.graphml")

    # Export to JSON (for D3.js)
    from networkx.readwrite import json_graph
    data = json_graph.node_link_data(G)
    import json
    with open("ontology.json", "w") as f:
        json.dump(data, f, indent=2)

DataFrame Converter
-------------------

Convert ontologies to pandas DataFrames for tabular analysis.

Basic Usage
~~~~~~~~~~~

.. code-block:: python

    from ista.converters import ontology_to_dataframe
    import pandas as pd

    # Convert to DataFrame
    df = ontology_to_dataframe(ont)

    # View structure
    print(df.head())
    print(df.columns)
    print(df.dtypes)

DataFrame Structure
~~~~~~~~~~~~~~~~~~~

The DataFrame typically has columns:

- **subject**: Subject IRI
- **predicate**: Relation/property IRI
- **object**: Object IRI or literal value
- **subject_type**: Entity type (CLASS, PROPERTY, etc.)
- **object_type**: Entity type or LITERAL
- **axiom_type**: Type of axiom (SUBCLASS_OF, DECLARATION, etc.)

.. code-block:: python

    # Filter by axiom type
    subclass_axioms = df[df['axiom_type'] == 'SUBCLASS_OF']
    print(f"Found {len(subclass_axioms)} subclass axioms")

    # Find all properties of a class
    disease_iri = "http://example.org/Disease"
    disease_props = df[df['subject'] == disease_iri]
    print(disease_props[['predicate', 'object']])

    # Group by predicate
    predicate_counts = df['predicate'].value_counts()
    print("Most common predicates:")
    print(predicate_counts.head(10))

Data Analysis
~~~~~~~~~~~~~

Use pandas for powerful data analysis:

.. code-block:: python

    # Statistics
    print(f"Total triples: {len(df)}")
    print(f"Unique subjects: {df['subject'].nunique()}")
    print(f"Unique predicates: {df['predicate'].nunique()}")
    print(f"Unique objects: {df['object'].nunique()}")

    # Entity type distribution
    entity_dist = df['subject_type'].value_counts()
    print("Entity type distribution:")
    print(entity_dist)

    # Find classes with most subclasses
    subclasses = df[df['predicate'].str.contains('subClassOf', na=False)]
    parent_counts = subclasses['object'].value_counts()
    print("Classes with most subclasses:")
    print(parent_counts.head(10))

Export Options
~~~~~~~~~~~~~~

Export DataFrames to various formats:

.. code-block:: python

    # CSV
    df.to_csv("ontology.csv", index=False)

    # Excel
    df.to_excel("ontology.xlsx", index=False)

    # Parquet (efficient binary format)
    df.to_parquet("ontology.parquet")

    # JSON
    df.to_json("ontology.json", orient="records", indent=2)

    # SQL database
    import sqlite3
    conn = sqlite3.connect("ontology.db")
    df.to_sql("axioms", conn, if_exists="replace", index=False)
    conn.close()

RDF Converter
-------------

Convert to RDF formats for integration with RDF tools.

.. code-block:: python

    from ista.converters import ontology_to_rdf

    # Convert to RDF graph
    rdf_graph = ontology_to_rdf(ont)

    # Serialize to different RDF formats
    rdf_graph.serialize("ontology.ttl", format="turtle")
    rdf_graph.serialize("ontology.rdf", format="xml")
    rdf_graph.serialize("ontology.nt", format="nt")
    rdf_graph.serialize("ontology.jsonld", format="json-ld")

Edge List Converter
-------------------

Simple edge list representation.

.. code-block:: python

    from ista.converters import ontology_to_edgelist

    # Get edge list
    edges = ontology_to_edgelist(ont)

    # edges is a list of (source, target, relation) tuples
    for source, target, relation in edges[:10]:
        print(f"{source} --[{relation}]--> {target}")

    # Save to file
    with open("edges.txt", "w") as f:
        for source, target, relation in edges:
            f.write(f"{source}\t{target}\t{relation}\n")

Adjacency Matrix Converter
---------------------------

Matrix representation for mathematical analysis.

.. code-block:: python

    from ista.converters import ontology_to_adjacency_matrix
    import numpy as np

    # Get adjacency matrix and node list
    adj_matrix, nodes = ontology_to_adjacency_matrix(ont)

    # adj_matrix is a numpy array
    print(f"Matrix shape: {adj_matrix.shape}")
    print(f"Density: {np.count_nonzero(adj_matrix) / adj_matrix.size:.4f}")

    # Find node with most connections
    out_degrees = adj_matrix.sum(axis=1)
    max_idx = np.argmax(out_degrees)
    print(f"Most connected node: {nodes[max_idx]}")
    print(f"Out-degree: {out_degrees[max_idx]}")

Round-Trip Conversion
---------------------

Convert between formats while preserving information.

.. code-block:: python

    # Ontology -> NetworkX -> Ontology
    from ista.converters import networkx_to_ontology

    G = ontology_to_networkx(ont)
    # ... modify graph ...
    ont_modified = networkx_to_ontology(G)

    # Ontology -> DataFrame -> Ontology
    from ista.converters import dataframe_to_ontology

    df = ontology_to_dataframe(ont)
    # ... modify dataframe ...
    ont_modified = dataframe_to_ontology(df)

Custom Converters
-----------------

Create your own custom converters:

.. code-block:: python

    from ista import owl2

    def ontology_to_custom_format(ont):
        """Convert ontology to custom format."""
        result = []

        for axiom in ont.get_axioms():
            # Process each axiom type
            if isinstance(axiom, owl2.SubClassOf):
                result.append({
                    'type': 'hierarchy',
                    'child': axiom.get_subclass().get_iri().get_short_form(),
                    'parent': axiom.get_superclass().get_iri().get_short_form()
                })
            elif isinstance(axiom, owl2.Declaration):
                result.append({
                    'type': 'entity',
                    'entity_type': axiom.get_entity_type(),
                    'iri': axiom.get_iri().toString()
                })
            # ... handle other axiom types ...

        return result

Performance Tips
----------------

For large ontologies:

1. **Filter First**: Use subgraph extraction before conversion
2. **Selective Conversion**: Only include needed axiom types
3. **Batch Processing**: Convert in chunks if memory is limited
4. **Use Efficient Formats**: Parquet for DataFrames, binary for graphs
5. **Index DataFrames**: Create indexes on frequently queried columns

.. code-block:: python

    # Example: Efficient conversion of large ontology
    from ista.owl2 import OntologyFilter

    # Extract relevant subgraph first
    filter_obj = OntologyFilter(large_ont)
    result = filter_obj.extract_neighborhood(seed_iri, depth=3)
    subgraph = result.get_ontology()

    # Convert smaller subgraph
    G = ontology_to_networkx(subgraph, include_individuals=False)

    # For DataFrame, create indexes
    df = ontology_to_dataframe(subgraph)
    df.set_index('subject', inplace=True)  # Fast subject lookups

See Also
--------

- :doc:`python_library` - Python library guide
- :doc:`subgraph_extraction` - Extract relevant portions
- :doc:`../api/owl2` - Complete API reference
- NetworkX documentation: https://networkx.org/
- pandas documentation: https://pandas.pydata.org/
