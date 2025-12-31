# Data Loading Architecture Redesign

## Problem Statement

The current approach to populating knowledge graphs (as seen in `neurokb.py`) has several issues:

1. **Fragile Configuration**: Large dictionaries with deeply nested `parse_config` parameters are error-prone and hard to validate
2. **Tight Coupling**: Data source parsers are tightly coupled to specific ontology properties via Python object references (`onto.xrefDrugbank`)
3. **No Declarative Specification**: Mappings are embedded in Python code rather than being declarative/serializable
4. **GUI Incompatibility**: The current system cannot be driven from the GUI which needs a structured way to define mappings
5. **Lambda Functions**: Data transforms use lambdas which can't be serialized or displayed in a UI
6. **Duplicate Code**: Much repeated logic across different `parse_node_type` and `parse_relationship_type` calls
7. **External Dependencies**: Heavy reliance on pandas, MySQLdb, openpyxl when simpler native solutions exist

## Design Goals

1. **Declarative Mapping Specifications**: Define mappings in YAML/JSON that can be:
   - Version controlled
   - Validated at load time
   - Displayed and edited in the GUI
   - Shared between projects

2. **Modular Pipeline Architecture**: Break loading into composable stages:
   - Source Connector (read data)
   - Field Extractor (select/rename columns)
   - Value Transformer (apply transformations)
   - Entity Mapper (map to ontology entities)
   - Axiom Generator (create OWL axioms)

3. **Built-in Transform Library**: Replace lambdas with named, parameterized transforms:
   - `split(delimiter, index)` - Split string and take index
   - `prefix(value)` - Add prefix
   - `suffix(value)` - Add suffix  
   - `strip_prefix(pattern)` - Remove prefix matching pattern
   - `lowercase`, `uppercase` - Case transforms
   - `to_int`, `to_float` - Type coercion

4. **Native C++ Core**: Implement performance-critical operations in C++ with Python bindings, consistent with ista's architecture

5. **GUI Integration**: Design for seamless GUI workflow:
   - Data source registration (already started)
   - Visual mapping configuration
   - Preview/validation before execution
   - Progress reporting during load

## Key Concept: Primary Authority Pattern

A common pattern in knowledge graph construction is that **multiple data sources contribute properties to the same entity type**:

1. **Primary Source (Authority)**: Defines the existence of individuals and their canonical identifiers
   - Creates new individuals
   - Sets the IRI and core identifying properties
   - Example: DrugBank defines Drug entities with DrugBank IDs

2. **Secondary Sources (Enrichment)**: Add properties to existing individuals via matching
   - Does NOT create new individuals
   - Matches existing individuals by a shared property (e.g., CAS number, gene symbol)
   - Adds additional properties from the secondary source
   - Example: EPA toxicity data matched to drugs via CAS number

This pattern is explicitly supported in the mapping specification via the `mode` field:
- `mode: create` - Primary source, creates individuals (default)
- `mode: enrich` - Secondary source, only adds to existing individuals

## Proposed Architecture

### 1. Data Mapping Specification Format

```yaml
# Example: neurokb_mappings.yaml
version: "1.0"
base_iri: "http://example.org/neurokb#"

# Define reusable transforms
transforms:
  extract_drugbank_id:
    type: split
    params: { delimiter: "::", index: -1 }
  
  extract_ncbi_gene:
    type: chain
    steps:
      - { type: split, params: { delimiter: "::", index: -1 } }
      - { type: to_int }

# Data sources with their file locations
sources:
  drugbank:
    type: csv
    path: "${DATA_DIR}/drugbank/drug links.csv"
    delimiter: ","
  
  epa_toxicity:
    type: csv
    path: "${DATA_DIR}/epa/chemical_toxicity.csv"
    
  hetionet_nodes:
    type: tsv
    path: "${DATA_DIR}/hetionet/hetionet-v1.0-nodes.tsv"
    
  aopdb:
    type: mysql
    connection:
      host: "${MYSQL_HOST}"
      database: "aopdb"

# Entity type definitions - specify primary authority and enrichment sources
entity_types:
  Drug:
    # Primary source creates individuals
    primary:
      source: drugbank
      iri_column: "DrugBank ID"
      properties:
        - column: "DrugBank ID"
          property: "xrefDrugbank"
        - column: "CAS Number"
          property: "xrefCasRN"
        - column: "Name"
          property: "commonName"
    
    # Secondary sources enrich existing individuals
    enrichments:
      - name: "EPA Toxicity Data"
        source: epa_toxicity
        match:
          source_column: "CAS"
          target_property: "xrefCasRN"  # Match on CAS number
        properties:
          - column: "LD50"
            property: "toxicityLD50"
          - column: "LC50"
            property: "toxicityLC50"
          - column: "EPA_ID"
            property: "xrefEPA"
      
      - name: "AOP-DB Chemical Info"
        source: aopdb
        table: "chemical_info"
        match:
          source_column: "DTX_id"
          target_property: "xrefDTXSID"
        properties:
          - column: "ChemicalID"
            property: "xrefMeSH"

  Gene:
    primary:
      source: ncbigene
      iri_column: "Symbol"
      properties:
        - column: "GeneID"
          property: "xrefNcbiGene"
        - column: "Symbol"
          property: "geneSymbol"
        - column: "Full_name_from_nomenclature_authority"
          property: "commonName"
    
    enrichments:
      - name: "HGNC Cross-references"
        source: ncbigene  # Same source, different columns via compound fields
        match:
          source_column: "Symbol"
          target_property: "geneSymbol"
        compound_field:
          column: "dbXrefs"
          delimiter: "|"
          field_prefix: ":"
        properties:
          - field: "MIM"
            property: "xrefOMIM"
          - field: "HGNC"
            property: "xrefHGNC"
          - field: "Ensembl"
            property: "xrefEnsembl"

# ALTERNATIVE: Flat node_mappings with explicit mode (for simpler cases)
# This is equivalent to the entity_types structure above but flatter
node_mappings:
  # Primary source - creates individuals
  - name: "DrugBank Drugs"
    source: drugbank
    target_class: "Drug"
    mode: create  # This is the default
    iri_column: "DrugBank ID"
    properties:
      - column: "DrugBank ID"
        property: "xrefDrugbank"
      - column: "CAS Number"
        property: "xrefCasRN"
      - column: "Name"
        property: "commonName"
  
  # Secondary source - enriches existing individuals
  - name: "EPA Toxicity for Drugs"
    source: epa_toxicity
    target_class: "Drug"
    mode: enrich  # Only adds to existing individuals
    match:
      source_column: "CAS"
      target_property: "xrefCasRN"
    properties:
      - column: "LD50"
        property: "toxicityLD50"
      - column: "LC50"
        property: "toxicityLC50"
        
  - name: "Hetionet Drug Classes"
    source: hetionet_nodes
    target_class: "DrugClass"
    iri_column: "name"
    filter:
      column: "kind"
      value: "Pharmacologic Class"
    properties:
      - column: "id"
        property: "xrefNciThesaurus"
        transform: extract_drugbank_id
      - column: "name"
        property: "commonName"

# Relationship mappings
relationship_mappings:
  - name: "Gene-Disease Associations"
    source: disgenet
    relationship: "geneAssociatesWithDisease"
    subject:
      class: "Gene"
      column: "geneSymbol"
      match_property: "geneSymbol"
    object:
      class: "Disease"
      column: "diseaseId"
      match_property: "xrefUmlsCUI"
    filter:
      column: "diseaseType"
      value: "disease"
```

### 2. Core Components (C++)

#### DataMappingSpec (lib/owl2/loader/mapping_spec.hpp)

```cpp
// Represents a complete mapping specification
struct DataMappingSpec {
    std::string version;
    std::string base_iri;
    std::map<std::string, TransformDef> transforms;
    std::map<std::string, DataSourceDef> sources;
    std::vector<NodeMapping> node_mappings;
    std::vector<RelationshipMapping> relationship_mappings;
    
    // Load from YAML file
    static DataMappingSpec load_from_file(const std::string& filepath);
    
    // Validate against ontology
    ValidationResult validate(const Ontology& ontology) const;
    
    // Serialize back to YAML
    void save_to_file(const std::string& filepath) const;
};

struct TransformDef {
    std::string type;  // "split", "chain", "prefix", etc.
    std::map<std::string, std::string> params;
    std::vector<TransformDef> steps;  // For chain transforms
};

struct DataSourceDef {
    std::string type;  // "csv", "tsv", "mysql", "sqlite"
    std::string path;
    char delimiter = ',';
    // Database-specific fields
    std::optional<DatabaseConnectionInfo> connection;
};

struct MatchCriteria {
    std::string source_column;      // Column in data source to match
    std::string target_property;    // Property IRI to match against in ontology
};

struct PropertyMapping {
    std::string column;
    std::string property;  // Local name, resolved against ontology
    std::optional<std::string> transform;  // Reference to named transform
};

enum class MappingMode {
    CREATE,   // Primary source - creates new individuals
    ENRICH    // Secondary source - only adds properties to existing individuals
};

struct NodeMapping {
    std::string name;
    std::string source;  // Reference to data source
    std::string target_class;  // Local name of OWL class
    
    MappingMode mode = MappingMode::CREATE;
    
    // For CREATE mode: column used to generate IRI
    std::optional<std::string> iri_column;
    
    // For ENRICH mode: how to find existing individuals
    std::optional<MatchCriteria> match;
    
    std::optional<FilterDef> filter;
    std::vector<PropertyMapping> properties;
};

struct RelationshipMapping {
    std::string name;
    std::string source;
    std::string relationship;  // Local name of object property
    EntityRef subject;
    EntityRef object;
    std::optional<FilterDef> filter;
};
```

#### TransformEngine (lib/owl2/loader/transform_engine.hpp)

```cpp
class TransformEngine {
public:
    // Register built-in transforms
    TransformEngine();
    
    // Apply a transform by name
    std::string apply(const std::string& transform_name,
                      const std::string& value,
                      const std::map<std::string, TransformDef>& transforms) const;
    
    // Register a custom transform (for extensibility)
    void register_transform(const std::string& name,
                           std::function<std::string(const std::string&, 
                                                     const std::map<std::string, std::string>&)> fn);
    
private:
    std::map<std::string, TransformFunc> builtin_transforms_;
};
```

#### DataLoader (lib/owl2/loader/data_loader.hpp)

```cpp
// Progress callback for UI integration
using ProgressCallback = std::function<void(size_t current, size_t total, const std::string& message)>;

class DataLoader {
public:
    DataLoader(Ontology& ontology, const DataMappingSpec& spec);
    
    // Execute all mappings
    LoadResult execute_all(ProgressCallback progress = nullptr);
    
    // Execute specific node mapping by name
    LoadResult execute_node_mapping(const std::string& name, 
                                    ProgressCallback progress = nullptr);
    
    // Execute specific relationship mapping by name
    LoadResult execute_relationship_mapping(const std::string& name,
                                            ProgressCallback progress = nullptr);
    
    // Dry run - validate without modifying ontology
    ValidationResult validate() const;
    
    // Preview - show sample of what would be created
    PreviewResult preview(const std::string& mapping_name, size_t max_rows = 10) const;
    
private:
    Ontology& ontology_;
    DataMappingSpec spec_;
    TransformEngine transform_engine_;
    
    // Internal execution methods
    size_t execute_node_mapping_internal(const NodeMapping& mapping, 
                                         ProgressCallback progress);
    size_t execute_relationship_mapping_internal(const RelationshipMapping& mapping,
                                                  ProgressCallback progress);
};

struct LoadResult {
    bool success;
    size_t entities_created;
    size_t entities_merged;
    size_t relationships_created;
    std::vector<std::string> warnings;
    std::vector<std::string> errors;
    std::chrono::milliseconds duration;
};
```

### 3. Python Interface

```python
# ista/loader.py
from ista import owl2

class DataLoader:
    """High-level interface for loading data into ontologies."""
    
    def __init__(self, ontology: owl2.Ontology, mapping_file: str = None):
        """
        Initialize a data loader.
        
        Parameters
        ----------
        ontology : owl2.Ontology
            The ontology to populate
        mapping_file : str, optional
            Path to YAML mapping specification file
        """
        self._ontology = ontology
        self._spec = None
        if mapping_file:
            self.load_mapping(mapping_file)
    
    def load_mapping(self, filepath: str) -> None:
        """Load a mapping specification from YAML file."""
        self._spec = owl2.DataMappingSpec.load_from_file(filepath)
    
    def validate(self) -> ValidationResult:
        """Validate mappings against the ontology."""
        return self._spec.validate(self._ontology)
    
    def preview(self, mapping_name: str, max_rows: int = 10) -> PreviewResult:
        """Preview what a mapping would create without executing."""
        loader = owl2.DataLoader(self._ontology, self._spec)
        return loader.preview(mapping_name, max_rows)
    
    def execute(self, mapping_name: str = None, progress_callback=None) -> LoadResult:
        """
        Execute mappings.
        
        Parameters
        ----------
        mapping_name : str, optional
            Execute only this mapping. If None, executes all.
        progress_callback : callable, optional
            Function(current, total, message) for progress updates
        """
        loader = owl2.DataLoader(self._ontology, self._spec)
        if mapping_name:
            if mapping_name in [m.name for m in self._spec.node_mappings]:
                return loader.execute_node_mapping(mapping_name, progress_callback)
            else:
                return loader.execute_relationship_mapping(mapping_name, progress_callback)
        else:
            return loader.execute_all(progress_callback)


# Example usage (replaces neurokb.py)
def build_neurokb():
    ont = owl2.RDFXMLParser.parse_from_file("neurokb.rdf")
    
    loader = DataLoader(ont, "neurokb_mappings.yaml")
    
    # Validate before execution
    validation = loader.validate()
    if not validation.is_valid:
        for error in validation.errors:
            print(f"ERROR: {error}")
        return
    
    # Execute with progress reporting
    def on_progress(current, total, message):
        print(f"[{current}/{total}] {message}")
    
    result = loader.execute(progress_callback=on_progress)
    
    print(f"Created {result.entities_created} entities")
    print(f"Created {result.relationships_created} relationships")
    
    owl2.RDFXMLSerializer.serialize_to_file(ont, "neurokb-populated.rdf")
```

### 4. GUI Integration

The GUI already has `DataSource` structures. We extend this with mapping configuration:

```cpp
// In kg_editor.hpp - extend DataSource struct
struct ColumnMapping {
    std::string column_name;
    std::string target_property;  // IRI of data property
    std::string transform;  // Optional transform name
};

struct DataSourceMapping {
    std::string target_class_iri;
    std::string iri_column;
    std::vector<ColumnMapping> property_mappings;
    
    // For relationship sources
    bool is_relationship = false;
    std::string relationship_iri;
    std::string subject_column;
    std::string subject_match_property;
    std::string object_column;
    std::string object_match_property;
};

// Add to DataSource
struct DataSource {
    // ... existing fields ...
    
    std::optional<DataSourceMapping> mapping;
    bool mapping_validated = false;
    std::vector<std::string> validation_errors;
};
```

GUI workflow:
1. User adds data source (file or database) - **Already implemented**
2. User clicks "Configure Mapping" on a data source
3. Dialog shows:
   - Target class dropdown (populated from ontology classes)
   - IRI column dropdown (populated from source columns)
   - Property mapping table: source column -> ontology property
   - Transform selection for each column
4. User clicks "Validate" to check mapping
5. User clicks "Preview" to see sample output
6. User clicks "Execute" to run the mapping

### 5. Implementation Phases

#### Phase 1: Core C++ Infrastructure
- [ ] Create `lib/owl2/loader/` directory
- [ ] Implement `TransformEngine` with builtin transforms
- [ ] Implement `DataMappingSpec` parsing (simple YAML parser or header-only library)
- [ ] Implement basic `DataLoader` for CSV sources
- [ ] Add Python bindings

#### Phase 2: Python API and Migration
- [ ] Create `ista/loader.py` high-level interface
- [ ] Migrate one node type from neurokb.py as proof of concept
- [ ] Create `neurokb_mappings.yaml` specification
- [ ] Validate against original neurokb output

#### Phase 3: Full Data Source Support
- [ ] Add TSV support (trivial - delimiter change)
- [ ] Add SQLite support (use existing libs or minimal native)
- [ ] Evaluate MySQL support (may keep as optional dependency)
- [ ] Add Excel support (via CSV export or minimal reader)

#### Phase 4: GUI Integration
- [ ] Add mapping configuration dialog
- [ ] Implement preview functionality
- [ ] Implement validation display
- [ ] Add execute with progress bar
- [ ] Export/import mapping specifications

#### Phase 5: Complete Migration
- [ ] Convert all neurokb.py mappings to YAML
- [ ] Remove old DatabaseParser classes
- [ ] Update documentation
- [ ] Add comprehensive tests

### 6. Minimal External Dependencies

Following ista's principle of minimal dependencies:

1. **YAML Parsing**: Use header-only yaml-cpp or implement minimal YAML subset parser
2. **CSV Parsing**: Already have native implementation in CSVParser
3. **SQLite**: Use bundled SQLite amalgamation (single .c file)
4. **MySQL/PostgreSQL**: Keep as optional, use existing MySQLdb in Python wrapper only
5. **Excel**: Support via CSV export, or use minimal xlsx reader (header-only)

### 7. Comparison: Before vs After

#### Example 1: Primary Source (Creating Individuals)

**Before (neurokb.py):**
```python
drugbank.parse_node_type(
    node_type="Drug",
    source_filename="drug links.csv",
    fmt="csv",
    parse_config={
        "iri_column_name": "DrugBank ID",
        "headers": True,
        "data_property_map": {
            "DrugBank ID": onto.xrefDrugbank,
            "CAS Number": onto.xrefCasRN,
            "Name": onto.commonName,
        },
    },
    merge=False,
    skip=False,
)
```

**After (neurokb_mappings.yaml):**
```yaml
node_mappings:
  - name: "DrugBank Drugs"
    source: drugbank
    target_class: Drug
    mode: create  # Primary authority - creates individuals
    iri_column: DrugBank ID
    properties:
      - column: DrugBank ID
        property: xrefDrugbank
      - column: CAS Number
        property: xrefCasRN
      - column: Name
        property: commonName
```

#### Example 2: Secondary Source (Enriching Existing Individuals)

**Before (neurokb.py):**
```python
# Add EPA toxicity data to existing drugs
aopdb.parse_node_type(
    node_type="Drug",
    source_table="chemical_info",
    parse_config={
        "iri_column_name": "DTX_id",
        "data_property_map": {"ChemicalID": onto.xrefMeSH},
        "merge_column": {
            "source_column_name": "DTX_id",
            "data_property": onto.xrefDTXSID,
        },
    },
    merge=True,  # Merge with existing entities
    skip=False,
)
```

**After (neurokb_mappings.yaml):**
```yaml
node_mappings:
  # ... primary Drug mapping first ...
  
  - name: "AOP-DB Chemical Enrichment"
    source: aopdb
    target_class: Drug
    mode: enrich  # Secondary source - only adds to existing individuals
    match:
      source_column: DTX_id
      target_property: xrefDTXSID
    properties:
      - column: ChemicalID
        property: xrefMeSH
```

#### Example 3: Using Entity Types for Grouped Definitions

For complex entity types with multiple sources, use the `entity_types` section:

```yaml
entity_types:
  Drug:
    primary:
      source: drugbank
      iri_column: DrugBank ID
      properties:
        - { column: DrugBank ID, property: xrefDrugbank }
        - { column: CAS Number, property: xrefCasRN }
        - { column: Name, property: commonName }
    
    enrichments:
      - name: "EPA Toxicity"
        source: epa_toxicity
        match: { source_column: CAS, target_property: xrefCasRN }
        properties:
          - { column: LD50, property: toxicityLD50 }
          - { column: LC50, property: toxicityLC50 }
      
      - name: "AOP-DB Cross-refs"
        source: aopdb
        match: { source_column: DTX_id, target_property: xrefDTXSID }
        properties:
          - { column: ChemicalID, property: xrefMeSH }
```

#### Python Usage

**After (Python - simple):**
```python
from ista import owl2
from ista.loader import DataLoader

ont = owl2.RDFXMLParser.parse_from_file("neurokb.rdf")
loader = DataLoader(ont, "neurokb_mappings.yaml")
result = loader.execute()
owl2.RDFXMLSerializer.serialize_to_file(ont, "neurokb-populated.rdf")
```

**After (Python - with control):**
```python
from ista import owl2
from ista.loader import DataLoader

ont = owl2.RDFXMLParser.parse_from_file("neurokb.rdf")
loader = DataLoader(ont, "neurokb_mappings.yaml")

# Execute in order: primary sources first, then enrichments
result1 = loader.execute("DrugBank Drugs")  # Creates Drug individuals
result2 = loader.execute("EPA Toxicity")     # Enriches with toxicity data
result3 = loader.execute("AOP-DB Cross-refs") # Enriches with more xrefs

print(f"Created {result1.entities_created} drugs")
print(f"Enriched {result2.entities_merged} drugs with EPA data")
print(f"Enriched {result3.entities_merged} drugs with AOP-DB data")
```

### 8. Benefits

1. **Declarative**: Mappings are data, not code
2. **Validated**: Catch errors before execution
3. **Portable**: YAML files can be shared, version controlled, reviewed
4. **GUI-compatible**: Same spec drives both CLI and GUI
5. **Testable**: Preview functionality allows verification
6. **Maintainable**: Clear separation of concerns
7. **Performant**: C++ core with Python convenience layer
8. **Minimal dependencies**: Consistent with ista philosophy
9. **Primary/Enrich Pattern**: Explicit support for multiple sources per entity type
   - Primary sources define entity existence and IRIs
   - Secondary sources enrich with additional properties via matching
   - Clear execution order and dependency management
