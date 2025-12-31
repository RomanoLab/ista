"""
OWL2 ontology manipulation using the libista C++ library.

This module provides Python bindings to the high-performance C++ OWL2 library,
offering an alternative to owlready2 for OWL ontology manipulation.

The `ista.owl2` module is the single public interface for all OWL2 functionality,
including:
- Core ontology types (IRI, Literal, Class, ObjectProperty, etc.)
- Axiom types (ClassAssertion, SubClassOf, etc.)
- Ontology creation and manipulation
- Serialization (RDF/XML, Functional Syntax)
- Parsing (RDF/XML)
- High-performance subgraph extraction (OntologyFilter)

Example
-------
Basic usage:

    >>> from ista import owl2
    >>>
    >>> # Create an ontology
    >>> ont = owl2.Ontology(owl2.IRI("http://example.org/test"))
    >>>
    >>> # Add classes and individuals
    >>> person_cls = owl2.Class(owl2.IRI("http://example.org/test#Person"))
    >>> alice = owl2.NamedIndividual(owl2.IRI("http://example.org/test#Alice"))
    >>> ont.add_axiom(owl2.ClassAssertion(person_cls, alice))
    >>>
    >>> # Serialize
    >>> rdf_xml = owl2.RDFXMLSerializer.serialize(ont)
    >>>
    >>> # Filter/extract subgraphs
    >>> filter_obj = owl2.OntologyFilter(ont)
    >>> result = filter_obj.extract_neighborhood(alice.get_iri(), depth=2)

Notes
-----
This module wraps the low-level `_libista_owl2` C++ extension module.
Always import from `ista.owl2`, never from `_libista_owl2` directly.
"""

try:
    # Import everything from the C++ extension
    from _libista_owl2 import *

    # Import specific items to ensure they're available
    from _libista_owl2 import (
        ANNOTATION_PROPERTY,
        # Entity type constants
        CLASS,
        DATA_PROPERTY,
        DATATYPE,
        # Core types
        IRI,
        NAMED_INDIVIDUAL,
        OBJECT_PROPERTY,
        # Axioms
        Axiom,
        Class,
        ClassAssertion,
        # Class Expressions
        ClassExpression,
        DataLoader,
        DataLoaderException,
        DataMappingSpec,
        DataProperty,
        DataPropertyAssertion,
        DataPropertyDomain,
        DataPropertyRange,
        DataSourceDef,
        Declaration,
        # Entities
        Entity,
        EntityRef,
        EntityType,
        FilterCriteria,
        FilterDef,
        FilterResult,
        FunctionalDataProperty,
        FunctionalObjectProperty,
        # Serializers & Parsers
        FunctionalSyntaxSerializer,
        Literal,
        LoadingStats,
        # Data Loading
        MappingMode,
        MappingSpecException,
        MatchCriteria,
        NamedClass,
        NamedIndividual,
        NodeMapping,
        ObjectProperty,
        ObjectPropertyAssertion,
        ObjectPropertyDomain,
        ObjectPropertyRange,
        # Ontology
        Ontology,
        # Subgraph extraction (high-performance C++ filtering)
        OntologyFilter,
        PropertyMapping,
        RDFXMLParseException,
        RDFXMLParser,
        RDFXMLSerializer,
        RelationshipMapping,
        SubClassOf,
        TransformDef,
        TurtleParseException,
        TurtleParser,
        TurtleSerializer,
        ValidationResult,
        YamlParseException,
        # Constants
        xsd,
    )

    HAS_CPP_BINDINGS = True

except ImportError as e:
    HAS_CPP_BINDINGS = False
    _import_error = str(e)

    # Provide helpful error message
    import warnings

    warnings.warn(
        f"C++ OWL2 library not available: {_import_error}\n"
        "The C++ extension was not built. Install with: pip install -e .\n"
        "Or build manually: mkdir build && cd build && cmake .. && cmake --build .",
        ImportWarning,
    )


def is_available():
    """
    Check if C++ OWL2 bindings are available.

    Returns
    -------
    bool
        True if the C++ extension is loaded and functional, False otherwise.

    Examples
    --------
    >>> from ista import owl2
    >>> if owl2.is_available():
    ...     ont = owl2.Ontology()
    ... else:
    ...     print("Please build the C++ extension")
    """
    return HAS_CPP_BINDINGS


# Define public API
if HAS_CPP_BINDINGS:
    __all__ = [
        # Core types
        "IRI",
        "Literal",
        # Entities
        "Entity",
        "EntityType",
        "Class",
        "ObjectProperty",
        "DataProperty",
        "NamedIndividual",
        # Class Expressions
        "ClassExpression",
        "NamedClass",
        # Axioms
        "Axiom",
        "Declaration",
        "SubClassOf",
        "ClassAssertion",
        "ObjectPropertyAssertion",
        "DataPropertyAssertion",
        "ObjectPropertyDomain",
        "ObjectPropertyRange",
        "DataPropertyDomain",
        "DataPropertyRange",
        "FunctionalObjectProperty",
        "FunctionalDataProperty",
        # Ontology
        "Ontology",
        # Serializers & Parsers
        "FunctionalSyntaxSerializer",
        "RDFXMLSerializer",
        "RDFXMLParser",
        "RDFXMLParseException",
        "TurtleSerializer",
        "TurtleParser",
        "TurtleParseException",
        # Subgraph extraction
        "OntologyFilter",
        "FilterCriteria",
        "FilterResult",
        # Constants
        "xsd",
        "CLASS",
        "OBJECT_PROPERTY",
        "DATA_PROPERTY",
        "NAMED_INDIVIDUAL",
        "DATATYPE",
        "ANNOTATION_PROPERTY",
        # Data Loading
        "MappingMode",
        "FilterDef",
        "MatchCriteria",
        "PropertyMapping",
        "DataSourceDef",
        "NodeMapping",
        "EntityRef",
        "RelationshipMapping",
        "TransformDef",
        "ValidationResult",
        "LoadingStats",
        "DataMappingSpec",
        "DataLoader",
        "MappingSpecException",
        "DataLoaderException",
        "YamlParseException",
        # Utilities
        "is_available",
    ]
else:
    __all__ = ["is_available"]
