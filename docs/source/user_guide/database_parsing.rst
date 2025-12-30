Database Parsing
================

The ista database parsers enable conversion of structured databases (CSV, TSV, Excel, MySQL) into
OWL2 ontologies using the native ista.owl2 library. This facilitates integration of existing knowledge
bases and data sources into formal ontologies.

Overview
--------

The database parser provides:

- **Automatic Individual Extraction**: Create OWL individuals from database rows
- **Property Mapping**: Map database columns to OWL2 data and object properties
- **Flexible Configuration**: Customize parsing rules via parse_config dictionaries
- **Merge Operations**: Merge new data with existing individuals
- **Relationship Parsing**: Extract relationships from separate tables/files
- **Data Transformations**: Apply transformations to values during parsing

Supported Formats
-----------------

- **Flat Files**: CSV, TSV, Excel (.xlsx)
- **Databases**: MySQL databases
- **Pandas DataFrames**: In-memory pandas support (via TSV adapter)

Parser Classes
--------------

FlatFileDatabaseParser
~~~~~~~~~~~~~~~~~~~~~~

Parses flat files (CSV, TSV, Excel) into ontologies.

.. code-block:: python

    from ista import FlatFileDatabaseParser, owl2

    # Load base ontology
    onto = owl2.RDFXMLParser.parse_from_file("my_ontology.owl")

    # Create parser for a database directory
    parser = FlatFileDatabaseParser(
        name="DrugDB",        # Database name
        destination=onto,     # Target ontology
        data_dir="./data"     # Directory containing database files
    )

MySQLDatabaseParser
~~~~~~~~~~~~~~~~~~~

Parses MySQL database tables into ontologies.

.. code-block:: python

    from ista import MySQLDatabaseParser, owl2

    # MySQL configuration
    mysql_config = {
        'host': 'localhost',
        'user': 'myuser',
        'passwd': 'mypassword',
        'socket': '/path/to/mysql.sock'  # Optional
    }

    # Load base ontology
    onto = owl2.RDFXMLParser.parse_from_file("my_ontology.owl")

    # Create parser
    parser = MySQLDatabaseParser(
        name="BioDB",         # MySQL database name
        destination=onto,     # Target ontology
        config_dict=mysql_config
    )

Parsing Nodes (Individuals)
----------------------------

Basic Node Parsing
~~~~~~~~~~~~~~~~~~

Parse database rows into OWL individuals:

.. code-block:: python

    from ista import FlatFileDatabaseParser, owl2

    onto = owl2.Ontology(owl2.IRI("http://example.org/drugs"))

    # Create classes and properties first
    drug_class = owl2.Class(owl2.IRI("http://example.org/Drug"))
    has_name = owl2.DataProperty(owl2.IRI("http://example.org/hasName"))
    drugbank_id = owl2.DataProperty(owl2.IRI("http://example.org/drugbankId"))

    parser = FlatFileDatabaseParser("DrugDB", onto, "./data")

    parser.parse_node_type(
        node_type="Drug",                    # Class name in ontology
        source_filename="drugs.csv",         # Source file
        fmt="csv",                           # Format: csv, tsv, xlsx
        parse_config={
            "iri_column_name": "drug_id",    # Column for IRI generation
            "headers": True,                 # File has headers
            "data_property_map": {
                "name": has_name,            # Map columns to properties
                "drugbank_id": drugbank_id,
            },
            "merge_column": {                 # Merge strategy
                "source_column_name": "drugbank_id",
                "data_property": drugbank_id,
            },
        },
        merge=True,      # Merge with existing individuals
        skip=False       # Set True to skip this parsing step
    )

Configuration Options
~~~~~~~~~~~~~~~~~~~~~

**Required parse_config keys:**

- ``iri_column_name``: Column used to generate individual IRIs
- ``headers``: Whether the file has column headers (True/False or list of header names)

**Optional parse_config keys:**

- ``data_property_map``: Dictionary mapping column names to DataProperty objects
- ``merge_column``: Dictionary specifying how to merge with existing individuals

  - ``source_column_name``: Column to check for existing individuals
  - ``data_property``: DataProperty to search on

- ``filter_column``: Column to filter rows
- ``filter_value``: Value that filter_column must contain
- ``skip_n_lines``: Number of lines to skip after headers
- ``compound_fields``: Dictionary for parsing delimited multi-value fields
- ``data_transforms``: Dictionary of lambda functions to transform values
- ``custom_sql_query``: Custom SQL query (MySQL only)

File Formats
~~~~~~~~~~~~

**CSV Files:**

.. code-block:: python

    parser.parse_node_type(
        node_type="Gene",
        source_filename="genes.csv",
        fmt="csv",
        parse_config={
            "iri_column_name": "gene_symbol",
            "headers": True,
            "data_property_map": {
                "gene_symbol": onto.geneSymbol,
                "description": onto.hasDescription,
            }
        }
    )

**TSV Files:**

.. code-block:: python

    parser.parse_node_type(
        node_type="Disease",
        source_filename="diseases.tsv",
        fmt="tsv",
        parse_config={
            "iri_column_name": "disease_id",
            "headers": True,
            "data_property_map": {
                "disease_name": onto.commonName,
                "umls_cui": onto.xrefUmlsCUI,
            }
        }
    )

**Excel Files:**

.. code-block:: python

    parser.parse_node_type(
        node_type="Drug",
        source_filename="drugs.xlsx",
        fmt="xlsx",
        parse_config={
            "iri_column_name": "DrugID",
            "headers": True,
            "data_property_map": {
                "DrugName": onto.commonName,
                "SMILES": onto.hasSMILES,
            }
        }
    )

**Pandas DataFrames:**

.. code-block:: python

    # Use tsv-pandas format for in-memory DataFrames
    parser.parse_node_type(
        node_type="Protein",
        source_filename="proteins.tsv",  # Pandas-compatible
        fmt="tsv-pandas",
        parse_config={
            "iri_column_name": "uniprot_id",
            "headers": True,
            "data_property_map": {
                "protein_name": onto.proteinName,
                "mass": onto.molecularMass,
            }
        }
    )

Merging vs Creating New
~~~~~~~~~~~~~~~~~~~~~~~~

**merge=False**: Always create new individuals

.. code-block:: python

    parser.parse_node_type(
        node_type="Sample",
        source_filename="samples.csv",
        fmt="csv",
        parse_config={
            "iri_column_name": "sample_id",
            "headers": True,
            "data_property_map": {
                "sample_id": onto.sampleId,
                "date": onto.collectionDate,
            }
        },
        merge=False  # Always create new individuals
    )

**merge=True**: Merge with existing individuals based on merge_column

.. code-block:: python

    parser.parse_node_type(
        node_type="Drug",
        source_filename="additional_drug_info.csv",
        fmt="csv",
        parse_config={
            "iri_column_name": "drug_name",
            "headers": True,
            "data_property_map": {
                "fda_approved": onto.fdaApproved,
                "year_approved": onto.yearApproved,
            },
            "merge_column": {
                "source_column_name": "drugbank_id",
                "data_property": onto.drugbankId,
            }
        },
        merge=True  # Merge with existing drugs
    )

Data Transformations
~~~~~~~~~~~~~~~~~~~~

Apply transformations to column values:

.. code-block:: python

    parser.parse_node_type(
        node_type="Gene",
        source_filename="genes.tsv",
        fmt="tsv",
        parse_config={
            "iri_column_name": "gene_id",
            "headers": True,
            "data_transforms": {
                # Extract numeric ID from formatted string
                "gene_id": lambda x: int(x.split("::")[-1]),
                # Convert to uppercase
                "gene_symbol": lambda x: x.upper(),
            },
            "data_property_map": {
                "gene_id": onto.geneId,
                "gene_symbol": onto.geneSymbol,
            }
        }
    )

Compound Fields
~~~~~~~~~~~~~~~

Parse multi-value fields with delimiters:

.. code-block:: python

    parser.parse_node_type(
        node_type="Gene",
        source_filename="gene_xrefs.tsv",
        fmt="tsv",
        parse_config={
            "iri_column_name": "Symbol",
            "headers": True,
            "compound_fields": {
                "dbXrefs": {
                    "delimiter": "|",          # Split on pipe
                    "field_split_prefix": ":"  # Further split on colon
                }
            },
            "data_property_map": {
                "Ensembl": onto.xrefEnsembl,
                "HGNC": onto.xrefHGNC,
            }
        }
    )

    # Example data:
    # Symbol | dbXrefs
    # BRCA1  | Ensembl:ENSG00000012048|HGNC:1100
    #
    # Creates properties:
    # BRCA1 xrefEnsembl "ENSG00000012048"
    # BRCA1 xrefHGNC "1100"

Filtering Rows
~~~~~~~~~~~~~~

Filter which rows to process:

.. code-block:: python

    parser.parse_node_type(
        node_type="Disease",
        source_filename="diseases.tsv",
        fmt="tsv",
        parse_config={
            "iri_column_name": "disease_id",
            "headers": True,
            "filter_column": "disease_type",
            "filter_value": "genetic",  # Only process genetic diseases
            "data_property_map": {
                "disease_name": onto.commonName,
            }
        }
    )

Parsing Relationships
---------------------

Basic Relationship Parsing
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Parse relationships from a separate file/table:

.. code-block:: python

    parser.parse_relationship_type(
        relationship_type=onto.geneAssociatesWithDisease,
        source_filename="gene_disease_associations.tsv",
        fmt="tsv",
        parse_config={
            "subject_node_type": onto.Gene,
            "subject_column_name": "gene_symbol",
            "subject_match_property": onto.geneSymbol,
            "object_node_type": onto.Disease,
            "object_column_name": "disease_id",
            "object_match_property": onto.diseaseId,
            "headers": True
        }
    )

Bidirectional Relationships
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create inverse relationships:

.. code-block:: python

    parser.parse_relationship_type(
        relationship_type=onto.geneInPathway,
        inverse_relationship_type=onto.pathwayContainsGene,
        source_filename="gene_pathways.csv",
        fmt="csv",
        parse_config={
            "subject_node_type": onto.Gene,
            "subject_column_name": "gene_id",
            "subject_match_property": onto.geneId,
            "object_node_type": onto.Pathway,
            "object_column_name": "pathway_id",
            "object_match_property": onto.pathwayId,
            "headers": True
        }
    )

Relationship Transformations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Transform relationship values:

.. code-block:: python

    parser.parse_relationship_type(
        relationship_type=onto.chemicalIncreasesExpression,
        source_filename="interactions.tsv",
        fmt="tsv",
        parse_config={
            "subject_node_type": onto.Drug,
            "subject_column_name": "drug_id",
            "subject_match_property": onto.drugbankId,
            "object_node_type": onto.Gene,
            "object_column_name": "gene_id",
            "object_match_property": onto.geneId,
            "filter_column": "interaction_type",
            "filter_value": "upregulation",
            "headers": True,
            "data_transforms": {
                "drug_id": lambda x: x.split("::")[-1],
                "gene_id": lambda x: int(x.split("::")[-1])
            }
        }
    )

MySQL Examples
--------------

Parsing from MySQL Tables
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from ista import MySQLDatabaseParser, owl2

    mysql_config = {
        'host': 'localhost',
        'user': 'biouser',
        'passwd': 'biopass'
    }

    onto = owl2.Ontology(owl2.IRI("http://example.org/bio"))
    parser = MySQLDatabaseParser("biomedical_db", onto, mysql_config)

    # Parse a table
    parser.parse_node_type(
        node_type="Protein",
        source_table="proteins",
        parse_config={
            "iri_column_name": "uniprot_id",
            "data_property_map": {
                "protein_name": onto.proteinName,
                "organism": onto.fromOrganism,
            },
            "merge_column": {
                "source_column_name": "uniprot_id",
                "data_property": onto.uniprotId,
            }
        },
        merge=True
    )

Custom SQL Queries
~~~~~~~~~~~~~~~~~~

.. code-block:: python

    # Use custom SQL query
    parser.parse_node_type(
        node_type="Pathway",
        source_table="pathways",  # Not actually used when custom_sql_query is set
        parse_config={
            "iri_column_name": "pathway_id",
            "custom_sql_query": """
                SELECT DISTINCT pathway_id, pathway_name, source_db
                FROM pathway_genes
                WHERE organism = 'Homo sapiens'
            """,
            "data_property_map": {
                "pathway_name": onto.pathwayName,
                "source_db": onto.sourceDatabase,
            }
        },
        merge=False
    )

MySQL Relationships
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    parser.parse_relationship_type(
        relationship_type=onto.proteinInteractsWithProtein,
        parse_config={
            "subject_node_type": onto.Protein,
            "subject_column_name": "protein_a",
            "subject_match_property": onto.uniprotId,
            "object_node_type": onto.Protein,
            "object_column_name": "protein_b",
            "object_match_property": onto.uniprotId,
            "source_table": "protein_interactions",
            "source_table_type": "foreignKey",
            "custom_sql_query": """
                SELECT protein_a, protein_b, confidence
                FROM protein_interactions
                WHERE confidence > 0.8
            """
        }
    )

Complete Example
----------------

.. code-block:: python

    from ista import FlatFileDatabaseParser, MySQLDatabaseParser, owl2

    # 1. Load base ontology
    onto = owl2.RDFXMLParser.parse_from_file("biomedical_ontology.owl")

    # 2. Create parsers
    drug_parser = FlatFileDatabaseParser("DrugBank", onto, "./data")
    gene_parser = FlatFileDatabaseParser("GeneDB", onto, "./data")
    disease_parser = FlatFileDatabaseParser("DiseaseDB", onto, "./data")

    # 3. Parse drugs
    drug_parser.parse_node_type(
        node_type="Drug",
        source_filename="drugs.csv",
        fmt="csv",
        parse_config={
            "iri_column_name": "drugbank_id",
            "headers": True,
            "data_property_map": {
                "name": onto.commonName,
                "drugbank_id": onto.drugbankId,
                "cas_number": onto.casNumber,
            },
            "merge_column": {
                "source_column_name": "drugbank_id",
                "data_property": onto.drugbankId,
            }
        },
        merge=True
    )

    # 4. Parse genes
    gene_parser.parse_node_type(
        node_type="Gene",
        source_filename="genes.tsv",
        fmt="tsv-pandas",
        parse_config={
            "iri_column_name": "gene_symbol",
            "headers": True,
            "compound_fields": {
                "cross_refs": {
                    "delimiter": "|",
                    "field_split_prefix": ":"
                }
            },
            "data_property_map": {
                "gene_symbol": onto.geneSymbol,
                "gene_id": onto.geneId,
                "HGNC": onto.xrefHGNC,
                "Ensembl": onto.xrefEnsembl,
            }
        },
        merge=False
    )

    # 5. Parse diseases
    disease_parser.parse_node_type(
        node_type="Disease",
        source_filename="diseases.csv",
        fmt="csv",
        parse_config={
            "iri_column_name": "disease_id",
            "headers": True,
            "filter_column": "category",
            "filter_value": "genetic",
            "data_property_map": {
                "disease_name": onto.commonName,
                "umls_cui": onto.xrefUmlsCUI,
            }
        },
        merge=False
    )

    # 6. Parse relationships
    drug_parser.parse_relationship_type(
        relationship_type=onto.drugTargetsGene,
        source_filename="drug_targets.tsv",
        fmt="tsv",
        parse_config={
            "subject_node_type": onto.Drug,
            "subject_column_name": "drugbank_id",
            "subject_match_property": onto.drugbankId,
            "object_node_type": onto.Gene,
            "object_column_name": "gene_symbol",
            "object_match_property": onto.geneSymbol,
            "headers": True
        }
    )

    gene_parser.parse_relationship_type(
        relationship_type=onto.geneAssociatesWithDisease,
        source_filename="gene_disease.tsv",
        fmt="tsv",
        parse_config={
            "subject_node_type": onto.Gene,
            "subject_column_name": "gene_symbol",
            "subject_match_property": onto.geneSymbol,
            "object_node_type": onto.Disease,
            "object_column_name": "disease_id",
            "object_match_property": onto.xrefUmlsCUI,
            "filter_column": "association_type",
            "filter_value": "causal",
            "headers": True
        }
    )

    # 7. Print statistics
    from ista.util import print_onto_stats
    print_onto_stats(onto)

    # 8. Save populated ontology
    serializer = owl2.RDFXMLSerializer()
    rdf_content = serializer.serialize(onto)
    with open("populated_biomedical.owl", "w") as f:
        f.write(rdf_content)

Utility Functions
-----------------

ista provides utility functions in ``ista.util``:

.. code-block:: python

    from ista.util import (
        safe_add_property,           # Safely add properties with duplicate checking
        get_onto_class_by_node_type, # Find class by local name
        safe_make_individual_name,   # Generate unique individual IRI suffixes
        print_onto_stats,            # Print ontology statistics
    )

    # Find a class by name
    drug_class = get_onto_class_by_node_type(onto, "Drug")

    # Generate safe individual name
    individual_name = safe_make_individual_name("Aspirin", drug_class)
    # Returns: "drug_aspirin"

    # Print statistics
    print_onto_stats(onto)

Best Practices
--------------

1. **Load Base Ontology First**: Start with a base ontology defining classes and properties
2. **Define Schema**: Create all classes and properties before parsing data
3. **Use Merge Strategically**: Merge when combining data from multiple sources
4. **Apply Transformations**: Clean and normalize data during parsing
5. **Filter Early**: Use filter_column to reduce unnecessary processing
6. **Test on Samples**: Test parsing configuration on small data samples first
7. **Add Provenance**: Document data sources as ontology annotations
8. **Check Statistics**: Use print_onto_stats to verify parsing results

Performance Tips
----------------

1. Set ``skip=True`` for parse operations you don't need
2. Use ``filter_column`` to reduce rows processed
3. Process smaller files first to validate configuration
4. Use appropriate file formats (CSV is faster than Excel for large files)
5. For MySQL, use indexed columns in merge_column

Error Handling
--------------

.. code-block:: python

    try:
        parser.parse_node_type(...)
    except FileNotFoundError:
        print("Source file not found")
    except KeyError as e:
        print(f"Column not found: {e}")
    except Exception as e:
        print(f"Parsing error: {e}")

See Also
--------

- :doc:`owl2_interfaces` - OWL2 interface documentation
- :doc:`python_library` - Python library guide
- :doc:`../api/owl2` - Complete API reference
- Example knowledge bases: ``examples/kg_projects/neurokb/``, ``examples/kg_projects/alzkb/``
