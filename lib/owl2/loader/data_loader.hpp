#ifndef ISTA_OWL2_LOADER_DATA_LOADER_HPP
#define ISTA_OWL2_LOADER_DATA_LOADER_HPP

#include "mapping_spec.hpp"
#include "transform_engine.hpp"
#include "../core/ontology.hpp"
#include <string>
#include <vector>
#include <map>
#include <functional>
#include <memory>
#include <sstream>
#include <optional>

namespace ista {
namespace owl2 {
namespace loader {

/**
 * @brief Exception thrown when data loading fails
 */
class DataLoaderException : public std::runtime_error {
public:
    explicit DataLoaderException(const std::string& message)
        : std::runtime_error("Data loader error: " + message) {}
};

/**
 * @brief Progress callback for loading operations
 * 
 * @param current Current row number
 * @param total Total rows (0 if unknown)
 * @param mapping_name Name of the current mapping being processed
 */
using ProgressCallback = std::function<void(size_t current, size_t total, const std::string& mapping_name)>;

/**
 * @brief Statistics from a loading operation
 */
struct LoadingStats {
    size_t rows_processed = 0;
    size_t individuals_created = 0;
    size_t individuals_enriched = 0;
    size_t properties_added = 0;
    size_t relationships_created = 0;
    size_t rows_skipped = 0;
    size_t errors = 0;
    std::vector<std::string> error_messages;
    
    void merge(const LoadingStats& other) {
        rows_processed += other.rows_processed;
        individuals_created += other.individuals_created;
        individuals_enriched += other.individuals_enriched;
        properties_added += other.properties_added;
        relationships_created += other.relationships_created;
        rows_skipped += other.rows_skipped;
        errors += other.errors;
        for (const auto& msg : other.error_messages) {
            error_messages.push_back(msg);
        }
    }
    
    std::string summary() const {
        std::ostringstream ss;
        ss << "Loading Statistics:\n";
        ss << "  Rows processed: " << rows_processed << "\n";
        ss << "  Individuals created: " << individuals_created << "\n";
        ss << "  Individuals enriched: " << individuals_enriched << "\n";
        ss << "  Properties added: " << properties_added << "\n";
        ss << "  Relationships created: " << relationships_created << "\n";
        ss << "  Rows skipped: " << rows_skipped << "\n";
        ss << "  Errors: " << errors;
        return ss.str();
    }
};

/**
 * @brief Row of data from a data source
 */
using DataRow = std::map<std::string, std::string>;

/**
 * @brief Abstract data source reader interface
 */
class DataSourceReader {
public:
    virtual ~DataSourceReader() = default;
    
    /**
     * @brief Open the data source
     * @return true if successful
     */
    virtual bool open() = 0;
    
    /**
     * @brief Close the data source
     */
    virtual void close() = 0;
    
    /**
     * @brief Check if there are more rows
     */
    virtual bool has_next() const = 0;
    
    /**
     * @brief Read the next row
     */
    virtual DataRow next() = 0;
    
    /**
     * @brief Get the column headers
     */
    virtual std::vector<std::string> headers() const = 0;
    
    /**
     * @brief Get total row count (0 if unknown)
     */
    virtual size_t row_count() const { return 0; }
    
    /**
     * @brief Reset to beginning
     */
    virtual void reset() = 0;
};

/**
 * @brief CSV file reader implementation
 */
class CsvReader : public DataSourceReader {
public:
    CsvReader(const std::string& filepath, char delimiter = ',', bool has_headers = true);
    ~CsvReader() override;
    
    bool open() override;
    void close() override;
    bool has_next() const override;
    DataRow next() override;
    std::vector<std::string> headers() const override;
    size_t row_count() const override;
    void reset() override;
    
private:
    std::string filepath_;
    char delimiter_;
    bool has_headers_;
    std::vector<std::string> headers_;
    std::unique_ptr<std::ifstream> file_;
    size_t current_line_;
    size_t total_lines_;
    bool at_end_;
    
    std::vector<std::string> parse_line(const std::string& line) const;
    void count_lines();
};

/**
 * @brief Factory for creating data source readers
 */
class DataSourceFactory {
public:
    /**
     * @brief Create a reader for the given data source definition
     */
    static std::unique_ptr<DataSourceReader> create_reader(const DataSourceDef& source);
};

/**
 * @brief Main data loading engine
 * 
 * The DataLoader uses a mapping specification to populate an ontology
 * from one or more data sources. It supports both CREATE mode (for
 * primary data sources that define individual existence) and ENRICH
 * mode (for secondary sources that add properties to existing individuals).
 */
class DataLoader {
public:
    /**
     * @brief Create a DataLoader for the given ontology
     * 
     * @param ontology The ontology to populate
     */
    explicit DataLoader(Ontology& ontology);
    
    /**
     * @brief Set the mapping specification
     */
    void set_mapping_spec(const DataMappingSpec& spec);
    
    /**
     * @brief Load the mapping specification from a YAML file
     */
    void load_mapping_spec(const std::string& filepath);
    
    /**
     * @brief Set a progress callback
     */
    void set_progress_callback(ProgressCallback callback);
    
    /**
     * @brief Execute all mappings in the specification
     * 
     * @return Loading statistics
     */
    LoadingStats execute();
    
    /**
     * @brief Execute a specific node mapping by name
     */
    LoadingStats execute_node_mapping(const std::string& mapping_name);
    
    /**
     * @brief Execute a specific relationship mapping by name
     */
    LoadingStats execute_relationship_mapping(const std::string& mapping_name);
    
    /**
     * @brief Execute all node mappings
     */
    LoadingStats execute_all_node_mappings();
    
    /**
     * @brief Execute all relationship mappings
     */
    LoadingStats execute_all_relationship_mappings();
    
    /**
     * @brief Get the current mapping specification
     */
    const DataMappingSpec& mapping_spec() const { return spec_; }
    
    /**
     * @brief Validate the mapping specification against the ontology
     */
    ValidationResult validate();
    
private:
    Ontology& ontology_;
    DataMappingSpec spec_;
    TransformEngine transform_engine_;
    ProgressCallback progress_callback_;
    
    // Cache for data source readers
    std::map<std::string, std::unique_ptr<DataSourceReader>> readers_;
    
    /**
     * @brief Get or create a reader for the given source
     */
    DataSourceReader* get_reader(const std::string& source_name);
    
    /**
     * @brief Process a single node mapping
     */
    LoadingStats process_node_mapping(const NodeMapping& mapping);
    
    /**
     * @brief Process a single relationship mapping
     */
    LoadingStats process_relationship_mapping(const RelationshipMapping& mapping);
    
    /**
     * @brief Apply a transform to a value
     */
    std::string apply_transform(const std::string& value, 
                                const std::optional<std::string>& transform_name);
    
    /**
     * @brief Check if a row passes the filter criteria
     */
    bool passes_filter(const DataRow& row, const std::optional<FilterDef>& filter);
    
    /**
     * @brief Find a class by local name
     * @return optional containing the class if found
     */
    std::optional<Class> find_class(const std::string& local_name);
    
    /**
     * @brief Find a data property by local name
     * @return optional containing the property if found
     */
    std::optional<DataProperty> find_data_property(const std::string& local_name);
    
    /**
     * @brief Find an object property by local name
     * @return optional containing the property if found
     */
    std::optional<ObjectProperty> find_object_property(const std::string& local_name);
    
    /**
     * @brief Find an individual by property value
     * @return optional containing the individual if found
     */
    std::optional<NamedIndividual> find_individual_by_property(
        const std::string& property_name,
        const std::string& value);
    
    /**
     * @brief Create an IRI for a new individual
     */
    IRI make_individual_iri(const std::string& base_value, 
                            const Class& cls);
    
    /**
     * @brief Sanitize a string for use in an IRI
     */
    static std::string sanitize_for_iri(const std::string& value);
    
    /**
     * @brief Add a data property assertion to an individual
     */
    void add_data_property(const NamedIndividual& individual,
                           const std::string& property_name,
                           const std::string& value,
                           const std::optional<std::string>& datatype,
                           LoadingStats& stats);
};

} // namespace loader
} // namespace owl2
} // namespace ista

#endif // ISTA_OWL2_LOADER_DATA_LOADER_HPP
