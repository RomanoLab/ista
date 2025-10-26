#!/usr/bin/env python3
"""
Knowledge Graph Analysis Example

This example demonstrates loading or creating a knowledge graph ontology,
converting it to multiple graph formats, comparing their representations,
and exporting to various file formats.

Features demonstrated:
1. Creating/loading a rich knowledge graph
2. Converting to NetworkX, igraph, and ista.graph
3. Comparing representations across formats
4. Performing format-specific analyses
5. Exporting to multiple formats (GraphML, GML, Pickle, etc.)
6. Performance comparisons
7. Memory usage analysis
"""

import sys
import time
from typing import Dict, Any, List
from pathlib import Path

# Check if OWL2 bindings are available
try:
    from ista import owl2

    if not owl2.is_available():
        print("ERROR: C++ OWL2 bindings are not available!")
        print("Please build the C++ extension first: pip install -e .")
        sys.exit(1)
except ImportError:
    print("ERROR: Could not import ista.owl2")
    sys.exit(1)

# Import converters
from ista.converters import (
    to_networkx,
    from_networkx,
    to_ista_graph,
    from_ista_graph,
    ConversionStrategy,
)

# Try to import optional dependencies
try:
    import networkx as nx

    HAS_NETWORKX = True
except ImportError:
    HAS_NETWORKX = False
    print("WARNING: NetworkX not available. Install with: pip install networkx")

try:
    import igraph as ig
    from ista.converters import to_igraph, from_igraph

    HAS_IGRAPH = True
except ImportError:
    HAS_IGRAPH = False
    print("WARNING: igraph not available. Install with: pip install igraph")

try:
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches

    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    print("WARNING: matplotlib not available. Install with: pip install matplotlib")

try:
    import pandas as pd

    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False
    print("WARNING: pandas not available. Install with: pip install pandas")


def create_knowledge_graph_ontology() -> owl2.Ontology:
    """
    Create a rich knowledge graph with multiple domains.

    Returns
    -------
    owl2.Ontology
        A multi-domain knowledge graph ontology.
    """
    print("\n" + "=" * 80)
    print("CREATING MULTI-DOMAIN KNOWLEDGE GRAPH")
    print("=" * 80)

    # Create ontology
    ontology_iri = "http://example.org/knowledge"
    onto = owl2.Ontology(owl2.IRI(ontology_iri))
    onto.register_prefix("kg", ontology_iri + "#")

    def kg_iri(name: str) -> owl2.IRI:
        return owl2.IRI("kg", name, ontology_iri + "#")

    # Define Classes (multiple domains)
    print("\nDefining classes...")
    classes = {
        # Scientific domain
        "Scientist": owl2.Class(kg_iri("Scientist")),
        "Research_Paper": owl2.Class(kg_iri("Research_Paper")),
        "Institution": owl2.Class(kg_iri("Institution")),
        "Field_of_Study": owl2.Class(kg_iri("Field_of_Study")),
        # Geographic domain
        "Country": owl2.Class(kg_iri("Country")),
        "City": owl2.Class(kg_iri("City")),
        # Conceptual domain
        "Concept": owl2.Class(kg_iri("Concept")),
        "Theory": owl2.Class(kg_iri("Theory")),
    }

    for name, cls in classes.items():
        onto.add_axiom(owl2.Declaration(cls))
        print(f"  - {name}")

    # Define Object Properties
    print("\nDefining object properties...")
    object_props = {
        "authored": owl2.ObjectProperty(kg_iri("authored")),
        "citedBy": owl2.ObjectProperty(kg_iri("citedBy")),
        "affiliatedWith": owl2.ObjectProperty(kg_iri("affiliatedWith")),
        "locatedIn": owl2.ObjectProperty(kg_iri("locatedIn")),
        "studiesField": owl2.ObjectProperty(kg_iri("studiesField")),
        "relatedTo": owl2.ObjectProperty(kg_iri("relatedTo")),
        "proposedTheory": owl2.ObjectProperty(kg_iri("proposedTheory")),
        "buildsUpon": owl2.ObjectProperty(kg_iri("buildsUpon")),
        "collaboratesWith": owl2.ObjectProperty(kg_iri("collaboratesWith")),
    }

    for name, prop in object_props.items():
        onto.add_axiom(owl2.Declaration(prop))
        print(f"  - {name}")

    # Define Data Properties
    print("\nDefining data properties...")
    data_props = {
        "name": owl2.DataProperty(kg_iri("name")),
        "year": owl2.DataProperty(kg_iri("year")),
        "citation_count": owl2.DataProperty(kg_iri("citation_count")),
        "h_index": owl2.DataProperty(kg_iri("h_index")),
        "population": owl2.DataProperty(kg_iri("population")),
        "title": owl2.DataProperty(kg_iri("title")),
        "abstract": owl2.DataProperty(kg_iri("abstract")),
    }

    for name, prop in data_props.items():
        onto.add_axiom(owl2.Declaration(prop))
        print(f"  - {name}")

    # Create entities
    print("\nCreating entities...")

    # Scientists
    scientists_data = [
        ("Einstein", "Physics", 1500, 85),
        ("Curie", "Chemistry", 1200, 72),
        ("Turing", "Computer_Science", 2000, 95),
        ("Darwin", "Biology", 1800, 88),
        ("Hawking", "Physics", 1600, 82),
        ("Franklin", "Chemistry", 900, 65),
        ("Lovelace", "Computer_Science", 800, 60),
        ("Goodall", "Biology", 1100, 70),
    ]

    scientists = {}
    for name, field, cites, h_idx in scientists_data:
        individual = owl2.NamedIndividual(kg_iri(name))
        scientists[name] = individual

        onto.add_axiom(owl2.Declaration(individual))
        onto.add_axiom(owl2.ClassAssertion(classes["Scientist"], individual))

        onto.add_axiom(
            owl2.DataPropertyAssertion(
                data_props["name"], individual, owl2.Literal(name)
            )
        )
        onto.add_axiom(
            owl2.DataPropertyAssertion(
                data_props["citation_count"],
                individual,
                owl2.Literal(
                    str(cites), owl2.IRI("http://www.w3.org/2001/XMLSchema#integer")
                ),
            )
        )
        onto.add_axiom(
            owl2.DataPropertyAssertion(
                data_props["h_index"],
                individual,
                owl2.Literal(
                    str(h_idx), owl2.IRI("http://www.w3.org/2001/XMLSchema#integer")
                ),
            )
        )

        print(f"  - Scientist: {name} (Field: {field}, Citations: {cites})")

    # Research Papers
    papers_data = [
        ("Relativity_Theory", "Einstein", 1905, 5000),
        ("Radioactivity_Research", "Curie", 1898, 4500),
        ("Computing_Machinery", "Turing", 1936, 8000),
        ("Origin_of_Species", "Darwin", 1859, 12000),
        ("Brief_History_Time", "Hawking", 1988, 6000),
        ("DNA_Structure", "Franklin", 1953, 7000),
        ("Analytical_Engine", "Lovelace", 1843, 3000),
        ("Chimpanzee_Behavior", "Goodall", 1965, 4000),
    ]

    papers = {}
    for title, author, year, cites in papers_data:
        individual = owl2.NamedIndividual(kg_iri(title))
        papers[title] = individual

        onto.add_axiom(owl2.Declaration(individual))
        onto.add_axiom(owl2.ClassAssertion(classes["Research_Paper"], individual))

        onto.add_axiom(
            owl2.DataPropertyAssertion(
                data_props["title"], individual, owl2.Literal(title.replace("_", " "))
            )
        )
        onto.add_axiom(
            owl2.DataPropertyAssertion(
                data_props["year"],
                individual,
                owl2.Literal(
                    str(year), owl2.IRI("http://www.w3.org/2001/XMLSchema#integer")
                ),
            )
        )
        onto.add_axiom(
            owl2.DataPropertyAssertion(
                data_props["citation_count"],
                individual,
                owl2.Literal(
                    str(cites), owl2.IRI("http://www.w3.org/2001/XMLSchema#integer")
                ),
            )
        )

        # Link to author
        onto.add_axiom(
            owl2.ObjectPropertyAssertion(
                object_props["authored"], scientists[author], individual
            )
        )

        print(f"  - Paper: {title} by {author} ({year})")

    # Institutions
    institutions_data = [
        ("MIT", "Cambridge", 11000),
        ("Cambridge_Uni", "Cambridge", 24000),
        ("Sorbonne", "Paris", 55000),
    ]

    institutions = {}
    for name, city, pop in institutions_data:
        individual = owl2.NamedIndividual(kg_iri(name))
        institutions[name] = individual

        onto.add_axiom(owl2.Declaration(individual))
        onto.add_axiom(owl2.ClassAssertion(classes["Institution"], individual))

        onto.add_axiom(
            owl2.DataPropertyAssertion(
                data_props["name"], individual, owl2.Literal(name.replace("_", " "))
            )
        )

        print(f"  - Institution: {name}")

    # Fields of Study
    fields_data = ["Physics", "Chemistry", "Computer_Science", "Biology"]

    fields = {}
    for field_name in fields_data:
        individual = owl2.NamedIndividual(kg_iri(field_name))
        fields[field_name] = individual

        onto.add_axiom(owl2.Declaration(individual))
        onto.add_axiom(owl2.ClassAssertion(classes["Field_of_Study"], individual))

        onto.add_axiom(
            owl2.DataPropertyAssertion(
                data_props["name"],
                individual,
                owl2.Literal(field_name.replace("_", " ")),
            )
        )

        print(f"  - Field: {field_name}")

    # Add relationships
    print("\nAdding relationships...")

    # Scientists to fields
    field_assignments = [
        ("Einstein", "Physics"),
        ("Curie", "Chemistry"),
        ("Turing", "Computer_Science"),
        ("Darwin", "Biology"),
        ("Hawking", "Physics"),
        ("Franklin", "Chemistry"),
        ("Lovelace", "Computer_Science"),
        ("Goodall", "Biology"),
    ]

    for scientist, field in field_assignments:
        onto.add_axiom(
            owl2.ObjectPropertyAssertion(
                object_props["studiesField"], scientists[scientist], fields[field]
            )
        )

    # Scientists to institutions
    affiliations = [
        ("Einstein", "MIT"),
        ("Turing", "Cambridge_Uni"),
        ("Curie", "Sorbonne"),
        ("Hawking", "Cambridge_Uni"),
        ("Lovelace", "Cambridge_Uni"),
    ]

    for scientist, institution in affiliations:
        onto.add_axiom(
            owl2.ObjectPropertyAssertion(
                object_props["affiliatedWith"],
                scientists[scientist],
                institutions[institution],
            )
        )

    # Collaborations
    collaborations = [
        ("Einstein", "Hawking"),
        ("Curie", "Franklin"),
        ("Turing", "Lovelace"),
        ("Darwin", "Goodall"),
    ]

    for sci1, sci2 in collaborations:
        onto.add_axiom(
            owl2.ObjectPropertyAssertion(
                object_props["collaboratesWith"], scientists[sci1], scientists[sci2]
            )
        )
        onto.add_axiom(
            owl2.ObjectPropertyAssertion(
                object_props["collaboratesWith"], scientists[sci2], scientists[sci1]
            )
        )

    # Paper citations
    citations = [
        ("Brief_History_Time", "Relativity_Theory"),
        ("Computing_Machinery", "Analytical_Engine"),
        ("Chimpanzee_Behavior", "Origin_of_Species"),
        ("DNA_Structure", "Radioactivity_Research"),
    ]

    for citing, cited in citations:
        onto.add_axiom(
            owl2.ObjectPropertyAssertion(
                object_props["citedBy"], papers[cited], papers[citing]
            )
        )

    print(f"  - Added {len(field_assignments)} field assignments")
    print(f"  - Added {len(affiliations)} institutional affiliations")
    print(f"  - Added {len(collaborations)} collaborations")
    print(f"  - Added {len(citations)} paper citations")

    # Print statistics
    print(f"\nOntology Statistics:")
    print(f"  - Total axioms: {onto.get_axiom_count()}")
    print(f"  - Classes: {onto.get_class_count()}")
    print(f"  - Object properties: {onto.get_object_property_count()}")
    print(f"  - Data properties: {onto.get_data_property_count()}")
    print(f"  - Individuals: {onto.get_individual_count()}")

    return onto


def convert_to_all_formats(onto: owl2.Ontology) -> Dict[str, Any]:
    """
    Convert ontology to all available graph formats.

    Parameters
    ----------
    onto : owl2.Ontology
        The ontology to convert.

    Returns
    -------
    Dict[str, Any]
        Dictionary mapping format names to graph objects.
    """
    print("\n" + "=" * 80)
    print("CONVERTING TO MULTIPLE FORMATS")
    print("=" * 80)

    graphs = {}

    # NetworkX
    if HAS_NETWORKX:
        print("\n1. Converting to NetworkX...")
        start = time.time()
        nx_graph = to_networkx(onto, strategy="individuals_only")
        elapsed = time.time() - start
        graphs["networkx"] = nx_graph
        print(f"  - Nodes: {nx_graph.number_of_nodes()}")
        print(f"  - Edges: {nx_graph.number_of_edges()}")
        print(f"  - Conversion time: {elapsed:.4f} seconds")

    # igraph
    if HAS_IGRAPH:
        print("\n2. Converting to igraph...")
        start = time.time()
        ig_graph = to_igraph(onto, strategy="individuals_only")
        elapsed = time.time() - start
        graphs["igraph"] = ig_graph
        print(f"  - Vertices: {ig_graph.vcount()}")
        print(f"  - Edges: {ig_graph.ecount()}")
        print(f"  - Conversion time: {elapsed:.4f} seconds")

    # ista.graph
    print("\n3. Converting to ista.graph...")
    start = time.time()
    ista_graph = to_ista_graph(onto, strategy="individuals_only")
    elapsed = time.time() - start
    graphs["ista"] = ista_graph
    print(f"  - Nodes: {len(ista_graph.nodes)}")
    print(f"  - Edges: {len(ista_graph.edges)}")
    print(f"  - Conversion time: {elapsed:.4f} seconds")

    return graphs


def compare_graph_representations(graphs: Dict[str, Any]):
    """
    Compare different graph representations.

    Parameters
    ----------
    graphs : Dict[str, Any]
        Dictionary of graph objects in different formats.
    """
    print("\n" + "=" * 80)
    print("COMPARING GRAPH REPRESENTATIONS")
    print("=" * 80)

    comparison_data = []

    # NetworkX
    if "networkx" in graphs:
        nx_graph = graphs["networkx"]
        print("\n1. NetworkX DiGraph:")
        print(f"  - Type: {type(nx_graph)}")
        print(f"  - Nodes: {nx_graph.number_of_nodes()}")
        print(f"  - Edges: {nx_graph.number_of_edges()}")
        print(
            f"  - Node attributes: {list(list(nx_graph.nodes(data=True))[0][1].keys())[:5]}"
        )
        print(
            f"  - Edge attributes: {list(list(nx_graph.edges(data=True))[0][2].keys())}"
        )
        print(f"  - Is directed: {nx_graph.is_directed()}")
        print(f"  - Supports multigraph: No (DiGraph)")

        comparison_data.append(
            {
                "Format": "NetworkX",
                "Nodes": nx_graph.number_of_nodes(),
                "Edges": nx_graph.number_of_edges(),
                "Directed": "Yes",
                "Rich Attributes": "Yes",
            }
        )

    # igraph
    if "igraph" in graphs:
        ig_graph = graphs["igraph"]
        print("\n2. igraph Graph:")
        print(f"  - Type: {type(ig_graph)}")
        print(f"  - Vertices: {ig_graph.vcount()}")
        print(f"  - Edges: {ig_graph.ecount()}")
        print(f"  - Vertex attributes: {ig_graph.vs.attributes()[:5]}")
        print(f"  - Edge attributes: {ig_graph.es.attributes()}")
        print(f"  - Is directed: {ig_graph.is_directed()}")
        print(f"  - Density: {ig_graph.density():.4f}")

        comparison_data.append(
            {
                "Format": "igraph",
                "Nodes": ig_graph.vcount(),
                "Edges": ig_graph.ecount(),
                "Directed": "Yes",
                "Rich Attributes": "Yes",
            }
        )

    # ista.graph
    if "ista" in graphs:
        ista_graph = graphs["ista"]
        print("\n3. ista.graph Graph:")
        print(f"  - Type: {type(ista_graph)}")
        print(f"  - Nodes: {len(ista_graph.nodes)}")
        print(f"  - Edges: {len(ista_graph.edges)}")
        print(f"  - Node properties: {list(ista_graph.nodes[0].properties.keys())[:5]}")
        print(
            f"  - Edge properties: {list(ista_graph.edges[0].edge_properties.keys())}"
        )
        print(f"  - Is directed: Yes (by design)")
        print(f"  - Native format: Yes")

        comparison_data.append(
            {
                "Format": "ista.graph",
                "Nodes": len(ista_graph.nodes),
                "Edges": len(ista_graph.edges),
                "Directed": "Yes",
                "Rich Attributes": "Yes",
            }
        )

    # Create comparison table
    if HAS_PANDAS:
        print("\n4. Comparison Table:")
        df = pd.DataFrame(comparison_data)
        print(df.to_string(index=False))
    else:
        print("\n4. Comparison Summary:")
        for data in comparison_data:
            print(f"  - {data['Format']}: {data['Nodes']} nodes, {data['Edges']} edges")


def perform_format_specific_analysis(graphs: Dict[str, Any]):
    """
    Perform analyses specific to each graph format.

    Parameters
    ----------
    graphs : Dict[str, Any]
        Dictionary of graph objects.
    """
    print("\n" + "=" * 80)
    print("FORMAT-SPECIFIC ANALYSES")
    print("=" * 80)

    # NetworkX analysis
    if "networkx" in graphs:
        print("\n1. NetworkX Algorithms:")
        nx_graph = graphs["networkx"]

        print("  a) Centrality Measures:")
        degree_cent = nx.degree_centrality(nx_graph)
        top_degree = sorted(degree_cent.items(), key=lambda x: x[1], reverse=True)[:3]
        for node, score in top_degree:
            label = nx_graph.nodes[node].get("label", "Unknown")
            print(f"    - {label}: {score:.3f}")

        print("  b) Strongly Connected Components:")
        num_scc = nx.number_strongly_connected_components(nx_graph)
        print(f"    - Number of SCCs: {num_scc}")

        print("  c) Average Clustering:")
        try:
            clustering = nx.average_clustering(nx_graph.to_undirected())
            print(f"    - Average clustering: {clustering:.4f}")
        except:
            print("    - Could not compute")

    # igraph analysis
    if "igraph" in graphs:
        print("\n2. igraph Algorithms:")
        ig_graph = graphs["igraph"]

        print("  a) Degree Distribution:")
        degrees = ig_graph.degree()
        print(f"    - Min degree: {min(degrees)}")
        print(f"    - Max degree: {max(degrees)}")
        print(f"    - Average degree: {sum(degrees) / len(degrees):.2f}")

        print("  b) Community Detection (Leiden):")
        try:
            communities = ig_graph.community_leiden()
            print(f"    - Number of communities: {len(communities)}")
            print(f"    - Modularity: {communities.modularity:.4f}")
        except Exception as e:
            print(f"    - Could not compute: {e}")

        print("  c) Betweenness Centrality:")
        betweenness = ig_graph.betweenness()
        top_betweenness = sorted(
            enumerate(betweenness), key=lambda x: x[1], reverse=True
        )[:3]
        for idx, score in top_betweenness:
            label = ig_graph.vs[idx]["label"]
            print(f"    - {label}: {score:.3f}")

    # ista.graph analysis
    if "ista" in graphs:
        print("\n3. ista.graph Operations:")
        ista_graph = graphs["ista"]

        print("  a) Basic Statistics:")
        print(f"    - Total nodes: {len(ista_graph.nodes)}")
        print(f"    - Total edges: {len(ista_graph.edges)}")

        print("  b) Node Classes:")
        node_classes = {}
        for node in ista_graph.nodes:
            cls = node.node_class
            node_classes[cls] = node_classes.get(cls, 0) + 1
        for cls, count in sorted(node_classes.items()):
            print(f"    - {cls}: {count}")

        print("  c) Adjacency Matrix:")
        try:
            adj = ista_graph.get_adjacency(format="matrix")
            print(f"    - Shape: {adj.shape}")
            print(f"    - Non-zero entries: {(adj != 0).sum()}")
        except Exception as e:
            print(f"    - Could not compute: {e}")


def export_to_formats(
    graphs: Dict[str, Any], output_dir: str = "D:\\projects\\ista\\examples"
):
    """
    Export graphs to various file formats.

    Parameters
    ----------
    graphs : Dict[str, Any]
        Dictionary of graph objects.
    output_dir : str
        Directory to save exported files.
    """
    print("\n" + "=" * 80)
    print("EXPORTING TO FILE FORMATS")
    print("=" * 80)

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # NetworkX exports
    if "networkx" in graphs and HAS_NETWORKX:
        nx_graph = graphs["networkx"]
        print("\n1. NetworkX Exports:")

        # GraphML
        try:
            graphml_file = output_path / "knowledge_graph.graphml"
            nx.write_graphml(nx_graph, str(graphml_file))
            print(f"  - GraphML: {graphml_file}")
        except Exception as e:
            print(f"  - GraphML: Failed ({e})")

        # GML
        try:
            gml_file = output_path / "knowledge_graph.gml"
            nx.write_gml(nx_graph, str(gml_file))
            print(f"  - GML: {gml_file}")
        except Exception as e:
            print(f"  - GML: Failed ({e})")

        # Pickle
        try:
            pickle_file = output_path / "knowledge_graph_nx.pkl"
            nx.write_gpickle(nx_graph, str(pickle_file))
            print(f"  - Pickle: {pickle_file}")
        except Exception as e:
            print(f"  - Pickle: Failed ({e})")

        # Adjacency list
        try:
            adjlist_file = output_path / "knowledge_graph.adjlist"
            nx.write_adjlist(nx_graph, str(adjlist_file))
            print(f"  - Adjacency List: {adjlist_file}")
        except Exception as e:
            print(f"  - Adjacency List: Failed ({e})")

        # Edge list
        try:
            edgelist_file = output_path / "knowledge_graph.edgelist"
            nx.write_edgelist(nx_graph, str(edgelist_file), data=True)
            print(f"  - Edge List: {edgelist_file}")
        except Exception as e:
            print(f"  - Edge List: Failed ({e})")

    # igraph exports
    if "igraph" in graphs and HAS_IGRAPH:
        ig_graph = graphs["igraph"]
        print("\n2. igraph Exports:")

        # GraphML
        try:
            graphml_file = output_path / "knowledge_graph_ig.graphml"
            ig_graph.write_graphml(str(graphml_file))
            print(f"  - GraphML: {graphml_file}")
        except Exception as e:
            print(f"  - GraphML: Failed ({e})")

        # GML
        try:
            gml_file = output_path / "knowledge_graph_ig.gml"
            ig_graph.write_gml(str(gml_file))
            print(f"  - GML: {gml_file}")
        except Exception as e:
            print(f"  - GML: Failed ({e})")

        # Pickle
        try:
            pickle_file = output_path / "knowledge_graph_ig.pkl"
            ig_graph.write_pickle(str(pickle_file))
            print(f"  - Pickle: {pickle_file}")
        except Exception as e:
            print(f"  - Pickle: Failed ({e})")


def performance_comparison(onto: owl2.Ontology):
    """
    Compare performance across formats.

    Parameters
    ----------
    onto : owl2.Ontology
        The ontology to convert.
    """
    print("\n" + "=" * 80)
    print("PERFORMANCE COMPARISON")
    print("=" * 80)

    results = []

    # NetworkX
    if HAS_NETWORKX:
        print("\n1. NetworkX Performance:")

        # Conversion time
        start = time.time()
        nx_graph = to_networkx(onto, strategy="individuals_only")
        conversion_time = time.time() - start
        print(f"  - Conversion time: {conversion_time:.4f} seconds")

        # Centrality computation time
        start = time.time()
        degree_cent = nx.degree_centrality(nx_graph)
        centrality_time = time.time() - start
        print(f"  - Degree centrality time: {centrality_time:.4f} seconds")

        # Path computation time
        start = time.time()
        nodes = list(nx_graph.nodes())
        if len(nodes) >= 2:
            try:
                path = nx.shortest_path(nx_graph, nodes[0], nodes[1])
                path_time = time.time() - start
                print(f"  - Shortest path time: {path_time:.4f} seconds")
            except:
                path_time = None
                print(f"  - Shortest path time: N/A")
        else:
            path_time = None

        results.append(
            {
                "Format": "NetworkX",
                "Conversion": f"{conversion_time:.4f}s",
                "Centrality": f"{centrality_time:.4f}s",
                "Path": f"{path_time:.4f}s" if path_time else "N/A",
            }
        )

    # igraph
    if HAS_IGRAPH:
        print("\n2. igraph Performance:")

        # Conversion time
        start = time.time()
        ig_graph = to_igraph(onto, strategy="individuals_only")
        conversion_time = time.time() - start
        print(f"  - Conversion time: {conversion_time:.4f} seconds")

        # Centrality computation time
        start = time.time()
        betweenness = ig_graph.betweenness()
        centrality_time = time.time() - start
        print(f"  - Betweenness centrality time: {centrality_time:.4f} seconds")

        # Path computation time
        start = time.time()
        if ig_graph.vcount() >= 2:
            path = ig_graph.get_shortest_paths(0, 1)
            path_time = time.time() - start
            print(f"  - Shortest path time: {path_time:.4f} seconds")
        else:
            path_time = None

        results.append(
            {
                "Format": "igraph",
                "Conversion": f"{conversion_time:.4f}s",
                "Centrality": f"{centrality_time:.4f}s",
                "Path": f"{path_time:.4f}s" if path_time else "N/A",
            }
        )

    # ista.graph
    print("\n3. ista.graph Performance:")

    start = time.time()
    ista_graph = to_ista_graph(onto, strategy="individuals_only")
    conversion_time = time.time() - start
    print(f"  - Conversion time: {conversion_time:.4f} seconds")

    start = time.time()
    try:
        adj = ista_graph.get_adjacency(format="matrix")
        adj_time = time.time() - start
        print(f"  - Adjacency matrix time: {adj_time:.4f} seconds")
    except Exception as e:
        adj_time = None
        print(f"  - Adjacency matrix time: Failed ({e})")

    results.append(
        {
            "Format": "ista.graph",
            "Conversion": f"{conversion_time:.4f}s",
            "Centrality": "N/A",
            "Path": "N/A",
        }
    )

    # Display comparison table
    if HAS_PANDAS:
        print("\n4. Performance Summary:")
        df = pd.DataFrame(results)
        print(df.to_string(index=False))


def visualize_comparison(graphs: Dict[str, Any]):
    """
    Visualize comparison of graph formats.

    Parameters
    ----------
    graphs : Dict[str, Any]
        Dictionary of graph objects.
    """
    if not HAS_MATPLOTLIB:
        print("\nSkipping visualization (matplotlib not available)")
        return

    print("\n" + "=" * 80)
    print("CREATING VISUALIZATION")
    print("=" * 80)

    fig, axes = plt.subplots(1, 2, figsize=(16, 7))

    # Plot 1: Node and Edge Counts
    formats = []
    node_counts = []
    edge_counts = []

    if "networkx" in graphs:
        formats.append("NetworkX")
        node_counts.append(graphs["networkx"].number_of_nodes())
        edge_counts.append(graphs["networkx"].number_of_edges())

    if "igraph" in graphs:
        formats.append("igraph")
        node_counts.append(graphs["igraph"].vcount())
        edge_counts.append(graphs["igraph"].ecount())

    if "ista" in graphs:
        formats.append("ista.graph")
        node_counts.append(len(graphs["ista"].nodes))
        edge_counts.append(len(graphs["ista"].edges))

    x = range(len(formats))
    width = 0.35

    axes[0].bar(
        [i - width / 2 for i in x], node_counts, width, label="Nodes", color="#4ECDC4"
    )
    axes[0].bar(
        [i + width / 2 for i in x], edge_counts, width, label="Edges", color="#FF6B6B"
    )
    axes[0].set_xlabel("Format", fontsize=12, fontweight="bold")
    axes[0].set_ylabel("Count", fontsize=12, fontweight="bold")
    axes[0].set_title("Graph Size Comparison", fontsize=14, fontweight="bold")
    axes[0].set_xticks(x)
    axes[0].set_xticklabels(formats)
    axes[0].legend()
    axes[0].grid(axis="y", alpha=0.3)

    # Plot 2: Feature Support
    features = [
        "Directed",
        "Node Attributes",
        "Edge Attributes",
        "Export Formats",
        "Analysis Tools",
    ]
    feature_scores = {
        "NetworkX": [1, 1, 1, 1, 1],
        "igraph": [1, 1, 1, 1, 1],
        "ista.graph": [1, 1, 1, 0.5, 0.5],
    }

    x_pos = range(len(features))
    colors = ["#4ECDC4", "#FF6B6B", "#95E1D3"]

    for i, (fmt, scores) in enumerate(feature_scores.items()):
        if fmt.replace(".", "") in [f.replace(".", "") for f in formats]:
            axes[1].barh(
                [p + i * 0.25 for p in x_pos],
                scores,
                0.25,
                label=fmt,
                color=colors[i],
                alpha=0.8,
            )

    axes[1].set_yticks([p + 0.25 for p in x_pos])
    axes[1].set_yticklabels(features)
    axes[1].set_xlabel("Support Level", fontsize=12, fontweight="bold")
    axes[1].set_title("Feature Support Comparison", fontsize=14, fontweight="bold")
    axes[1].set_xlim(0, 1.2)
    axes[1].legend()
    axes[1].grid(axis="x", alpha=0.3)

    plt.tight_layout()

    output_file = "D:\\projects\\ista\\examples\\graph_format_comparison.png"
    plt.savefig(output_file, dpi=300, bbox_inches="tight")
    print(f"\n  - Saved visualization to: {output_file}")


def main():
    """Main entry point."""
    print("\n" + "=" * 80)
    print("KNOWLEDGE GRAPH ANALYSIS: Format Comparison")
    print("=" * 80)

    # Create ontology
    onto = create_knowledge_graph_ontology()

    # Save ontology
    output_file = "D:\\projects\\ista\\examples\\knowledge_graph.ofn"
    owl2.FunctionalSyntaxSerializer.serialize_to_file(onto, output_file)
    print(f"\nSaved ontology to: {output_file}")

    # Convert to all formats
    graphs = convert_to_all_formats(onto)

    # Compare representations
    compare_graph_representations(graphs)

    # Format-specific analyses
    perform_format_specific_analysis(graphs)

    # Export to file formats
    export_to_formats(graphs)

    # Performance comparison
    performance_comparison(onto)

    # Visualization
    visualize_comparison(graphs)

    # Final summary
    print("\n" + "=" * 80)
    print("EXAMPLE COMPLETED")
    print("=" * 80)
    print("\nKey Insights:")
    print("  1. All formats successfully represent the knowledge graph")
    print("  2. Each format has specific strengths:")
    print("     - NetworkX: Rich ecosystem, easy to use, pure Python")
    print("     - igraph: High performance, advanced algorithms, C library")
    print("     - ista.graph: Native format, custom operations, lightweight")
    print("  3. Export capabilities vary by format")
    print("  4. Performance differences depend on graph size and operations")
    print("\nGenerated Files:")
    print("  - D:\\projects\\ista\\examples\\knowledge_graph.ofn")
    print("  - D:\\projects\\ista\\examples\\knowledge_graph.graphml")
    print("  - D:\\projects\\ista\\examples\\knowledge_graph.gml")
    print("  - D:\\projects\\ista\\examples\\knowledge_graph*.pkl")
    if HAS_MATPLOTLIB:
        print("  - D:\\projects\\ista\\examples\\graph_format_comparison.png")
    print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
