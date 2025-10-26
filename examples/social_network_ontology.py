#!/usr/bin/env python3
"""
Social Network Ontology Example

This example demonstrates creating and analyzing a social network represented
as an OWL2 ontology, then converting it to graph formats for network analysis.

Domain: Social Network
- Individuals: People with names, ages, locations
- Object properties: knows, follows, friendOf, worksAt, studiedAt
- Data properties: name, age, location, email, occupation

Features demonstrated:
1. Creating a social network ontology
2. Converting to graph representations
3. Finding influencers (high centrality nodes)
4. Community detection
5. Friend recommendation (path finding)
6. Network statistics
"""

import sys
from typing import List, Tuple, Dict

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
from ista.converters import to_networkx, to_ista_graph

# Try to import optional dependencies
try:
    import networkx as nx

    HAS_NETWORKX = True
except ImportError:
    HAS_NETWORKX = False
    print("WARNING: NetworkX not available. Install with: pip install networkx")

try:
    import igraph as ig
    from ista.converters import to_igraph

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


def create_social_network_ontology() -> owl2.Ontology:
    """
    Create a social network ontology with people, relationships, and organizations.

    Returns
    -------
    owl2.Ontology
        A populated social network ontology.
    """
    print("\n" + "=" * 80)
    print("CREATING SOCIAL NETWORK ONTOLOGY")
    print("=" * 80)

    # Create ontology
    ontology_iri = "http://example.org/socialnet"
    onto = owl2.Ontology(owl2.IRI(ontology_iri))
    onto.register_prefix("sn", ontology_iri + "#")

    # Helper function
    def sn_iri(name: str) -> owl2.IRI:
        return owl2.IRI("sn", name, ontology_iri + "#")

    # Define Classes
    print("\nDefining classes...")
    classes = {
        "Person": owl2.Class(sn_iri("Person")),
        "Organization": owl2.Class(sn_iri("Organization")),
        "University": owl2.Class(sn_iri("University")),
        "Company": owl2.Class(sn_iri("Company")),
    }

    for name, cls in classes.items():
        onto.add_axiom(owl2.Declaration(cls))
        print(f"  - {name}")

    # Add class hierarchy
    onto.add_axiom(
        owl2.SubClassOf(
            owl2.NamedClass(classes["University"]),
            owl2.NamedClass(classes["Organization"]),
        )
    )
    onto.add_axiom(
        owl2.SubClassOf(
            owl2.NamedClass(classes["Company"]),
            owl2.NamedClass(classes["Organization"]),
        )
    )
    print("  - University subClassOf Organization")
    print("  - Company subClassOf Organization")

    # Define Object Properties
    print("\nDefining object properties...")
    object_props = {
        "knows": owl2.ObjectProperty(sn_iri("knows")),
        "follows": owl2.ObjectProperty(sn_iri("follows")),
        "friendOf": owl2.ObjectProperty(sn_iri("friendOf")),
        "worksAt": owl2.ObjectProperty(sn_iri("worksAt")),
        "studiedAt": owl2.ObjectProperty(sn_iri("studiedAt")),
        "collaboratesWith": owl2.ObjectProperty(sn_iri("collaboratesWith")),
    }

    for name, prop in object_props.items():
        onto.add_axiom(owl2.Declaration(prop))
        print(f"  - {name}")

    # Define Data Properties
    print("\nDefining data properties...")
    data_props = {
        "name": owl2.DataProperty(sn_iri("name")),
        "age": owl2.DataProperty(sn_iri("age")),
        "location": owl2.DataProperty(sn_iri("location")),
        "email": owl2.DataProperty(sn_iri("email")),
        "occupation": owl2.DataProperty(sn_iri("occupation")),
        "followers_count": owl2.DataProperty(sn_iri("followers_count")),
    }

    for name, prop in data_props.items():
        onto.add_axiom(owl2.Declaration(prop))
        print(f"  - {name}")

    # Create People
    print("\nCreating people...")
    people_data = [
        ("Alice", 28, "New York", "alice@example.com", "Software Engineer"),
        ("Bob", 32, "San Francisco", "bob@example.com", "Data Scientist"),
        ("Carol", 25, "Boston", "carol@example.com", "Product Manager"),
        ("David", 35, "Seattle", "david@example.com", "DevOps Engineer"),
        ("Eve", 29, "Austin", "eve@example.com", "UX Designer"),
        ("Frank", 31, "Chicago", "frank@example.com", "Backend Developer"),
        ("Grace", 27, "Portland", "grace@example.com", "Frontend Developer"),
        ("Henry", 33, "Denver", "henry@example.com", "ML Engineer"),
        ("Iris", 26, "Miami", "iris@example.com", "Technical Writer"),
        ("Jack", 30, "New York", "jack@example.com", "Solutions Architect"),
    ]

    people = {}
    for name, age, location, email, occupation in people_data:
        individual = owl2.NamedIndividual(sn_iri(name))
        people[name] = individual

        onto.add_axiom(owl2.Declaration(individual))
        onto.add_axiom(owl2.ClassAssertion(classes["Person"], individual))

        # Add data properties
        onto.add_axiom(
            owl2.DataPropertyAssertion(
                data_props["name"], individual, owl2.Literal(name)
            )
        )
        onto.add_axiom(
            owl2.DataPropertyAssertion(
                data_props["age"],
                individual,
                owl2.Literal(
                    str(age), owl2.IRI("http://www.w3.org/2001/XMLSchema#integer")
                ),
            )
        )
        onto.add_axiom(
            owl2.DataPropertyAssertion(
                data_props["location"], individual, owl2.Literal(location)
            )
        )
        onto.add_axiom(
            owl2.DataPropertyAssertion(
                data_props["email"], individual, owl2.Literal(email)
            )
        )
        onto.add_axiom(
            owl2.DataPropertyAssertion(
                data_props["occupation"], individual, owl2.Literal(occupation)
            )
        )

        print(f"  - {name} ({age}, {location}, {occupation})")

    # Create Organizations
    print("\nCreating organizations...")
    orgs_data = [
        ("TechCorp", "Company", "San Francisco"),
        ("DataInc", "Company", "New York"),
        ("MIT", "University", "Cambridge"),
        ("Stanford", "University", "Palo Alto"),
    ]

    orgs = {}
    for name, org_type, location in orgs_data:
        individual = owl2.NamedIndividual(sn_iri(name))
        orgs[name] = individual

        onto.add_axiom(owl2.Declaration(individual))
        onto.add_axiom(owl2.ClassAssertion(classes[org_type], individual))

        onto.add_axiom(
            owl2.DataPropertyAssertion(
                data_props["name"], individual, owl2.Literal(name)
            )
        )
        onto.add_axiom(
            owl2.DataPropertyAssertion(
                data_props["location"], individual, owl2.Literal(location)
            )
        )

        print(f"  - {name} ({org_type}, {location})")

    # Add social relationships
    print("\nAdding social relationships...")

    # Friendship network (mutual relationships)
    friendships = [
        ("Alice", "Bob"),
        ("Alice", "Carol"),
        ("Bob", "David"),
        ("Carol", "Eve"),
        ("David", "Frank"),
        ("Eve", "Grace"),
        ("Frank", "Henry"),
        ("Grace", "Alice"),  # Creates a cycle
        ("Henry", "Bob"),
        ("Iris", "Jack"),
        ("Jack", "Alice"),
        ("Carol", "David"),
        ("Eve", "Frank"),
    ]

    for person1, person2 in friendships:
        # friendOf is symmetric
        onto.add_axiom(
            owl2.ObjectPropertyAssertion(
                object_props["friendOf"], people[person1], people[person2]
            )
        )
        onto.add_axiom(
            owl2.ObjectPropertyAssertion(
                object_props["friendOf"], people[person2], people[person1]
            )
        )
        print(f"  - {person1} friendOf {person2} (mutual)")

    # Knows relationships (not necessarily mutual)
    knows_relationships = [
        ("Alice", "David"),
        ("Bob", "Eve"),
        ("Carol", "Frank"),
        ("Henry", "Iris"),
        ("Jack", "Bob"),
        ("Grace", "Henry"),
    ]

    for person1, person2 in knows_relationships:
        onto.add_axiom(
            owl2.ObjectPropertyAssertion(
                object_props["knows"], people[person1], people[person2]
            )
        )
        print(f"  - {person1} knows {person2}")

    # Follows relationships (directed, like social media)
    follows_relationships = [
        ("Alice", "Bob"),
        ("Alice", "Carol"),
        ("Bob", "Alice"),
        ("Carol", "Alice"),
        ("David", "Alice"),
        ("Eve", "Alice"),
        ("Frank", "Bob"),
        ("Grace", "Carol"),
        ("Henry", "Bob"),
        ("Iris", "Alice"),
        ("Jack", "Alice"),
        ("Jack", "Bob"),
    ]

    for person1, person2 in follows_relationships:
        onto.add_axiom(
            owl2.ObjectPropertyAssertion(
                object_props["follows"], people[person1], people[person2]
            )
        )

    # Count followers for each person
    follower_counts = {}
    for person1, person2 in follows_relationships:
        follower_counts[person2] = follower_counts.get(person2, 0) + 1

    for person, count in follower_counts.items():
        onto.add_axiom(
            owl2.DataPropertyAssertion(
                data_props["followers_count"],
                people[person],
                owl2.Literal(
                    str(count), owl2.IRI("http://www.w3.org/2001/XMLSchema#integer")
                ),
            )
        )

    print(f"  - Added {len(follows_relationships)} follow relationships")

    # Work and study relationships
    work_study = [
        ("Alice", "worksAt", "TechCorp"),
        ("Bob", "worksAt", "DataInc"),
        ("Carol", "worksAt", "TechCorp"),
        ("David", "worksAt", "TechCorp"),
        ("Eve", "worksAt", "DataInc"),
        ("Frank", "worksAt", "TechCorp"),
        ("Grace", "worksAt", "DataInc"),
        ("Henry", "worksAt", "TechCorp"),
        ("Alice", "studiedAt", "MIT"),
        ("Bob", "studiedAt", "Stanford"),
        ("Carol", "studiedAt", "MIT"),
        ("David", "studiedAt", "Stanford"),
        ("Eve", "studiedAt", "MIT"),
    ]

    print("\nAdding organizational affiliations...")
    for person, relation, org in work_study:
        onto.add_axiom(
            owl2.ObjectPropertyAssertion(
                object_props[relation], people[person], orgs[org]
            )
        )
        print(f"  - {person} {relation} {org}")

    # Collaboration relationships
    print("\nAdding collaboration relationships...")
    collaborations = [
        ("Alice", "Carol"),
        ("Alice", "David"),
        ("Bob", "Eve"),
        ("Frank", "Henry"),
    ]

    for person1, person2 in collaborations:
        onto.add_axiom(
            owl2.ObjectPropertyAssertion(
                object_props["collaboratesWith"], people[person1], people[person2]
            )
        )
        onto.add_axiom(
            owl2.ObjectPropertyAssertion(
                object_props["collaboratesWith"], people[person2], people[person1]
            )
        )
        print(f"  - {person1} collaboratesWith {person2}")

    # Print statistics
    print(f"\nOntology Statistics:")
    print(f"  - Total axioms: {onto.get_axiom_count()}")
    print(f"  - Classes: {onto.get_class_count()}")
    print(f"  - Object properties: {onto.get_object_property_count()}")
    print(f"  - Data properties: {onto.get_data_property_count()}")
    print(f"  - Individuals: {onto.get_individual_count()}")

    return onto


def find_influencers(nx_graph) -> List[Tuple[str, float]]:
    """
    Find influential people in the social network using centrality measures.

    Parameters
    ----------
    nx_graph : nx.DiGraph
        The social network graph.

    Returns
    -------
    List[Tuple[str, float]]
        List of (name, score) tuples for top influencers.
    """
    print("\n" + "=" * 80)
    print("FINDING INFLUENCERS")
    print("=" * 80)

    # Filter to only Person nodes
    person_nodes = [
        n for n, d in nx_graph.nodes(data=True) if "Person" in str(d.get("classes", []))
    ]
    person_graph = nx_graph.subgraph(person_nodes).copy()

    influencers = {}

    # Degree centrality (number of connections)
    print("\n1. Degree Centrality (most connected):")
    degree_cent = nx.degree_centrality(person_graph)
    sorted_degree = sorted(degree_cent.items(), key=lambda x: x[1], reverse=True)[:5]
    for node_iri, score in sorted_degree:
        name = nx_graph.nodes[node_iri].get("data_name", "Unknown")
        print(f"  - {name}: {score:.3f}")
        influencers[name] = influencers.get(name, 0) + score

    # Betweenness centrality (bridge between communities)
    print("\n2. Betweenness Centrality (network bridges):")
    betweenness = nx.betweenness_centrality(person_graph)
    sorted_betweenness = sorted(betweenness.items(), key=lambda x: x[1], reverse=True)[
        :5
    ]
    for node_iri, score in sorted_betweenness:
        name = nx_graph.nodes[node_iri].get("data_name", "Unknown")
        print(f"  - {name}: {score:.3f}")
        influencers[name] = influencers.get(name, 0) + score

    # PageRank (importance based on connections)
    print("\n3. PageRank (overall importance):")
    pagerank = nx.pagerank(person_graph)
    sorted_pagerank = sorted(pagerank.items(), key=lambda x: x[1], reverse=True)[:5]
    for node_iri, score in sorted_pagerank:
        name = nx_graph.nodes[node_iri].get("data_name", "Unknown")
        print(f"  - {name}: {score:.3f}")
        influencers[name] = influencers.get(name, 0) + score

    # Eigenvector centrality (connected to other influential people)
    print("\n4. Eigenvector Centrality (influential connections):")
    try:
        eigenvector = nx.eigenvector_centrality(person_graph, max_iter=1000)
        sorted_eigenvector = sorted(
            eigenvector.items(), key=lambda x: x[1], reverse=True
        )[:5]
        for node_iri, score in sorted_eigenvector:
            name = nx_graph.nodes[node_iri].get("data_name", "Unknown")
            print(f"  - {name}: {score:.3f}")
            influencers[name] = influencers.get(name, 0) + score
    except nx.PowerIterationFailedConvergence:
        print("  - Could not compute (convergence failed)")

    # Combine scores to get overall influencers
    print("\n5. Overall Top Influencers (combined scores):")
    top_influencers = sorted(influencers.items(), key=lambda x: x[1], reverse=True)[:5]
    for name, score in top_influencers:
        print(f"  - {name}: {score:.3f}")

    return top_influencers


def detect_communities(graph_obj):
    """
    Detect communities in the social network.

    Parameters
    ----------
    graph_obj : nx.DiGraph or ig.Graph
        The social network graph.
    """
    print("\n" + "=" * 80)
    print("DETECTING COMMUNITIES")
    print("=" * 80)

    if HAS_NETWORKX and isinstance(graph_obj, nx.DiGraph):
        print("\nUsing NetworkX algorithms...")

        # Convert to undirected for community detection
        person_nodes = [
            n
            for n, d in graph_obj.nodes(data=True)
            if "Person" in str(d.get("classes", []))
        ]
        person_graph = graph_obj.subgraph(person_nodes).copy()
        undirected = person_graph.to_undirected()

        # Greedy modularity communities
        print("\n1. Greedy Modularity Communities:")
        communities = nx.community.greedy_modularity_communities(undirected)
        for i, community in enumerate(communities):
            members = [
                graph_obj.nodes[n].get("data_name", "Unknown") for n in community
            ]
            print(f"  Community {i + 1}: {', '.join(members)}")

        # Louvain communities (if available)
        try:
            print("\n2. Louvain Communities:")
            louvain_communities = nx.community.louvain_communities(undirected)
            for i, community in enumerate(louvain_communities):
                members = [
                    graph_obj.nodes[n].get("data_name", "Unknown") for n in community
                ]
                print(f"  Community {i + 1}: {', '.join(members)}")
        except AttributeError:
            print("  Louvain method not available in this NetworkX version")

    elif HAS_IGRAPH and hasattr(graph_obj, "vcount"):
        print("\nUsing igraph algorithms...")

        # Filter to Person vertices
        person_indices = [
            i for i, v in enumerate(graph_obj.vs) if "Person" in str(v["classes"])
        ]
        person_graph = graph_obj.subgraph(person_indices)

        # Leiden algorithm
        print("\n1. Leiden Community Detection:")
        try:
            communities = person_graph.community_leiden(objective_function="modularity")
            print(f"  Found {len(communities)} communities")
            print(f"  Modularity: {communities.modularity:.4f}")
            for i, community in enumerate(communities):
                members = [person_graph.vs[idx]["data_name"] for idx in community]
                print(f"  Community {i + 1}: {', '.join(members)}")
        except Exception as e:
            print(f"  Could not compute: {e}")

        # Infomap algorithm
        print("\n2. Infomap Community Detection:")
        try:
            communities = person_graph.community_infomap()
            print(f"  Found {len(communities)} communities")
            for i, community in enumerate(communities):
                members = [person_graph.vs[idx]["data_name"] for idx in community]
                print(f"  Community {i + 1}: {', '.join(members)}")
        except Exception as e:
            print(f"  Could not compute: {e}")


def recommend_friends(nx_graph, person_name: str):
    """
    Recommend potential friends using network analysis.

    Parameters
    ----------
    nx_graph : nx.DiGraph
        The social network graph.
    person_name : str
        Name of the person to recommend friends for.
    """
    print("\n" + "=" * 80)
    print(f"FRIEND RECOMMENDATIONS FOR {person_name}")
    print("=" * 80)

    # Find the person's node
    person_node = None
    for node, data in nx_graph.nodes(data=True):
        if data.get("data_name") == person_name:
            person_node = node
            break

    if not person_node:
        print(f"  Could not find {person_name}")
        return

    # Get current friends
    friends = set()
    for u, v, data in nx_graph.out_edges(person_node, data=True):
        if "friend" in data.get("property_label", "").lower():
            friends.add(v)

    print(f"\nCurrent friends ({len(friends)}):")
    for friend in friends:
        name = nx_graph.nodes[friend].get("data_name", "Unknown")
        print(f"  - {name}")

    # Strategy 1: Friends of friends
    print("\n1. Friends of Friends:")
    fof_scores = {}
    for friend in friends:
        for u, v, data in nx_graph.out_edges(friend, data=True):
            if "friend" in data.get("property_label", "").lower():
                if v != person_node and v not in friends:
                    name = nx_graph.nodes[v].get("data_name", "Unknown")
                    fof_scores[name] = fof_scores.get(name, 0) + 1

    if fof_scores:
        sorted_fof = sorted(fof_scores.items(), key=lambda x: x[1], reverse=True)[:5]
        for name, count in sorted_fof:
            print(f"  - {name} ({count} mutual friends)")
    else:
        print("  - No recommendations found")

    # Strategy 2: Same organization
    print("\n2. Same Organization:")
    person_orgs = set()
    for u, v, data in nx_graph.out_edges(person_node, data=True):
        if data.get("property_label") in ["worksAt", "studiedAt"]:
            person_orgs.add(v)

    org_colleagues = {}
    for org in person_orgs:
        org_name = nx_graph.nodes[org].get("data_name", "Unknown")
        for u, v, data in nx_graph.in_edges(org, data=True):
            if u != person_node and u not in friends:
                colleague_name = nx_graph.nodes[u].get("data_name", "Unknown")
                if "Person" in str(nx_graph.nodes[u].get("classes", [])):
                    if colleague_name not in org_colleagues:
                        org_colleagues[colleague_name] = []
                    org_colleagues[colleague_name].append(org_name)

    if org_colleagues:
        for name, orgs in list(org_colleagues.items())[:5]:
            print(f"  - {name} (shares: {', '.join(orgs)})")
    else:
        print("  - No recommendations found")

    # Strategy 3: Shortest path to interesting people
    print("\n3. Shortest Paths to Non-Friends:")
    person_nodes = [
        n for n, d in nx_graph.nodes(data=True) if "Person" in str(d.get("classes", []))
    ]

    paths = []
    for target in person_nodes:
        if target != person_node and target not in friends:
            try:
                if nx.has_path(nx_graph, person_node, target):
                    path = nx.shortest_path(nx_graph, person_node, target)
                    if len(path) <= 4:  # Within 3 hops
                        target_name = nx_graph.nodes[target].get("data_name", "Unknown")
                        paths.append((target_name, len(path) - 1))
            except:
                pass

    if paths:
        sorted_paths = sorted(paths, key=lambda x: x[1])[:5]
        for name, distance in sorted_paths:
            print(f"  - {name} ({distance} hops away)")
    else:
        print("  - No paths found")


def visualize_social_network(nx_graph):
    """
    Visualize the social network.

    Parameters
    ----------
    nx_graph : nx.DiGraph
        The social network graph.
    """
    if not HAS_MATPLOTLIB or not HAS_NETWORKX:
        print("\nSkipping visualization (matplotlib or NetworkX not available)")
        return

    print("\n" + "=" * 80)
    print("VISUALIZING SOCIAL NETWORK")
    print("=" * 80)

    # Filter to people only
    person_nodes = [
        n for n, d in nx_graph.nodes(data=True) if "Person" in str(d.get("classes", []))
    ]
    person_graph = nx_graph.subgraph(person_nodes).copy()

    # Create figure
    plt.figure(figsize=(16, 12))

    # Create layout
    pos = nx.spring_layout(person_graph, k=3, iterations=50, seed=42)

    # Color nodes by location
    locations = set()
    for node in person_graph.nodes():
        loc = person_graph.nodes[node].get("data_location", "Unknown")
        locations.add(loc)

    location_colors = {}
    colors = plt.cm.Set3(range(len(locations)))
    for i, loc in enumerate(locations):
        location_colors[loc] = colors[i]

    node_colors = []
    for node in person_graph.nodes():
        loc = person_graph.nodes[node].get("data_location", "Unknown")
        node_colors.append(location_colors[loc])

    # Calculate node sizes based on followers
    node_sizes = []
    for node in person_graph.nodes():
        followers = person_graph.nodes[node].get("data_followers_count", 1)
        try:
            size = 500 + int(followers) * 200
        except:
            size = 500
        node_sizes.append(size)

    # Draw nodes
    nx.draw_networkx_nodes(
        person_graph,
        pos,
        node_color=node_colors,
        node_size=node_sizes,
        alpha=0.9,
        edgecolors="black",
        linewidths=2,
    )

    # Separate edges by type
    friend_edges = []
    knows_edges = []
    follows_edges = []
    collab_edges = []

    for u, v, data in person_graph.edges(data=True):
        prop = data.get("property_label", "")
        if "friend" in prop.lower():
            friend_edges.append((u, v))
        elif "knows" in prop.lower():
            knows_edges.append((u, v))
        elif "follows" in prop.lower():
            follows_edges.append((u, v))
        elif "collaborates" in prop.lower():
            collab_edges.append((u, v))

    # Draw edges
    if friend_edges:
        nx.draw_networkx_edges(
            person_graph,
            pos,
            edgelist=friend_edges,
            edge_color="#FF6B6B",
            width=3,
            alpha=0.7,
            arrows=True,
            arrowsize=15,
            arrowstyle="->",
        )
    if knows_edges:
        nx.draw_networkx_edges(
            person_graph,
            pos,
            edgelist=knows_edges,
            edge_color="#4ECDC4",
            width=2,
            alpha=0.5,
            arrows=True,
            arrowsize=12,
            arrowstyle="->",
        )
    if follows_edges:
        nx.draw_networkx_edges(
            person_graph,
            pos,
            edgelist=follows_edges,
            edge_color="#95E1D3",
            width=1.5,
            alpha=0.4,
            arrows=True,
            arrowsize=10,
            arrowstyle="->",
        )
    if collab_edges:
        nx.draw_networkx_edges(
            person_graph,
            pos,
            edgelist=collab_edges,
            edge_color="#FFE66D",
            width=2.5,
            alpha=0.6,
            arrows=True,
            arrowsize=13,
            arrowstyle="->",
        )

    # Draw labels
    labels = {
        node: person_graph.nodes[node].get("data_name", "Unknown")
        for node in person_graph.nodes()
    }
    nx.draw_networkx_labels(person_graph, pos, labels, font_size=11, font_weight="bold")

    plt.title("Social Network Visualization", fontsize=18, fontweight="bold", pad=20)
    plt.axis("off")
    plt.tight_layout()

    # Add legends
    from matplotlib.patches import Patch
    from matplotlib.lines import Line2D

    # Location legend
    legend_elements = [
        Patch(facecolor=location_colors[loc], label=loc, edgecolor="black")
        for loc in sorted(locations)
    ]
    legend1 = plt.legend(
        handles=legend_elements, loc="upper left", title="Locations", fontsize=9
    )
    plt.gca().add_artist(legend1)

    # Relationship legend
    rel_elements = [
        Line2D([0], [0], color="#FF6B6B", linewidth=3, label="friendOf"),
        Line2D([0], [0], color="#4ECDC4", linewidth=2, label="knows"),
        Line2D([0], [0], color="#95E1D3", linewidth=1.5, label="follows"),
        Line2D([0], [0], color="#FFE66D", linewidth=2.5, label="collaboratesWith"),
    ]
    plt.legend(
        handles=rel_elements, loc="upper right", title="Relationships", fontsize=9
    )

    # Save
    output_file = "D:\\projects\\ista\\examples\\social_network_visualization.png"
    plt.savefig(output_file, dpi=300, bbox_inches="tight")
    print(f"\n  - Saved to: {output_file}")


def main():
    """Main entry point."""
    print("\n" + "=" * 80)
    print("SOCIAL NETWORK ONTOLOGY EXAMPLE")
    print("=" * 80)

    # Create ontology
    onto = create_social_network_ontology()

    # Save ontology
    output_file = "D:\\projects\\ista\\examples\\social_network.ofn"
    owl2.FunctionalSyntaxSerializer.serialize_to_file(onto, output_file)
    print(f"\nSaved ontology to: {output_file}")

    # Convert to NetworkX
    if HAS_NETWORKX:
        print("\n" + "=" * 80)
        print("CONVERTING TO NETWORKX")
        print("=" * 80)
        nx_graph = to_networkx(onto, strategy="individuals_only")
        print(f"  - Nodes: {nx_graph.number_of_nodes()}")
        print(f"  - Edges: {nx_graph.number_of_edges()}")

        # Analyze
        find_influencers(nx_graph)
        detect_communities(nx_graph)
        recommend_friends(nx_graph, "Alice")
        visualize_social_network(nx_graph)

    # Convert to igraph
    if HAS_IGRAPH:
        print("\n" + "=" * 80)
        print("CONVERTING TO IGRAPH")
        print("=" * 80)
        ig_graph = to_igraph(onto, strategy="individuals_only")
        print(f"  - Vertices: {ig_graph.vcount()}")
        print(f"  - Edges: {ig_graph.ecount()}")

        detect_communities(ig_graph)

    # Summary
    print("\n" + "=" * 80)
    print("EXAMPLE COMPLETED")
    print("=" * 80)
    print("\nKey Findings:")
    print("  1. Identified influential members of the social network")
    print("  2. Detected natural communities within the network")
    print("  3. Generated friend recommendations using graph structure")
    print("  4. Visualized the social network with different relationship types")
    print("\nGenerated Files:")
    print("  - D:\\projects\\ista\\examples\\social_network.ofn")
    if HAS_MATPLOTLIB:
        print("  - D:\\projects\\ista\\examples\\social_network_visualization.png")
    print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
