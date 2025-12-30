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
    disease_class = owl2.Class(disease_iri)
    declaration = owl2.Declaration(owl2.Declaration.EntityType.CLASS, disease_iri)
    ont.add_axiom(declaration)

    # Query axioms
    count = ont.get_axiom_count()
    axioms = ont.get_axioms()

    # Check if axiom exists
    has_axiom = ont.contains_axiom(declaration)

Entity Types
------------

Classes
~~~~~~~

OWL2 classes represent sets of individuals:

.. code-block:: python

    # Declare a class
    disease_iri = owl2.IRI("ex", "Disease", "http://example.org/")
    disease = owl2.Class(disease_iri)
    declaration = owl2.Declaration(owl2.Declaration.EntityType.CLASS, disease_iri)
    ont.add_axiom(declaration)

    # Subclass axiom
    alzheimers_iri = owl2.IRI("ex", "AlzheimersDisease", "http://example.org/")
    alzheimers = owl2.Class(alzheimers_iri)
    alzheimers_decl = owl2.Declaration(owl2.Declaration.EntityType.CLASS, alzheimers_iri)
    ont.add_axiom(alzheimers_decl)

    subclass_axiom = owl2.SubClassOf(owl2.NamedClass(alzheimers), owl2.NamedClass(disease))
    ont.add_axiom(subclass_axiom)

Object Properties
~~~~~~~~~~~~~~~~~

Object properties relate individuals to other individuals:

.. code-block:: python

    # Declare object property
    causes_iri = owl2.IRI("ex", "causes", "http://example.org/")
    causes = owl2.ObjectProperty(causes_iri)
    declaration = owl2.Declaration(owl2.Declaration.EntityType.OBJECT_PROPERTY, causes_iri)
    ont.add_axiom(declaration)

    # Property characteristics
    transitive_axiom = owl2.TransitiveObjectProperty(causes)
    ont.add_axiom(transitive_axiom)

    asymmetric_axiom = owl2.AsymmetricObjectProperty(causes)
    ont.add_axiom(asymmetric_axiom)

Data Properties
~~~~~~~~~~~~~~~

Data properties relate individuals to literal values:

.. code-block:: python

    # Declare data property
    has_age_iri = owl2.IRI("ex", "hasAge", "http://example.org/")
    has_age = owl2.DataProperty(has_age_iri)
    declaration = owl2.Declaration(owl2.Declaration.EntityType.DATA_PROPERTY, has_age_iri)
    ont.add_axiom(declaration)

    # Domain and range
    person_class = owl2.NamedClass(owl2.Class(owl2.IRI("ex", "Person", "http://example.org/")))
    domain_axiom = owl2.DataPropertyDomain(has_age, person_class)
    ont.add_axiom(domain_axiom)

    xsd_integer = owl2.Datatype(owl2.IRI("http://www.w3.org/2001/XMLSchema#integer"))
    range_axiom = owl2.DataPropertyRange(has_age, xsd_integer)
    ont.add_axiom(range_axiom)

Individuals
~~~~~~~~~~~

Named individuals are instances of classes:

.. code-block:: python

    # Create individual with class assertion
    john_iri = owl2.IRI("ex", "John", "http://example.org/")
    person_class = owl2.Class(owl2.IRI("ex", "Person", "http://example.org/"))
    john = ont.create_individual(person_class, john_iri)

    # Add property assertions
    knows_prop = owl2.ObjectProperty(owl2.IRI("ex", "knows", "http://example.org/"))
    mary = owl2.NamedIndividual(owl2.IRI("ex", "Mary", "http://example.org/"))
    ont.add_object_property_assertion(john, knows_prop, mary)

    has_age = owl2.DataProperty(owl2.IRI("ex", "hasAge", "http://example.org/"))
    age_value = owl2.Literal("30")
    ont.add_data_property_assertion(john, has_age, age_value)

Querying Individuals
~~~~~~~~~~~~~~~~~~~~~

Search and query individuals in the ontology:

.. code-block:: python

    # Search by data property value
    has_name = owl2.DataProperty(owl2.IRI("ex", "hasName", "http://example.org/"))
    name_value = owl2.Literal("John")
    results = ont.search_by_data_property(has_name, name_value)

    # Search by object property
    knows_prop = owl2.ObjectProperty(owl2.IRI("ex", "knows", "http://example.org/"))
    mary = owl2.NamedIndividual(owl2.IRI("ex", "Mary", "http://example.org/"))
    results = ont.search_by_object_property(knows_prop, mary)

    # Get all property assertions for an individual
    data_props = ont.get_data_property_assertions_for_individual(john)
    obj_props = ont.get_object_property_assertions_for_individual(john)

    # Check class membership
    person_class = owl2.Class(owl2.IRI("ex", "Person", "http://example.org/"))
    is_person = ont.is_instance_of(john, person_class)

    # Get all classes for an individual
    classes = ont.get_classes_for_individual(john)

Class Expressions
-----------------

OWL2 supports complex class expressions:

.. code-block:: python

    # Intersection (AND)
    class1 = owl2.NamedClass(owl2.Class(owl2.IRI("ex", "Class1", "http://example.org/")))
    class2 = owl2.NamedClass(owl2.Class(owl2.IRI("ex", "Class2", "http://example.org/")))
    class3 = owl2.NamedClass(owl2.Class(owl2.IRI("ex", "Class3", "http://example.org/")))
    expr1 = owl2.ObjectIntersectionOf([class1, class2, class3])

    # Union (OR)
    expr2 = owl2.ObjectUnionOf([class1, class2])

    # Complement (NOT)
    expr3 = owl2.ObjectComplementOf(class1)

    # Existential restriction (∃)
    has_part = owl2.ObjectProperty(owl2.IRI("ex", "hasPart", "http://example.org/"))
    protein_class = owl2.NamedClass(owl2.Class(owl2.IRI("ex", "Protein", "http://example.org/")))
    expr4 = owl2.ObjectSomeValuesFrom(has_part, protein_class)

    # Universal restriction (∀)
    expr5 = owl2.ObjectAllValuesFrom(has_part, protein_class)

    # Cardinality restrictions
    expr6 = owl2.ObjectMinCardinality(2, has_part, protein_class)
    expr7 = owl2.ObjectMaxCardinality(5, has_part, protein_class)
    expr8 = owl2.ObjectExactCardinality(3, has_part, protein_class)

Parsing and Serialization
--------------------------

Load and Save Ontologies
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from ista.owl2 import RDFXMLParser, RDFXMLSerializer
    from ista.owl2 import FunctionalSyntaxParser, FunctionalSyntaxSerializer

    # Parse RDF/XML
    parser = RDFXMLParser()
    ont = parser.parse_from_file("ontology.rdf")

    # Parse Functional Syntax
    parser = FunctionalSyntaxParser()
    ont = parser.parse_from_file("ontology.ofn")

    # Serialize to RDF/XML
    serializer = RDFXMLSerializer()
    rdf_content = serializer.serialize(ont)
    with open("output.rdf", "w") as f:
        f.write(rdf_content)

    # Serialize to Functional Syntax
    serializer = FunctionalSyntaxSerializer()
    ofn_content = serializer.serialize(ont)
    with open("output.ofn", "w") as f:
        f.write(ofn_content)

Subgraph Extraction
-------------------

Extract relevant portions of large ontologies:

.. code-block:: python

    from ista.owl2 import OntologyFilter, FilterCriteria

    # Create filter
    filter_obj = OntologyFilter(ontology)

    # Extract neighborhood around an IRI
    seed_iri = owl2.IRI("ex", "AlzheimersDisease", "http://example.org/")
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

Parse structured databases into knowledge graphs. See :doc:`database_parsing` for detailed documentation.

.. code-block:: python

    from ista import owl2
    from ista.database_parser import FlatFileDatabaseParser

    # Load base ontology
    ont = owl2.RDFXMLParser().parse_from_file("base_ontology.rdf")

    # Parse CSV/TSV/Excel file
    parser = FlatFileDatabaseParser(ont)

    parse_config = {
        "file_path": "diseases.csv",
        "entity_class_iri": "http://example.org/Disease",
        "id_column": "DiseaseID",
        "property_mappings": {
            "Name": {"property_iri": "http://example.org/hasName", "is_data_property": True},
            "Symptom": {"property_iri": "http://example.org/hasSymptom", "is_data_property": True}
        }
    }

    parser.parse(parse_config)

    # Save updated ontology
    serializer = owl2.RDFXMLSerializer()
    rdf_content = serializer.serialize(ont)
    with open("populated_ontology.rdf", "w") as f:
        f.write(rdf_content)

Best Practices
--------------

1. **IRI Management**: Use consistent IRI patterns with prefixes
2. **Axiom Organization**: Group related axioms together
3. **Memory Efficiency**: Use subgraph extraction for large ontologies
4. **Property Assertions**: Use ``create_individual()`` to automatically add declarations and class assertions
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
    protein_iri = make_iri("Protein")
    protein = owl2.Class(protein_iri)

    enzyme_iri = make_iri("Enzyme")
    enzyme = owl2.Class(enzyme_iri)

    # Declare classes
    ont.add_axiom(owl2.Declaration(owl2.Declaration.EntityType.CLASS, protein_iri))
    ont.add_axiom(owl2.Declaration(owl2.Declaration.EntityType.CLASS, enzyme_iri))

    # Add subclass relationship
    subclass_axiom = owl2.SubClassOf(owl2.NamedClass(enzyme), owl2.NamedClass(protein))
    ont.add_axiom(subclass_axiom)

    # Add annotations
    rdfs_label = owl2.AnnotationProperty(owl2.IRI("http://www.w3.org/2000/01/rdf-schema#label"))
    label_value = owl2.Literal("Protein", language="en")
    annotation_assertion = owl2.AnnotationAssertion(rdfs_label, protein_iri, label_value)
    ont.add_axiom(annotation_assertion)

    # Save
    serializer = owl2.RDFXMLSerializer()
    rdf_content = serializer.serialize(ont)
    with open("biomedical.rdf", "w") as f:
        f.write(rdf_content)

Working with Utility Functions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``ista.util`` module provides helper functions for common operations:

.. code-block:: python

    from ista import owl2
    from ista.util import safe_add_property, get_onto_class_by_node_type

    # Safely add property (checks for duplicates)
    ont = owl2.Ontology(owl2.IRI("http://example.org/onto"))
    individual = owl2.NamedIndividual(owl2.IRI("http://example.org/John"))
    prop = owl2.DataProperty(owl2.IRI("http://example.org/hasName"))
    value = owl2.Literal("John")

    safe_add_property(ont, individual, prop, value)

    # Get class by type name
    classes = ont.get_classes()
    disease_class = get_onto_class_by_node_type(classes, "Disease")

See Also
--------

- :doc:`owl2_interfaces` - Detailed OWL2 interface documentation
- :doc:`database_parsing` - Database parsing guide
- :doc:`subgraph_extraction` - Advanced subgraph extraction techniques
- :doc:`graph_converters` - Graph conversion utilities
- :doc:`../api/owl2` - Complete API reference
