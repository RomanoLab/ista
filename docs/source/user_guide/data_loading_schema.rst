Data Loading YAML Schema Reference
===================================

This document provides a complete reference for the YAML mapping specification schema used
by the ista data loading system. For a tutorial introduction, see :doc:`database_parsing`.

Schema Version
--------------

The current schema version is **1.0**. Always specify the version in your mapping files:

.. code-block:: yaml

    version: "1.0"

Top-Level Structure
-------------------

A complete mapping specification has the following top-level keys:

.. code-block:: yaml

    version: "1.0"              # Required: Schema version
    base_iri: "..."             # Required: Base IRI for generated individuals
    sources: {...}              # Required: Data source definitions
    transforms: {...}           # Optional: Custom transform definitions
    node_mappings: [...]        # Optional: Node/individual mappings
    relationship_mappings: [...] # Optional: Relationship mappings

.. list-table:: Top-Level Keys
   :header-rows: 1
   :widths: 20 10 70

   * - Key
     - Required
     - Description
   * - ``version``
     - Yes
     - Schema version string (currently "1.0")
   * - ``base_iri``
     - Yes
     - Base IRI namespace for generated individual IRIs
   * - ``sources``
     - Yes
     - Map of data source definitions (at least one required)
   * - ``transforms``
     - No
     - Map of custom transform definitions
   * - ``node_mappings``
     - No
     - List of node mapping definitions
   * - ``relationship_mappings``
     - No
     - List of relationship mapping definitions

Sources
-------

The ``sources`` section defines data sources as a map from source name to source definition.

Structure
~~~~~~~~~

.. code-block:: yaml

    sources:
      <source_name>:
        type: <source_type>
        path: <file_path>
        has_headers: <boolean>
        delimiter: <delimiter_char>
        encoding: <encoding>

Source Definition Keys
~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 20 10 15 55

   * - Key
     - Required
     - Type
     - Description
   * - ``type``
     - Yes
     - string
     - Source type: ``csv``, ``tsv``, ``sqlite``, ``mysql``, ``postgres``
   * - ``path``
     - File sources
     - string
     - File path (relative to YAML file or absolute). Supports ``${ENV_VAR}`` syntax.
   * - ``has_headers``
     - No
     - boolean
     - Whether first row contains column headers. Default: ``true``
   * - ``delimiter``
     - No
     - string
     - Field delimiter character. Default: ``,`` for CSV, ``\t`` for TSV
   * - ``connection``
     - DB sources
     - object
     - Database connection parameters (see below)
   * - ``table``
     - DB sources*
     - string
     - Table name to query
   * - ``query``
     - DB sources*
     - string
     - Custom SQL query (alternative to ``table``)

\* For database sources, either ``table`` or ``query`` is required.

File-Based Source Types
~~~~~~~~~~~~~~~~~~~~~~~

**CSV** (Comma-Separated Values)

.. code-block:: yaml

    sources:
      drugs:
        type: csv
        path: "./data/drugs.csv"
        has_headers: true
        delimiter: ","

**TSV** (Tab-Separated Values)

.. code-block:: yaml

    sources:
      genes:
        type: tsv
        path: "./data/genes.tsv"
        has_headers: true

Database Source Types
~~~~~~~~~~~~~~~~~~~~~

**SQLite** (File-Based Database)

SQLite databases are file-based and require only a path:

.. code-block:: yaml

    sources:
      local_db:
        type: sqlite
        path: "./data/biomedical.sqlite"
        table: drugs
        # Or use a custom query:
        # query: "SELECT * FROM drugs WHERE approved = 1"

**MySQL**

MySQL databases require connection parameters:

.. code-block:: yaml

    sources:
      clinical_trials:
        type: mysql
        connection:
          host: "${DB_HOST}"
          port: 3306
          database: clinical_data
          username: "${DB_USER}"
          password: "${DB_PASSWORD}"
        table: trials

      # With custom query
      human_pathways:
        type: mysql
        connection:
          host: localhost
          database: aopdb
          username: "${DB_USER}"
          password: "${DB_PASSWORD}"
        query: |
          SELECT DISTINCT path_id, path_name
          FROM pathway_gene
          WHERE tax_id = 9606

**PostgreSQL**

PostgreSQL uses similar syntax to MySQL:

.. code-block:: yaml

    sources:
      research_db:
        type: postgres  # or "postgresql"
        connection:
          host: db.example.org
          port: 5432
          database: research
          username: "${PG_USER}"
          password: "${PG_PASSWORD}"
        table: experiments

      # Using connection string
      analytics:
        type: postgresql
        connection:
          connection_string: "postgresql://${PG_USER}:${PG_PASSWORD}@host:5432/analytics"
        query: "SELECT * FROM results WHERE status = 'complete'"

Database Connection Parameters
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 22 10 68

   * - Key
     - Required
     - Description
   * - ``host``
     - Yes*
     - Database server hostname
   * - ``port``
     - No
     - Port number (default: 3306 for MySQL, 5432 for PostgreSQL)
   * - ``database``
     - Yes*
     - Database name
   * - ``username``
     - Yes*
     - Database username
   * - ``password``
     - Yes*
     - Database password (use environment variables!)
   * - ``connection_string``
     - Alt
     - Full connection string (alternative to individual parameters)

\* Required unless using ``connection_string``

Environment Variables
~~~~~~~~~~~~~~~~~~~~~

Paths and connection parameters support environment variable expansion:

.. code-block:: yaml

    sources:
      # File path with env var
      drugbank:
        type: csv
        path: "${DATA_ROOT}/drugbank/drugs.csv"

      # Database credentials with env vars
      aopdb:
        type: mysql
        connection:
          host: "${MYSQL_HOST}"
          database: aopdb
          username: "${MYSQL_USER}"
          password: "${MYSQL_PASSWORD}"
        table: chemicals

Environment variables are resolved when loading the specification or by calling
``spec.resolve_environment_variables()``.

.. warning::

   Never hardcode database passwords in YAML files. Always use environment variables
   for sensitive credentials.

Transforms
----------

The ``transforms`` section defines custom, named transforms that can be referenced
in property mappings.

Structure
~~~~~~~~~

.. code-block:: yaml

    transforms:
      <transform_name>:
        type: <builtin_type>
        params:
          <param_name>: <param_value>

Transform Definition Keys
~~~~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 20 10 15 55

   * - Key
     - Required
     - Type
     - Description
   * - ``type``
     - Yes
     - string
     - Builtin transform type (see list below)
   * - ``params``
     - Depends
     - map
     - Parameters for the transform (if required by type)

Builtin Transform Types
~~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 18 35 47

   * - Type
     - Parameters
     - Description
   * - ``lowercase``
     - (none)
     - Convert string to lowercase
   * - ``uppercase``
     - (none)
     - Convert string to uppercase
   * - ``trim``
     - (none)
     - Remove leading and trailing whitespace
   * - ``prefix``
     - ``value``: string to prepend
     - Add prefix to value
   * - ``suffix``
     - ``value``: string to append
     - Add suffix to value
   * - ``strip_prefix``
     - ``value``: prefix to remove
     - Remove prefix if present
   * - ``strip_suffix``
     - ``value``: suffix to remove
     - Remove suffix if present
   * - ``split``
     - ``delimiter``: split character, ``index``: element index
     - Split string and return element at index (-1 for last)
   * - ``replace``
     - ``old``: substring to find, ``new``: replacement
     - Replace all occurrences of substring
   * - ``regex_extract``
     - ``pattern``: regex, ``group``: capture group number
     - Extract regex capture group
   * - ``to_int``
     - (none)
     - Parse and format as integer
   * - ``to_float``
     - (none)
     - Parse and format as floating point
   * - ``identity``
     - (none)
     - Return value unchanged (useful in chains)
   * - ``default_if_empty``
     - ``default``: fallback value
     - Use default if input is empty
   * - ``chain``
     - ``transforms``: comma-separated list
     - Apply multiple transforms in sequence

Transform Examples
~~~~~~~~~~~~~~~~~~

**Simple transform:**

.. code-block:: yaml

    transforms:
      clean_symbol:
        type: uppercase

**Transform with parameters:**

.. code-block:: yaml

    transforms:
      remove_db_prefix:
        type: strip_prefix
        params:
          value: "DB:"

**Chained transforms:**

.. code-block:: yaml

    transforms:
      normalize_id:
        type: chain
        params:
          transforms: "trim,uppercase,strip_prefix"

**Split and extract:**

.. code-block:: yaml

    transforms:
      get_last_segment:
        type: split
        params:
          delimiter: "::"
          index: "-1"

Node Mappings
-------------

The ``node_mappings`` section defines how data rows become OWL individuals.

Structure
~~~~~~~~~

.. code-block:: yaml

    node_mappings:
      - name: <mapping_name>
        source: <source_name>
        target_class: <class_local_name>
        mode: <create|enrich>
        iri_column: <column_name>
        filter:
          column: <column_name>
          value: <filter_value>
          contains: <boolean>
        match:
          source_column: <column_name>
          target_property: <property_local_name>
        properties:
          - column: <column_name>
            property: <property_local_name>
            transform: <transform_name>
            datatype: <xsd_type>

Node Mapping Keys
~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 20 10 15 55

   * - Key
     - Required
     - Type
     - Description
   * - ``name``
     - Yes
     - string
     - Unique, descriptive name for this mapping
   * - ``source``
     - Yes
     - string
     - Name of a source defined in ``sources`` section
   * - ``target_class``
     - Yes
     - string
     - Local name of the OWL class for individuals
   * - ``mode``
     - Yes
     - string
     - ``create`` for new individuals, ``enrich`` for existing
   * - ``iri_column``
     - Create only
     - string
     - Column used to generate individual IRIs
   * - ``filter``
     - No
     - object
     - Row filter criteria (see below)
   * - ``match``
     - Enrich only
     - object
     - How to match existing individuals (see below)
   * - ``properties``
     - No
     - list
     - List of property mappings (see below)

Mapping Modes
~~~~~~~~~~~~~

**create**: Creates new individuals. The ``iri_column`` value is used to generate a unique IRI.

.. code-block:: yaml

    node_mappings:
      - name: "Create Drugs"
        source: drugbank
        target_class: Drug
        mode: create
        iri_column: drugbank_id
        properties:
          - column: name
            property: commonName

**enrich**: Adds properties to existing individuals matched by a property value.

.. code-block:: yaml

    node_mappings:
      - name: "Add Toxicity Data"
        source: epa_data
        target_class: Drug
        mode: enrich
        match:
          source_column: cas_number
          target_property: casNumber
        properties:
          - column: toxicity_class
            property: toxicityClassification

Filter Definition
~~~~~~~~~~~~~~~~~

Filters control which rows are processed.

.. list-table::
   :header-rows: 1
   :widths: 20 10 15 55

   * - Key
     - Required
     - Type
     - Description
   * - ``column``
     - Yes
     - string
     - Column to filter on
   * - ``value``
     - Yes
     - string
     - Value to match
   * - ``contains``
     - No
     - boolean
     - If ``true``, substring match. If ``false``, exact match. Default: ``true``

.. code-block:: yaml

    filter:
      column: species
      value: "Homo sapiens"
      contains: false  # Exact match

Match Criteria
~~~~~~~~~~~~~~

Match criteria specify how to find existing individuals in ``enrich`` mode.

.. list-table::
   :header-rows: 1
   :widths: 20 10 15 55

   * - Key
     - Required
     - Type
     - Description
   * - ``source_column``
     - Yes
     - string
     - Column in the data source containing the match value
   * - ``target_property``
     - Yes
     - string
     - Data property local name to search for matching individuals

.. code-block:: yaml

    match:
      source_column: cas_number
      target_property: casNumber

Property Mappings
~~~~~~~~~~~~~~~~~

Property mappings define how columns become data property assertions.

.. list-table::
   :header-rows: 1
   :widths: 20 10 15 55

   * - Key
     - Required
     - Type
     - Description
   * - ``column``
     - Yes
     - string
     - Source column name
   * - ``property``
     - Yes
     - string
     - Target data property local name
   * - ``transform``
     - No
     - string
     - Transform name to apply to value
   * - ``datatype``
     - No
     - string
     - XSD datatype for typed literal (see below)

.. code-block:: yaml

    properties:
      - column: gene_id
        property: geneId
        datatype: xsd:integer

      - column: symbol
        property: geneSymbol
        transform: uppercase

      - column: description
        property: hasDescription

XSD Datatypes
~~~~~~~~~~~~~

Supported ``datatype`` values:

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Datatype
     - Description
   * - ``xsd:string``
     - Plain string (default if no datatype specified)
   * - ``xsd:integer``
     - Integer number
   * - ``xsd:int``
     - 32-bit integer
   * - ``xsd:long``
     - 64-bit integer
   * - ``xsd:double``
     - Double-precision floating point
   * - ``xsd:float``
     - Single-precision floating point
   * - ``xsd:decimal``
     - Arbitrary precision decimal
   * - ``xsd:boolean``
     - Boolean (true/false)
   * - ``xsd:date``
     - Date (YYYY-MM-DD)
   * - ``xsd:dateTime``
     - Date and time
   * - ``xsd:anyURI``
     - URI reference

Relationship Mappings
---------------------

The ``relationship_mappings`` section defines how to create object property assertions
between individuals.

Structure
~~~~~~~~~

.. code-block:: yaml

    relationship_mappings:
      - name: <mapping_name>
        source: <source_name>
        relationship: <object_property_local_name>
        inverse_relationship: <object_property_local_name>
        filter:
          column: <column_name>
          value: <filter_value>
          contains: <boolean>
        subject:
          class: <class_local_name>
          column: <column_name>
          match_property: <data_property_local_name>
        object:
          class: <class_local_name>
          column: <column_name>
          match_property: <data_property_local_name>

Relationship Mapping Keys
~~~~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 22 10 15 53

   * - Key
     - Required
     - Type
     - Description
   * - ``name``
     - Yes
     - string
     - Unique, descriptive name for this mapping
   * - ``source``
     - Yes
     - string
     - Name of a source defined in ``sources`` section
   * - ``relationship``
     - Yes
     - string
     - Local name of the object property
   * - ``inverse_relationship``
     - No
     - string
     - Local name of inverse object property (optional)
   * - ``filter``
     - No
     - object
     - Row filter criteria (same as node mappings)
   * - ``subject``
     - Yes
     - object
     - Subject entity reference (see below)
   * - ``object``
     - Yes
     - object
     - Object entity reference (see below)

Entity Reference
~~~~~~~~~~~~~~~~

Entity references (``subject`` and ``object``) specify how to find individuals.

.. list-table::
   :header-rows: 1
   :widths: 20 10 15 55

   * - Key
     - Required
     - Type
     - Description
   * - ``class``
     - Yes
     - string
     - Local name of the OWL class
   * - ``column``
     - Yes
     - string
     - Source column containing the match value
   * - ``match_property``
     - Yes
     - string
     - Data property local name to match against

.. code-block:: yaml

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

Complete Example
----------------

Here is a complete, annotated mapping specification:

.. code-block:: yaml

    # Schema version (required)
    version: "1.0"

    # Base IRI for generated individuals (required)
    base_iri: "http://example.org/biomedical#"

    # Custom transforms (optional)
    transforms:
      # Remove "GENE:" prefix
      clean_gene_id:
        type: strip_prefix
        params:
          value: "GENE:"

      # Normalize drug identifiers
      normalize_drug_id:
        type: chain
        params:
          transforms: "trim,uppercase"

    # Data sources (required, at least one)
    sources:
      # Primary drug data from DrugBank
      drugbank:
        type: csv
        path: "${DATA_DIR}/drugbank/drugs.csv"
        has_headers: true

      # Gene data from NCBI
      ncbi_gene:
        type: tsv
        path: "${DATA_DIR}/ncbi/genes.tsv"
        has_headers: true

      # Drug-gene interaction data
      drug_targets:
        type: csv
        path: "${DATA_DIR}/interactions/drug_targets.csv"
        has_headers: true

    # Node/individual mappings
    node_mappings:
      # Primary source for Drug individuals
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
            transform: normalize_drug_id
          - column: cas_number
            property: casNumber
          - column: molecular_weight
            property: molecularWeight
            datatype: xsd:double

      # Primary source for Gene individuals (human genes only)
      - name: "NCBI Human Genes"
        source: ncbi_gene
        target_class: Gene
        mode: create
        iri_column: gene_id
        filter:
          column: tax_id
          value: "9606"
          contains: false
        properties:
          - column: gene_id
            property: geneId
            transform: clean_gene_id
          - column: symbol
            property: geneSymbol
            transform: uppercase
          - column: description
            property: hasDescription

    # Relationship mappings
    relationship_mappings:
      # Create drug-gene target relationships
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

Validation
----------

The loader validates mapping specifications against the target ontology. Common validation errors:

**Class not found:**

.. code-block:: text

    Error: Class 'DrugXYZ' not found in ontology

The ``target_class`` in a node mapping doesn't exist in the ontology.

**Property not found:**

.. code-block:: text

    Error: Data property 'unknownProperty' not found in ontology

A ``property`` in a property mapping doesn't exist in the ontology.

**Source not defined:**

.. code-block:: text

    Error: Source 'undefined_source' referenced in mapping 'My Mapping' not defined

A node or relationship mapping references a source that wasn't defined.

**Missing required keys:**

.. code-block:: text

    Error: Node mapping 'My Mapping' with mode 'create' requires 'iri_column'

A create-mode mapping is missing the ``iri_column`` specification.

**Transform not found:**

.. code-block:: text

    Error: Transform 'nonexistent_transform' not defined

A property mapping references an undefined transform.

Best Practices
--------------

1. **Use descriptive mapping names**: Names appear in error messages and statistics

2. **Validate before loading**: Always call ``loader.validate()`` before ``loader.execute()``

3. **Use environment variables for paths**: Makes specs portable across environments

4. **Define transforms once, use many times**: Avoid duplicating transform logic

5. **Order mappings correctly**: Create primary individuals before enrichment mappings

6. **Use explicit datatypes**: Specify datatypes for numeric and boolean values

7. **Document your specs**: Add YAML comments to explain non-obvious mappings

See Also
--------

- :doc:`database_parsing` - Tutorial and usage guide
- :doc:`owl2_interfaces` - OWL2 API documentation
- :doc:`python_library` - Python library reference
