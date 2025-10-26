"""
libista_owl2 - Python bindings for the libista OWL2 library

This module provides Python bindings for working with OWL2 ontologies using
the native C++ libista library.

Example usage:
    >>> from libista_owl2 import IRI, Class, Ontology, Declaration, EntityType
    >>>
    >>> # Create an ontology
    >>> onto = Ontology(IRI("http://example.org/myontology"))
    >>> onto.register_prefix("ex", "http://example.org/myontology#")
    >>>
    >>> # Create classes
    >>> person_cls = Class(IRI("ex", "Person", "http://example.org/myontology#"))
    >>>
    >>> # Add declarations
    >>> decl = Declaration(EntityType.CLASS, person_cls.get_iri())
    >>> onto.add_axiom(decl)
    >>>
    >>> # Serialize to functional syntax
    >>> print(onto.to_functional_syntax())
"""

from _libista_owl2 import *

__version__ = "0.1.0"
__author__ = "ISTA OWL2 Library Contributors"

# Re-export all public symbols
__all__ = [
    # Core classes
    "IRI",
    "Entity",
    "Class",
    "Datatype",
    "ObjectProperty",
    "DataProperty",
    "AnnotationProperty",
    "NamedIndividual",
    "AnonymousIndividual",
    # Literal
    "Literal",
    # Annotations
    "Annotation",
    # Data Ranges
    "DataRange",
    "NamedDatatype",
    "DataIntersectionOf",
    "DataUnionOf",
    "DataComplementOf",
    "DataOneOf",
    "DatatypeRestriction",
    # Class Expressions
    "ClassExpression",
    "NamedClass",
    "ObjectIntersectionOf",
    "ObjectUnionOf",
    "ObjectSomeValuesFrom",
    "ObjectAllValuesFrom",
    # Axioms
    "Axiom",
    "EntityType",
    "Declaration",
    # Class Axioms
    "SubClassOf",
    "EquivalentClasses",
    "DisjointClasses",
    "DisjointUnion",
    # Object Property Axioms
    "SubObjectPropertyOf",
    "EquivalentObjectProperties",
    "DisjointObjectProperties",
    "InverseObjectProperties",
    "ObjectPropertyDomain",
    "ObjectPropertyRange",
    "FunctionalObjectProperty",
    "InverseFunctionalObjectProperty",
    "ReflexiveObjectProperty",
    "IrreflexiveObjectProperty",
    "SymmetricObjectProperty",
    "AsymmetricObjectProperty",
    "TransitiveObjectProperty",
    # Data Property Axioms
    "SubDataPropertyOf",
    "EquivalentDataProperties",
    "DisjointDataProperties",
    "DataPropertyDomain",
    "DataPropertyRange",
    "FunctionalDataProperty",
    # Other Axioms
    "DatatypeDefinition",
    "HasKey",
    # Assertion Axioms
    "SameIndividual",
    "DifferentIndividuals",
    "ClassAssertion",
    "ObjectPropertyAssertion",
    "NegativeObjectPropertyAssertion",
    "DataPropertyAssertion",
    "NegativeDataPropertyAssertion",
    # Annotation Axioms
    "AnnotationAssertion",
    "SubAnnotationPropertyOf",
    "AnnotationPropertyDomain",
    "AnnotationPropertyRange",
    # Ontology
    "Ontology",
    # Serializer
    "FunctionalSyntaxSerializer",
    # Helper functions
    "format_object_property_expression",
    "format_individual",
    "format_annotation_subject",
    "format_annotation_value",
]
