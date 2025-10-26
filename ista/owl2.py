"""
OWL2 ontology manipulation using the libista C++ library.

This module provides Python bindings to the high-performance C++ OWL2 library,
offering an alternative to owlready2 for OWL ontology manipulation.
"""

try:
    from _libista_owl2 import *
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
        ImportWarning
    )


def is_available():
    """Check if C++ OWL2 bindings are available."""
    return HAS_CPP_BINDINGS


if HAS_CPP_BINDINGS:
    __all__ = [
        # Core types
        'IRI',
        'Literal',
        
        # Entities
        'Entity',
        'Class',
        'Datatype',
        'ObjectProperty',
        'DataProperty',
        'AnnotationProperty',
        'NamedIndividual',
        'AnonymousIndividual',
        
        # Class Expressions
        'ClassExpression',
        'NamedClass',
        'ObjectIntersectionOf',
        'ObjectUnionOf',
        'ObjectSomeValuesFrom',
        'ObjectAllValuesFrom',
        
        # Data Ranges
        'DataRange',
        'NamedDatatype',
        'DataIntersectionOf',
        'DataUnionOf',
        
        # Annotations
        'Annotation',
        
        # Axioms
        'Axiom',
        'Declaration',
        'EntityType',
        'SubClassOf',
        'EquivalentClasses',
        'DisjointClasses',
        'DisjointUnion',
        'SubObjectPropertyOf',
        'EquivalentObjectProperties',
        'DisjointObjectProperties',
        'InverseObjectProperties',
        'ObjectPropertyDomain',
        'ObjectPropertyRange',
        'FunctionalObjectProperty',
        'InverseFunctionalObjectProperty',
        'ReflexiveObjectProperty',
        'IrreflexiveObjectProperty',
        'SymmetricObjectProperty',
        'AsymmetricObjectProperty',
        'TransitiveObjectProperty',
        'SubDataPropertyOf',
        'EquivalentDataProperties',
        'DisjointDataProperties',
        'DataPropertyDomain',
        'DataPropertyRange',
        'FunctionalDataProperty',
        'ClassAssertion',
        'ObjectPropertyAssertion',
        'DataPropertyAssertion',
        'SameIndividual',
        'DifferentIndividuals',
        'AnnotationAssertion',
        
        # Ontology
        'Ontology',
        
        # Serializers
        'FunctionalSyntaxSerializer',
        'RDFXMLSerializer',
        
        # Constants
        'xsd',
        'facets',
        
        # Utilities
        'is_available',
    ]
else:
    __all__ = ['is_available']
