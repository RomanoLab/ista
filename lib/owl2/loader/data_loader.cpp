#include "data_loader.hpp"
#include <fstream>
#include <sstream>
#include <algorithm>
#include <cctype>
#include <regex>
#include <unordered_set>
#include <filesystem>

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

namespace {

/// Split a string by a multi-character delimiter, trimming whitespace from each token.
std::vector<std::string> split_multi_value(const std::string& value, const std::string& delimiter) {
    std::vector<std::string> result;
    size_t start = 0;
    size_t pos;
    while ((pos = value.find(delimiter, start)) != std::string::npos) {
        std::string token = value.substr(start, pos - start);
        size_t begin = token.find_first_not_of(" \t");
        size_t end = token.find_last_not_of(" \t");
        if (begin != std::string::npos) {
            result.push_back(token.substr(begin, end - begin + 1));
        }
        start = pos + delimiter.length();
    }
    std::string last = value.substr(start);
    size_t begin = last.find_first_not_of(" \t");
    size_t end = last.find_last_not_of(" \t");
    if (begin != std::string::npos) {
        result.push_back(last.substr(begin, end - begin + 1));
    }
    return result;
}

} // anonymous namespace

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
    spec_.resolve_source_paths();
    readers_.clear();
}

void DataLoader::set_progress_callback(ProgressCallback callback) {
    progress_callback_ = callback;
}

void DataLoader::set_progress_interval(size_t interval) {
    progress_interval_ = interval;
}

void DataLoader::emit_progress(const ProgressEvent& event) {
    if (!progress_callback_) return;
    // Always emit structural events (mapping start/finish, cache building)
    if (event.mapping_started || event.mapping_finished ||
        event.phase == LoadingPhase::BUILD_CACHE) {
        progress_callback_(event);
        return;
    }
    // Throttle row-level events
    if (progress_interval_ == 0 ||
        event.current_row % progress_interval_ == 0 ||
        (event.total_rows > 0 && event.current_row == event.total_rows)) {
        progress_callback_(event);
    }
}

void DataLoader::auto_declare_schema() {
    std::string base = spec_.base_iri;
    if (base.empty()) {
        auto onto_iri = ontology_.getOntologyIRI();
        if (onto_iri.has_value()) {
            base = onto_iri.value().getNamespace();
        } else {
            base = "http://example.org/onto#";
        }
    }
    // Ensure base ends with # or /
    if (!base.empty() && base.back() != '#' && base.back() != '/') {
        base += '#';
    }

    std::unordered_set<std::string> class_names;
    std::unordered_set<std::string> data_property_names;
    std::unordered_set<std::string> object_property_names;

    // Collect from entity_types
    for (const auto& [name, entity] : spec_.entity_types) {
        class_names.insert(name);
        for (const auto& prop : entity.primary.properties) {
            data_property_names.insert(prop.property);
        }
        for (const auto& enrich : entity.enrichments) {
            for (const auto& prop : enrich.properties) {
                data_property_names.insert(prop.property);
            }
        }
    }

    // Collect from node_mappings
    for (const auto& mapping : spec_.node_mappings) {
        class_names.insert(mapping.target_class);
        for (const auto& prop : mapping.properties) {
            data_property_names.insert(prop.property);
        }
        for (const auto& cls_name : mapping.additional_classes) {
            class_names.insert(cls_name);
        }
    }

    // Collect from relationship_mappings
    for (const auto& mapping : spec_.relationship_mappings) {
        object_property_names.insert(mapping.relationship);
        if (mapping.inverse_relationship.has_value()) {
            object_property_names.insert(mapping.inverse_relationship.value());
        }
        class_names.insert(mapping.subject.class_name);
        class_names.insert(mapping.object.class_name);
    }

    // Declare classes (skip if already declared)
    for (const auto& name : class_names) {
        if (!find_class(name).has_value()) {
            IRI cls_iri(base + name);
            auto decl = std::make_shared<Declaration>(
                Declaration::EntityType::CLASS, cls_iri);
            ontology_.addAxiom(decl);
        }
    }

    // Declare data properties (skip if already declared)
    for (const auto& name : data_property_names) {
        if (!find_data_property(name).has_value()) {
            IRI prop_iri(base + name);
            auto decl = std::make_shared<Declaration>(
                Declaration::EntityType::DATA_PROPERTY, prop_iri);
            ontology_.addAxiom(decl);
        }
    }

    // Declare object properties (skip if already declared)
    for (const auto& name : object_property_names) {
        if (!find_object_property(name).has_value()) {
            IRI prop_iri(base + name);
            auto decl = std::make_shared<Declaration>(
                Declaration::EntityType::OBJECT_PROPERTY, prop_iri);
            ontology_.addAxiom(decl);
        }
    }

    // Generate domain/range axioms for object properties from relationship mappings
    // Track already-declared domain/range to avoid duplicates on repeated calls
    std::unordered_set<std::string> existing_domains;
    std::unordered_set<std::string> existing_ranges;
    for (const auto& axiom : ontology_.getAxioms()) {
        if (auto* domain = dynamic_cast<ObjectPropertyDomain*>(axiom.get())) {
            auto expr = domain->getProperty();
            if (auto* prop = std::get_if<ObjectProperty>(&expr)) {
                existing_domains.insert(prop->getIRI().getFullIRI());
            }
        } else if (auto* range = dynamic_cast<ObjectPropertyRange*>(axiom.get())) {
            auto expr = range->getProperty();
            if (auto* prop = std::get_if<ObjectProperty>(&expr)) {
                existing_ranges.insert(prop->getIRI().getFullIRI());
            }
        }
    }

    for (const auto& mapping : spec_.relationship_mappings) {
        auto obj_prop_opt = find_object_property(mapping.relationship);
        if (obj_prop_opt.has_value()) {
            auto prop_iri = obj_prop_opt.value().getIRI().getFullIRI();
            auto domain_class_opt = find_class(mapping.subject.class_name);
            auto range_class_opt = find_class(mapping.object.class_name);

            if (domain_class_opt.has_value() && existing_domains.find(prop_iri) == existing_domains.end()) {
                auto domain_expr = std::make_shared<NamedClass>(domain_class_opt.value());
                auto domain_axiom = std::make_shared<ObjectPropertyDomain>(
                    ObjectPropertyExpression(obj_prop_opt.value()), domain_expr);
                ontology_.addAxiom(domain_axiom);
                existing_domains.insert(prop_iri);
            }

            if (range_class_opt.has_value() && existing_ranges.find(prop_iri) == existing_ranges.end()) {
                auto range_expr = std::make_shared<NamedClass>(range_class_opt.value());
                auto range_axiom = std::make_shared<ObjectPropertyRange>(
                    ObjectPropertyExpression(obj_prop_opt.value()), range_expr);
                ontology_.addAxiom(range_axiom);
                existing_ranges.insert(prop_iri);
            }
        }
    }
}

LoadingStats DataLoader::execute() {
    // Auto-declare schema from mapping spec
    auto_declare_schema();

    // Use batch mode to defer index invalidation during population
    ontology_.beginBatchMode();

    LoadingStats total_stats;

    // Pre-collect active mappings per phase for accurate totals
    auto all_node_mappings = spec_.get_all_node_mappings();

    std::vector<const NodeMapping*> create_mappings, enrich_mappings;
    for (const auto& m : all_node_mappings) {
        if (m.skip) continue;
        if (m.mode == MappingMode::CREATE) create_mappings.push_back(&m);
        else if (m.mode == MappingMode::ENRICH) enrich_mappings.push_back(&m);
    }
    std::vector<const RelationshipMapping*> rel_mappings;
    for (const auto& m : spec_.relationship_mappings) {
        if (!m.skip) rel_mappings.push_back(&m);
    }

    // Helper to emit mapping start/finish events
    auto run_node_phase = [&](LoadingPhase phase, const std::string& kind,
                              const std::vector<const NodeMapping*>& mappings) {
        current_phase_ = phase;
        current_mapping_total_ = mappings.size();
        current_mapping_index_ = 0;

        for (const auto* mp : mappings) {
            const auto& mapping = *mp;
            MappingResult mr;
            mr.name = mapping.name;
            mr.source = mapping.source;
            mr.kind = kind;

            // Emit mapping_started
            ProgressEvent start_evt;
            start_evt.phase = phase;
            start_evt.mapping_name = mapping.name;
            start_evt.mapping_index = current_mapping_index_;
            start_evt.mapping_total = current_mapping_total_;
            start_evt.mapping_started = true;
            emit_progress(start_evt);

            try {
                auto ms = process_node_mapping(mapping);
                mr.rows_processed = ms.rows_processed;
                mr.items_created = (phase == LoadingPhase::CREATE)
                    ? ms.individuals_created : ms.individuals_enriched;
                mr.rows_skipped = ms.rows_skipped;
                mr.errors = ms.errors;
                total_stats.merge(ms);
            } catch (const std::exception& e) {
                total_stats.errors++;
                total_stats.error_messages.push_back(
                    "Mapping '" + mapping.name + "' failed: " + e.what());
                mr.errors = 1;
                mr.error_detail = e.what();
            }
            total_stats.mapping_results.push_back(mr);

            // Emit mapping_finished
            ProgressEvent end_evt;
            end_evt.phase = phase;
            end_evt.mapping_name = mapping.name;
            end_evt.mapping_index = current_mapping_index_;
            end_evt.mapping_total = current_mapping_total_;
            end_evt.current_row = mr.rows_processed;
            end_evt.total_rows = mr.rows_processed;
            end_evt.mapping_finished = true;
            emit_progress(end_evt);

            current_mapping_index_++;
        }
    };

    // Phase 1: CREATE
    run_node_phase(LoadingPhase::CREATE, "create", create_mappings);

    // Build individual cache
    {
        ProgressEvent cache_evt;
        cache_evt.phase = LoadingPhase::BUILD_CACHE;
        emit_progress(cache_evt);
    }
    build_individual_cache();

    // Phase 2: ENRICH
    run_node_phase(LoadingPhase::ENRICH, "enrich", enrich_mappings);

    // Phase 3: RELATIONSHIP
    current_phase_ = LoadingPhase::RELATIONSHIP;
    current_mapping_total_ = rel_mappings.size();
    current_mapping_index_ = 0;

    for (const auto* mp : rel_mappings) {
        const auto& mapping = *mp;
        MappingResult mr;
        mr.name = mapping.name;
        mr.source = mapping.source;
        mr.kind = "relationship";

        ProgressEvent start_evt;
        start_evt.phase = LoadingPhase::RELATIONSHIP;
        start_evt.mapping_name = mapping.name;
        start_evt.mapping_index = current_mapping_index_;
        start_evt.mapping_total = current_mapping_total_;
        start_evt.mapping_started = true;
        emit_progress(start_evt);

        try {
            auto ms = process_relationship_mapping(mapping);
            mr.rows_processed = ms.rows_processed;
            mr.items_created = ms.relationships_created;
            mr.rows_skipped = ms.rows_skipped;
            mr.errors = ms.errors;
            total_stats.merge(ms);
        } catch (const std::exception& e) {
            total_stats.errors++;
            total_stats.error_messages.push_back(
                "Relationship mapping '" + mapping.name + "' failed: " + e.what());
            mr.errors = 1;
            mr.error_detail = e.what();
        }
        total_stats.mapping_results.push_back(mr);

        ProgressEvent end_evt;
        end_evt.phase = LoadingPhase::RELATIONSHIP;
        end_evt.mapping_name = mapping.name;
        end_evt.mapping_index = current_mapping_index_;
        end_evt.mapping_total = current_mapping_total_;
        end_evt.current_row = mr.rows_processed;
        end_evt.total_rows = mr.rows_processed;
        end_evt.mapping_finished = true;
        emit_progress(end_evt);

        current_mapping_index_++;
    }

    // Exit batch mode — rebuilds indices once
    ontology_.endBatchMode();

    // Clear caches (they're only valid during a single execute() call)
    clear_caches();

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

DataSourceReader* DataLoader::get_reader(const std::string& source_name,
                                          const std::optional<std::string>& table_override,
                                          const std::optional<std::string>& query_override) {
    // Build a cache key that includes table/query overrides
    std::string cache_key = source_name;
    if (table_override.has_value()) {
        cache_key += "::table=" + table_override.value();
    }
    if (query_override.has_value()) {
        cache_key += "::query=" + query_override.value();
    }

    // Check cache first
    auto it = readers_.find(cache_key);
    if (it != readers_.end()) {
        it->second->reset();
        return it->second.get();
    }

    // Create new reader
    auto source_it = spec_.sources.find(source_name);
    if (source_it == spec_.sources.end()) {
        throw DataLoaderException("Data source not found: " + source_name);
    }

    // Apply table/query overrides
    DataSourceDef effective_source = source_it->second;
    if (table_override.has_value()) {
        effective_source.table = table_override.value();
    }
    if (query_override.has_value()) {
        effective_source.query = query_override.value();
    }

    auto reader = DataSourceFactory::create_reader(effective_source);
    if (!reader->open()) {
        std::string detail = "Failed to open data source '" + source_name + "'";
        if (!effective_source.path.empty()) {
            detail += ": file not found at " + effective_source.path;
        }
        throw DataLoaderException(detail);
    }

    DataSourceReader* ptr = reader.get();
    readers_[cache_key] = std::move(reader);
    return ptr;
}

LoadingStats DataLoader::process_node_mapping(const NodeMapping& mapping) {
    LoadingStats stats;

    auto reader = get_reader(mapping.source, mapping.table, mapping.query);
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

        {
            ProgressEvent evt;
            evt.phase = current_phase_;
            evt.mapping_name = mapping.name;
            evt.mapping_index = current_mapping_index_;
            evt.mapping_total = current_mapping_total_;
            evt.current_row = current;
            evt.total_rows = total;
            emit_progress(evt);
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

        // Add additional class assertions (for ENRICH mode append_class pattern)
        for (const auto& cls_name : mapping.additional_classes) {
            auto cls_opt = find_class(cls_name);
            if (cls_opt.has_value()) {
                ontology_.addClassAssertion(individual, cls_opt.value());
            }
        }
    }

    return stats;
}

LoadingStats DataLoader::process_relationship_mapping(const RelationshipMapping& mapping) {
    LoadingStats stats;

    auto reader = get_reader(mapping.source, mapping.table, mapping.query);
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

        {
            ProgressEvent evt;
            evt.phase = current_phase_;
            evt.mapping_name = mapping.name;
            evt.mapping_index = current_mapping_index_;
            evt.mapping_total = current_mapping_total_;
            evt.current_row = current;
            evt.total_rows = total;
            emit_progress(evt);
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
        std::string subj_raw = apply_transform(subj_col_it->second, mapping.subject.transform);

        // Get object value
        auto obj_col_it = row.find(mapping.object.column);
        if (obj_col_it == row.end() || obj_col_it->second.empty()) {
            stats.rows_skipped++;
            continue;
        }
        std::string obj_raw = apply_transform(obj_col_it->second, mapping.object.transform);

        // Expand multi-value fields if delimiter is specified
        std::vector<std::string> subj_values;
        if (mapping.subject.multi_value_delimiter.has_value()) {
            subj_values = split_multi_value(subj_raw, mapping.subject.multi_value_delimiter.value());
        } else {
            subj_values = {subj_raw};
        }

        std::vector<std::string> obj_values;
        if (mapping.object.multi_value_delimiter.has_value()) {
            obj_values = split_multi_value(obj_raw, mapping.object.multi_value_delimiter.value());
        } else {
            obj_values = {obj_raw};
        }

        // Create relationships for each (subject, object) pair
        bool any_matched = false;
        for (const auto& subj_value : subj_values) {
            if (subj_value.empty()) continue;

            auto subject_opt = find_individual_by_property(mapping.subject.match_property, subj_value);
            if (!subject_opt.has_value()) continue;

            for (const auto& obj_value : obj_values) {
                if (obj_value.empty()) continue;

                auto object_opt = find_individual_by_property(mapping.object.match_property, obj_value);
                if (!object_opt.has_value()) continue;

                ontology_.addObjectPropertyAssertion(subject_opt.value(), relationship, object_opt.value());
                stats.relationships_created++;
                any_matched = true;

                if (inverse_relationship.has_value()) {
                    ontology_.addObjectPropertyAssertion(object_opt.value(), inverse_relationship.value(), subject_opt.value());
                    stats.relationships_created++;
                }
            }
        }

        if (!any_matched) {
            stats.rows_skipped++;
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

void DataLoader::build_individual_cache() {
    individual_cache_.clear();

    // Scan all axioms once to build the cache
    for (const auto& axiom : ontology_.getAxioms()) {
        auto data_prop = std::dynamic_pointer_cast<DataPropertyAssertion>(axiom);
        if (!data_prop) continue;

        // Get property local name
        auto prop_ln = data_prop->getProperty().getIRI().getLocalName();
        if (!prop_ln.has_value()) continue;

        // Get the individual
        Individual source = data_prop->getSource();
        if (!std::holds_alternative<NamedIndividual>(source)) continue;

        // Build cache key: "propertyLocalName\0value"
        std::string key = prop_ln.value();
        key += '\0';
        key += data_prop->getTarget().getLexicalForm();

        // Only store the first match (consistent with previous behavior)
        if (individual_cache_.find(key) == individual_cache_.end()) {
            individual_cache_.emplace(key, std::get<NamedIndividual>(source));
        }
    }

    caches_built_ = true;
}

void DataLoader::clear_caches() {
    class_cache_.clear();
    data_property_cache_.clear();
    object_property_cache_.clear();
    individual_cache_.clear();
    caches_built_ = false;
}

std::optional<Class> DataLoader::find_class(const std::string& local_name) {
    // Check cache first
    auto it = class_cache_.find(local_name);
    if (it != class_cache_.end()) {
        return it->second;
    }

    for (const auto& cls : ontology_.getClasses()) {
        auto ln = cls.getIRI().getLocalName();
        if (ln.has_value() && ln.value() == local_name) {
            class_cache_.emplace(local_name, cls);
            return cls;
        }
    }
    return std::nullopt;
}

std::optional<DataProperty> DataLoader::find_data_property(const std::string& local_name) {
    // Check cache first
    auto it = data_property_cache_.find(local_name);
    if (it != data_property_cache_.end()) {
        return it->second;
    }

    for (const auto& prop : ontology_.getDataProperties()) {
        auto ln = prop.getIRI().getLocalName();
        if (ln.has_value() && ln.value() == local_name) {
            data_property_cache_.emplace(local_name, prop);
            return prop;
        }
    }
    return std::nullopt;
}

std::optional<ObjectProperty> DataLoader::find_object_property(const std::string& local_name) {
    // Check cache first
    auto it = object_property_cache_.find(local_name);
    if (it != object_property_cache_.end()) {
        return it->second;
    }

    for (const auto& prop : ontology_.getObjectProperties()) {
        auto ln = prop.getIRI().getLocalName();
        if (ln.has_value() && ln.value() == local_name) {
            object_property_cache_.emplace(local_name, prop);
            return prop;
        }
    }
    return std::nullopt;
}

std::optional<NamedIndividual> DataLoader::find_individual_by_property(
    const std::string& property_name,
    const std::string& value) {

    // Use individual cache if built (O(1) lookup)
    if (caches_built_) {
        std::string key = property_name;
        key += '\0';
        key += value;
        auto it = individual_cache_.find(key);
        if (it != individual_cache_.end()) {
            return it->second;
        }
        return std::nullopt;
    }

    // Fallback to ontology scan
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
