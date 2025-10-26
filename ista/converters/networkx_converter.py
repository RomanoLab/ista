"""
NetworkX converter for OWL2 ontologies.

This module provides functions to convert between OWL2 ontologies and NetworkX
directed graphs.
"""

from typing import Any, Dict, Optional

try:
    import networkx as nx

    HAS_NETWORKX = True
except ImportError:
    HAS_NETWORKX = False
    nx = None

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


class NetworkXConverter(OntologyToGraphConverter):
    """Converter from OWL2 ontology to NetworkX directed graph.

    This converter creates a NetworkX DiGraph where:
    - Nodes represent individuals (and optionally classes/properties)
    - Edges represent object property assertions
    - Node attributes store IRIs, types, classes, and data properties
    - Edge attributes store property IRIs and types

    Examples
    --------
    >>> from ista import owl2
    >>> from ista.converters import NetworkXConverter, ConversionOptions
    >>>
    >>> ontology = owl2.Ontology("http://example.org/ontology")
    >>> converter = NetworkXConverter(ontology)
    >>> graph = converter.convert()
    >>>
    >>> # Access node attributes
    >>> for node, attrs in graph.nodes(data=True):
    ...     print(f"Node: {attrs['label']}, Type: {attrs['type']}")
    >>>
    >>> # Access edge attributes
    >>> for u, v, attrs in graph.edges(data=True):
    ...     print(f"Edge: {u} --[{attrs['property_label']}]--> {v}")
    """

    def convert(self) -> "nx.DiGraph":
        """Convert the ontology to a NetworkX DiGraph.

        Returns
        -------
        networkx.DiGraph
            The converted graph with nodes and edges representing the ontology.

        Raises
        ------
        ImportError
            If NetworkX is not installed.
        """
        if not HAS_NETWORKX:
            raise ImportError(
                "NetworkX is required for this converter. "
                "Install it with: pip install networkx"
            )

        graph = nx.DiGraph()

        # Add individuals as nodes
        individuals = self._extract_individuals()
        for individual in individuals:
            individual_iri = str(individual.iri)
            attrs = self._build_node_attributes(individual, "individual")
            graph.add_node(individual_iri, **attrs)

        # Add object property edges
        for individual in individuals:
            object_props = self._get_object_properties(individual)
            for prop in object_props:
                source_iri = str(individual.iri)
                target_iri = prop["target"]
                prop_iri = prop["property"]

                edge_attrs = {
                    "property_iri": prop_iri,
                    "property_label": self._simplify_iri(prop_iri),
                    "property_type": "object_property",
                }

                if self.options.preserve_namespaces:
                    edge_attrs["property_namespace"] = self._get_namespace(prop_iri)

                graph.add_edge(source_iri, target_iri, **edge_attrs)

        # Optionally add classes
        if self.options.strategy in [
            ConversionStrategy.INCLUDE_CLASSES,
            ConversionStrategy.INCLUDE_PROPERTIES,
        ]:
            classes = self._extract_classes()
            for cls in classes:
                class_iri = str(cls.iri)
                attrs = self._build_node_attributes(cls, "class")
                graph.add_node(class_iri, **attrs)

            # Add subclass relationships
            for axiom in self.ontology.axioms:
                if (
                    hasattr(axiom, "__class__")
                    and axiom.__class__.__name__ == "SubClassOf"
                ):
                    subclass_iri = str(axiom.subclass.iri)
                    superclass_iri = str(axiom.superclass.iri)

                    edge_attrs = {
                        "property_iri": "http://www.w3.org/2000/01/rdf-schema#subClassOf",
                        "property_label": "subClassOf",
                        "property_type": "class_hierarchy",
                    }

                    graph.add_edge(subclass_iri, superclass_iri, **edge_attrs)

            # Add class membership edges from individuals to classes
            for individual in individuals:
                individual_iri = str(individual.iri)
                classes = self._get_individual_classes(individual)
                for class_iri in classes:
                    edge_attrs = {
                        "property_iri": "http://www.w3.org/1999/02/22-rdf-syntax-ns#type",
                        "property_label": "type",
                        "property_type": "class_membership",
                    }
                    graph.add_edge(individual_iri, class_iri, **edge_attrs)

        # Optionally add properties
        if self.options.strategy == ConversionStrategy.INCLUDE_PROPERTIES:
            properties = self._extract_properties()

            for prop in properties["object"]:
                prop_iri = str(prop.iri)
                attrs = self._build_node_attributes(prop, "object_property")
                graph.add_node(prop_iri, **attrs)

            for prop in properties["data"]:
                prop_iri = str(prop.iri)
                attrs = self._build_node_attributes(prop, "data_property")
                graph.add_node(prop_iri, **attrs)

            if self.options.include_annotations:
                for prop in properties["annotation"]:
                    prop_iri = str(prop.iri)
                    attrs = self._build_node_attributes(prop, "annotation_property")
                    graph.add_node(prop_iri, **attrs)

            # Add property hierarchy edges
            for axiom in self.ontology.axioms:
                axiom_class = axiom.__class__.__name__
                if axiom_class == "SubObjectPropertyOf":
                    sub_prop = str(axiom.subproperty.iri)
                    super_prop = str(axiom.superproperty.iri)
                    edge_attrs = {
                        "property_iri": "http://www.w3.org/2000/01/rdf-schema#subPropertyOf",
                        "property_label": "subPropertyOf",
                        "property_type": "property_hierarchy",
                    }
                    graph.add_edge(sub_prop, super_prop, **edge_attrs)
                elif axiom_class == "SubDataPropertyOf":
                    sub_prop = str(axiom.subproperty.iri)
                    super_prop = str(axiom.superproperty.iri)
                    edge_attrs = {
                        "property_iri": "http://www.w3.org/2000/01/rdf-schema#subPropertyOf",
                        "property_label": "subPropertyOf",
                        "property_type": "property_hierarchy",
                    }
                    graph.add_edge(sub_prop, super_prop, **edge_attrs)

        return graph

    def reverse_convert(self, graph: "nx.DiGraph", ontology_iri: str) -> Any:
        """Convert a NetworkX DiGraph back to an OWL2 ontology.

        Parameters
        ----------
        graph : networkx.DiGraph
            The NetworkX graph to convert.

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
        for node, attrs in graph.nodes(data=True):
            node_type = attrs.get("type", "individual")
            node_iri = attrs.get("iri", node)

            if node_type == "individual":
                individual = owl2.NamedIndividual(owl2.IRI(node_iri))
                individuals_map[node_iri] = individual

                # Declare the individual
                ontology.add_axiom(owl2.Declaration(individual))

                # Add class assertions
                classes = attrs.get("classes", [])
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
                for key, value in attrs.items():
                    if key.startswith(self.options.data_property_prefix):
                        prop_name = key[len(self.options.data_property_prefix) :]
                        # Reconstruct property IRI (simplified approach)
                        prop_iri = (
                            attrs.get("namespace", ontology_iri + "#") + prop_name
                        )

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
        for u, v, attrs in graph.edges(data=True):
            prop_type = attrs.get("property_type", "object_property")
            prop_iri = attrs.get("property_iri")

            if prop_type == "object_property":
                # Object property assertion
                if u in individuals_map and v in individuals_map:
                    if prop_iri not in properties_map:
                        obj_prop = owl2.ObjectProperty(owl2.IRI(prop_iri))
                        properties_map[prop_iri] = obj_prop
                        ontology.add_axiom(owl2.Declaration(obj_prop))

                    obj_prop_assertion = owl2.ObjectPropertyAssertion(
                        properties_map[prop_iri], individuals_map[u], individuals_map[v]
                    )
                    ontology.add_axiom(obj_prop_assertion)

            elif prop_type == "class_hierarchy":
                # SubClassOf axiom
                if u in classes_map and v in classes_map:
                    subclass_axiom = owl2.SubClassOf(classes_map[u], classes_map[v])
                    ontology.add_axiom(subclass_axiom)

            elif prop_type == "class_membership":
                # Type assertion (handled in first pass)
                pass

            elif prop_type == "property_hierarchy":
                # SubPropertyOf axiom
                if u in properties_map and v in properties_map:
                    # Determine property type
                    u_prop = properties_map[u]
                    if u_prop.__class__.__name__ == "ObjectProperty":
                        subprop_axiom = owl2.SubObjectPropertyOf(
                            u_prop, properties_map[v]
                        )
                    elif u_prop.__class__.__name__ == "DataProperty":
                        subprop_axiom = owl2.SubDataPropertyOf(
                            u_prop, properties_map[v]
                        )
                    else:
                        continue

                    ontology.add_axiom(subprop_axiom)

        return ontology


def to_networkx(
    ontology: Any, strategy: str = "individuals_only", **options
) -> "nx.DiGraph":
    """Convert an OWL2 ontology to a NetworkX directed graph.

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
    networkx.DiGraph
        The converted NetworkX directed graph.

    Examples
    --------
    >>> from ista import owl2
    >>> from ista.converters import to_networkx
    >>>
    >>> ontology = owl2.Ontology("http://example.org/ontology")
    >>>
    >>> # Convert with individuals only
    >>> graph = to_networkx(ontology)
    >>>
    >>> # Convert including classes
    >>> graph = to_networkx(ontology, strategy='include_classes')
    >>>
    >>> # Convert with custom options
    >>> graph = to_networkx(ontology,
    ...                     strategy='individuals_only',
    ...                     include_annotations=True,
    ...                     simplify_iris=False)
    >>>
    >>> # Analyze the graph
    >>> print(f"Nodes: {graph.number_of_nodes()}")
    >>> print(f"Edges: {graph.number_of_edges()}")
    >>>
    >>> # Get node with specific IRI
    >>> node_attrs = graph.nodes['http://example.org/ontology#Individual1']
    >>> print(f"Classes: {node_attrs['classes']}")
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
    converter = NetworkXConverter(ontology, conv_options)
    return converter.convert()


def from_networkx(graph: "nx.DiGraph", ontology_iri: str, **options) -> Any:
    """Convert a NetworkX directed graph to an OWL2 ontology.

    Parameters
    ----------
    graph : networkx.DiGraph
        The NetworkX graph to convert. Should have been created by
        to_networkx() or follow the same structure.

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
    >>> import networkx as nx
    >>> from ista.converters import from_networkx
    >>>
    >>> # Create a simple graph
    >>> graph = nx.DiGraph()
    >>> graph.add_node('http://example.org/ont#Ind1',
    ...                iri='http://example.org/ont#Ind1',
    ...                type='individual',
    ...                label='Ind1',
    ...                classes=['http://example.org/ont#Class1'])
    >>> graph.add_node('http://example.org/ont#Ind2',
    ...                iri='http://example.org/ont#Ind2',
    ...                type='individual',
    ...                label='Ind2',
    ...                classes=['http://example.org/ont#Class1'])
    >>> graph.add_edge('http://example.org/ont#Ind1',
    ...                'http://example.org/ont#Ind2',
    ...                property_iri='http://example.org/ont#relatedTo',
    ...                property_label='relatedTo',
    ...                property_type='object_property')
    >>>
    >>> # Convert to ontology
    >>> ontology = from_networkx(graph, 'http://example.org/ont')
    >>>
    >>> # Ontology now contains the individuals, classes, and relationships
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
    converter = NetworkXConverter(dummy_ontology, conv_options)
    return converter.reverse_convert(graph, ontology_iri)
