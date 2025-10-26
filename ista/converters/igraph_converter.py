"""
igraph converter for OWL2 ontologies.

This module provides functions to convert between OWL2 ontologies and igraph
Graph objects. igraph is a high-performance graph library with excellent
support for network analysis algorithms.
"""

from typing import Any, Dict, Optional

try:
    import igraph as ig

    HAS_IGRAPH = True
except ImportError:
    HAS_IGRAPH = False
    ig = None

from .ontology_to_graph import (
    OntologyToGraphConverter,
    ConversionOptions,
    ConversionStrategy,
)

try:
    from ista import owl2

    HAS_OWL2 = owl2.is_available()
except ImportError:
    HAS_OWL2 = False


class IGraphConverter(OntologyToGraphConverter):
    """Converter from OWL2 ontology to igraph Graph.

    This converter creates an igraph Graph where:
    - Vertices represent individuals (and optionally classes/properties)
    - Edges represent object property assertions
    - Vertex attributes store IRIs, types, classes, and data properties
    - Edge attributes store property IRIs and types

    igraph uses numeric vertex IDs, so we maintain a mapping between
    IRIs and vertex indices.

    Examples
    --------
    >>> from ista import owl2
    >>> from ista.converters import IGraphConverter, ConversionOptions
    >>>
    >>> ontology = owl2.Ontology("http://example.org/ontology")
    >>> converter = IGraphConverter(ontology)
    >>> graph = converter.convert()
    >>>
    >>> # Access vertex attributes
    >>> for v in graph.vs:
    ...     print(f"Vertex: {v['label']}, Type: {v['type']}")
    >>>
    >>> # Access edge attributes
    >>> for e in graph.es:
    ...     print(f"Edge: {e.source} --[{e['property_label']}]--> {e.target}")
    """

    def convert(self) -> "ig.Graph":
        """Convert the ontology to an igraph Graph.

        Returns
        -------
        igraph.Graph
            The converted directed graph with vertices and edges representing
            the ontology.

        Raises
        ------
        ImportError
            If igraph is not installed.
        """
        if not HAS_IGRAPH:
            raise ImportError(
                "igraph is required for this converter. "
                "Install it with: pip install igraph"
            )

        graph = ig.Graph(directed=True)

        # Mapping from IRI to vertex index
        iri_to_vertex = {}

        # Add individuals as vertices
        individuals = self._extract_individuals()
        for individual in individuals:
            individual_iri = str(individual.iri)
            attrs = self._build_node_attributes(individual, "individual")

            # Add vertex and store mapping
            vertex_idx = graph.vcount()
            graph.add_vertex(name=individual_iri, **attrs)
            iri_to_vertex[individual_iri] = vertex_idx

        # Add object property edges
        for individual in individuals:
            object_props = self._get_object_properties(individual)
            for prop in object_props:
                source_iri = str(individual.iri)
                target_iri = prop["target"]
                prop_iri = prop["property"]

                # Only add edge if target exists in graph
                if target_iri in iri_to_vertex:
                    edge_attrs = {
                        "property_iri": prop_iri,
                        "property_label": self._simplify_iri(prop_iri),
                        "property_type": "object_property",
                    }

                    if self.options.preserve_namespaces:
                        edge_attrs["property_namespace"] = self._get_namespace(prop_iri)

                    graph.add_edge(
                        iri_to_vertex[source_iri],
                        iri_to_vertex[target_iri],
                        **edge_attrs,
                    )

        # Optionally add classes
        if self.options.strategy in [
            ConversionStrategy.INCLUDE_CLASSES,
            ConversionStrategy.INCLUDE_PROPERTIES,
        ]:
            classes = self._extract_classes()
            for cls in classes:
                class_iri = str(cls.iri)
                attrs = self._build_node_attributes(cls, "class")

                vertex_idx = graph.vcount()
                graph.add_vertex(name=class_iri, **attrs)
                iri_to_vertex[class_iri] = vertex_idx

            # Add subclass relationships
            for axiom in self.ontology.axioms:
                if (
                    hasattr(axiom, "__class__")
                    and axiom.__class__.__name__ == "SubClassOf"
                ):
                    subclass_iri = str(axiom.subclass.iri)
                    superclass_iri = str(axiom.superclass.iri)

                    if (
                        subclass_iri in iri_to_vertex
                        and superclass_iri in iri_to_vertex
                    ):
                        edge_attrs = {
                            "property_iri": "http://www.w3.org/2000/01/rdf-schema#subClassOf",
                            "property_label": "subClassOf",
                            "property_type": "class_hierarchy",
                        }

                        graph.add_edge(
                            iri_to_vertex[subclass_iri],
                            iri_to_vertex[superclass_iri],
                            **edge_attrs,
                        )

            # Add class membership edges from individuals to classes
            for individual in individuals:
                individual_iri = str(individual.iri)
                classes = self._get_individual_classes(individual)
                for class_iri in classes:
                    if class_iri in iri_to_vertex:
                        edge_attrs = {
                            "property_iri": "http://www.w3.org/1999/02/22-rdf-syntax-ns#type",
                            "property_label": "type",
                            "property_type": "class_membership",
                        }
                        graph.add_edge(
                            iri_to_vertex[individual_iri],
                            iri_to_vertex[class_iri],
                            **edge_attrs,
                        )

        # Optionally add properties
        if self.options.strategy == ConversionStrategy.INCLUDE_PROPERTIES:
            properties = self._extract_properties()

            for prop in properties["object"]:
                prop_iri = str(prop.iri)
                attrs = self._build_node_attributes(prop, "object_property")

                vertex_idx = graph.vcount()
                graph.add_vertex(name=prop_iri, **attrs)
                iri_to_vertex[prop_iri] = vertex_idx

            for prop in properties["data"]:
                prop_iri = str(prop.iri)
                attrs = self._build_node_attributes(prop, "data_property")

                vertex_idx = graph.vcount()
                graph.add_vertex(name=prop_iri, **attrs)
                iri_to_vertex[prop_iri] = vertex_idx

            if self.options.include_annotations:
                for prop in properties["annotation"]:
                    prop_iri = str(prop.iri)
                    attrs = self._build_node_attributes(prop, "annotation_property")

                    vertex_idx = graph.vcount()
                    graph.add_vertex(name=prop_iri, **attrs)
                    iri_to_vertex[prop_iri] = vertex_idx

            # Add property hierarchy edges
            for axiom in self.ontology.axioms:
                axiom_class = axiom.__class__.__name__
                if axiom_class == "SubObjectPropertyOf":
                    sub_prop = str(axiom.subproperty.iri)
                    super_prop = str(axiom.superproperty.iri)

                    if sub_prop in iri_to_vertex and super_prop in iri_to_vertex:
                        edge_attrs = {
                            "property_iri": "http://www.w3.org/2000/01/rdf-schema#subPropertyOf",
                            "property_label": "subPropertyOf",
                            "property_type": "property_hierarchy",
                        }
                        graph.add_edge(
                            iri_to_vertex[sub_prop],
                            iri_to_vertex[super_prop],
                            **edge_attrs,
                        )
                elif axiom_class == "SubDataPropertyOf":
                    sub_prop = str(axiom.subproperty.iri)
                    super_prop = str(axiom.superproperty.iri)

                    if sub_prop in iri_to_vertex and super_prop in iri_to_vertex:
                        edge_attrs = {
                            "property_iri": "http://www.w3.org/2000/01/rdf-schema#subPropertyOf",
                            "property_label": "subPropertyOf",
                            "property_type": "property_hierarchy",
                        }
                        graph.add_edge(
                            iri_to_vertex[sub_prop],
                            iri_to_vertex[super_prop],
                            **edge_attrs,
                        )

        return graph

    def reverse_convert(self, graph: "ig.Graph", ontology_iri: str) -> Any:
        """Convert an igraph Graph back to an OWL2 ontology.

        Parameters
        ----------
        graph : igraph.Graph
            The igraph Graph to convert.

        ontology_iri : str
            The IRI for the new ontology.

        Returns
        -------
        owl2.Ontology
            The converted ontology.

        Raises
        ------
        ImportError
            If OWL2 library is not available.
        """
        if not HAS_OWL2:
            raise ImportError(
                "OWL2 library is required for reverse conversion. "
                "Please build the C++ extensions."
            )

        ontology = owl2.Ontology(ontology_iri)

        # Track created entities
        individuals_map = {}
        classes_map = {}
        properties_map = {}

        # First pass: Create all entities
        for vertex in graph.vs:
            node_type = vertex["type"]
            node_iri = vertex["iri"]

            if node_type == "individual":
                individual = owl2.NamedIndividual(owl2.IRI(node_iri))
                individuals_map[node_iri] = individual

                # Declare the individual
                ontology.add_axiom(owl2.Declaration(individual))

                # Add class assertions
                classes = vertex["classes"]
                for class_iri in classes:
                    if class_iri not in classes_map:
                        cls = owl2.Class(owl2.IRI(class_iri))
                        classes_map[class_iri] = cls
                        ontology.add_axiom(owl2.Declaration(cls))

                    class_assertion = owl2.ClassAssertion(
                        classes_map[class_iri], individual
                    )
                    ontology.add_axiom(class_assertion)

                # Add data property assertions
                for key in vertex.attributes():
                    if key.startswith(self.options.data_property_prefix):
                        prop_name = key[len(self.options.data_property_prefix) :]
                        value = vertex[key]

                        # Reconstruct property IRI (simplified approach)
                        namespace = vertex.get("namespace", ontology_iri + "#")
                        prop_iri = namespace + prop_name

                        if prop_iri not in properties_map:
                            data_prop = owl2.DataProperty(owl2.IRI(prop_iri))
                            properties_map[prop_iri] = data_prop
                            ontology.add_axiom(owl2.Declaration(data_prop))

                        # Create literal value
                        literal = owl2.Literal(str(value))

                        data_prop_assertion = owl2.DataPropertyAssertion(
                            properties_map[prop_iri], individual, literal
                        )
                        ontology.add_axiom(data_prop_assertion)

            elif node_type == "class":
                cls = owl2.Class(owl2.IRI(node_iri))
                classes_map[node_iri] = cls
                ontology.add_axiom(owl2.Declaration(cls))

            elif node_type in [
                "object_property",
                "data_property",
                "annotation_property",
            ]:
                if node_type == "object_property":
                    prop = owl2.ObjectProperty(owl2.IRI(node_iri))
                elif node_type == "data_property":
                    prop = owl2.DataProperty(owl2.IRI(node_iri))
                else:
                    prop = owl2.AnnotationProperty(owl2.IRI(node_iri))

                properties_map[node_iri] = prop
                ontology.add_axiom(owl2.Declaration(prop))

        # Second pass: Create edges (relationships)
        for edge in graph.es:
            source_vertex = graph.vs[edge.source]
            target_vertex = graph.vs[edge.target]

            source_iri = source_vertex["iri"]
            target_iri = target_vertex["iri"]

            prop_type = edge["property_type"]
            prop_iri = edge["property_iri"]

            if prop_type == "object_property":
                # Object property assertion
                if source_iri in individuals_map and target_iri in individuals_map:
                    if prop_iri not in properties_map:
                        obj_prop = owl2.ObjectProperty(owl2.IRI(prop_iri))
                        properties_map[prop_iri] = obj_prop
                        ontology.add_axiom(owl2.Declaration(obj_prop))

                    obj_prop_assertion = owl2.ObjectPropertyAssertion(
                        properties_map[prop_iri],
                        individuals_map[source_iri],
                        individuals_map[target_iri],
                    )
                    ontology.add_axiom(obj_prop_assertion)

            elif prop_type == "class_hierarchy":
                # SubClassOf axiom
                if source_iri in classes_map and target_iri in classes_map:
                    subclass_axiom = owl2.SubClassOf(
                        classes_map[source_iri], classes_map[target_iri]
                    )
                    ontology.add_axiom(subclass_axiom)

            elif prop_type == "class_membership":
                # Type assertion (handled in first pass)
                pass

            elif prop_type == "property_hierarchy":
                # SubPropertyOf axiom
                if source_iri in properties_map and target_iri in properties_map:
                    # Determine property type
                    source_prop = properties_map[source_iri]
                    if source_prop.__class__.__name__ == "ObjectProperty":
                        subprop_axiom = owl2.SubObjectPropertyOf(
                            source_prop, properties_map[target_iri]
                        )
                    elif source_prop.__class__.__name__ == "DataProperty":
                        subprop_axiom = owl2.SubDataPropertyOf(
                            source_prop, properties_map[target_iri]
                        )
                    else:
                        continue

                    ontology.add_axiom(subprop_axiom)

        return ontology


def to_igraph(
    ontology: Any, strategy: str = "individuals_only", **options
) -> "ig.Graph":
    """Convert an OWL2 ontology to an igraph Graph.

    Parameters
    ----------
    ontology : owl2.Ontology
        The OWL2 ontology to convert.

    strategy : str, optional
        Conversion strategy. One of:
        - 'individuals_only': Only individuals as vertices (default)
        - 'include_classes': Include classes as vertices
        - 'include_properties': Include properties as vertices

    **options
        Additional conversion options. See ConversionOptions for details.
        Common options:
        - include_data_properties: bool (default True)
        - include_annotations: bool (default False)
        - filter_classes: Set[str] (default None)
        - simplify_iris: bool (default True)

    Returns
    -------
    igraph.Graph
        The converted igraph directed graph.

    Examples
    --------
    >>> from ista import owl2
    >>> from ista.converters import to_igraph
    >>>
    >>> ontology = owl2.Ontology("http://example.org/ontology")
    >>>
    >>> # Convert with individuals only
    >>> graph = to_igraph(ontology)
    >>>
    >>> # Convert including classes
    >>> graph = to_igraph(ontology, strategy='include_classes')
    >>>
    >>> # Analyze the graph
    >>> print(f"Vertices: {graph.vcount()}")
    >>> print(f"Edges: {graph.ecount()}")
    >>> print(f"Density: {graph.density()}")
    >>>
    >>> # Run community detection
    >>> communities = graph.community_leiden()
    >>> print(f"Found {len(communities)} communities")
    >>>
    >>> # Calculate centrality
    >>> betweenness = graph.betweenness()
    >>> for i, v in enumerate(graph.vs):
    ...     print(f"{v['label']}: {betweenness[i]}")
    """
    # Convert strategy string to enum
    strategy_map = {
        "individuals_only": ConversionStrategy.INDIVIDUALS_ONLY,
        "include_classes": ConversionStrategy.INCLUDE_CLASSES,
        "include_properties": ConversionStrategy.INCLUDE_PROPERTIES,
    }

    strategy_enum = strategy_map.get(strategy, ConversionStrategy.INDIVIDUALS_ONLY)

    # Build conversion options
    conv_options = ConversionOptions(strategy=strategy_enum)

    # Update with provided options
    for key, value in options.items():
        if hasattr(conv_options, key):
            setattr(conv_options, key, value)

    # Convert
    converter = IGraphConverter(ontology, conv_options)
    return converter.convert()


def from_igraph(graph: "ig.Graph", ontology_iri: str, **options) -> Any:
    """Convert an igraph Graph to an OWL2 ontology.

    Parameters
    ----------
    graph : igraph.Graph
        The igraph Graph to convert. Should have been created by
        to_igraph() or follow the same structure.

    ontology_iri : str
        The IRI for the new ontology.

    **options
        Additional conversion options. See ConversionOptions for details.

    Returns
    -------
    owl2.Ontology
        The converted OWL2 ontology.

    Examples
    --------
    >>> import igraph as ig
    >>> from ista.converters import from_igraph
    >>>
    >>> # Create a simple graph
    >>> graph = ig.Graph(directed=True)
    >>> graph.add_vertex(name='http://example.org/ont#Ind1',
    ...                  iri='http://example.org/ont#Ind1',
    ...                  type='individual',
    ...                  label='Ind1',
    ...                  classes=['http://example.org/ont#Class1'])
    >>> graph.add_vertex(name='http://example.org/ont#Ind2',
    ...                  iri='http://example.org/ont#Ind2',
    ...                  type='individual',
    ...                  label='Ind2',
    ...                  classes=['http://example.org/ont#Class1'])
    >>> graph.add_edge(0, 1,
    ...                property_iri='http://example.org/ont#relatedTo',
    ...                property_label='relatedTo',
    ...                property_type='object_property')
    >>>
    >>> # Convert to ontology
    >>> ontology = from_igraph(graph, 'http://example.org/ont')
    """
    # Build conversion options
    conv_options = ConversionOptions()

    # Update with provided options
    for key, value in options.items():
        if hasattr(conv_options, key):
            setattr(conv_options, key, value)

    # Create dummy ontology for converter initialization
    if HAS_OWL2:
        dummy_ontology = owl2.Ontology("http://dummy.org/ontology")
    else:
        raise ImportError("OWL2 library is required. Please build the C++ extensions.")

    # Convert
    converter = IGraphConverter(dummy_ontology, conv_options)
    return converter.reverse_convert(graph, ontology_iri)
