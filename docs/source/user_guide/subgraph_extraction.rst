Subgraph Extraction
===================

Subgraph extraction enables working with focused portions of large ontologies by extracting
relevant entities and axioms based on specific criteria. This is essential for performance,
analysis, and visualization of complex knowledge graphs.

Overview
--------

Why extract subgraphs?

- **Performance**: Work with manageable portions of large ontologies
- **Focus**: Concentrate on specific domains or concepts
- **Visualization**: Create comprehensible visualizations
- **Analysis**: Perform targeted analysis on relevant portions
- **Export**: Generate domain-specific knowledge bases

The OntologyFilter Class
-------------------------

The ``OntologyFilter`` class provides the main interface for subgraph extraction.

Basic Usage
~~~~~~~~~~~

.. code-block:: python

    from ista.owl2 import OntologyFilter, FunctionalSyntaxParser

    # Load ontology
    parser = FunctionalSyntaxParser()
    ont = parser.parse("large_ontology.ofn")

    # Create filter
    filter_obj = OntologyFilter(ont)

    # Extract subgraph
    seed_iri = IRI("http://example.org/AlzheimersDisease")
    result = filter_obj.extract_neighborhood(seed_iri, depth=2)

    # Get extracted ontology
    subgraph_ont = result.get_ontology()
    print(f"Original axioms: {ont.get_axiom_count()}")
    print(f"Extracted axioms: {subgraph_ont.get_axiom_count()}")

Neighborhood Extraction
-----------------------

Extract entities within a certain distance from a seed entity.

Basic Neighborhood
~~~~~~~~~~~~~~~~~~

.. code-block:: python

    # Extract 2-hop neighborhood
    result = filter_obj.extract_neighborhood(
        seed_iri=seed_iri,
        depth=2
    )

Directional Extraction
~~~~~~~~~~~~~~~~~~~~~~

Control which directions to follow:

.. code-block:: python

    # Only follow superclass relationships
    result = filter_obj.extract_neighborhood(
        seed_iri=seed_iri,
        depth=3,
        include_superclasses=True,
        include_subclasses=False,
        include_properties=False
    )

    # Only follow subclass relationships (get entire subtree)
    result = filter_obj.extract_neighborhood(
        seed_iri=seed_iri,
        depth=10,  # Large depth to get entire subtree
        include_superclasses=False,
        include_subclasses=True,
        include_properties=False
    )

    # Include related properties and individuals
    result = filter_obj.extract_neighborhood(
        seed_iri=seed_iri,
        depth=2,
        include_superclasses=True,
        include_subclasses=True,
        include_properties=True,
        include_individuals=True
    )

Property-Specific Extraction
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Follow only specific properties:

.. code-block:: python

    # Only follow certain relationships
    part_of = IRI("http://example.org/partOf")
    has_symptom = IRI("http://example.org/hasSymptom")

    result = filter_obj.extract_neighborhood(
        seed_iri=seed_iri,
        depth=2,
        property_iris=[part_of, has_symptom]
    )

Multiple Seed Extraction
~~~~~~~~~~~~~~~~~~~~~~~~

Extract neighborhoods around multiple seed entities:

.. code-block:: python

    seed_iris = [
        IRI("http://example.org/AlzheimersDisease"),
        IRI("http://example.org/ParkinsonsDisease"),
        IRI("http://example.org/HuntingtonsDisease")
    ]

    # Extract combined neighborhood
    results = []
    for seed in seed_iris:
        result = filter_obj.extract_neighborhood(seed, depth=2)
        results.append(result)

    # Merge results
    combined_ont = merge_filter_results(results)

Criteria-Based Extraction
--------------------------

Extract based on flexible filtering criteria.

FilterCriteria Class
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from ista.owl2 import FilterCriteria

    # Create criteria
    criteria = FilterCriteria()

    # Add IRI pattern (regex)
    criteria.add_iri_pattern(".*Disease.*")
    criteria.add_iri_pattern(".*Symptom.*")

    # Add specific IRIs
    criteria.add_specific_iri(IRI("http://example.org/Protein"))

    # Add entity type filter
    criteria.set_entity_types(['CLASS', 'OBJECT_PROPERTY'])

    # Extract
    result = filter_obj.extract_by_criteria(criteria)

Pattern Matching
~~~~~~~~~~~~~~~~

Use regular expressions for flexible matching:

.. code-block:: python

    # Match all neurodegenerative diseases
    criteria = FilterCriteria()
    criteria.add_iri_pattern(".*/Neuro.*Disease$")

    # Match entities from specific namespace
    criteria.add_iri_pattern("^http://purl.obolibrary.org/obo/.*")

    # Combine multiple patterns (OR logic)
    criteria.add_iri_pattern(".*Alzheimer.*")
    criteria.add_iri_pattern(".*Parkinson.*")
    criteria.add_iri_pattern(".*Huntington.*")

    result = filter_obj.extract_by_criteria(criteria)

Annotation-Based Filtering
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Filter based on annotation values:

.. code-block:: python

    # Extract entities with specific labels
    criteria = FilterCriteria()
    criteria.add_annotation_filter(
        property_iri=IRI("rdfs", "label", "..."),
        value_pattern=".*disease.*",
        case_sensitive=False
    )

    # Filter by definition
    criteria.add_annotation_filter(
        property_iri=IRI("obo", "IAO_0000115", "..."),  # definition
        value_pattern=".*neurodegenerative.*"
    )

    result = filter_obj.extract_by_criteria(criteria)

Axiom Type Filtering
~~~~~~~~~~~~~~~~~~~~~

Include only specific axiom types:

.. code-block:: python

    criteria = FilterCriteria()
    criteria.set_axiom_types([
        'SUBCLASS_OF',
        'EQUIVALENT_CLASSES',
        'CLASS_ASSERTION'
    ])

    result = filter_obj.extract_by_criteria(criteria)

Combining Criteria
~~~~~~~~~~~~~~~~~~

Combine multiple filtering conditions:

.. code-block:: python

    criteria = FilterCriteria()

    # Must match IRI pattern AND have annotation
    criteria.add_iri_pattern(".*Disease.*")
    criteria.add_annotation_filter(
        property_iri=rdfs_label,
        value_pattern=".*",
        required=True  # Must have a label
    )

    # Only include classes and properties
    criteria.set_entity_types(['CLASS', 'OBJECT_PROPERTY'])

    # Only specific axiom types
    criteria.set_axiom_types(['SUBCLASS_OF', 'DECLARATION'])

    result = filter_obj.extract_by_criteria(criteria)

FilterResult Analysis
---------------------

The ``FilterResult`` object provides information about the extraction.

Basic Information
~~~~~~~~~~~~~~~~~

.. code-block:: python

    result = filter_obj.extract_neighborhood(seed_iri, depth=2)

    # Get extracted ontology
    subgraph = result.get_ontology()

    # Get list of included IRIs
    included_iris = result.get_included_iris()
    print(f"Extracted {len(included_iris)} entities")

    # Get statistics
    stats = result.get_statistics()
    print(f"Classes: {stats['class_count']}")
    print(f"Properties: {stats['property_count']}")
    print(f"Individuals: {stats['individual_count']}")
    print(f"Axioms: {stats['axiom_count']}")

Extraction Depth Analysis
~~~~~~~~~~~~~~~~~~~~~~~~~~

Analyze entities by their distance from seed:

.. code-block:: python

    # Get entities by depth level
    depth_map = result.get_depth_map()

    for depth, iris in depth_map.items():
        print(f"Depth {depth}: {len(iris)} entities")
        for iri in iris[:5]:  # Show first 5
            print(f"  {iri.get_short_form()}")

Coverage Analysis
~~~~~~~~~~~~~~~~~

Check what was included/excluded:

.. code-block:: python

    # Check if specific IRI was included
    target_iri = IRI("http://example.org/SomeEntity")
    if result.contains_iri(target_iri):
        print(f"{target_iri} was included")
    else:
        print(f"{target_iri} was excluded")

    # Get excluded IRIs (if tracked)
    excluded = result.get_excluded_iris()
    print(f"Excluded {len(excluded)} entities")

Advanced Extraction Patterns
-----------------------------

Module Extraction
~~~~~~~~~~~~~~~~~

Extract self-contained modules:

.. code-block:: python

    def extract_module(ont, seed_iris, closure_depth=5):
        """Extract a self-contained module around seed IRIs."""
        filter_obj = OntologyFilter(ont)

        # Extract large neighborhood to get closure
        all_iris = set()
        for seed in seed_iris:
            result = filter_obj.extract_neighborhood(
                seed,
                depth=closure_depth,
                include_superclasses=True,
                include_subclasses=True
            )
            all_iris.update(result.get_included_iris())

        # Create criteria from collected IRIs
        criteria = FilterCriteria()
        for iri in all_iris:
            criteria.add_specific_iri(iri)

        # Extract complete module
        result = filter_obj.extract_by_criteria(criteria)
        return result.get_ontology()

Hierarchical Slicing
~~~~~~~~~~~~~~~~~~~~

Extract specific levels of a hierarchy:

.. code-block:: python

    def extract_hierarchy_slice(ont, root_iri, min_depth, max_depth):
        """Extract entities between min_depth and max_depth from root."""
        filter_obj = OntologyFilter(ont)

        # Get full neighborhood up to max_depth
        full_result = filter_obj.extract_neighborhood(
            root_iri,
            depth=max_depth,
            include_subclasses=True,
            include_superclasses=False
        )

        # Filter by depth
        depth_map = full_result.get_depth_map()
        selected_iris = []
        for depth in range(min_depth, max_depth + 1):
            if depth in depth_map:
                selected_iris.extend(depth_map[depth])

        # Extract selected entities
        criteria = FilterCriteria()
        for iri in selected_iris:
            criteria.add_specific_iri(iri)

        result = filter_obj.extract_by_criteria(criteria)
        return result.get_ontology()

Domain-Specific Extraction
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Extract domain-specific slices:

.. code-block:: python

    def extract_disease_module(ont):
        """Extract all disease-related entities."""
        filter_obj = OntologyFilter(ont)
        criteria = FilterCriteria()

        # Match disease entities
        criteria.add_iri_pattern(".*Disease.*")
        criteria.add_iri_pattern(".*Disorder.*")
        criteria.add_iri_pattern(".*Syndrome.*")

        # Include relevant annotation properties
        criteria.add_annotation_filter(
            property_iri=rdfs_label,
            value_pattern=".*(disease|disorder|syndrome).*",
            case_sensitive=False
        )

        # Get seed entities
        seed_result = filter_obj.extract_by_criteria(criteria)
        seed_iris = seed_result.get_included_iris()

        # Expand to include relationships
        expanded_iris = set(seed_iris)
        for seed in seed_iris:
            result = filter_obj.extract_neighborhood(
                seed,
                depth=1,
                include_properties=True
            )
            expanded_iris.update(result.get_included_iris())

        # Create final criteria
        final_criteria = FilterCriteria()
        for iri in expanded_iris:
            final_criteria.add_specific_iri(iri)

        result = filter_obj.extract_by_criteria(final_criteria)
        return result.get_ontology()

Iterative Refinement
~~~~~~~~~~~~~~~~~~~~

Refine extraction iteratively:

.. code-block:: python

    def iterative_extraction(ont, initial_seeds, max_iterations=5):
        """Iteratively expand subgraph until convergence."""
        filter_obj = OntologyFilter(ont)

        current_iris = set(initial_seeds)
        previous_size = 0
        iteration = 0

        while len(current_iris) != previous_size and iteration < max_iterations:
            previous_size = len(current_iris)
            iteration += 1

            # Extract neighborhood of current IRIs
            new_iris = set()
            for iri in current_iris:
                result = filter_obj.extract_neighborhood(iri, depth=1)
                new_iris.update(result.get_included_iris())

            # Add new IRIs
            current_iris.update(new_iris)
            print(f"Iteration {iteration}: {len(current_iris)} entities")

        # Create final criteria
        criteria = FilterCriteria()
        for iri in current_iris:
            criteria.add_specific_iri(iri)

        result = filter_obj.extract_by_criteria(criteria)
        return result.get_ontology()

Performance Optimization
------------------------

For Large Ontologies
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    # 1. Use smaller depth values
    result = filter_obj.extract_neighborhood(seed_iri, depth=2)  # Not 10

    # 2. Limit extraction directions
    result = filter_obj.extract_neighborhood(
        seed_iri,
        depth=3,
        include_individuals=False,  # Skip individuals
        include_properties=False    # Skip property axioms
    )

    # 3. Use specific criteria instead of broad patterns
    criteria = FilterCriteria()
    criteria.add_specific_iri(iri1)
    criteria.add_specific_iri(iri2)
    # Better than: criteria.add_iri_pattern(".*")

    # 4. Extract in batches
    batch_size = 100
    all_results = []
    for i in range(0, len(seed_iris), batch_size):
        batch = seed_iris[i:i+batch_size]
        # Process batch
        result = extract_batch(filter_obj, batch)
        all_results.append(result)

Caching Results
~~~~~~~~~~~~~~~

.. code-block:: python

    # Cache extracted subgraphs
    cache = {}

    def get_or_extract(filter_obj, seed_iri, depth):
        cache_key = (seed_iri.toString(), depth)
        if cache_key not in cache:
            result = filter_obj.extract_neighborhood(seed_iri, depth)
            cache[cache_key] = result
        return cache[cache_key]

Export and Visualization
-------------------------

Export Subgraphs
~~~~~~~~~~~~~~~~

.. code-block:: python

    from ista.owl2 import FunctionalSyntaxSerializer
    from ista.converters import ontology_to_networkx

    # Extract subgraph
    result = filter_obj.extract_neighborhood(seed_iri, depth=2)
    subgraph = result.get_ontology()

    # Save as OWL
    serializer = FunctionalSyntaxSerializer()
    serializer.serialize(subgraph, "subgraph.ofn")

    # Convert to NetworkX for visualization
    G = ontology_to_networkx(subgraph)

    # Export for Gephi
    import networkx as nx
    nx.write_gexf(G, "subgraph.gexf")

Visualize Extraction
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    import matplotlib.pyplot as plt
    import networkx as nx

    # Extract and convert
    result = filter_obj.extract_neighborhood(seed_iri, depth=2)
    G = ontology_to_networkx(result.get_ontology())

    # Color by depth
    depth_map = result.get_depth_map()
    node_colors = {}
    color_palette = ['red', 'orange', 'yellow', 'green', 'blue']

    for depth, iris in depth_map.items():
        color = color_palette[min(depth, len(color_palette)-1)]
        for iri in iris:
            node_colors[iri.get_short_form()] = color

    colors = [node_colors.get(n, 'gray') for n in G.nodes()]

    # Draw
    plt.figure(figsize=(12, 8))
    pos = nx.spring_layout(G)
    nx.draw(G, pos, node_color=colors, with_labels=True,
            node_size=500, font_size=8)
    plt.title(f"Subgraph around {seed_iri.get_short_form()}")
    plt.savefig("subgraph_visualization.png", dpi=300)

Use Cases
---------

1. **Focused Analysis**: Extract disease-specific portions for detailed study
2. **Ontology Modularization**: Create smaller, reusable ontology modules
3. **Visualization**: Extract manageable portions for graph visualization
4. **Data Export**: Generate domain-specific knowledge bases for applications
5. **Performance**: Work with relevant portions of very large ontologies
6. **Integration**: Extract compatible subsets for merging with other ontologies

Best Practices
--------------

1. **Start Small**: Begin with small depth values and expand as needed
2. **Profile Performance**: Measure extraction time for large ontologies
3. **Validate Results**: Check that extracted subgraphs are complete and consistent
4. **Cache Frequently Used Extractions**: Store commonly used subgraphs
5. **Document Extraction Logic**: Keep track of criteria used for reproducibility
6. **Test Coverage**: Verify that all expected entities are included

See Also
--------

- :doc:`python_library` - Python library guide
- :doc:`graph_converters` - Convert extracted subgraphs
- :doc:`../api/owl2` - Complete API reference
- :doc:`../examples` - Example extraction workflows
