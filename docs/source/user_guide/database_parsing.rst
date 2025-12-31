Data Loading
============

The ista data loading system enables population of OWL2 ontologies from structured data sources
(CSV, TSV, databases) using a declarative YAML-based mapping specification. This approach replaces
the older Python-based database parsers with a more robust, documented, and GUI-compatible solution.

Overview
--------

The data loading system provides:

- **Declarative Mapping Specs**: Define data-to-ontology mappings in YAML files
- **Primary/Enrichment Pattern**: One source defines individuals, others add properties
- **Named Transforms**: Replace Python lambdas with reusable, named transformations
- **High Performance**: Native C++ implementation with Python bindings
- **GUI Compatible**: Same engine works from scripts and the graphical interface
- **Validation**: Validate mappings against ontology schema before loading

Quick Start
-----------

Here's a minimal example of loading data from a CSV file:

.. code-block:: python

    from ista import owl2

    # Load your ontology
    onto = owl2.RDFXMLParser.parse_from_file("my_ontology.owl")

    # Create a loader
    loader = owl2.DataLoader(onto)

    # Load mapping specification from YAML
    loader.load_mapping_spec("drugs_mapping.yaml")

    # Validate before loading
    result = loader.validate()
    if not result.is_valid:
        for error in result.errors:
            print(f"Error: {error}")

    # Execute the loading
    stats = loader.execute()
    print(stats.summary())

Example YAML mapping file (``drugs_mapping.yaml``):

.. code-block:: yaml

    version: "1.0"
    base_iri: "http://example.org/drugs#"

    sources:
      drugbank:
        type: csv
        path: "./data/drugs.csv"
        has_headers: true

    node_mappings:
      - name: "DrugBank Drugs"
        source: drugbank
        target_class: Drug
        mode: create
        iri_column: drugbank_id
        properties:
          - column: name
            property: commonName
          - column: drugbank_id
            property: drugbankId
          - column: cas_number
            property: casNumber

Mapping Specification
---------------------

The mapping specification is a YAML file that defines how data sources map to ontology entities.
See :doc:`data_loading_schema` for the complete YAML schema reference.

Core Concepts
~~~~~~~~~~~~~

**Data Sources**: Define where data comes from (CSV files, TSV files, databases)

**Node Mappings**: Define how rows become individuals with properties

**Relationship Mappings**: Define how to create object property assertions between individuals

**Transforms**: Named functions that transform column values during loading

**Modes**:

- ``create``: Primary source that creates new individuals
- ``enrich``: Secondary source that adds properties to existing individuals

Primary Authority Pattern
~~~~~~~~~~~~~~~~~~~~~~~~~

A key design principle is the "primary authority" pattern. For each entity type:

1. One data source is the **primary authority** that defines which individuals exist
2. Other sources can **enrich** those individuals with additional properties

.. code-block:: yaml

    node_mappings:
      # Primary source - creates Drug individuals
      - name: "DrugBank Drugs (Primary)"
        source: drugbank
        target_class: Drug
        mode: create
        iri_column: drugbank_id
        properties:
          - column: name
            property: commonName
          - column: drugbank_id
            property: drugbankId

      # Enrichment source - adds EPA toxicity data to existing drugs
      - name: "EPA Toxicity Data"
        source: epa_data
        target_class: Drug
        mode: enrich
        match:
          source_column: cas_number
          target_property: casNumber
        properties:
          - column: toxicity_class
            property: toxicityClassification
          - column: ld50
            property: ld50Value
            datatype: xsd:double

Data Sources
------------

CSV and TSV Files
~~~~~~~~~~~~~~~~~

.. code-block:: yaml

    sources:
      my_csv:
        type: csv
        path: "./data/file.csv"
        has_headers: true
        delimiter: ","  # Optional, defaults to comma

      my_tsv:
        type: tsv
        path: "./data/file.tsv"
        has_headers: true

Environment Variables
~~~~~~~~~~~~~~~~~~~~~

Paths can use environment variables:

.. code-block:: yaml

    sources:
      drugbank:
        type: csv
        path: "${DATA_DIR}/drugbank/drugs.csv"

Call ``spec.resolve_environment_variables()`` or the loader does this automatically.

Node Mappings
-------------

Basic Node Mapping
~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

    node_mappings:
      - name: "Gene Entities"
        source: ncbi_gene
        target_class: Gene
        mode: create
        iri_column: gene_id
        properties:
          - column: symbol
            property: geneSymbol
          - column: description
            property: hasDescription
          - column: chromosome
            property: chromosome

Property Mapping Options
~~~~~~~~~~~~~~~~~~~~~~~~

Each property mapping can specify:

- ``column``: Source column name (required)
- ``property``: Target property local name (required)
- ``transform``: Named transform to apply (optional)
- ``datatype``: XSD datatype for typed literals (optional)

.. code-block:: yaml

    properties:
      - column: gene_id
        property: geneId
        datatype: xsd:integer

      - column: gene_symbol
        property: geneSymbol
        transform: uppercase

      - column: aliases
        property: hasAlias
        transform: split_pipe

Filtering Rows
~~~~~~~~~~~~~~

Filter which rows to process:

.. code-block:: yaml

    node_mappings:
      - name: "Human Genes Only"
        source: ncbi_gene
        target_class: Gene
        mode: create
        iri_column: gene_id
        filter:
          column: species
          value: "Homo sapiens"
          contains: false  # Exact match (default: true for substring)
        properties:
          - column: symbol
            property: geneSymbol

Enrichment Mode
~~~~~~~~~~~~~~~

Add properties to existing individuals:

.. code-block:: yaml

    node_mappings:
      - name: "Add UniProt Cross-References"
        source: uniprot_xrefs
        target_class: Gene
        mode: enrich
        match:
          source_column: ncbi_gene_id
          target_property: geneId
        properties:
          - column: uniprot_id
            property: xrefUniProt

Relationship Mappings
---------------------

Create object property assertions between individuals:

.. code-block:: yaml

    relationship_mappings:
      - name: "Drug-Gene Targets"
        source: drug_targets
        relationship: drugTargetsGene
        subject:
          class: Drug
          column: drugbank_id
          match_property: drugbankId
        object:
          class: Gene
          column: gene_symbol
          match_property: geneSymbol

Inverse Relationships
~~~~~~~~~~~~~~~~~~~~~

Automatically create inverse relationships:

.. code-block:: yaml

    relationship_mappings:
      - name: "Gene-Disease Associations"
        source: gene_disease
        relationship: geneAssociatedWithDisease
        inverse_relationship: diseaseAssociatedWithGene
        subject:
          class: Gene
          column: gene_id
          match_property: geneId
        object:
          class: Disease
          column: disease_id
          match_property: diseaseId

Transforms
----------

Transforms modify column values during loading. They replace Python lambdas with
named, reusable, and serializable functions.

Built-in Transforms
~~~~~~~~~~~~~~~~~~~

The following transforms are available without definition:

.. list-table::
   :header-rows: 1
   :widths: 20 30 50

   * - Transform
     - Parameters
     - Description
   * - ``lowercase``
     - (none)
     - Convert to lowercase
   * - ``uppercase``
     - (none)
     - Convert to uppercase
   * - ``trim``
     - (none)
     - Remove leading/trailing whitespace
   * - ``prefix``
     - ``value``
     - Add prefix to value
   * - ``suffix``
     - ``value``
     - Add suffix to value
   * - ``strip_prefix``
     - ``value``
     - Remove prefix if present
   * - ``strip_suffix``
     - ``value``
     - Remove suffix if present
   * - ``split``
     - ``delimiter``, ``index``
     - Split and return element at index
   * - ``replace``
     - ``old``, ``new``
     - Replace substring
   * - ``regex_extract``
     - ``pattern``, ``group``
     - Extract regex match group
   * - ``to_int``
     - (none)
     - Convert to integer string
   * - ``to_float``
     - (none)
     - Convert to float string
   * - ``identity``
     - (none)
     - Return value unchanged
   * - ``default_if_empty``
     - ``default``
     - Use default if value is empty
   * - ``chain``
     - ``transforms``
     - Apply multiple transforms in sequence

Custom Transforms
~~~~~~~~~~~~~~~~~

Define custom transforms in your mapping spec:

.. code-block:: yaml

    transforms:
      # Simple transform using a builtin
      extract_id:
        type: split
        params:
          delimiter: "::"
          index: "-1"

      # Chained transforms
      clean_gene_symbol:
        type: chain
        params:
          transforms: "uppercase,trim"

      # Prefix with namespace
      add_drugbank_prefix:
        type: prefix
        params:
          value: "DB:"

Using Transforms
~~~~~~~~~~~~~~~~

Reference transforms by name in property mappings:

.. code-block:: yaml

    properties:
      - column: raw_id
        property: entityId
        transform: extract_id

      - column: gene_symbol
        property: geneSymbol
        transform: clean_gene_symbol

Python API
----------

DataLoader Class
~~~~~~~~~~~~~~~~

.. code-block:: python

    from ista import owl2

    # Create loader for an ontology
    loader = owl2.DataLoader(onto)

    # Load mapping spec from file
    loader.load_mapping_spec("mapping.yaml")

    # Or set a spec object directly
    spec = owl2.DataMappingSpec.load_from_file("mapping.yaml")
    loader.set_mapping_spec(spec)

    # Validate against ontology
    result = loader.validate()
    print(f"Valid: {result.is_valid}")
    for error in result.errors:
        print(f"  Error: {error}")
    for warning in result.warnings:
        print(f"  Warning: {warning}")

    # Execute all mappings
    stats = loader.execute()

    # Or execute specific mappings
    stats = loader.execute_node_mapping("DrugBank Drugs")
    stats = loader.execute_relationship_mapping("Drug-Gene Targets")

    # Execute by category
    stats = loader.execute_all_node_mappings()
    stats = loader.execute_all_relationship_mappings()

Progress Callbacks
~~~~~~~~~~~~~~~~~~

Monitor loading progress:

.. code-block:: python

    def on_progress(current, total, mapping_name):
        if total > 0:
            pct = (current / total) * 100
            print(f"{mapping_name}: {current}/{total} ({pct:.1f}%)")
        else:
            print(f"{mapping_name}: {current} rows processed")

    loader.set_progress_callback(on_progress)
    stats = loader.execute()

Loading Statistics
~~~~~~~~~~~~~~~~~~

The ``LoadingStats`` object provides detailed statistics:

.. code-block:: python

    stats = loader.execute()

    print(f"Rows processed: {stats.rows_processed}")
    print(f"Individuals created: {stats.individuals_created}")
    print(f"Individuals enriched: {stats.individuals_enriched}")
    print(f"Properties added: {stats.properties_added}")
    print(f"Relationships created: {stats.relationships_created}")
    print(f"Rows skipped: {stats.rows_skipped}")
    print(f"Errors: {stats.errors}")

    if stats.error_messages:
        for msg in stats.error_messages:
            print(f"  {msg}")

    # Or use the summary
    print(stats.summary())

Building Specs Programmatically
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create mapping specs in code:

.. code-block:: python

    from ista import owl2

    # Create empty spec
    spec = owl2.DataMappingSpec()
    spec.base_iri = "http://example.org/myonto#"

    # Add a data source
    source = owl2.DataSourceDef()
    source.name = "drugs"
    source.type = "csv"
    source.path = "./data/drugs.csv"
    source.has_headers = True
    spec.sources["drugs"] = source

    # Add a node mapping
    mapping = owl2.NodeMapping()
    mapping.name = "Drug Entities"
    mapping.source = "drugs"
    mapping.target_class = "Drug"
    mapping.mode = owl2.MappingMode.CREATE
    mapping.iri_column = "drug_id"

    prop = owl2.PropertyMapping()
    prop.column = "name"
    prop.property = "commonName"
    mapping.properties.append(prop)

    spec.node_mappings.append(mapping)

    # Save to YAML
    spec.save_to_file("generated_mapping.yaml")

    # Or use directly
    loader = owl2.DataLoader(onto)
    loader.set_mapping_spec(spec)
    stats = loader.execute()

Complete Example
----------------

.. code-block:: python

    from ista import owl2

    # 1. Load base ontology with class and property definitions
    onto = owl2.RDFXMLParser.parse_from_file("biomedical_ontology.owl")

    # 2. Create loader
    loader = owl2.DataLoader(onto)

    # 3. Load mapping specification
    loader.load_mapping_spec("biomedical_mapping.yaml")

    # 4. Add progress monitoring
    def progress(current, total, name):
        print(f"  {name}: {current} rows...")

    loader.set_progress_callback(progress)

    # 5. Validate
    result = loader.validate()
    if not result.is_valid:
        print("Validation failed:")
        for err in result.errors:
            print(f"  {err}")
        exit(1)

    if result.warnings:
        print("Warnings:")
        for warn in result.warnings:
            print(f"  {warn}")

    # 6. Execute loading
    print("Loading data...")
    stats = loader.execute()

    # 7. Print results
    print(stats.summary())

    # 8. Save populated ontology
    owl2.RDFXMLSerializer.serialize_to_file(onto, "populated_ontology.owl")

Example mapping file (``biomedical_mapping.yaml``):

.. code-block:: yaml

    version: "1.0"
    base_iri: "http://example.org/bio#"

    transforms:
      clean_id:
        type: strip_prefix
        params:
          value: "ID:"

    sources:
      drugbank:
        type: csv
        path: "./data/drugbank_drugs.csv"
        has_headers: true

      ncbi_gene:
        type: tsv
        path: "./data/ncbi_genes.tsv"
        has_headers: true

      drug_targets:
        type: csv
        path: "./data/drug_gene_targets.csv"
        has_headers: true

    node_mappings:
      - name: "DrugBank Drugs"
        source: drugbank
        target_class: Drug
        mode: create
        iri_column: drugbank_id
        properties:
          - column: name
            property: commonName
          - column: drugbank_id
            property: drugbankId
          - column: cas_number
            property: casNumber
          - column: smiles
            property: hasSMILES

      - name: "NCBI Genes"
        source: ncbi_gene
        target_class: Gene
        mode: create
        iri_column: gene_id
        filter:
          column: species
          value: "9606"
        properties:
          - column: gene_id
            property: geneId
            transform: clean_id
          - column: symbol
            property: geneSymbol
            transform: uppercase
          - column: description
            property: hasDescription

    relationship_mappings:
      - name: "Drug-Gene Targets"
        source: drug_targets
        relationship: drugTargetsGene
        inverse_relationship: geneTargetedByDrug
        subject:
          class: Drug
          column: drugbank_id
          match_property: drugbankId
        object:
          class: Gene
          column: gene_symbol
          match_property: geneSymbol

Migration from Legacy Parsers
-----------------------------

If you're using the older ``FlatFileDatabaseParser`` or ``MySQLDatabaseParser``,
here's how to migrate to the new system.

Before (Python-based):

.. code-block:: python

    from ista import FlatFileDatabaseParser

    parser = FlatFileDatabaseParser("DrugDB", onto, "./data")

    parser.parse_node_type(
        node_type="Drug",
        source_filename="drugs.csv",
        fmt="csv",
        parse_config={
            "iri_column_name": "drugbank_id",
            "headers": True,
            "data_property_map": {
                "name": onto.commonName,
                "drugbank_id": onto.drugbankId,
            },
            "data_transforms": {
                "drugbank_id": lambda x: x.upper(),
            },
            "merge_column": {
                "source_column_name": "drugbank_id",
                "data_property": onto.drugbankId,
            }
        },
        merge=True
    )

After (YAML-based):

.. code-block:: yaml

    # drugs_mapping.yaml
    sources:
      drugdb:
        type: csv
        path: "./data/DrugDB/drugs.csv"
        has_headers: true

    node_mappings:
      - name: "DrugDB Drugs"
        source: drugdb
        target_class: Drug
        mode: create  # or enrich for merge behavior
        iri_column: drugbank_id
        properties:
          - column: name
            property: commonName
          - column: drugbank_id
            property: drugbankId
            transform: uppercase

.. code-block:: python

    from ista import owl2

    loader = owl2.DataLoader(onto)
    loader.load_mapping_spec("drugs_mapping.yaml")
    stats = loader.execute()

Key Migration Notes
~~~~~~~~~~~~~~~~~~~

1. **Replace lambdas with transforms**: Define named transforms instead of inline lambdas
2. **merge=True becomes mode: enrich**: With a ``match`` criteria
3. **merge=False becomes mode: create**: The default behavior
4. **Property references**: Use property local names (strings) instead of property objects
5. **File paths**: Are relative to the YAML file or use environment variables

Best Practices
--------------

1. **Define Schema First**: Create your ontology with all classes and properties before loading data
2. **Use Primary/Enrichment Pattern**: Clearly separate data sources by authority
3. **Validate Before Loading**: Always call ``loader.validate()`` before ``loader.execute()``
4. **Use Descriptive Names**: Give node and relationship mappings clear, descriptive names
5. **Version Your Specs**: Include version info and keep specs in version control
6. **Test on Samples**: Test with small data samples before running on full datasets
7. **Monitor Progress**: Use progress callbacks for long-running loads
8. **Check Statistics**: Review LoadingStats to verify expected counts

See Also
--------

- :doc:`data_loading_schema` - Complete YAML schema reference
- :doc:`owl2_interfaces` - OWL2 interface documentation
- :doc:`python_library` - Python library guide
- Example knowledge bases: ``examples/kg_projects/``
