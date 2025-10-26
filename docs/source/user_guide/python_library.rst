Python Library Guide
====================

The ista Python library provides a comprehensive interface for working with OWL2 ontologies
and knowledge graphs. This guide covers the main features and usage patterns.

Overview
--------

The Python library is organized into several modules:

- **ista.owl2** - Core OWL2 ontology manipulation
- **ista.converters** - Convert between different graph formats
- **ista.database_parser** - Parse databases into knowledge graphs
- **ista.graph** - Graph utilities and operations

Core Components
---------------

IRI (Internationalized Resource Identifier)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

IRIs uniquely identify resources in OWL2 ontologies:

.. code-block:: python

    from ista import owl2

    # Create IRI from full URL
    iri1 = owl2.IRI("http://example.org/ontology#Disease")

    # Create IRI with prefix and name
    iri2 = owl2.IRI("ex", "Disease", "http://example.org/ontology#")

    # Get components
    print(iri1.get_namespace())  # http://example.org/ontology#
    print(iri1.get_short_form())  # Disease

Literals
~~~~~~~~

Literals represent data values with optional datatypes:

.. code-block:: python

    # String literal
    name = owl2.Literal("Alzheimer's Disease")

    # Typed literal
    age = owl2.Literal("65", datatype=owl2.IRI("xsd", "integer", "..."))

    # Language-tagged literal
    label_en = owl2.Literal("Disease", language="en")

Ontology Container
------------------

The Ontology class is the main container for OWL2 axioms:

.. code-block:: python

    from ista import owl2

    # Create a new ontology
    ont = owl2.Ontology(owl2.IRI("http://example.org/biomedical"))

    # Add axioms
    disease_iri = owl2.IRI("ex", "Disease", "http://example.org/")
    ont.add_axiom(owl2.Declaration(owl2.CLASS, disease_iri))

    # Query axioms
    count = ont.get_axiom_count()
    axioms = ont.get_axioms()

    # Check if axiom exists
    has_axiom = ont.contains_axiom(axiom)

Entity Types
------------

Classes
~~~~~~~

OWL2 classes represent sets of individuals:

.. code-block:: python

    # Declare a class
    disease = owl2.Class(owl2.IRI("ex", "Disease", "..."))
    ont.add_axiom(owl2.Declaration(owl2.CLASS, disease.get_iri()))

    # Subclass axiom
    alzheimers = owl2.Class(owl2.IRI("ex", "AlzheimersDisease", "..."))
    ont.add_axiom(owl2.SubClassOf(alzheimers, disease))

Object Properties
~~~~~~~~~~~~~~~~~

Object properties relate individuals to other individuals:

.. code-block:: python

    # Declare object property
    causes = owl2.ObjectProperty(owl2.IRI("ex", "causes", "..."))
    ont.add_axiom(owl2.Declaration(owl2.OBJECT_PROPERTY, causes.get_iri()))

    # Property characteristics
    ont.add_axiom(owl2.TransitiveObjectProperty(causes))
    ont.add_axiom(owl2.AsymmetricObjectProperty(causes))

Data Properties
~~~~~~~~~~~~~~~

Data properties relate individuals to literal values:

.. code-block:: python

    # Declare data property
    has_age = owl2.DataProperty(owl2.IRI("ex", "hasAge", "..."))
    ont.add_axiom(owl2.Declaration(owl2.DATA_PROPERTY, has_age.get_iri()))

    # Domain and range
    ont.add_axiom(owl2.DataPropertyDomain(has_age, person_class))
    ont.add_axiom(owl2.DataPropertyRange(has_age, xsd_integer))

Individuals
~~~~~~~~~~~

Named individuals are instances of classes:

.. code-block:: python

    # Declare individual
    john = owl2.NamedIndividual(owl2.IRI("ex", "John", "..."))
    ont.add_axiom(owl2.Declaration(owl2.NAMED_INDIVIDUAL, john.get_iri()))

    # Class assertion
    ont.add_axiom(owl2.ClassAssertion(person_class, john))

    # Property assertions
    ont.add_axiom(owl2.ObjectPropertyAssertion(knows_prop, john, mary))
    ont.add_axiom(owl2.DataPropertyAssertion(has_age, john, owl2.Literal("30")))

Class Expressions
-----------------

OWL2 supports complex class expressions:

.. code-block:: python

    # Intersection (AND)
    expr1 = owl2.ObjectIntersectionOf([class1, class2, class3])

    # Union (OR)
    expr2 = owl2.ObjectUnionOf([class1, class2])

    # Complement (NOT)
    expr3 = owl2.ObjectComplementOf(class1)

    # Existential restriction (∃)
    expr4 = owl2.ObjectSomeValuesFrom(has_part, protein_class)

    # Universal restriction (∀)
    expr5 = owl2.ObjectAllValuesFrom(has_part, protein_class)

    # Cardinality restrictions
    expr6 = owl2.ObjectMinCardinality(2, has_part, protein_class)
    expr7 = owl2.ObjectMaxCardinality(5, has_part, protein_class)
    expr8 = owl2.ObjectExactCardinality(3, has_part, protein_class)

Serialization
-------------

Save and Load Ontologies
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from ista.owl2 import FunctionalSyntaxSerializer, FunctionalSyntaxParser

    # Save to file
    serializer = FunctionalSyntaxSerializer()
    serializer.serialize(ont, "output.ofn")

    # Load from file
    parser = FunctionalSyntaxParser()
    loaded_ont = parser.parse("output.ofn")

Subgraph Extraction
-------------------

Extract relevant portions of large ontologies:

.. code-block:: python

    from ista.owl2 import OntologyFilter, FilterCriteria, FilterResult

    # Create filter
    filter_obj = OntologyFilter(ontology)

    # Extract neighborhood around an IRI
    seed_iri = owl2.IRI("ex", "AlzheimersDisease", "...")
    result = filter_obj.extract_neighborhood(
        seed_iri=seed_iri,
        depth=2,
        include_superclasses=True,
        include_subclasses=True
    )

    # Extract by criteria
    criteria = FilterCriteria()
    criteria.add_iri_pattern(".*Disease.*")  # Regex pattern
    result = filter_obj.extract_by_criteria(criteria)

    # Get resulting ontology
    subgraph_ont = result.get_ontology()
    included_iris = result.get_included_iris()

Graph Conversion
----------------

Convert ontologies to graph formats:

.. code-block:: python

    from ista.converters import ontology_to_networkx, ontology_to_dataframe
    import networkx as nx

    # Convert to NetworkX graph
    G = ontology_to_networkx(ontology)

    # Analyze with NetworkX
    print(f"Nodes: {G.number_of_nodes()}")
    print(f"Edges: {G.number_of_edges()}")
    print(f"Connected: {nx.is_connected(G.to_undirected())}")

    # Convert to pandas DataFrame
    df = ontology_to_dataframe(ontology)
    print(df.head())

Database Parsing
----------------

Parse structured databases into knowledge graphs:

.. code-block:: python

    from ista.database_parser import DatabaseParser

    # Parse Excel/CSV database
    parser = DatabaseParser("disease_database.xlsx")

    # Configure entity extraction
    parser.set_entity_column("Disease Name")
    parser.set_property_mappings({
        "Symptoms": "hasSymptom",
        "Treatments": "hasTreatment",
        "Genes": "associatedWithGene"
    })

    # Generate ontology
    ont = parser.to_ontology()

Best Practices
--------------

1. **IRI Management**: Use consistent IRI patterns with prefixes
2. **Axiom Organization**: Group related axioms together
3. **Memory Efficiency**: Use subgraph extraction for large ontologies
4. **Validation**: Check axiom consistency before serialization
5. **Documentation**: Add rdfs:label and rdfs:comment annotations

Common Patterns
---------------

Building an Ontology from Scratch
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from ista import owl2

    # Initialize
    base_iri = "http://example.org/bio#"
    ont = owl2.Ontology(owl2.IRI(base_iri + "ontology"))

    # Helper function for IRIs
    def make_iri(name):
        return owl2.IRI("bio", name, base_iri)

    # Define classes
    protein = owl2.Class(make_iri("Protein"))
    enzyme = owl2.Class(make_iri("Enzyme"))

    ont.add_axiom(owl2.Declaration(owl2.CLASS, protein.get_iri()))
    ont.add_axiom(owl2.Declaration(owl2.CLASS, enzyme.get_iri()))
    ont.add_axiom(owl2.SubClassOf(enzyme, protein))

    # Add annotations
    ont.add_axiom(owl2.AnnotationAssertion(
        owl2.IRI("rdfs", "label", "..."),
        protein.get_iri(),
        owl2.Literal("Protein", language="en")
    ))

    # Save
    serializer = owl2.FunctionalSyntaxSerializer()
    serializer.serialize(ont, "biomedical.ofn")

See Also
--------

- :doc:`owl2_interfaces` - Detailed OWL2 interface documentation
- :doc:`subgraph_extraction` - Advanced subgraph extraction techniques
- :doc:`graph_converters` - Graph conversion utilities
- :doc:`../api/owl2` - Complete API reference
