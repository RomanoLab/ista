#ifndef ISTA_OWL2_LOADER_MAPPING_SPEC_HPP
#define ISTA_OWL2_LOADER_MAPPING_SPEC_HPP

#include "transform_engine.hpp"
#include "../core/ontology.hpp"
#include <string>
#include <vector>
#include <map>
#include <optional>
#include <memory>

namespace ista {
namespace owl2 {
namespace loader {

/**
 * @brief Exception thrown when mapping specification is invalid
 */
class MappingSpecException : public std::runtime_error {
public:
    explicit MappingSpecException(const std::string& message)
        : std::runtime_error("Mapping spec error: " + message) {}
};

/**
 * @brief Filter criteria for rows
 */
struct FilterDef {
    std::string column;
    std::string value;
    bool contains = true;  // If true, value must be contained; if false, exact match
};

/**
 * @brief Criteria for matching existing individuals
 */
struct MatchCriteria {
    std::string source_column;      // Column in data source to match
    std::string target_property;    // Property local name to match against in ontology
};

/**
 * @brief Mapping from a source column to an ontology property
 */
struct PropertyMapping {
    std::string column;             // Source column name
    std::string property;           // Target property local name
    std::optional<std::string> transform;  // Optional transform name
    std::optional<std::string> datatype;   // Optional XSD datatype (for literals)
};

/**
 * @brief Database connection configuration
 */
struct DatabaseConnectionDef {
    std::string host = "localhost";
    int port = 0;
    std::string database;
    std::string username;
    std::string password;
    std::string connection_string;
    bool use_connection_string = false;
};

/**
 * @brief Definition of a data source
 */
struct DataSourceDef {
    std::string name;
    std::string type;  // "csv", "tsv", "sqlite", "mysql", "postgres"
    std::string path;  // File path (for file sources)
    char delimiter = ',';
    bool has_headers = true;
    
    // For database sources
    std::optional<DatabaseConnectionDef> connection;
    std::optional<std::string> table;
    std::optional<std::string> query;  // Custom SQL query
};

/**
 * @brief Mode for node mapping
 */
enum class MappingMode {
    CREATE,   // Primary source - creates new individuals
    ENRICH    // Secondary source - only adds properties to existing individuals
};

/**
 * @brief Mapping definition for creating/enriching individuals of a class
 */
struct NodeMapping {
    std::string name;               // Human-readable name for this mapping
    std::string source;             // Reference to data source name
    std::string target_class;       // OWL class local name
    
    MappingMode mode = MappingMode::CREATE;
    
    // For CREATE mode: column used to generate IRI
    std::optional<std::string> iri_column;
    
    // For ENRICH mode: how to find existing individuals
    std::optional<MatchCriteria> match;
    
    // Row filtering
    std::optional<FilterDef> filter;
    
    // Property mappings
    std::vector<PropertyMapping> properties;
    
    // Skip this mapping during execution
    bool skip = false;
};

/**
 * @brief Reference to an entity in a relationship
 */
struct EntityRef {
    std::string class_name;         // OWL class local name
    std::string column;             // Column containing the value
    std::string match_property;     // Property to match on
    std::optional<std::string> transform;  // Optional transform for column value
};

/**
 * @brief Mapping definition for creating relationships between individuals
 */
struct RelationshipMapping {
    std::string name;               // Human-readable name
    std::string source;             // Reference to data source name
    std::string relationship;       // Object property local name
    
    EntityRef subject;
    EntityRef object;
    
    std::optional<FilterDef> filter;
    
    // Optional inverse relationship to also create
    std::optional<std::string> inverse_relationship;
    
    bool skip = false;
};

/**
 * @brief Enrichment source for an entity type
 */
struct EnrichmentDef {
    std::string name;
    std::string source;
    std::optional<std::string> table;  // For database sources
    MatchCriteria match;
    std::vector<PropertyMapping> properties;
};

/**
 * @brief Complete definition for an entity type with primary and enrichment sources
 */
struct EntityTypeDef {
    std::string class_name;
    
    // Primary source (creates individuals)
    struct {
        std::string source;
        std::optional<std::string> table;
        std::string iri_column;
        std::optional<FilterDef> filter;
        std::vector<PropertyMapping> properties;
    } primary;
    
    // Secondary sources (enrich existing individuals)
    std::vector<EnrichmentDef> enrichments;
};

/**
 * @brief Result of validating a mapping specification
 */
struct ValidationResult {
    bool is_valid = true;
    std::vector<std::string> errors;
    std::vector<std::string> warnings;
    
    void add_error(const std::string& msg) {
        errors.push_back(msg);
        is_valid = false;
    }
    
    void add_warning(const std::string& msg) {
        warnings.push_back(msg);
    }
};

/**
 * @brief Complete mapping specification
 * 
 * This represents a complete specification for populating an ontology from
 * multiple data sources. It can be loaded from YAML files and validated
 * against an ontology.
 */
class DataMappingSpec {
public:
    std::string version = "1.0";
    std::string base_iri;
    
    // Named transforms
    std::map<std::string, TransformDef> transforms;
    
    // Data sources
    std::map<std::string, DataSourceDef> sources;
    
    // Entity type definitions (grouped primary + enrichments)
    std::map<std::string, EntityTypeDef> entity_types;
    
    // Flat node mappings (alternative to entity_types)
    std::vector<NodeMapping> node_mappings;
    
    // Relationship mappings
    std::vector<RelationshipMapping> relationship_mappings;
    
    /**
     * @brief Load a mapping specification from a YAML file
     * 
     * @param filepath Path to the YAML file
     * @return Parsed mapping specification
     * @throws MappingSpecException if parsing fails
     */
    static DataMappingSpec load_from_file(const std::string& filepath);
    
    /**
     * @brief Parse a mapping specification from YAML string
     * 
     * @param yaml_content YAML content as string
     * @return Parsed mapping specification
     */
    static DataMappingSpec parse(const std::string& yaml_content);
    
    /**
     * @brief Validate the specification against an ontology
     * 
     * Checks that:
     * - All referenced classes exist
     * - All referenced properties exist
     * - All referenced data sources are defined
     * - All referenced transforms are defined
     * 
     * @param ontology The ontology to validate against
     * @return Validation result with errors and warnings
     */
    ValidationResult validate(const Ontology& ontology) const;
    
    /**
     * @brief Serialize the specification to YAML string
     */
    std::string to_yaml() const;
    
    /**
     * @brief Save the specification to a YAML file
     */
    void save_to_file(const std::string& filepath) const;
    
    /**
     * @brief Expand entity_types into node_mappings
     * 
     * Converts the grouped entity_types definitions into flat node_mappings
     * for easier processing.
     */
    void expand_entity_types();
    
    /**
     * @brief Get all node mappings (including expanded entity_types)
     */
    std::vector<NodeMapping> get_all_node_mappings() const;
    
    /**
     * @brief Resolve environment variables in paths
     * 
     * Replaces ${VAR_NAME} with the value of environment variable VAR_NAME
     */
    void resolve_environment_variables();
    
private:
    // Helper to find a class by local name
    static bool has_class(const Ontology& ontology, const std::string& local_name);
    
    // Helper to find a property by local name
    static bool has_property(const Ontology& ontology, const std::string& local_name);
};

} // namespace loader
} // namespace owl2
} // namespace ista

#endif // ISTA_OWL2_LOADER_MAPPING_SPEC_HPP
