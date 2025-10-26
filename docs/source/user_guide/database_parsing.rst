Database Parsing
================

The ista database parser enables conversion of structured databases (Excel, CSV, JSON) into
OWL2 ontologies. This facilitates integration of existing knowledge bases and data sources
into formal ontologies.

Overview
--------

The database parser provides:

- **Automatic Entity Extraction**: Identify entities from database columns
- **Relationship Mapping**: Map database relationships to OWL2 properties
- **Flexible Configuration**: Customize parsing rules and mappings
- **Data Type Handling**: Properly handle different data types
- **Batch Processing**: Efficiently process large databases

Supported Formats
-----------------

- Excel files (.xlsx, .xls)
- CSV files (.csv)
- TSV files (.tsv)
- JSON files (.json)
- Pandas DataFrames (in-memory)

DatabaseParser Class
--------------------

Basic Usage
~~~~~~~~~~~

.. code-block:: python

    from ista.database_parser import DatabaseParser
    from ista import owl2

    # Load database
    parser = DatabaseParser("disease_database.xlsx")

    # Configure entity extraction
    parser.set_entity_column("Disease Name")

    # Generate ontology
    ont = parser.to_ontology()

    # Save result
    serializer = owl2.FunctionalSyntaxSerializer()
    serializer.serialize(ont, "diseases.ofn")

Configuration
~~~~~~~~~~~~~

.. code-block:: python

    # Set base IRI
    parser.set_base_iri("http://example.org/diseases#")

    # Set entity column (primary entities)
    parser.set_entity_column("Disease Name")

    # Set entity type
    parser.set_entity_type(owl2.EntityType.CLASS)

    # Set property mappings
    parser.set_property_mappings({
        "Symptoms": "hasSymptom",
        "Treatments": "hasTreatment",
        "Genes": "associatedWithGene",
        "Prevalence": "hasPrevalence"
    })

Entity Extraction
-----------------

Single Entity Column
~~~~~~~~~~~~~~~~~~~~

Extract entities from one primary column:

.. code-block:: python

    # Disease database example
    parser = DatabaseParser("diseases.xlsx")
    parser.set_entity_column("Disease Name")
    parser.set_base_iri("http://example.org/bio#")

    # Each row becomes a class
    # "Alzheimer's Disease" -> bio:AlzheimersDisease
    ont = parser.to_ontology()

Multiple Entity Columns
~~~~~~~~~~~~~~~~~~~~~~~~

Extract different entity types from different columns:

.. code-block:: python

    parser = DatabaseParser("interactions.csv")

    # Proteins as named individuals
    parser.add_entity_column(
        column_name="Protein A",
        entity_type=owl2.EntityType.NAMED_INDIVIDUAL,
        iri_prefix="protein"
    )

    # Also extract Protein B
    parser.add_entity_column(
        column_name="Protein B",
        entity_type=owl2.EntityType.NAMED_INDIVIDUAL,
        iri_prefix="protein"
    )

    # Interaction types as classes
    parser.add_entity_column(
        column_name="Interaction Type",
        entity_type=owl2.EntityType.CLASS,
        iri_prefix="interaction"
    )

    ont = parser.to_ontology()

IRI Generation
~~~~~~~~~~~~~~

Control how IRIs are generated from values:

.. code-block:: python

    # Default: CamelCase conversion
    # "Alzheimer's Disease" -> "AlzheimersDisease"
    parser.set_iri_style("camelcase")

    # Snake case
    # "Alzheimer's Disease" -> "alzheimers_disease"
    parser.set_iri_style("snakecase")

    # Kebab case
    # "Alzheimer's Disease" -> "alzheimers-disease"
    parser.set_iri_style("kebabcase")

    # Custom function
    def custom_iri_generator(value):
        # Custom IRI generation logic
        return value.upper().replace(" ", "_")

    parser.set_iri_generator(custom_iri_generator)

Property Mapping
----------------

Simple Property Mapping
~~~~~~~~~~~~~~~~~~~~~~~

Map columns to object properties:

.. code-block:: python

    parser.set_property_mappings({
        "Symptoms": "hasSymptom",
        "Treatments": "hasTreatment",
        "Risk Factors": "hasRiskFactor"
    })

    # Creates axioms like:
    # AlzheimersDisease hasSymptom MemoryLoss
    # AlzheimersDisease hasTreatment Donepezil

Data Property Mapping
~~~~~~~~~~~~~~~~~~~~~~

Map columns to data properties with literal values:

.. code-block:: python

    parser.set_data_property_mappings({
        "Prevalence": ("hasPrevalence", "xsd:float"),
        "Age of Onset": ("hasAgeOfOnset", "xsd:integer"),
        "Description": ("hasDescription", "xsd:string"),
        "IsCurable": ("isCurable", "xsd:boolean")
    })

    # Creates axioms like:
    # AlzheimersDisease hasPrevalence "0.05"^^xsd:float
    # AlzheimersDisease hasAgeOfOnset "65"^^xsd:integer

Multi-Valued Properties
~~~~~~~~~~~~~~~~~~~~~~~~

Handle cells with multiple values:

.. code-block:: python

    # Configure delimiter
    parser.set_value_delimiter(";")

    # Example data:
    # Disease Name | Symptoms
    # Alzheimer's  | Memory Loss; Confusion; Disorientation

    # Creates multiple axioms:
    # Alzheimers hasSymptom MemoryLoss
    # Alzheimers hasSymptom Confusion
    # Alzheimers hasSymptom Disorientation

Complex Mappings
~~~~~~~~~~~~~~~~

Define complex relationship mappings:

.. code-block:: python

    # Bidirectional relationships
    parser.add_bidirectional_mapping(
        column="Related Diseases",
        forward_property="relatedTo",
        inverse_property="relatedTo"  # Symmetric
    )

    # Typed relationships
    parser.add_typed_relationship(
        subject_column="Gene",
        object_column="Disease",
        relationship_column="Association Type",
        property_mapping={
            "Causal": "causes",
            "Risk Factor": "increasesRiskOf",
            "Protective": "protectsAgainst"
        }
    )

Hierarchical Structures
-----------------------

Parent-Child Relationships
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    # Extract class hierarchy from parent column
    parser = DatabaseParser("taxonomy.csv")
    parser.set_entity_column("Term")
    parser.set_parent_column("Parent Term")

    # Creates SubClassOf axioms automatically
    # If row has: Term="Protein", Parent="Molecule"
    # Creates: Protein SubClassOf Molecule

    ont = parser.to_ontology()

Multi-Level Hierarchies
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    # Database with multiple hierarchy levels
    # Category | Subcategory | Term
    # Biological | Protein | Enzyme

    parser.set_hierarchy_columns([
        "Category",
        "Subcategory",
        "Term"
    ])

    # Creates:
    # Enzyme SubClassOf Protein
    # Protein SubClassOf Biological

Annotations
-----------

Label and Comment Extraction
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    # Add labels from column
    parser.add_annotation_mapping(
        column="Display Name",
        property=owl2.IRI("rdfs", "label", "..."),
        language="en"
    )

    # Add definitions
    parser.add_annotation_mapping(
        column="Definition",
        property=owl2.IRI("obo", "IAO_0000115", "..."),
        language="en"
    )

    # Add comments
    parser.add_annotation_mapping(
        column="Notes",
        property=owl2.IRI("rdfs", "comment", "..."),
        language="en"
    )

Database Metadata
~~~~~~~~~~~~~~~~~

.. code-block:: python

    # Add provenance annotations
    parser.set_provenance({
        "source": "Disease Database v2.0",
        "date": "2024-01-15",
        "curator": "John Doe",
        "license": "CC BY 4.0"
    })

    # These are added as ontology-level annotations

Advanced Features
-----------------

Filtering and Validation
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    # Filter rows before processing
    def row_filter(row):
        # Only include rows where Status is "Approved"
        return row.get("Status") == "Approved"

    parser.set_row_filter(row_filter)

    # Validate values
    def value_validator(column, value):
        if column == "Prevalence":
            # Must be numeric
            try:
                float(value)
                return True
            except ValueError:
                return False
        return True

    parser.set_value_validator(value_validator)

Custom Axiom Generation
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    # Add custom axiom generation logic
    def custom_axiom_generator(row, ont, base_iri):
        disease_name = row["Disease Name"]
        disease_iri = create_iri(base_iri, disease_name)

        # Custom logic: if prevalence > 0.1, add "CommonDisease" class
        prevalence = float(row.get("Prevalence", 0))
        if prevalence > 0.1:
            common_disease = owl2.Class(create_iri(base_iri, "CommonDisease"))
            ont.add_axiom(owl2.SubClassOf(
                owl2.Class(disease_iri),
                common_disease
            ))

    parser.add_custom_generator(custom_axiom_generator)

Relationship Inference
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    # Infer transitive relationships
    parser.enable_transitivity_inference(
        property="partOf",
        max_depth=5
    )

    # If A partOf B and B partOf C, infer A partOf C

    # Infer symmetric relationships
    parser.mark_as_symmetric("relatedTo")

Handling Missing Data
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    # Configure missing data handling
    parser.set_missing_value_strategy(
        strategy="skip",  # or "default", "infer"
        default_value=None
    )

    # Skip rows with missing critical values
    parser.set_required_columns(["Disease Name", "Category"])

Examples
--------

Disease Database
~~~~~~~~~~~~~~~~

.. code-block:: python

    from ista.database_parser import DatabaseParser
    from ista import owl2

    # Load disease database
    parser = DatabaseParser("diseases.xlsx")

    # Configure
    parser.set_base_iri("http://example.org/diseases#")
    parser.set_entity_column("Disease Name")
    parser.set_entity_type(owl2.EntityType.CLASS)

    # Set up hierarchy
    parser.set_parent_column("Disease Category")

    # Map properties
    parser.set_property_mappings({
        "Symptoms": "hasSymptom",
        "Treatments": "hasTreatment",
        "Risk Factors": "hasRiskFactor"
    })

    # Map data properties
    parser.set_data_property_mappings({
        "Prevalence": ("hasPrevalence", "xsd:float"),
        "Age of Onset": ("hasAgeOfOnset", "xsd:integer")
    })

    # Add annotations
    parser.add_annotation_mapping("Definition",
                                   owl2.IRI("obo", "IAO_0000115", "..."),
                                   language="en")

    # Generate ontology
    ont = parser.to_ontology()

    # Save
    serializer = owl2.FunctionalSyntaxSerializer()
    serializer.serialize(ont, "diseases.ofn")

Protein Interaction Database
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    # Protein-protein interactions
    parser = DatabaseParser("ppi.csv")

    parser.set_base_iri("http://example.org/proteins#")

    # Both proteins are individuals
    parser.add_entity_column("Protein A",
                             owl2.EntityType.NAMED_INDIVIDUAL,
                             iri_prefix="protein")
    parser.add_entity_column("Protein B",
                             owl2.EntityType.NAMED_INDIVIDUAL,
                             iri_prefix="protein")

    # Interaction type determines property
    parser.add_typed_relationship(
        subject_column="Protein A",
        object_column="Protein B",
        relationship_column="Interaction Type",
        property_mapping={
            "Binding": "bindsTo",
            "Phosphorylation": "phosphorylates",
            "Activation": "activates",
            "Inhibition": "inhibits"
        }
    )

    # Add confidence scores as data properties
    parser.set_data_property_mappings({
        "Confidence Score": ("hasConfidence", "xsd:float")
    })

    ont = parser.to_ontology()

Gene-Disease Associations
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    # Gene-disease association database
    parser = DatabaseParser("gene_disease.tsv", delimiter="\t")

    parser.set_base_iri("http://example.org/biomedical#")

    # Genes and diseases as different entity types
    parser.add_entity_column("Gene Symbol",
                             owl2.EntityType.NAMED_INDIVIDUAL,
                             iri_prefix="gene")
    parser.add_entity_column("Disease Name",
                             owl2.EntityType.CLASS,
                             iri_prefix="disease")

    # Association types
    parser.add_typed_relationship(
        subject_column="Gene Symbol",
        object_column="Disease Name",
        relationship_column="Association",
        property_mapping={
            "Causal Mutation": "hasCausalMutation",
            "Risk Factor": "isRiskFactorFor",
            "Biomarker": "isBiomarkerFor"
        }
    )

    # Add evidence codes as annotations
    parser.add_relationship_annotation(
        annotation_column="Evidence Code",
        property=owl2.IRI("obo", "ECO_0000000", "...")
    )

    ont = parser.to_ontology()

Batch Processing
----------------

Processing Multiple Files
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    import glob
    from ista.database_parser import DatabaseParser

    # Process all CSV files in directory
    files = glob.glob("data/*.csv")

    all_ontologies = []
    for file in files:
        parser = DatabaseParser(file)
        # Configure parser...
        ont = parser.to_ontology()
        all_ontologies.append(ont)

    # Merge ontologies
    merged = merge_ontologies(all_ontologies)

Large File Processing
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    # Process large files in chunks
    parser = DatabaseParser("large_database.csv")
    parser.set_chunk_size(1000)  # Process 1000 rows at a time

    # Stream processing
    for chunk_ont in parser.stream_to_ontologies():
        # Process each chunk
        print(f"Processed chunk with {chunk_ont.get_axiom_count()} axioms")

Performance Tips
----------------

1. **Set Column Types**: Explicitly set data types to avoid inference
2. **Batch Axiom Addition**: Use bulk add methods when available
3. **Filter Early**: Apply row filters before processing
4. **Chunk Large Files**: Process in chunks for memory efficiency
5. **Use Caching**: Cache frequently accessed entity IRIs

.. code-block:: python

    # Optimize performance
    parser = DatabaseParser("large_db.csv")

    # Pre-filter data
    parser.set_row_filter(lambda r: r["Status"] == "Active")

    # Set explicit types
    parser.set_column_types({
        "Prevalence": float,
        "Year": int,
        "Description": str
    })

    # Enable caching
    parser.enable_iri_cache()

    # Process in chunks
    parser.set_chunk_size(5000)

Error Handling
--------------

.. code-block:: python

    from ista.database_parser import ParsingError

    try:
        parser = DatabaseParser("database.xlsx")
        parser.set_entity_column("Name")
        ont = parser.to_ontology()
    except ParsingError as e:
        print(f"Parsing error: {e}")
        print(f"Row: {e.row_number}")
        print(f"Column: {e.column_name}")
    except FileNotFoundError:
        print("Database file not found")
    except Exception as e:
        print(f"Unexpected error: {e}")

Best Practices
--------------

1. **Validate Input Data**: Check for missing values, duplicates, data types
2. **Document Mappings**: Keep track of column-to-property mappings
3. **Test with Samples**: Test parsing logic on small data samples first
4. **Use Consistent IRIs**: Ensure IRI generation is consistent and reversible
5. **Add Provenance**: Always include source information as annotations
6. **Version Control**: Track changes to parsing configurations
7. **Validate Output**: Check generated ontology for consistency

See Also
--------

- :doc:`python_library` - Python library guide
- :doc:`../api/owl2` - Complete API reference
- :doc:`../examples` - Example parsing workflows
- pandas documentation: https://pandas.pydata.org/
