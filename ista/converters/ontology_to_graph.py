"""
Base classes and utilities for converting OWL2 ontologies to graph representations.

This module provides the core conversion logic that is shared across different
graph backends (NetworkX, igraph, ista.graph).
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Union

try:
    from ista import owl2

    HAS_OWL2 = owl2.is_available()
except ImportError:
    HAS_OWL2 = False


class ConversionStrategy(Enum):
    """Strategy for converting ontology to graph.

    Attributes
    ----------
    INDIVIDUALS_ONLY : str
        Only include individuals as nodes and object properties as edges.
        This is the most common use case for knowledge graphs.

    INCLUDE_CLASSES : str
        Include both individuals and classes as nodes. Class hierarchy
        is represented with edges.

    INCLUDE_PROPERTIES : str
        Include individuals, classes, and properties as nodes. This creates
        a more complete representation of the ontology structure.
    """

    INDIVIDUALS_ONLY = "individuals_only"
    INCLUDE_CLASSES = "include_classes"
    INCLUDE_PROPERTIES = "include_properties"


@dataclass
class ConversionOptions:
    """Configuration options for ontology to graph conversion.

    Attributes
    ----------
    strategy : ConversionStrategy
        The conversion strategy to use.

    include_data_properties : bool
        If True, include data property values as node attributes.
        Default: True

    include_annotations : bool
        If True, include annotation property values as node attributes.
        Default: False

    filter_classes : Optional[Set[str]]
        If provided, only include individuals of these classes.
        Classes should be specified as IRIs.
        Default: None (include all)

    include_inferred : bool
        If True, include inferred relationships (requires reasoning).
        Default: False

    data_property_prefix : str
        Prefix to use for data property attributes in nodes.
        Default: "data_"

    annotation_property_prefix : str
        Prefix to use for annotation property attributes in nodes.
        Default: "annot_"

    simplify_iris : bool
        If True, attempt to simplify IRIs to local names where possible.
        Default: True

    preserve_namespaces : bool
        If True, preserve namespace information in node/edge attributes.
        Default: False
    """

    strategy: ConversionStrategy = ConversionStrategy.INDIVIDUALS_ONLY
    include_data_properties: bool = True
    include_annotations: bool = False
    filter_classes: Optional[Set[str]] = None
    include_inferred: bool = False
    data_property_prefix: str = "data_"
    annotation_property_prefix: str = "annot_"
    simplify_iris: bool = True
    preserve_namespaces: bool = False


class OntologyToGraphConverter(ABC):
    """Abstract base class for ontology to graph converters.

    This class provides the core conversion logic that can be specialized
    for different graph backends.

    Parameters
    ----------
    ontology : owl2.Ontology
        The OWL2 ontology to convert.

    options : ConversionOptions
        Configuration options for the conversion.

    Examples
    --------
    >>> from ista import owl2
    >>> from ista.converters import ConversionOptions, ConversionStrategy
    >>>
    >>> ontology = owl2.Ontology("http://example.org/ontology")
    >>> options = ConversionOptions(
    ...     strategy=ConversionStrategy.INDIVIDUALS_ONLY,
    ...     include_data_properties=True
    ... )
    >>> # Subclass implements convert() method
    >>> converter = SomeGraphConverter(ontology, options)
    >>> graph = converter.convert()
    """

    def __init__(self, ontology: Any, options: Optional[ConversionOptions] = None):
        """Initialize the converter.

        Parameters
        ----------
        ontology : owl2.Ontology
            The OWL2 ontology to convert.

        options : ConversionOptions, optional
            Configuration options for the conversion.
            If None, default options are used.
        """
        if not HAS_OWL2:
            raise ImportError(
                "OWL2 library is not available. Please build the C++ extensions."
            )

        self.ontology = ontology
        self.options = options or ConversionOptions()
        self._node_map: Dict[str, Any] = {}
        self._edge_list: List[Dict[str, Any]] = []

    @abstractmethod
    def convert(self) -> Any:
        """Convert the ontology to a graph.

        Returns
        -------
        graph
            The converted graph. Type depends on the specific converter.
        """
        pass

    @abstractmethod
    def reverse_convert(self, graph: Any, ontology_iri: str) -> Any:
        """Convert a graph back to an ontology.

        Parameters
        ----------
        graph
            The graph to convert. Type depends on the specific converter.

        ontology_iri : str
            The IRI for the new ontology.

        Returns
        -------
        owl2.Ontology
            The converted ontology.
        """
        pass

    def _simplify_iri(self, iri: str) -> str:
        """Simplify an IRI to its local name if possible.

        Parameters
        ----------
        iri : str
            The full IRI to simplify.

        Returns
        -------
        str
            The simplified IRI (local name) if possible, otherwise the full IRI.
        """
        if not self.options.simplify_iris:
            return iri

        # Extract local name after last # or /
        if "#" in iri:
            return iri.split("#")[-1]
        elif "/" in iri:
            return iri.split("/")[-1]
        return iri

    def _get_namespace(self, iri: str) -> str:
        """Extract namespace from an IRI.

        Parameters
        ----------
        iri : str
            The IRI to extract namespace from.

        Returns
        -------
        str
            The namespace part of the IRI.
        """
        if "#" in iri:
            return iri.rsplit("#", 1)[0] + "#"
        elif "/" in iri:
            return iri.rsplit("/", 1)[0] + "/"
        return iri

    def _extract_individuals(self) -> List[Any]:
        """Extract all individuals from the ontology.

        Returns
        -------
        List[owl2.NamedIndividual]
            List of named individuals in the ontology.
        """
        individuals = []

        for axiom in self.ontology.axioms:
            if (
                hasattr(axiom, "__class__")
                and axiom.__class__.__name__ == "ClassAssertion"
            ):
                individual = axiom.individual
                if (
                    hasattr(individual, "__class__")
                    and individual.__class__.__name__ == "NamedIndividual"
                ):
                    if (
                        self.options.filter_classes is None
                        or str(axiom.class_expression.iri)
                        in self.options.filter_classes
                    ):
                        individuals.append(individual)

        return individuals

    def _extract_classes(self) -> List[Any]:
        """Extract all classes from the ontology.

        Returns
        -------
        List[owl2.Class]
            List of classes in the ontology.
        """
        classes = []

        for axiom in self.ontology.axioms:
            if (
                hasattr(axiom, "__class__")
                and axiom.__class__.__name__ == "Declaration"
            ):
                entity = axiom.entity
                if (
                    hasattr(entity, "__class__")
                    and entity.__class__.__name__ == "Class"
                ):
                    classes.append(entity)

        return classes

    def _extract_properties(self) -> Dict[str, List[Any]]:
        """Extract all properties from the ontology.

        Returns
        -------
        dict
            Dictionary with keys 'object', 'data', 'annotation' containing
            lists of respective property types.
        """
        properties = {"object": [], "data": [], "annotation": []}

        for axiom in self.ontology.axioms:
            if (
                hasattr(axiom, "__class__")
                and axiom.__class__.__name__ == "Declaration"
            ):
                entity = axiom.entity
                class_name = entity.__class__.__name__
                if class_name == "ObjectProperty":
                    properties["object"].append(entity)
                elif class_name == "DataProperty":
                    properties["data"].append(entity)
                elif class_name == "AnnotationProperty":
                    properties["annotation"].append(entity)

        return properties

    def _get_individual_classes(self, individual: Any) -> List[str]:
        """Get all classes that an individual is asserted to belong to.

        Parameters
        ----------
        individual : owl2.NamedIndividual
            The individual to get classes for.

        Returns
        -------
        List[str]
            List of class IRIs that the individual belongs to.
        """
        classes = []
        individual_iri = str(individual.iri)

        for axiom in self.ontology.axioms:
            if (
                hasattr(axiom, "__class__")
                and axiom.__class__.__name__ == "ClassAssertion"
            ):
                if str(axiom.individual.iri) == individual_iri:
                    class_iri = str(axiom.class_expression.iri)
                    classes.append(class_iri)

        return classes

    def _get_data_properties(self, individual: Any) -> Dict[str, Any]:
        """Get all data property values for an individual.

        Parameters
        ----------
        individual : owl2.NamedIndividual
            The individual to get data properties for.

        Returns
        -------
        dict
            Dictionary mapping property IRIs to their values.
        """
        data_props = {}
        individual_iri = str(individual.iri)

        for axiom in self.ontology.axioms:
            if (
                hasattr(axiom, "__class__")
                and axiom.__class__.__name__ == "DataPropertyAssertion"
            ):
                if str(axiom.source.iri) == individual_iri:
                    prop_iri = str(axiom.property.iri)
                    prop_name = self._simplify_iri(prop_iri)
                    value = axiom.target.value

                    if self.options.data_property_prefix:
                        prop_name = self.options.data_property_prefix + prop_name

                    data_props[prop_name] = value

        return data_props

    def _get_object_properties(self, individual: Any) -> List[Dict[str, str]]:
        """Get all object property assertions involving an individual.

        Parameters
        ----------
        individual : owl2.NamedIndividual
            The individual to get object properties for.

        Returns
        -------
        List[dict]
            List of dictionaries with keys 'property', 'target' containing
            the property IRI and target individual IRI.
        """
        object_props = []
        individual_iri = str(individual.iri)

        for axiom in self.ontology.axioms:
            if (
                hasattr(axiom, "__class__")
                and axiom.__class__.__name__ == "ObjectPropertyAssertion"
            ):
                if str(axiom.source.iri) == individual_iri:
                    prop_iri = str(axiom.property.iri)
                    target_iri = str(axiom.target.iri)
                    object_props.append({"property": prop_iri, "target": target_iri})

        return object_props

    def _get_annotations(self, entity: Any) -> Dict[str, Any]:
        """Get all annotation property values for an entity.

        Parameters
        ----------
        entity : owl2.Entity
            The entity to get annotations for.

        Returns
        -------
        dict
            Dictionary mapping annotation property IRIs to their values.
        """
        annotations = {}
        entity_iri = str(entity.iri)

        for axiom in self.ontology.axioms:
            if (
                hasattr(axiom, "__class__")
                and axiom.__class__.__name__ == "AnnotationAssertion"
            ):
                if str(axiom.subject) == entity_iri:
                    prop_iri = str(axiom.property.iri)
                    prop_name = self._simplify_iri(prop_iri)

                    # Handle different value types
                    if hasattr(axiom.value, "value"):
                        value = axiom.value.value
                    else:
                        value = str(axiom.value)

                    if self.options.annotation_property_prefix:
                        prop_name = self.options.annotation_property_prefix + prop_name

                    annotations[prop_name] = value

        return annotations

    def _build_node_attributes(self, entity: Any, entity_type: str) -> Dict[str, Any]:
        """Build attribute dictionary for a node.

        Parameters
        ----------
        entity : owl2.Entity
            The entity to build attributes for.

        entity_type : str
            The type of entity ('individual', 'class', 'property').

        Returns
        -------
        dict
            Dictionary of node attributes.
        """
        attributes = {
            "iri": str(entity.iri),
            "type": entity_type,
            "label": self._simplify_iri(str(entity.iri)),
        }

        if self.options.preserve_namespaces:
            attributes["namespace"] = self._get_namespace(str(entity.iri))

        if entity_type == "individual":
            # Add class membership
            classes = self._get_individual_classes(entity)
            attributes["classes"] = classes

            # Add data properties
            if self.options.include_data_properties:
                data_props = self._get_data_properties(entity)
                attributes.update(data_props)

        # Add annotations
        if self.options.include_annotations:
            annotations = self._get_annotations(entity)
            attributes.update(annotations)

        return attributes
