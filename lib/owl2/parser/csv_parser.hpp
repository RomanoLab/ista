#ifndef ISTA_OWL2_CSV_PARSER_HPP
#define ISTA_OWL2_CSV_PARSER_HPP

#include "../core/ontology.hpp"
#include <string>
#include <vector>
#include <unordered_map>
#include <functional>
#include <memory>
#include <stdexcept>
#include <fstream>
#include <sstream>

namespace ista {
namespace owl2 {

/**
 * @brief Exception thrown when CSV parsing fails
 */
class CSVParseException : public std::runtime_error {
public:
    explicit CSVParseException(const std::string& message)
        : std::runtime_error("CSV Parse Error: " + message) {}
};

/**
 * @brief Configuration for parsing node types from CSV files
 */
struct NodeTypeConfig {
    // Default constructor
    NodeTypeConfig() = default;
    
    // Column name that contains unique identifiers for creating IRIs
    std::string iri_column_name;
    
    // Whether the file has a header row
    bool has_headers = true;
    
    // Map from CSV column names to data property IRIs
    std::unordered_map<std::string, IRI> data_property_map;
    
    // Optional: Transform functions for column data
    // Key is column name, value is transform function
    std::unordered_map<std::string, std::function<std::string(const std::string&)>> data_transforms;
    
    // Optional: Filter rows based on column value
    std::string filter_column;
    std::string filter_value;
    
    // Optional: Merge with existing individuals based on property value
    bool merge_mode = false;
    std::optional<IRI> merge_property_iri;
    std::string merge_column_name;
};

/**
 * @brief Configuration for parsing relationship types from CSV files
 */
struct RelationshipTypeConfig {
    // Default constructor
    RelationshipTypeConfig() = default;
    
    // Whether the file has a header row
    bool has_headers = true;
    
    // Subject (source) configuration
    std::optional<IRI> subject_class_iri;
    std::string subject_column_name;
    std::optional<IRI> subject_match_property_iri;
    
    // Object (target) configuration
    std::optional<IRI> object_class_iri;
    std::string object_column_name;
    std::optional<IRI> object_match_property_iri;
    
    // Optional: Filter rows
    std::string filter_column;
    std::string filter_value;
    
    // Optional: Transform functions
    std::unordered_map<std::string, std::function<std::string(const std::string&)>> data_transforms;
};

/**
 * @brief High-performance CSV parser for populating OWL2 ontologies
 * 
 * This class provides efficient parsing of large CSV files to dynamically
 * create ontology instances and relationships. It supports:
 * - Memory-efficient streaming parsing
 * - Data transformations
 * - Row filtering
 * - Merging with existing individuals
 * - Both node (individual) and edge (relationship) parsing
 */
class CSVParser {
public:
    /**
     * @brief Construct a CSV parser
     * 
     * @param ontology The ontology to populate
     * @param base_iri Base IRI for creating individual IRIs
     */
    explicit CSVParser(Ontology& ontology, const std::string& base_iri);
    
    /**
     * @brief Parse a CSV file to create individuals of a specific class
     * 
     * @param filename Path to the CSV file
     * @param class_iri IRI of the class to instantiate
     * @param config Configuration for parsing
     * @param delimiter CSV delimiter (default: ',')
     * @return Number of individuals created
     */
    size_t parse_node_type(
        const std::string& filename,
        const IRI& class_iri,
        const NodeTypeConfig& config,
        char delimiter = ','
    );
    
    /**
     * @brief Parse a CSV file to create relationships between individuals
     * 
     * @param filename Path to the CSV file
     * @param property_iri IRI of the object property
     * @param config Configuration for parsing
     * @param delimiter CSV delimiter (default: ',')
     * @return Number of relationships created
     */
    size_t parse_relationship_type(
        const std::string& filename,
        const IRI& property_iri,
        const RelationshipTypeConfig& config,
        char delimiter = ','
    );
    
    /**
     * @brief Set a custom IRI generator function
     * 
     * By default, IRIs are generated as: base_iri + "#" + value
     * This allows custom IRI generation logic.
     * 
     * @param generator Function that takes (base_iri, column_value, class_name) and returns IRI string
     */
    void set_iri_generator(std::function<std::string(const std::string&, const std::string&, const std::string&)> generator);
    
    /**
     * @brief Get the ontology being populated
     */
    Ontology& get_ontology() { return ontology_; }
    
private:
    // Parse a CSV row into columns
    std::vector<std::string> parse_csv_line(const std::string& line, char delimiter);
    
    // Create an IRI for an individual
    IRI create_individual_iri(const std::string& value, const std::string& class_name);
    
    // Find an individual by property value
    std::shared_ptr<NamedIndividual> find_individual_by_property(
        const IRI& property_iri,
        const std::string& value
    );
    
    // Apply data transforms to a value
    std::string apply_transform(
        const std::string& column_name,
        const std::string& value,
        const std::unordered_map<std::string, std::function<std::string(const std::string&)>>& transforms
    );
    
    Ontology& ontology_;
    std::string base_iri_;
    std::function<std::string(const std::string&, const std::string&, const std::string&)> iri_generator_;
    
    // Cache for finding individuals by property values
    std::unordered_map<std::string, std::shared_ptr<NamedIndividual>> individual_cache_;
};

} // namespace owl2
} // namespace ista

#endif // ISTA_OWL2_CSV_PARSER_HPP
