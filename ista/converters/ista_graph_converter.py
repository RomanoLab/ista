"""
Native ista.graph converter for OWL2 ontologies.

This module provides functions to convert between OWL2 ontologies and ista's
native graph representation.
"""

from typing import Any, Dict, Optional

from ista.graph import Graph, Node, Edge

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


class IstaGraphConverter(OntologyToGraphConverter):
    """Converter from OWL2 ontology to ista.graph.Graph.

    This converter creates an ista Graph where:
    - Nodes represent individuals (and optionally classes/properties)
    - Edges represent object property assertions
    - Node properties store IRIs, types, classes, and data properties
    - Edge properties store property IRIs and types

    Examples
    --------
    >>> from ista import owl2
    >>> from ista.converters import IstaGraphConverter, ConversionOptions
    >>>
    >>> ontology = owl2.Ontology("http://example.org/ontology")
    >>> converter = IstaGraphConverter(ontology)
    >>> graph = converter.convert()
    >>>
    >>> # Access nodes
    >>> for node in graph.nodes:
    ...     print(f"Node: {node.name}, Class: {node.node_class}")
    >>>
    >>> # Access edges
    >>> for edge in graph.edges:
    ...     print(f"Edge: {edge.from_node.name} --> {edge.to_node.name}")
    """

    def convert(self) -> Graph:
        """Convert the ontology to an ista.graph.Graph.

        Returns
        -------
        ista.graph.Graph
            The converted graph with nodes and edges representing the ontology.
        """
        graph = Graph()

        # Mapping from IRI to Node object
        iri_to_node = {}

        # Add individuals as nodes
        individuals = self._extract_individuals()
        for idx, individual in enumerate(individuals):
            individual_iri = str(individual.iri)
            attrs = self._build_node_attributes(individual, "individual")

            # Determine node class from first class membership
            classes = attrs.get("classes", [])
            node_class = None
            if classes:
                node_class = self._simplify_iri(classes[0])

            # Create node
            node = Node(
                node_class=node_class,
                node_idx=idx,
                name=attrs.get("label", individual_iri),
                properties=attrs,
            )

            graph.nodes.append(node)
            iri_to_node[individual_iri] = node

        # Add object property edges
        for individual in individuals:
            object_props = self._get_object_properties(individual)
            for prop in object_props:
                source_iri = str(individual.iri)
                target_iri = prop["target"]
                prop_iri = prop["property"]

                # Only add edge if both nodes exist
                if source_iri in iri_to_node and target_iri in iri_to_node:
                    edge_attrs = {
                        "property_iri": prop_iri,
                        "property_label": self._simplify_iri(prop_iri),
                        "property_type": "object_property",
                    }

                    if self.options.preserve_namespaces:
                        edge_attrs["property_namespace"] = self._get_namespace(prop_iri)

                    edge = Edge(
                        from_node=iri_to_node[source_iri],
                        to_node=iri_to_node[target_iri],
                        weight=1.0,
                        edge_properties=edge_attrs,
                    )

                    graph.edges.append(edge)

        # Optionally add classes
        if self.options.strategy in [
            ConversionStrategy.INCLUDE_CLASSES,
            ConversionStrategy.INCLUDE_PROPERTIES,
        ]:
            classes = self._extract_classes()
            for cls in classes:
                class_iri = str(cls.iri)
                attrs = self._build_node_attributes(cls, "class")

                node_idx = len(graph.nodes)
                node = Node(
                    node_class="Class",
                    node_idx=node_idx,
                    name=attrs.get("label", class_iri),
                    properties=attrs,
                )

                graph.nodes.append(node)
                iri_to_node[class_iri] = node

            # Add subclass relationships
            for axiom in self.ontology.axioms:
                if (
                    hasattr(axiom, "__class__")
                    and axiom.__class__.__name__ == "SubClassOf"
                ):
                    subclass_iri = str(axiom.subclass.iri)
                    superclass_iri = str(axiom.superclass.iri)

                    if subclass_iri in iri_to_node and superclass_iri in iri_to_node:
                        edge_attrs = {
                            "property_iri": "http://www.w3.org/2000/01/rdf-schema#subClassOf",
                            "property_label": "subClassOf",
                            "property_type": "class_hierarchy",
                        }

                        edge = Edge(
                            from_node=iri_to_node[subclass_iri],
                            to_node=iri_to_node[superclass_iri],
                            weight=1.0,
                            edge_properties=edge_attrs,
                        )

                        graph.edges.append(edge)

            # Add class membership edges from individuals to classes
            for individual in individuals:
                individual_iri = str(individual.iri)
                classes = self._get_individual_classes(individual)
                for class_iri in classes:
                    if class_iri in iri_to_node:
                        edge_attrs = {
                            "property_iri": "http://www.w3.org/1999/02/22-rdf-syntax-ns#type",
                            "property_label": "type",
                            "property_type": "class_membership",
                        }

                        edge = Edge(
                            from_node=iri_to_node[individual_iri],
                            to_node=iri_to_node[class_iri],
                            weight=1.0,
                            edge_properties=edge_attrs,
                        )

                        graph.edges.append(edge)

        # Optionally add properties
        if self.options.strategy == ConversionStrategy.INCLUDE_PROPERTIES:
            properties = self._extract_properties()

            for prop in properties["object"]:
                prop_iri = str(prop.iri)
                attrs = self._build_node_attributes(prop, "object_property")

                node_idx = len(graph.nodes)
                node = Node(
                    node_class="ObjectProperty",
                    node_idx=node_idx,
                    name=attrs.get("label", prop_iri),
                    properties=attrs,
                )

                graph.nodes.append(node)
                iri_to_node[prop_iri] = node

            for prop in properties["data"]:
                prop_iri = str(prop.iri)
                attrs = self._build_node_attributes(prop, "data_property")

                node_idx = len(graph.nodes)
                node = Node(
                    node_class="DataProperty",
                    node_idx=node_idx,
                    name=attrs.get("label", prop_iri),
                    properties=attrs,
                )

                graph.nodes.append(node)
                iri_to_node[prop_iri] = node

            if self.options.include_annotations:
                for prop in properties["annotation"]:
                    prop_iri = str(prop.iri)
                    attrs = self._build_node_attributes(prop, "annotation_property")

                    node_idx = len(graph.nodes)
                    node = Node(
                        node_class="AnnotationProperty",
                        node_idx=node_idx,
                        name=attrs.get("label", prop_iri),
                        properties=attrs,
                    )

                    graph.nodes.append(node)
                    iri_to_node[prop_iri] = node

            # Add property hierarchy edges
            for axiom in self.ontology.axioms:
                axiom_class = axiom.__class__.__name__
                if axiom_class == "SubObjectPropertyOf":
                    sub_prop = str(axiom.subproperty.iri)
                    super_prop = str(axiom.superproperty.iri)

                    if sub_prop in iri_to_node and super_prop in iri_to_node:
                        edge_attrs = {
                            "property_iri": "http://www.w3.org/2000/01/rdf-schema#subPropertyOf",
                            "property_label": "subPropertyOf",
                            "property_type": "property_hierarchy",
                        }

                        edge = Edge(
                            from_node=iri_to_node[sub_prop],
                            to_node=iri_to_node[super_prop],
                            weight=1.0,
                            edge_properties=edge_attrs,
                        )

                        graph.edges.append(edge)
                elif axiom_class == "SubDataPropertyOf":
                    sub_prop = str(axiom.subproperty.iri)
                    super_prop = str(axiom.superproperty.iri)

                    if sub_prop in iri_to_node and super_prop in iri_to_node:
                        edge_attrs = {
                            "property_iri": "http://www.w3.org/2000/01/rdf-schema#subPropertyOf",
                            "property_label": "subPropertyOf",
                            "property_type": "property_hierarchy",
                        }

                        edge = Edge(
                            from_node=iri_to_node[sub_prop],
                            to_node=iri_to_node[super_prop],
                            weight=1.0,
                            edge_properties=edge_attrs,
                        )

                        graph.edges.append(edge)

        return graph

    def reverse_convert(self, graph: Graph, ontology_iri: str) -> Any:
        """Convert an ista.graph.Graph back to an OWL2 ontology.

        Parameters
        ----------
        graph : ista.graph.Graph
            The ista graph to convert.

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
        node_to_iri = {}

        # First pass: Create all entities
        for node in graph.nodes:
            node_props = node.properties
            node_type = node_props.get("type", "individual")
            node_iri = node_props.get("iri")

            if not node_iri:
                # Generate IRI from node name
                node_iri = ontology_iri + "#" + (node.name or f"node_{node.node_idx}")

            node_to_iri[node] = node_iri

            if node_type == "individual":
                individual = owl2.NamedIndividual(owl2.IRI(node_iri))
                individuals_map[node_iri] = individual

                # Declare the individual
                ontology.add_axiom(owl2.Declaration(individual))

                # Add class assertions
                classes = node_props.get("classes", [])
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
                for key, value in node_props.items():
                    if key.startswith(self.options.data_property_prefix):
                        prop_name = key[len(self.options.data_property_prefix) :]
                        # Reconstruct property IRI
                        namespace = node_props.get("namespace", ontology_iri + "#")
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
        for edge in graph.edges:
            source_node = edge.from_node
            target_node = edge.to_node
            edge_props = edge.edge_properties

            source_iri = node_to_iri.get(source_node)
            target_iri = node_to_iri.get(target_node)

            if not source_iri or not target_iri:
                continue

            prop_type = edge_props.get("property_type", "object_property")
            prop_iri = edge_props.get("property_iri")

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


def to_ista_graph(
    ontology: Any, strategy: str = "individuals_only", **options
) -> Graph:
    """Convert an OWL2 ontology to an ista.graph.Graph.

    Parameters
    ----------
    ontology : owl2.Ontology
        The OWL2 ontology to convert.

    strategy : str, optional
        Conversion strategy. One of:
        - 'individuals_only': Only individuals as nodes (default)
        - 'include_classes': Include classes as nodes
        - 'include_properties': Include properties as nodes

    **options
        Additional conversion options. See ConversionOptions for details.
        Common options:
        - include_data_properties: bool (default True)
        - include_annotations: bool (default False)
        - filter_classes: Set[str] (default None)
        - simplify_iris: bool (default True)

    Returns
    -------
    ista.graph.Graph
        The converted ista graph.

    Examples
    --------
    >>> from ista import owl2
    >>> from ista.converters import to_ista_graph
    >>>
    >>> ontology = owl2.Ontology("http://example.org/ontology")
    >>>
    >>> # Convert with individuals only
    >>> graph = to_ista_graph(ontology)
    >>>
    >>> # Convert including classes
    >>> graph = to_ista_graph(ontology, strategy='include_classes')
    >>>
    >>> # Access nodes
    >>> for node in graph.nodes:
    ...     print(f"Node: {node.name}, Class: {node.node_class}")
    ...     print(f"Properties: {node.properties}")
    >>>
    >>> # Access edges
    >>> for edge in graph.edges:
    ...     prop_label = edge.edge_properties.get('property_label', 'unknown')
    ...     print(f"{edge.from_node.name} --[{prop_label}]--> {edge.to_node.name}")
    >>>
    >>> # Get adjacency matrix
    >>> adj_matrix = graph.get_adjacency(format='matrix')
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
    converter = IstaGraphConverter(ontology, conv_options)
    return converter.convert()


def from_ista_graph(graph: Graph, ontology_iri: str, **options) -> Any:
    """Convert an ista.graph.Graph to an OWL2 ontology.

    Parameters
    ----------
    graph : ista.graph.Graph
        The ista graph to convert. Should have been created by
        to_ista_graph() or follow the same structure.

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
    >>> from ista.graph import Graph, Node, Edge
    >>> from ista.converters import from_ista_graph
    >>>
    >>> # Create a simple graph
    >>> graph = Graph()
    >>>
    >>> # Add nodes
    >>> node1 = Node(
    ...     node_class='Person',
    ...     node_idx=0,
    ...     name='Alice',
    ...     properties={
    ...         'iri': 'http://example.org/ont#Alice',
    ...         'type': 'individual',
    ...         'label': 'Alice',
    ...         'classes': ['http://example.org/ont#Person'],
    ...         'data_age': 30
    ...     }
    ... )
    >>> node2 = Node(
    ...     node_class='Person',
    ...     node_idx=1,
    ...     name='Bob',
    ...     properties={
    ...         'iri': 'http://example.org/ont#Bob',
    ...         'type': 'individual',
    ...         'label': 'Bob',
    ...         'classes': ['http://example.org/ont#Person'],
    ...         'data_age': 25
    ...     }
    ... )
    >>> graph.nodes.extend([node1, node2])
    >>>
    >>> # Add edge
    >>> edge = Edge(
    ...     from_node=node1,
    ...     to_node=node2,
    ...     weight=1.0,
    ...     edge_properties={
    ...         'property_iri': 'http://example.org/ont#knows',
    ...         'property_label': 'knows',
    ...         'property_type': 'object_property'
    ...     }
    ... )
    >>> graph.edges.append(edge)
    >>>
    >>> # Convert to ontology
    >>> ontology = from_ista_graph(graph, 'http://example.org/ont')
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
    converter = IstaGraphConverter(dummy_ontology, conv_options)
    return converter.reverse_convert(graph, ontology_iri)
