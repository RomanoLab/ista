#!/usr/bin/env python3
"""
Complete Ontology-to-Graph Conversion Workflow Example

This example demonstrates the full workflow of converting OWL2 ontologies
to various graph representations (NetworkX, igraph, ista.graph), performing
graph analysis, and converting back to ontologies.

Domain: Medical/Clinical Knowledge Graph
- Patients, Diseases, Treatments, Symptoms
- Object properties: diagnoses, treats, causes, prescribedFor
- Data properties: age, severity, dosage

Features demonstrated:
1. Creating a medical ontology
2. Converting to NetworkX with different strategies
3. Performing NetworkX analysis (centrality, paths, communities)
4. Converting to igraph (if available)
5. Performing igraph analysis (community detection, clustering)
6. Converting to ista.graph
7. Performing ista graph operations
8. Round-trip testing: ontology -> graph -> ontology
9. Visualization with matplotlib (if available)
"""

import sys
from typing import Optional

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
    ConversionOptions,
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

    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    print("WARNING: matplotlib not available. Install with: pip install matplotlib")


def create_medical_ontology() -> owl2.Ontology:
    """
    Create a sample medical ontology with patients, diseases, treatments, and symptoms.

    Returns
    -------
    owl2.Ontology
        A populated medical ontology.
    """
    print("\n" + "=" * 80)
    print("STEP 1: Creating Medical Ontology")
    print("=" * 80)

    # Create ontology
    ontology_iri = "http://example.org/medical"
    onto = owl2.Ontology(owl2.IRI(ontology_iri))
    onto.register_prefix("med", ontology_iri + "#")

    # Helper function to create IRI
    def med_iri(name: str) -> owl2.IRI:
        return owl2.IRI("med", name, ontology_iri + "#")

    # Define Classes
    print("\nDefining classes...")
    classes = {
        "Patient": owl2.Class(med_iri("Patient")),
        "Disease": owl2.Class(med_iri("Disease")),
        "Treatment": owl2.Class(med_iri("Treatment")),
        "Symptom": owl2.Class(med_iri("Symptom")),
    }

    for name, cls in classes.items():
        onto.add_axiom(owl2.Declaration(cls))
        print(f"  - Created class: {name}")

    # Define Object Properties
    print("\nDefining object properties...")
    object_props = {
        "diagnoses": owl2.ObjectProperty(med_iri("diagnoses")),
        "treats": owl2.ObjectProperty(med_iri("treats")),
        "causes": owl2.ObjectProperty(med_iri("causes")),
        "prescribedFor": owl2.ObjectProperty(med_iri("prescribedFor")),
        "exhibits": owl2.ObjectProperty(med_iri("exhibits")),
    }

    for name, prop in object_props.items():
        onto.add_axiom(owl2.Declaration(prop))
        print(f"  - Created object property: {name}")

    # Define Data Properties
    print("\nDefining data properties...")
    data_props = {
        "age": owl2.DataProperty(med_iri("age")),
        "severity": owl2.DataProperty(med_iri("severity")),
        "dosage": owl2.DataProperty(med_iri("dosage")),
        "name": owl2.DataProperty(med_iri("name")),
    }

    for name, prop in data_props.items():
        onto.add_axiom(owl2.Declaration(prop))
        print(f"  - Created data property: {name}")

    # Create Individuals
    print("\nCreating individuals...")

    # Patients
    patients = {
        "Patient1": owl2.NamedIndividual(med_iri("Patient1")),
        "Patient2": owl2.NamedIndividual(med_iri("Patient2")),
        "Patient3": owl2.NamedIndividual(med_iri("Patient3")),
    }

    for name, individual in patients.items():
        onto.add_axiom(owl2.Declaration(individual))
        onto.add_axiom(owl2.ClassAssertion(classes["Patient"], individual))
        print(f"  - Created patient: {name}")

    # Diseases
    diseases = {
        "Diabetes": owl2.NamedIndividual(med_iri("Diabetes")),
        "Hypertension": owl2.NamedIndividual(med_iri("Hypertension")),
        "Asthma": owl2.NamedIndividual(med_iri("Asthma")),
    }

    for name, individual in diseases.items():
        onto.add_axiom(owl2.Declaration(individual))
        onto.add_axiom(owl2.ClassAssertion(classes["Disease"], individual))
        print(f"  - Created disease: {name}")

    # Treatments
    treatments = {
        "Insulin": owl2.NamedIndividual(med_iri("Insulin")),
        "Metformin": owl2.NamedIndividual(med_iri("Metformin")),
        "Lisinopril": owl2.NamedIndividual(med_iri("Lisinopril")),
        "Albuterol": owl2.NamedIndividual(med_iri("Albuterol")),
    }

    for name, individual in treatments.items():
        onto.add_axiom(owl2.Declaration(individual))
        onto.add_axiom(owl2.ClassAssertion(classes["Treatment"], individual))
        print(f"  - Created treatment: {name}")

    # Symptoms
    symptoms = {
        "Fatigue": owl2.NamedIndividual(med_iri("Fatigue")),
        "Thirst": owl2.NamedIndividual(med_iri("Thirst")),
        "Headache": owl2.NamedIndividual(med_iri("Headache")),
        "Shortness_of_Breath": owl2.NamedIndividual(med_iri("Shortness_of_Breath")),
    }

    for name, individual in symptoms.items():
        onto.add_axiom(owl2.Declaration(individual))
        onto.add_axiom(owl2.ClassAssertion(classes["Symptom"], individual))
        print(f"  - Created symptom: {name}")

    # Add Object Property Assertions (relationships)
    print("\nAdding relationships...")

    # Patient1 has Diabetes, exhibits Fatigue and Thirst
    onto.add_axiom(
        owl2.ObjectPropertyAssertion(
            object_props["diagnoses"], patients["Patient1"], diseases["Diabetes"]
        )
    )
    onto.add_axiom(
        owl2.ObjectPropertyAssertion(
            object_props["exhibits"], patients["Patient1"], symptoms["Fatigue"]
        )
    )
    onto.add_axiom(
        owl2.ObjectPropertyAssertion(
            object_props["exhibits"], patients["Patient1"], symptoms["Thirst"]
        )
    )
    print("  - Patient1: diagnosed with Diabetes, exhibits Fatigue and Thirst")

    # Patient2 has Hypertension, exhibits Headache
    onto.add_axiom(
        owl2.ObjectPropertyAssertion(
            object_props["diagnoses"], patients["Patient2"], diseases["Hypertension"]
        )
    )
    onto.add_axiom(
        owl2.ObjectPropertyAssertion(
            object_props["exhibits"], patients["Patient2"], symptoms["Headache"]
        )
    )
    print("  - Patient2: diagnosed with Hypertension, exhibits Headache")

    # Patient3 has Asthma and Hypertension
    onto.add_axiom(
        owl2.ObjectPropertyAssertion(
            object_props["diagnoses"], patients["Patient3"], diseases["Asthma"]
        )
    )
    onto.add_axiom(
        owl2.ObjectPropertyAssertion(
            object_props["diagnoses"], patients["Patient3"], diseases["Hypertension"]
        )
    )
    onto.add_axiom(
        owl2.ObjectPropertyAssertion(
            object_props["exhibits"],
            patients["Patient3"],
            symptoms["Shortness_of_Breath"],
        )
    )
    print("  - Patient3: diagnosed with Asthma and Hypertension")

    # Treatments relationships
    onto.add_axiom(
        owl2.ObjectPropertyAssertion(
            object_props["treats"], treatments["Insulin"], diseases["Diabetes"]
        )
    )
    onto.add_axiom(
        owl2.ObjectPropertyAssertion(
            object_props["treats"], treatments["Metformin"], diseases["Diabetes"]
        )
    )
    onto.add_axiom(
        owl2.ObjectPropertyAssertion(
            object_props["treats"], treatments["Lisinopril"], diseases["Hypertension"]
        )
    )
    onto.add_axiom(
        owl2.ObjectPropertyAssertion(
            object_props["treats"], treatments["Albuterol"], diseases["Asthma"]
        )
    )
    print("  - Added treatment relationships")

    # Disease causes symptoms
    onto.add_axiom(
        owl2.ObjectPropertyAssertion(
            object_props["causes"], diseases["Diabetes"], symptoms["Fatigue"]
        )
    )
    onto.add_axiom(
        owl2.ObjectPropertyAssertion(
            object_props["causes"], diseases["Diabetes"], symptoms["Thirst"]
        )
    )
    onto.add_axiom(
        owl2.ObjectPropertyAssertion(
            object_props["causes"], diseases["Hypertension"], symptoms["Headache"]
        )
    )
    onto.add_axiom(
        owl2.ObjectPropertyAssertion(
            object_props["causes"], diseases["Asthma"], symptoms["Shortness_of_Breath"]
        )
    )
    print("  - Added disease-symptom relationships")

    # Add Data Property Assertions
    print("\nAdding data properties...")

    # Patient ages and names
    onto.add_axiom(
        owl2.DataPropertyAssertion(
            data_props["age"],
            patients["Patient1"],
            owl2.Literal("45", owl2.IRI("http://www.w3.org/2001/XMLSchema#integer")),
        )
    )
    onto.add_axiom(
        owl2.DataPropertyAssertion(
            data_props["name"], patients["Patient1"], owl2.Literal("John Doe")
        )
    )

    onto.add_axiom(
        owl2.DataPropertyAssertion(
            data_props["age"],
            patients["Patient2"],
            owl2.Literal("62", owl2.IRI("http://www.w3.org/2001/XMLSchema#integer")),
        )
    )
    onto.add_axiom(
        owl2.DataPropertyAssertion(
            data_props["name"], patients["Patient2"], owl2.Literal("Jane Smith")
        )
    )

    onto.add_axiom(
        owl2.DataPropertyAssertion(
            data_props["age"],
            patients["Patient3"],
            owl2.Literal("38", owl2.IRI("http://www.w3.org/2001/XMLSchema#integer")),
        )
    )
    onto.add_axiom(
        owl2.DataPropertyAssertion(
            data_props["name"], patients["Patient3"], owl2.Literal("Bob Johnson")
        )
    )
    print("  - Added patient data (age, name)")

    # Disease severity
    onto.add_axiom(
        owl2.DataPropertyAssertion(
            data_props["severity"], diseases["Diabetes"], owl2.Literal("moderate")
        )
    )
    onto.add_axiom(
        owl2.DataPropertyAssertion(
            data_props["severity"], diseases["Hypertension"], owl2.Literal("high")
        )
    )
    onto.add_axiom(
        owl2.DataPropertyAssertion(
            data_props["severity"], diseases["Asthma"], owl2.Literal("severe")
        )
    )
    print("  - Added disease severity")

    # Treatment dosages
    onto.add_axiom(
        owl2.DataPropertyAssertion(
            data_props["dosage"], treatments["Insulin"], owl2.Literal("10 units")
        )
    )
    onto.add_axiom(
        owl2.DataPropertyAssertion(
            data_props["dosage"], treatments["Metformin"], owl2.Literal("500 mg")
        )
    )
    onto.add_axiom(
        owl2.DataPropertyAssertion(
            data_props["dosage"], treatments["Lisinopril"], owl2.Literal("20 mg")
        )
    )
    onto.add_axiom(
        owl2.DataPropertyAssertion(
            data_props["dosage"], treatments["Albuterol"], owl2.Literal("2 puffs")
        )
    )
    print("  - Added treatment dosages")

    # Print statistics
    print(f"\nOntology Statistics:")
    print(f"  - Total axioms: {onto.get_axiom_count()}")
    print(f"  - Classes: {onto.get_class_count()}")
    print(f"  - Object properties: {onto.get_object_property_count()}")
    print(f"  - Data properties: {onto.get_data_property_count()}")
    print(f"  - Individuals: {onto.get_individual_count()}")

    return onto


def demonstrate_networkx_conversion(onto: owl2.Ontology) -> Optional[object]:
    """
    Convert ontology to NetworkX and perform various analyses.

    Parameters
    ----------
    onto : owl2.Ontology
        The medical ontology to convert.

    Returns
    -------
    nx.DiGraph or None
        The NetworkX graph, or None if NetworkX is not available.
    """
    if not HAS_NETWORKX:
        print("\nSkipping NetworkX examples (not installed)")
        return None

    print("\n" + "=" * 80)
    print("STEP 2: NetworkX Conversion and Analysis")
    print("=" * 80)

    # Convert with individuals only
    print("\n2.1: Converting to NetworkX (individuals only)...")
    nx_graph = to_networkx(onto, strategy="individuals_only")
    print(f"  - Nodes: {nx_graph.number_of_nodes()}")
    print(f"  - Edges: {nx_graph.number_of_edges()}")

    # Display node attributes
    print("\n  Sample node attributes:")
    for i, (node, attrs) in enumerate(nx_graph.nodes(data=True)):
        if i < 3:
            print(f"    {attrs['label']}:")
            print(f"      - Type: {attrs['type']}")
            print(f"      - Classes: {attrs.get('classes', [])}")
            if "data_age" in attrs:
                print(f"      - Age: {attrs['data_age']}")
            if "data_name" in attrs:
                print(f"      - Name: {attrs['data_name']}")

    # Display edge attributes
    print("\n  Sample edge attributes:")
    for i, (u, v, attrs) in enumerate(nx_graph.edges(data=True)):
        if i < 5:
            u_label = nx_graph.nodes[u]["label"]
            v_label = nx_graph.nodes[v]["label"]
            prop_label = attrs["property_label"]
            print(f"    {u_label} --[{prop_label}]--> {v_label}")

    # NetworkX Analysis
    print("\n2.2: Performing NetworkX Analysis...")

    # Degree centrality
    print("\n  Degree Centrality (top 5):")
    degree_cent = nx.degree_centrality(nx_graph)
    sorted_degree = sorted(degree_cent.items(), key=lambda x: x[1], reverse=True)
    for node_iri, centrality in sorted_degree[:5]:
        label = nx_graph.nodes[node_iri]["label"]
        print(f"    {label}: {centrality:.3f}")

    # Betweenness centrality
    print("\n  Betweenness Centrality (top 5):")
    betweenness = nx.betweenness_centrality(nx_graph)
    sorted_betweenness = sorted(betweenness.items(), key=lambda x: x[1], reverse=True)
    for node_iri, centrality in sorted_betweenness[:5]:
        label = nx_graph.nodes[node_iri]["label"]
        print(f"    {label}: {centrality:.3f}")

    # PageRank
    print("\n  PageRank (top 5):")
    pagerank = nx.pagerank(nx_graph)
    sorted_pagerank = sorted(pagerank.items(), key=lambda x: x[1], reverse=True)
    for node_iri, score in sorted_pagerank[:5]:
        label = nx_graph.nodes[node_iri]["label"]
        print(f"    {label}: {score:.3f}")

    # Find shortest paths
    print("\n  Sample Shortest Paths:")
    try:
        # Find a path from a patient to a treatment
        patient_nodes = [
            n for n, d in nx_graph.nodes(data=True) if "Patient" in d.get("classes", [])
        ]
        treatment_nodes = [
            n
            for n, d in nx_graph.nodes(data=True)
            if "Treatment" in d.get("classes", [])
        ]

        if patient_nodes and treatment_nodes:
            patient = patient_nodes[0]
            treatment = treatment_nodes[0]

            if nx.has_path(nx_graph, patient, treatment):
                path = nx.shortest_path(nx_graph, patient, treatment)
                print(
                    f"    Path from {nx_graph.nodes[patient]['label']} to {nx_graph.nodes[treatment]['label']}:"
                )
                for i in range(len(path) - 1):
                    from_label = nx_graph.nodes[path[i]]["label"]
                    to_label = nx_graph.nodes[path[i + 1]]["label"]
                    edge_data = nx_graph.get_edge_data(path[i], path[i + 1])
                    prop = edge_data["property_label"]
                    print(f"      {from_label} --[{prop}]--> {to_label}")
            else:
                print("    No path found between sample patient and treatment")
    except Exception as e:
        print(f"    Could not compute path: {e}")

    # Connected components
    print("\n  Graph Connectivity:")
    if nx.is_strongly_connected(nx_graph):
        print("    Graph is strongly connected")
    else:
        num_components = nx.number_weakly_connected_components(nx_graph)
        print(f"    Graph has {num_components} weakly connected components")

        # Show component sizes
        components = sorted(
            nx.weakly_connected_components(nx_graph), key=len, reverse=True
        )
        print("    Component sizes:", [len(c) for c in components])

    # Convert with classes included
    print("\n2.3: Converting to NetworkX (including classes)...")
    nx_graph_classes = to_networkx(onto, strategy="include_classes")
    print(f"  - Nodes: {nx_graph_classes.number_of_nodes()}")
    print(f"  - Edges: {nx_graph_classes.number_of_edges()}")
    print(
        f"  - Added {nx_graph_classes.number_of_nodes() - nx_graph.number_of_nodes()} class nodes"
    )

    return nx_graph


def demonstrate_igraph_conversion(onto: owl2.Ontology) -> Optional[object]:
    """
    Convert ontology to igraph and perform various analyses.

    Parameters
    ----------
    onto : owl2.Ontology
        The medical ontology to convert.

    Returns
    -------
    ig.Graph or None
        The igraph Graph, or None if igraph is not available.
    """
    if not HAS_IGRAPH:
        print("\nSkipping igraph examples (not installed)")
        return None

    print("\n" + "=" * 80)
    print("STEP 3: igraph Conversion and Analysis")
    print("=" * 80)

    # Convert to igraph
    print("\n3.1: Converting to igraph...")
    ig_graph = to_igraph(onto, strategy="individuals_only")
    print(f"  - Vertices: {ig_graph.vcount()}")
    print(f"  - Edges: {ig_graph.ecount()}")
    print(f"  - Density: {ig_graph.density():.4f}")

    # Display vertex attributes
    print("\n  Sample vertex attributes:")
    for i, v in enumerate(ig_graph.vs[:3]):
        print(f"    {v['label']}:")
        print(f"      - Type: {v['type']}")
        print(f"      - Classes: {v['classes']}")

    # igraph Analysis
    print("\n3.2: Performing igraph Analysis...")

    # Degree distribution
    print("\n  Degree Distribution:")
    in_degrees = ig_graph.indegree()
    out_degrees = ig_graph.outdegree()
    print(f"    Average in-degree: {sum(in_degrees) / len(in_degrees):.2f}")
    print(f"    Average out-degree: {sum(out_degrees) / len(out_degrees):.2f}")

    # Centrality measures
    print("\n  Betweenness Centrality (top 5):")
    betweenness = ig_graph.betweenness()
    top_betweenness = sorted(enumerate(betweenness), key=lambda x: x[1], reverse=True)[
        :5
    ]
    for idx, score in top_betweenness:
        print(f"    {ig_graph.vs[idx]['label']}: {score:.3f}")

    print("\n  Closeness Centrality (top 5):")
    closeness = ig_graph.closeness(mode="all")
    top_closeness = sorted(enumerate(closeness), key=lambda x: x[1], reverse=True)[:5]
    for idx, score in top_closeness:
        print(f"    {ig_graph.vs[idx]['label']}: {score:.3f}")

    # Community detection
    print("\n  Community Detection (Leiden algorithm):")
    try:
        communities = ig_graph.community_leiden(objective_function="modularity")
        print(f"    Found {len(communities)} communities")
        print(f"    Modularity: {communities.modularity:.4f}")

        for i, community in enumerate(communities):
            members = [ig_graph.vs[idx]["label"] for idx in community]
            print(f"    Community {i + 1}: {', '.join(members)}")
    except Exception as e:
        print(f"    Community detection failed: {e}")

    # Clustering coefficient
    print("\n  Clustering:")
    try:
        transitivity = ig_graph.transitivity_undirected()
        print(f"    Global clustering coefficient: {transitivity:.4f}")
    except Exception as e:
        print(f"    Could not compute clustering: {e}")

    # Diameter
    print("\n  Graph Properties:")
    try:
        if ig_graph.is_connected(mode="weak"):
            diameter = ig_graph.diameter(directed=True)
            print(f"    Diameter: {diameter}")
        else:
            print("    Graph is not connected (no diameter)")
    except Exception as e:
        print(f"    Could not compute diameter: {e}")

    return ig_graph


def demonstrate_ista_graph_conversion(onto: owl2.Ontology):
    """
    Convert ontology to ista.graph and demonstrate operations.

    Parameters
    ----------
    onto : owl2.Ontology
        The medical ontology to convert.

    Returns
    -------
    ista.graph.Graph
        The ista graph.
    """
    print("\n" + "=" * 80)
    print("STEP 4: ista.graph Conversion and Operations")
    print("=" * 80)

    # Convert to ista.graph
    print("\n4.1: Converting to ista.graph...")
    ista_graph = to_ista_graph(onto, strategy="individuals_only")
    print(f"  - Nodes: {len(ista_graph.nodes)}")
    print(f"  - Edges: {len(ista_graph.edges)}")

    # Display node information
    print("\n  Sample nodes:")
    for i, node in enumerate(ista_graph.nodes[:3]):
        print(f"    {node.name}:")
        print(f"      - Class: {node.node_class}")
        print(f"      - Index: {node.node_idx}")
        print(f"      - Properties: {list(node.properties.keys())[:5]}")

    # Display edge information
    print("\n  Sample edges:")
    for i, edge in enumerate(ista_graph.edges[:5]):
        prop = edge.edge_properties.get("property_label", "unknown")
        print(f"    {edge.from_node.name} --[{prop}]--> {edge.to_node.name}")

    # Get adjacency matrix
    print("\n4.2: Computing adjacency matrix...")
    try:
        adj_matrix = ista_graph.get_adjacency(format="matrix")
        print(f"  - Shape: {adj_matrix.shape}")
        print(f"  - Non-zero entries: {(adj_matrix != 0).sum()}")
    except Exception as e:
        print(f"  - Could not compute adjacency matrix: {e}")

    return ista_graph


def demonstrate_round_trip(onto: owl2.Ontology):
    """
    Demonstrate round-trip conversion: ontology -> graph -> ontology.

    Parameters
    ----------
    onto : owl2.Ontology
        The original medical ontology.
    """
    print("\n" + "=" * 80)
    print("STEP 5: Round-Trip Testing")
    print("=" * 80)

    original_axiom_count = onto.get_axiom_count()
    original_individual_count = onto.get_individual_count()

    print(f"\nOriginal ontology:")
    print(f"  - Axioms: {original_axiom_count}")
    print(f"  - Individuals: {original_individual_count}")

    # NetworkX round-trip
    if HAS_NETWORKX:
        print("\n5.1: NetworkX Round-Trip...")
        nx_graph = to_networkx(onto, strategy="individuals_only")
        print(f"  - Converted to NetworkX: {nx_graph.number_of_nodes()} nodes")

        reconstructed_onto = from_networkx(
            nx_graph, "http://example.org/medical-reconstructed"
        )
        print(f"  - Reconstructed ontology:")
        print(f"    - Axioms: {reconstructed_onto.get_axiom_count()}")
        print(f"    - Individuals: {reconstructed_onto.get_individual_count()}")

        # Save reconstructed ontology
        output_file = "D:\\projects\\ista\\examples\\medical_reconstructed_nx.ofn"
        owl2.FunctionalSyntaxSerializer.serialize_to_file(
            reconstructed_onto, output_file
        )
        print(f"  - Saved to: {output_file}")

    # igraph round-trip
    if HAS_IGRAPH:
        print("\n5.2: igraph Round-Trip...")
        ig_graph = to_igraph(onto, strategy="individuals_only")
        print(f"  - Converted to igraph: {ig_graph.vcount()} vertices")

        reconstructed_onto = from_igraph(
            ig_graph, "http://example.org/medical-reconstructed"
        )
        print(f"  - Reconstructed ontology:")
        print(f"    - Axioms: {reconstructed_onto.get_axiom_count()}")
        print(f"    - Individuals: {reconstructed_onto.get_individual_count()}")

    # ista.graph round-trip
    print("\n5.3: ista.graph Round-Trip...")
    ista_graph = to_ista_graph(onto, strategy="individuals_only")
    print(f"  - Converted to ista.graph: {len(ista_graph.nodes)} nodes")

    reconstructed_onto = from_ista_graph(
        ista_graph, "http://example.org/medical-reconstructed"
    )
    print(f"  - Reconstructed ontology:")
    print(f"    - Axioms: {reconstructed_onto.get_axiom_count()}")
    print(f"    - Individuals: {reconstructed_onto.get_individual_count()}")

    # Save reconstructed ontology
    output_file = "D:\\projects\\ista\\examples\\medical_reconstructed_ista.ofn"
    owl2.FunctionalSyntaxSerializer.serialize_to_file(reconstructed_onto, output_file)
    print(f"  - Saved to: {output_file}")


def visualize_graph(nx_graph, title: str = "Medical Knowledge Graph"):
    """
    Visualize the NetworkX graph using matplotlib.

    Parameters
    ----------
    nx_graph : nx.DiGraph
        The NetworkX graph to visualize.
    title : str
        Title for the plot.
    """
    if not HAS_MATPLOTLIB or not HAS_NETWORKX:
        print("\nSkipping visualization (matplotlib or NetworkX not available)")
        return

    print("\n" + "=" * 80)
    print("STEP 6: Visualization")
    print("=" * 80)

    print(f"\nCreating visualization: {title}")

    # Create figure
    plt.figure(figsize=(14, 10))

    # Color nodes by class
    node_colors = []
    for node in nx_graph.nodes():
        classes = nx_graph.nodes[node].get("classes", [])
        if any("Patient" in c for c in classes):
            node_colors.append("#FF6B6B")  # Red for patients
        elif any("Disease" in c for c in classes):
            node_colors.append("#4ECDC4")  # Teal for diseases
        elif any("Treatment" in c for c in classes):
            node_colors.append("#95E1D3")  # Light green for treatments
        elif any("Symptom" in c for c in classes):
            node_colors.append("#FFE66D")  # Yellow for symptoms
        else:
            node_colors.append("#C0C0C0")  # Gray for others

    # Create layout
    pos = nx.spring_layout(nx_graph, k=2, iterations=50, seed=42)

    # Draw nodes
    nx.draw_networkx_nodes(
        nx_graph, pos, node_color=node_colors, node_size=1500, alpha=0.9
    )

    # Draw edges with colors based on property type
    edge_colors = []
    for u, v, data in nx_graph.edges(data=True):
        prop_label = data.get("property_label", "")
        if "diagnoses" in prop_label:
            edge_colors.append("#FF0000")
        elif "treats" in prop_label:
            edge_colors.append("#00FF00")
        elif "causes" in prop_label:
            edge_colors.append("#FFA500")
        elif "exhibits" in prop_label:
            edge_colors.append("#0000FF")
        else:
            edge_colors.append("#808080")

    nx.draw_networkx_edges(
        nx_graph,
        pos,
        edge_color=edge_colors,
        arrows=True,
        arrowsize=20,
        width=2,
        alpha=0.6,
        arrowstyle="->",
        connectionstyle="arc3,rad=0.1",
    )

    # Draw labels
    labels = {node: nx_graph.nodes[node]["label"] for node in nx_graph.nodes()}
    nx.draw_networkx_labels(nx_graph, pos, labels, font_size=10, font_weight="bold")

    # Draw edge labels
    edge_labels = {
        (u, v): data["property_label"] for u, v, data in nx_graph.edges(data=True)
    }
    nx.draw_networkx_edge_labels(nx_graph, pos, edge_labels, font_size=8)

    plt.title(title, fontsize=16, fontweight="bold")
    plt.axis("off")
    plt.tight_layout()

    # Save figure
    output_file = "D:\\projects\\ista\\examples\\medical_graph_visualization.png"
    plt.savefig(output_file, dpi=300, bbox_inches="tight")
    print(f"  - Saved visualization to: {output_file}")

    # Show legend
    from matplotlib.patches import Patch

    legend_elements = [
        Patch(facecolor="#FF6B6B", label="Patient"),
        Patch(facecolor="#4ECDC4", label="Disease"),
        Patch(facecolor="#95E1D3", label="Treatment"),
        Patch(facecolor="#FFE66D", label="Symptom"),
    ]
    plt.legend(handles=legend_elements, loc="upper left", fontsize=10)

    print("  - Display the plot with plt.show() if needed")


def main():
    """Main entry point for the example."""
    print("\n" + "=" * 80)
    print("ONTOLOGY-TO-GRAPH CONVERSION: Complete Workflow Example")
    print("=" * 80)
    print("\nThis example demonstrates converting OWL2 ontologies to various graph")
    print("representations and performing analysis on them.")

    # Step 1: Create ontology
    onto = create_medical_ontology()

    # Save original ontology
    output_file = "D:\\projects\\ista\\examples\\medical_ontology.ofn"
    owl2.FunctionalSyntaxSerializer.serialize_to_file(onto, output_file)
    print(f"\nSaved original ontology to: {output_file}")

    # Step 2: NetworkX conversion and analysis
    nx_graph = demonstrate_networkx_conversion(onto)

    # Step 3: igraph conversion and analysis
    ig_graph = demonstrate_igraph_conversion(onto)

    # Step 4: ista.graph conversion
    ista_graph = demonstrate_ista_graph_conversion(onto)

    # Step 5: Round-trip testing
    demonstrate_round_trip(onto)

    # Step 6: Visualization
    if nx_graph is not None:
        visualize_graph(nx_graph, "Medical Knowledge Graph - Complete View")

    # Final summary
    print("\n" + "=" * 80)
    print("EXAMPLE COMPLETED SUCCESSFULLY")
    print("=" * 80)
    print("\nKey Takeaways:")
    print("  1. OWL2 ontologies can be converted to multiple graph formats")
    print("  2. Each format (NetworkX, igraph, ista.graph) has its strengths")
    print("  3. Graph analysis reveals network structure and important nodes")
    print("  4. Round-trip conversion preserves ontology structure")
    print("  5. Visualization helps understand knowledge graph relationships")
    print("\nGenerated Files:")
    print("  - D:\\projects\\ista\\examples\\medical_ontology.ofn")
    print("  - D:\\projects\\ista\\examples\\medical_reconstructed_nx.ofn")
    print("  - D:\\projects\\ista\\examples\\medical_reconstructed_ista.ofn")
    if HAS_MATPLOTLIB:
        print("  - D:\\projects\\ista\\examples\\medical_graph_visualization.png")
    print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
