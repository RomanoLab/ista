#include "data_loader.hpp"
#include <fstream>
#include <sstream>
#include <algorithm>
#include <cctype>
#include <regex>

// Conditional includes for database readers
#ifdef ISTA_HAS_SQLITE
#include "sqlite_reader.hpp"
#endif
#ifdef ISTA_HAS_MYSQL
#include "mysql_reader.hpp"
#endif
#ifdef ISTA_HAS_POSTGRES
#include "postgres_reader.hpp"
#endif

namespace ista {
namespace owl2 {
namespace loader {

// CsvReader implementation

CsvReader::CsvReader(const std::string& filepath, char delimiter, bool has_headers)
    : filepath_(filepath), delimiter_(delimiter), has_headers_(has_headers),
      current_line_(0), total_lines_(0), at_end_(false) {}

CsvReader::~CsvReader() {
    close();
}

bool CsvReader::open() {
    file_ = std::make_unique<std::ifstream>(filepath_);
    if (!file_->is_open()) {
        return false;
    }
    
    current_line_ = 0;
    at_end_ = false;
    
    // Count total lines for progress reporting
    count_lines();
    
    // Reset to beginning
    file_->clear();
    file_->seekg(0);
    
    // Read headers if present
    if (has_headers_) {
        std::string header_line;
        if (std::getline(*file_, header_line)) {
            headers_ = parse_line(header_line);
            current_line_++;
        }
    }
    
    return true;
}

void CsvReader::close() {
    if (file_ && file_->is_open()) {
        file_->close();
    }
    file_.reset();
}

bool CsvReader::has_next() const {
    return file_ && file_->is_open() && !at_end_ && file_->peek() != EOF;
}

DataRow CsvReader::next() {
    DataRow row;
    
    if (!has_next()) {
        at_end_ = true;
        return row;
    }
    
    std::string line;
    if (std::getline(*file_, line)) {
        current_line_++;
        std::vector<std::string> values = parse_line(line);
        
        // Map values to headers
        for (size_t i = 0; i < headers_.size() && i < values.size(); ++i) {
            row[headers_[i]] = values[i];
        }
    } else {
        at_end_ = true;
    }
    
    return row;
}

std::vector<std::string> CsvReader::headers() const {
    return headers_;
}

size_t CsvReader::row_count() const {
    return total_lines_ > 0 ? (has_headers_ ? total_lines_ - 1 : total_lines_) : 0;
}

void CsvReader::reset() {
    if (file_) {
        file_->clear();
        file_->seekg(0);
        current_line_ = 0;
        at_end_ = false;
        
        // Skip headers again
        if (has_headers_) {
            std::string header_line;
            std::getline(*file_, header_line);
            current_line_++;
        }
    }
}

std::vector<std::string> CsvReader::parse_line(const std::string& line) const {
    std::vector<std::string> result;
    std::string field;
    bool in_quotes = false;
    
    for (size_t i = 0; i < line.size(); ++i) {
        char c = line[i];
        
        if (c == '"') {
            if (in_quotes && i + 1 < line.size() && line[i + 1] == '"') {
                // Escaped quote
                field += '"';
                ++i;
            } else {
                in_quotes = !in_quotes;
            }
        } else if (c == delimiter_ && !in_quotes) {
            result.push_back(field);
            field.clear();
        } else {
            field += c;
        }
    }
    
    result.push_back(field);
    return result;
}

void CsvReader::count_lines() {
    if (!file_ || !file_->is_open()) return;
    
    total_lines_ = 0;
    std::string line;
    while (std::getline(*file_, line)) {
        total_lines_++;
    }
}

// DataSourceFactory implementation

std::unique_ptr<DataSourceReader> DataSourceFactory::create_reader(const DataSourceDef& source) {
    if (source.type == "csv") {
        return std::make_unique<CsvReader>(source.path, source.delimiter, source.has_headers);
    } else if (source.type == "tsv") {
        return std::make_unique<CsvReader>(source.path, '\t', source.has_headers);
    }
#ifdef ISTA_HAS_SQLITE
    else if (source.type == "sqlite") {
        return std::make_unique<SqliteReader>(source);
    }
#endif
#ifdef ISTA_HAS_MYSQL
    else if (source.type == "mysql") {
        return std::make_unique<MySqlReader>(source);
    }
#endif
#ifdef ISTA_HAS_POSTGRES
    else if (source.type == "postgres" || source.type == "postgresql") {
        return std::make_unique<PostgresReader>(source);
    }
#endif
    
    // Provide helpful error message about unsupported or not-compiled types
    std::string error_msg = "Unsupported data source type: " + source.type;
    
#ifndef ISTA_HAS_SQLITE
    if (source.type == "sqlite") {
        error_msg += " (SQLite support not compiled - rebuild with SQLite3 library)";
    }
#endif
#ifndef ISTA_HAS_MYSQL
    if (source.type == "mysql") {
        error_msg += " (MySQL support not compiled - rebuild with MySQL client library)";
    }
#endif
#ifndef ISTA_HAS_POSTGRES
    if (source.type == "postgres" || source.type == "postgresql") {
        error_msg += " (PostgreSQL support not compiled - rebuild with libpq)";
    }
#endif
    
    throw DataLoaderException(error_msg);
}

// DataLoader implementation

DataLoader::DataLoader(Ontology& ontology)
    : ontology_(ontology) {}

void DataLoader::set_mapping_spec(const DataMappingSpec& spec) {
    spec_ = spec;
    readers_.clear();  // Clear cached readers
}

void DataLoader::load_mapping_spec(const std::string& filepath) {
    spec_ = DataMappingSpec::load_from_file(filepath);
    spec_.resolve_environment_variables();
    readers_.clear();
}

void DataLoader::set_progress_callback(ProgressCallback callback) {
    progress_callback_ = callback;
}

LoadingStats DataLoader::execute() {
    LoadingStats total_stats;
    
    // Execute all node mappings first
    total_stats.merge(execute_all_node_mappings());
    
    // Then execute relationship mappings
    total_stats.merge(execute_all_relationship_mappings());
    
    return total_stats;
}

LoadingStats DataLoader::execute_node_mapping(const std::string& mapping_name) {
    auto all_mappings = spec_.get_all_node_mappings();
    
    for (const auto& mapping : all_mappings) {
        if (mapping.name == mapping_name) {
            return process_node_mapping(mapping);
        }
    }
    
    throw DataLoaderException("Node mapping not found: " + mapping_name);
}

LoadingStats DataLoader::execute_relationship_mapping(const std::string& mapping_name) {
    for (const auto& mapping : spec_.relationship_mappings) {
        if (mapping.name == mapping_name) {
            return process_relationship_mapping(mapping);
        }
    }
    
    throw DataLoaderException("Relationship mapping not found: " + mapping_name);
}

LoadingStats DataLoader::execute_all_node_mappings() {
    LoadingStats total_stats;
    auto all_mappings = spec_.get_all_node_mappings();
    
    for (const auto& mapping : all_mappings) {
        if (!mapping.skip) {
            total_stats.merge(process_node_mapping(mapping));
        }
    }
    
    return total_stats;
}

LoadingStats DataLoader::execute_all_relationship_mappings() {
    LoadingStats total_stats;
    
    for (const auto& mapping : spec_.relationship_mappings) {
        if (!mapping.skip) {
            total_stats.merge(process_relationship_mapping(mapping));
        }
    }
    
    return total_stats;
}

ValidationResult DataLoader::validate() {
    return spec_.validate(ontology_);
}

DataSourceReader* DataLoader::get_reader(const std::string& source_name) {
    // Check cache first
    auto it = readers_.find(source_name);
    if (it != readers_.end()) {
        it->second->reset();
        return it->second.get();
    }
    
    // Create new reader
    auto source_it = spec_.sources.find(source_name);
    if (source_it == spec_.sources.end()) {
        throw DataLoaderException("Data source not found: " + source_name);
    }
    
    auto reader = DataSourceFactory::create_reader(source_it->second);
    if (!reader->open()) {
        throw DataLoaderException("Failed to open data source: " + source_name);
    }
    
    DataSourceReader* ptr = reader.get();
    readers_[source_name] = std::move(reader);
    return ptr;
}

LoadingStats DataLoader::process_node_mapping(const NodeMapping& mapping) {
    LoadingStats stats;
    
    auto reader = get_reader(mapping.source);
    auto target_class_opt = find_class(mapping.target_class);
    
    if (!target_class_opt.has_value()) {
        stats.errors++;
        stats.error_messages.push_back("Class not found: " + mapping.target_class);
        return stats;
    }
    
    Class target_class = target_class_opt.value();
    
    size_t total = reader->row_count();
    size_t current = 0;
    
    while (reader->has_next()) {
        DataRow row = reader->next();
        stats.rows_processed++;
        current++;
        
        if (progress_callback_) {
            progress_callback_(current, total, mapping.name);
        }
        
        // Apply filter
        if (!passes_filter(row, mapping.filter)) {
            stats.rows_skipped++;
            continue;
        }
        
        NamedIndividual individual(IRI(""));  // Placeholder, will be assigned
        bool has_individual = false;
        
        if (mapping.mode == MappingMode::CREATE) {
            // CREATE mode: Create new individual
            if (!mapping.iri_column.has_value()) {
                stats.errors++;
                stats.error_messages.push_back("CREATE mode requires iri_column");
                continue;
            }
            
            auto col_it = row.find(mapping.iri_column.value());
            if (col_it == row.end() || col_it->second.empty()) {
                stats.rows_skipped++;
                continue;
            }
            
            IRI individual_iri = make_individual_iri(col_it->second, target_class);
            individual = ontology_.createIndividual(target_class, individual_iri);
            has_individual = true;
            stats.individuals_created++;
            
        } else {
            // ENRICH mode: Find existing individual
            if (!mapping.match.has_value()) {
                stats.errors++;
                stats.error_messages.push_back("ENRICH mode requires match criteria");
                continue;
            }
            
            const auto& match = mapping.match.value();
            auto col_it = row.find(match.source_column);
            if (col_it == row.end() || col_it->second.empty()) {
                stats.rows_skipped++;
                continue;
            }
            
            auto found_individual = find_individual_by_property(match.target_property, col_it->second);
            if (!found_individual.has_value()) {
                stats.rows_skipped++;
                continue;
            }
            individual = found_individual.value();
            has_individual = true;
            stats.individuals_enriched++;
        }
        
        if (!has_individual) {
            continue;
        }
        
        // Add properties
        for (const auto& prop_mapping : mapping.properties) {
            auto col_it = row.find(prop_mapping.column);
            if (col_it == row.end() || col_it->second.empty()) {
                continue;
            }
            
            std::string value = apply_transform(col_it->second, prop_mapping.transform);
            if (!value.empty()) {
                add_data_property(individual, prop_mapping.property, value, 
                                  prop_mapping.datatype, stats);
            }
        }
    }
    
    return stats;
}

LoadingStats DataLoader::process_relationship_mapping(const RelationshipMapping& mapping) {
    LoadingStats stats;
    
    auto reader = get_reader(mapping.source);
    auto relationship_opt = find_object_property(mapping.relationship);
    
    if (!relationship_opt.has_value()) {
        stats.errors++;
        stats.error_messages.push_back("Object property not found: " + mapping.relationship);
        return stats;
    }
    
    ObjectProperty relationship = relationship_opt.value();
    
    std::optional<ObjectProperty> inverse_relationship;
    if (mapping.inverse_relationship.has_value()) {
        inverse_relationship = find_object_property(mapping.inverse_relationship.value());
    }
    
    size_t total = reader->row_count();
    size_t current = 0;
    
    while (reader->has_next()) {
        DataRow row = reader->next();
        stats.rows_processed++;
        current++;
        
        if (progress_callback_) {
            progress_callback_(current, total, mapping.name);
        }
        
        // Apply filter
        if (!passes_filter(row, mapping.filter)) {
            stats.rows_skipped++;
            continue;
        }
        
        // Get subject value
        auto subj_col_it = row.find(mapping.subject.column);
        if (subj_col_it == row.end() || subj_col_it->second.empty()) {
            stats.rows_skipped++;
            continue;
        }
        std::string subj_value = apply_transform(subj_col_it->second, mapping.subject.transform);
        
        // Get object value
        auto obj_col_it = row.find(mapping.object.column);
        if (obj_col_it == row.end() || obj_col_it->second.empty()) {
            stats.rows_skipped++;
            continue;
        }
        std::string obj_value = apply_transform(obj_col_it->second, mapping.object.transform);
        
        // Find subject individual
        auto subject_opt = find_individual_by_property(mapping.subject.match_property, subj_value);
        if (!subject_opt.has_value()) {
            stats.rows_skipped++;
            continue;
        }
        
        // Find object individual
        auto object_opt = find_individual_by_property(mapping.object.match_property, obj_value);
        if (!object_opt.has_value()) {
            stats.rows_skipped++;
            continue;
        }
        
        // Add relationship
        ontology_.addObjectPropertyAssertion(subject_opt.value(), relationship, object_opt.value());
        stats.relationships_created++;
        
        // Add inverse if specified
        if (inverse_relationship.has_value()) {
            ontology_.addObjectPropertyAssertion(object_opt.value(), inverse_relationship.value(), subject_opt.value());
            stats.relationships_created++;
        }
    }
    
    return stats;
}

std::string DataLoader::apply_transform(const std::string& value, 
                                         const std::optional<std::string>& transform_name) {
    if (!transform_name.has_value()) {
        return value;
    }
    
    return transform_engine_.apply(transform_name.value(), value, spec_.transforms);
}

bool DataLoader::passes_filter(const DataRow& row, const std::optional<FilterDef>& filter) {
    if (!filter.has_value()) {
        return true;
    }
    
    const auto& f = filter.value();
    auto it = row.find(f.column);
    if (it == row.end()) {
        return false;
    }
    
    if (f.contains) {
        return it->second.find(f.value) != std::string::npos;
    } else {
        return it->second == f.value;
    }
}

std::optional<Class> DataLoader::find_class(const std::string& local_name) {
    for (const auto& cls : ontology_.getClasses()) {
        auto ln = cls.getIRI().getLocalName();
        if (ln.has_value() && ln.value() == local_name) {
            return cls;
        }
    }
    return std::nullopt;
}

std::optional<DataProperty> DataLoader::find_data_property(const std::string& local_name) {
    for (const auto& prop : ontology_.getDataProperties()) {
        auto ln = prop.getIRI().getLocalName();
        if (ln.has_value() && ln.value() == local_name) {
            return prop;
        }
    }
    return std::nullopt;
}

std::optional<ObjectProperty> DataLoader::find_object_property(const std::string& local_name) {
    for (const auto& prop : ontology_.getObjectProperties()) {
        auto ln = prop.getIRI().getLocalName();
        if (ln.has_value() && ln.value() == local_name) {
            return prop;
        }
    }
    return std::nullopt;
}

std::optional<NamedIndividual> DataLoader::find_individual_by_property(
    const std::string& property_name,
    const std::string& value) {
    
    auto prop_opt = find_data_property(property_name);
    if (!prop_opt.has_value()) {
        return std::nullopt;
    }
    
    Literal lit(value);
    auto matches = ontology_.searchByDataProperty(prop_opt.value(), lit);
    
    if (matches.empty()) {
        return std::nullopt;
    }
    
    return matches[0];
}

IRI DataLoader::make_individual_iri(const std::string& base_value, 
                                     const Class& cls) {
    std::string sanitized = sanitize_for_iri(base_value);
    
    // Use base_iri from spec or ontology
    std::string base_iri = spec_.base_iri;
    if (base_iri.empty()) {
        auto onto_iri = ontology_.getOntologyIRI();
        if (onto_iri.has_value()) {
            base_iri = onto_iri.value().getNamespace();
        } else {
            base_iri = "http://example.org/onto#";
        }
    }
    
    // Add class prefix for namespacing
    auto local_name_opt = cls.getIRI().getLocalName();
    std::string class_prefix = local_name_opt.has_value() ? local_name_opt.value() : "entity";
    std::transform(class_prefix.begin(), class_prefix.end(), class_prefix.begin(), ::tolower);
    
    return IRI(base_iri + class_prefix + "_" + sanitized);
}

std::string DataLoader::sanitize_for_iri(const std::string& value) {
    std::string result;
    result.reserve(value.size());
    
    for (char c : value) {
        if (std::isalnum(static_cast<unsigned char>(c))) {
            result += std::tolower(static_cast<unsigned char>(c));
        } else if (c == ' ' || c == '-' || c == '_') {
            result += '_';
        }
        // Skip other characters
    }
    
    // Remove consecutive underscores
    std::string cleaned;
    bool last_was_underscore = false;
    for (char c : result) {
        if (c == '_') {
            if (!last_was_underscore) {
                cleaned += c;
            }
            last_was_underscore = true;
        } else {
            cleaned += c;
            last_was_underscore = false;
        }
    }
    
    // Trim leading/trailing underscores
    size_t start = cleaned.find_first_not_of('_');
    size_t end = cleaned.find_last_not_of('_');
    if (start == std::string::npos) {
        return "unnamed";
    }
    
    return cleaned.substr(start, end - start + 1);
}

void DataLoader::add_data_property(const NamedIndividual& individual,
                                    const std::string& property_name,
                                    const std::string& value,
                                    const std::optional<std::string>& datatype,
                                    LoadingStats& stats) {
    auto prop_opt = find_data_property(property_name);
    if (!prop_opt.has_value()) {
        return;
    }
    
    Literal lit(value);
    
    // Set datatype if specified
    if (datatype.has_value()) {
        const std::string& dt = datatype.value();
        if (dt == "xsd:integer" || dt == "integer") {
            try {
                // Validate it's a valid integer, then create typed literal
                std::stoi(value);
                lit = Literal(value, xsd::INTEGER);
            } catch (...) {
                // Keep as string if conversion fails
            }
        } else if (dt == "xsd:double" || dt == "double") {
            try {
                std::stod(value);
                lit = Literal(value, xsd::DOUBLE);
            } catch (...) {
                // Keep as string if conversion fails
            }
        } else if (dt == "xsd:float" || dt == "float") {
            try {
                std::stof(value);
                lit = Literal(value, xsd::FLOAT);
            } catch (...) {
                // Keep as string if conversion fails
            }
        } else if (dt == "xsd:boolean" || dt == "boolean") {
            bool b = (value == "true" || value == "True" || value == "TRUE" || 
                      value == "yes" || value == "1");
            lit = Literal(b ? "true" : "false", xsd::BOOLEAN);
        }
        // Default: keep as string
    }
    
    ontology_.addDataPropertyAssertion(individual, prop_opt.value(), lit);
    stats.properties_added++;
}

} // namespace loader
} // namespace owl2
} // namespace ista
