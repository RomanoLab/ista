#include "mapping_spec.hpp"
#include "yaml_parser.hpp"
#include <fstream>
#include <sstream>
#include <algorithm>
#include <cstdlib>
#include <cstring>
#include <regex>
#include <set>

namespace ista {
namespace owl2 {
namespace loader {

namespace {

// Helper to convert string to MappingMode
MappingMode parse_mapping_mode(const std::string& mode_str) {
    if (mode_str == "create" || mode_str == "CREATE") {
        return MappingMode::CREATE;
    } else if (mode_str == "enrich" || mode_str == "ENRICH") {
        return MappingMode::ENRICH;
    }
    throw MappingSpecException("Invalid mapping mode: " + mode_str + ". Expected 'create' or 'enrich'");
}

// Parse a TransformDef from YAML node
TransformDef parse_transform_def(const YamlNodePtr& node) {
    TransformDef def;
    
    if (node->is_scalar()) {
        // Simple transform name reference
        def.type = node->as_string();
    } else if (node->is_map()) {
        def.type = node->get_string("type");
        
        if (node->has_key("params")) {
            auto params_node = node->get("params");
            if (params_node->is_map()) {
                for (const auto& [key, value] : params_node->as_map()) {
                    if (value->is_scalar()) {
                        def.params[key] = value->as_string();
                    }
                }
            }
        }
        
        // Allow inline parameters at same level as type
        for (const auto& [key, value] : node->as_map()) {
            if (key != "type" && key != "params" && value->is_scalar()) {
                def.params[key] = value->as_string();
            }
        }
    }
    
    return def;
}

// Parse FilterDef from YAML node
FilterDef parse_filter_def(const YamlNodePtr& node) {
    FilterDef filter;
    filter.column = node->get_string("column");
    filter.value = node->get_string("value");
    filter.contains = node->get_bool("contains", true);
    return filter;
}

// Parse MatchCriteria from YAML node
MatchCriteria parse_match_criteria(const YamlNodePtr& node) {
    MatchCriteria match;
    match.source_column = node->get_string("source_column");
    match.target_property = node->get_string("target_property");
    return match;
}

// Parse PropertyMapping from YAML node
PropertyMapping parse_property_mapping(const YamlNodePtr& node) {
    PropertyMapping prop;
    
    if (node->is_scalar()) {
        // Simple case: column name equals property name
        prop.column = node->as_string();
        prop.property = node->as_string();
    } else if (node->is_map()) {
        prop.column = node->get_string("column");
        prop.property = node->get_string("property", prop.column);
        
        if (node->has_key("transform")) {
            prop.transform = node->get_string("transform");
        }
        if (node->has_key("datatype")) {
            prop.datatype = node->get_string("datatype");
        }
    }
    
    return prop;
}

// Parse vector of PropertyMappings
std::vector<PropertyMapping> parse_property_mappings(const YamlNodePtr& node) {
    std::vector<PropertyMapping> props;
    if (node->is_list()) {
        for (const auto& item : node->as_list()) {
            props.push_back(parse_property_mapping(item));
        }
    }
    return props;
}

// Parse DatabaseConnectionDef from YAML node
DatabaseConnectionDef parse_database_connection(const YamlNodePtr& node) {
    DatabaseConnectionDef conn;
    conn.host = node->get_string("host", "localhost");
    conn.port = node->get_int("port", 0);
    conn.database = node->get_string("database");
    conn.username = node->get_string("username");
    conn.password = node->get_string("password");
    conn.connection_string = node->get_string("connection_string");
    conn.use_connection_string = !conn.connection_string.empty();
    return conn;
}

// Parse DataSourceDef from YAML node
DataSourceDef parse_data_source(const std::string& name, const YamlNodePtr& node) {
    DataSourceDef source;
    source.name = name;
    source.type = node->get_string("type", "csv");
    source.path = node->get_string("path");
    
    std::string delimiter = node->get_string("delimiter", ",");
    source.delimiter = delimiter.empty() ? ',' : delimiter[0];
    source.has_headers = node->get_bool("has_headers", true);
    
    if (node->has_key("connection")) {
        source.connection = parse_database_connection(node->get("connection"));
    }
    if (node->has_key("table")) {
        source.table = node->get_string("table");
    }
    if (node->has_key("query")) {
        source.query = node->get_string("query");
    }
    
    return source;
}

// Parse EntityRef from YAML node
EntityRef parse_entity_ref(const YamlNodePtr& node) {
    EntityRef ref;
    ref.class_name = node->get_string("class");
    ref.column = node->get_string("column");
    ref.match_property = node->get_string("match_property");
    if (node->has_key("transform")) {
        ref.transform = node->get_string("transform");
    }
    return ref;
}

// Parse NodeMapping from YAML node
NodeMapping parse_node_mapping(const YamlNodePtr& node) {
    NodeMapping mapping;
    mapping.name = node->get_string("name");
    mapping.source = node->get_string("source");
    mapping.target_class = node->get_string("target_class");
    mapping.skip = node->get_bool("skip", false);
    
    std::string mode_str = node->get_string("mode", "create");
    mapping.mode = parse_mapping_mode(mode_str);
    
    if (node->has_key("iri_column")) {
        mapping.iri_column = node->get_string("iri_column");
    }
    
    if (node->has_key("match")) {
        mapping.match = parse_match_criteria(node->get("match"));
    }
    
    if (node->has_key("filter")) {
        mapping.filter = parse_filter_def(node->get("filter"));
    }
    
    if (node->has_key("properties")) {
        mapping.properties = parse_property_mappings(node->get("properties"));
    }
    
    return mapping;
}

// Parse RelationshipMapping from YAML node
RelationshipMapping parse_relationship_mapping(const YamlNodePtr& node) {
    RelationshipMapping mapping;
    mapping.name = node->get_string("name");
    mapping.source = node->get_string("source");
    mapping.relationship = node->get_string("relationship");
    mapping.skip = node->get_bool("skip", false);
    
    if (node->has_key("subject")) {
        mapping.subject = parse_entity_ref(node->get("subject"));
    }
    if (node->has_key("object")) {
        mapping.object = parse_entity_ref(node->get("object"));
    }
    
    if (node->has_key("filter")) {
        mapping.filter = parse_filter_def(node->get("filter"));
    }
    
    if (node->has_key("inverse_relationship")) {
        mapping.inverse_relationship = node->get_string("inverse_relationship");
    }
    
    return mapping;
}

// Parse EnrichmentDef from YAML node
EnrichmentDef parse_enrichment_def(const YamlNodePtr& node) {
    EnrichmentDef enrich;
    enrich.name = node->get_string("name");
    enrich.source = node->get_string("source");
    
    if (node->has_key("table")) {
        enrich.table = node->get_string("table");
    }
    
    if (node->has_key("match")) {
        enrich.match = parse_match_criteria(node->get("match"));
    }
    
    if (node->has_key("properties")) {
        enrich.properties = parse_property_mappings(node->get("properties"));
    }
    
    return enrich;
}

// Parse EntityTypeDef from YAML node
EntityTypeDef parse_entity_type_def(const std::string& class_name, const YamlNodePtr& node) {
    EntityTypeDef entity;
    entity.class_name = class_name;
    
    if (node->has_key("primary")) {
        auto primary_node = node->get("primary");
        entity.primary.source = primary_node->get_string("source");
        entity.primary.iri_column = primary_node->get_string("iri_column");
        
        if (primary_node->has_key("table")) {
            entity.primary.table = primary_node->get_string("table");
        }
        if (primary_node->has_key("filter")) {
            entity.primary.filter = parse_filter_def(primary_node->get("filter"));
        }
        if (primary_node->has_key("properties")) {
            entity.primary.properties = parse_property_mappings(primary_node->get("properties"));
        }
    }
    
    if (node->has_key("enrichments")) {
        auto enrichments_node = node->get("enrichments");
        if (enrichments_node->is_list()) {
            for (const auto& item : enrichments_node->as_list()) {
                entity.enrichments.push_back(parse_enrichment_def(item));
            }
        }
    }
    
    return entity;
}

} // anonymous namespace

// DataMappingSpec implementation

DataMappingSpec DataMappingSpec::load_from_file(const std::string& filepath) {
    auto root = YamlParser::parse_file(filepath);
    if (root->is_null()) {
        throw MappingSpecException("Empty or invalid YAML file: " + filepath);
    }
    
    DataMappingSpec spec;
    
    // Parse version
    spec.version = root->get_string("version", "1.0");
    
    // Parse base_iri
    spec.base_iri = root->get_string("base_iri");
    
    // Parse transforms
    if (root->has_key("transforms")) {
        auto transforms_node = root->get("transforms");
        if (transforms_node->is_map()) {
            for (const auto& [name, def_node] : transforms_node->as_map()) {
                spec.transforms[name] = parse_transform_def(def_node);
            }
        }
    }
    
    // Parse sources
    if (root->has_key("sources")) {
        auto sources_node = root->get("sources");
        if (sources_node->is_map()) {
            for (const auto& [name, source_node] : sources_node->as_map()) {
                spec.sources[name] = parse_data_source(name, source_node);
            }
        }
    }
    
    // Parse entity_types
    if (root->has_key("entity_types")) {
        auto entity_types_node = root->get("entity_types");
        if (entity_types_node->is_map()) {
            for (const auto& [class_name, type_node] : entity_types_node->as_map()) {
                spec.entity_types[class_name] = parse_entity_type_def(class_name, type_node);
            }
        }
    }
    
    // Parse node_mappings
    if (root->has_key("node_mappings")) {
        auto mappings_node = root->get("node_mappings");
        if (mappings_node->is_list()) {
            for (const auto& mapping_node : mappings_node->as_list()) {
                spec.node_mappings.push_back(parse_node_mapping(mapping_node));
            }
        }
    }
    
    // Parse relationship_mappings
    if (root->has_key("relationship_mappings")) {
        auto rel_mappings_node = root->get("relationship_mappings");
        if (rel_mappings_node->is_list()) {
            for (const auto& rel_node : rel_mappings_node->as_list()) {
                spec.relationship_mappings.push_back(parse_relationship_mapping(rel_node));
            }
        }
    }
    
    return spec;
}

DataMappingSpec DataMappingSpec::parse(const std::string& yaml_content) {
    auto root = YamlParser::parse(yaml_content);
    if (root->is_null()) {
        throw MappingSpecException("Empty or invalid YAML content");
    }
    
    // Create a temporary file-like structure and reuse load logic
    // For simplicity, we'll duplicate the parsing logic here
    DataMappingSpec spec;
    
    spec.version = root->get_string("version", "1.0");
    spec.base_iri = root->get_string("base_iri");
    
    if (root->has_key("transforms")) {
        auto transforms_node = root->get("transforms");
        if (transforms_node->is_map()) {
            for (const auto& [name, def_node] : transforms_node->as_map()) {
                spec.transforms[name] = parse_transform_def(def_node);
            }
        }
    }
    
    if (root->has_key("sources")) {
        auto sources_node = root->get("sources");
        if (sources_node->is_map()) {
            for (const auto& [name, source_node] : sources_node->as_map()) {
                spec.sources[name] = parse_data_source(name, source_node);
            }
        }
    }
    
    if (root->has_key("entity_types")) {
        auto entity_types_node = root->get("entity_types");
        if (entity_types_node->is_map()) {
            for (const auto& [class_name, type_node] : entity_types_node->as_map()) {
                spec.entity_types[class_name] = parse_entity_type_def(class_name, type_node);
            }
        }
    }
    
    if (root->has_key("node_mappings")) {
        auto mappings_node = root->get("node_mappings");
        if (mappings_node->is_list()) {
            for (const auto& mapping_node : mappings_node->as_list()) {
                spec.node_mappings.push_back(parse_node_mapping(mapping_node));
            }
        }
    }
    
    if (root->has_key("relationship_mappings")) {
        auto rel_mappings_node = root->get("relationship_mappings");
        if (rel_mappings_node->is_list()) {
            for (const auto& rel_node : rel_mappings_node->as_list()) {
                spec.relationship_mappings.push_back(parse_relationship_mapping(rel_node));
            }
        }
    }
    
    return spec;
}

ValidationResult DataMappingSpec::validate(const Ontology& ontology) const {
    ValidationResult result;
    
    // Validate that all sources referenced in mappings exist
    auto check_source = [&](const std::string& source_name, const std::string& context) {
        if (sources.find(source_name) == sources.end()) {
            result.add_error(context + ": Unknown data source '" + source_name + "'");
        }
    };
    
    // Validate that all transforms referenced exist
    auto check_transform = [&](const std::optional<std::string>& transform_name, const std::string& context) {
        if (transform_name.has_value()) {
            const std::string& name = transform_name.value();
            // Check if it's a builtin or custom transform
            static const std::set<std::string> builtins = {
                "split", "prefix", "suffix", "strip_prefix", "strip_suffix",
                "lowercase", "uppercase", "trim", "to_int", "to_float",
                "replace", "regex_extract", "identity", "default_if_empty", "chain"
            };
            if (builtins.find(name) == builtins.end() && transforms.find(name) == transforms.end()) {
                result.add_warning(context + ": Unknown transform '" + name + "'");
            }
        }
    };
    
    // Validate node mappings
    for (size_t i = 0; i < node_mappings.size(); ++i) {
        const auto& mapping = node_mappings[i];
        std::string ctx = "node_mappings[" + std::to_string(i) + "] (" + mapping.name + ")";
        
        check_source(mapping.source, ctx);
        
        if (!has_class(ontology, mapping.target_class)) {
            result.add_error(ctx + ": Unknown class '" + mapping.target_class + "'");
        }
        
        if (mapping.mode == MappingMode::CREATE && !mapping.iri_column.has_value()) {
            result.add_warning(ctx + ": CREATE mode mapping without iri_column");
        }
        
        if (mapping.mode == MappingMode::ENRICH && !mapping.match.has_value()) {
            result.add_error(ctx + ": ENRICH mode mapping requires 'match' criteria");
        }
        
        for (size_t j = 0; j < mapping.properties.size(); ++j) {
            const auto& prop = mapping.properties[j];
            std::string prop_ctx = ctx + ".properties[" + std::to_string(j) + "]";
            
            if (!has_property(ontology, prop.property)) {
                result.add_warning(prop_ctx + ": Unknown property '" + prop.property + "'");
            }
            
            check_transform(prop.transform, prop_ctx);
        }
    }
    
    // Validate relationship mappings
    for (size_t i = 0; i < relationship_mappings.size(); ++i) {
        const auto& mapping = relationship_mappings[i];
        std::string ctx = "relationship_mappings[" + std::to_string(i) + "] (" + mapping.name + ")";
        
        check_source(mapping.source, ctx);
        
        if (!has_property(ontology, mapping.relationship)) {
            result.add_warning(ctx + ": Unknown object property '" + mapping.relationship + "'");
        }
        
        if (!has_class(ontology, mapping.subject.class_name)) {
            result.add_error(ctx + ".subject: Unknown class '" + mapping.subject.class_name + "'");
        }
        
        if (!has_class(ontology, mapping.object.class_name)) {
            result.add_error(ctx + ".object: Unknown class '" + mapping.object.class_name + "'");
        }
        
        check_transform(mapping.subject.transform, ctx + ".subject");
        check_transform(mapping.object.transform, ctx + ".object");
    }
    
    // Validate entity_types
    for (const auto& [class_name, entity] : entity_types) {
        std::string ctx = "entity_types[" + class_name + "]";
        
        if (!has_class(ontology, class_name)) {
            result.add_error(ctx + ": Unknown class '" + class_name + "'");
        }
        
        check_source(entity.primary.source, ctx + ".primary");
        
        for (const auto& prop : entity.primary.properties) {
            if (!has_property(ontology, prop.property)) {
                result.add_warning(ctx + ".primary: Unknown property '" + prop.property + "'");
            }
        }
        
        for (size_t i = 0; i < entity.enrichments.size(); ++i) {
            const auto& enrich = entity.enrichments[i];
            std::string enrich_ctx = ctx + ".enrichments[" + std::to_string(i) + "]";
            
            check_source(enrich.source, enrich_ctx);
            
            if (!has_property(ontology, enrich.match.target_property)) {
                result.add_warning(enrich_ctx + ": Unknown match property '" + enrich.match.target_property + "'");
            }
            
            for (const auto& prop : enrich.properties) {
                if (!has_property(ontology, prop.property)) {
                    result.add_warning(enrich_ctx + ": Unknown property '" + prop.property + "'");
                }
            }
        }
    }
    
    return result;
}

std::string DataMappingSpec::to_yaml() const {
    std::ostringstream out;
    
    out << "version: \"" << version << "\"\n";
    if (!base_iri.empty()) {
        out << "base_iri: \"" << base_iri << "\"\n";
    }
    out << "\n";
    
    // Serialize transforms
    if (!transforms.empty()) {
        out << "transforms:\n";
        for (const auto& [name, def] : transforms) {
            out << "  " << name << ":\n";
            out << "    type: " << def.type << "\n";
            if (!def.params.empty()) {
                out << "    params:\n";
                for (const auto& [key, value] : def.params) {
                    out << "      " << key << ": \"" << value << "\"\n";
                }
            }
        }
        out << "\n";
    }
    
    // Serialize sources
    if (!sources.empty()) {
        out << "sources:\n";
        for (const auto& [name, source] : sources) {
            out << "  " << name << ":\n";
            out << "    type: " << source.type << "\n";
            if (!source.path.empty()) {
                out << "    path: \"" << source.path << "\"\n";
            }
            if (source.delimiter != ',') {
                out << "    delimiter: \"" << source.delimiter << "\"\n";
            }
            if (!source.has_headers) {
                out << "    has_headers: false\n";
            }
            if (source.table.has_value()) {
                out << "    table: " << source.table.value() << "\n";
            }
            if (source.query.has_value()) {
                out << "    query: \"" << source.query.value() << "\"\n";
            }
        }
        out << "\n";
    }
    
    // Serialize node_mappings
    if (!node_mappings.empty()) {
        out << "node_mappings:\n";
        for (const auto& mapping : node_mappings) {
            out << "  - name: \"" << mapping.name << "\"\n";
            out << "    source: " << mapping.source << "\n";
            out << "    target_class: " << mapping.target_class << "\n";
            out << "    mode: " << (mapping.mode == MappingMode::CREATE ? "create" : "enrich") << "\n";
            
            if (mapping.iri_column.has_value()) {
                out << "    iri_column: " << mapping.iri_column.value() << "\n";
            }
            if (mapping.match.has_value()) {
                out << "    match:\n";
                out << "      source_column: " << mapping.match->source_column << "\n";
                out << "      target_property: " << mapping.match->target_property << "\n";
            }
            if (mapping.skip) {
                out << "    skip: true\n";
            }
            
            if (!mapping.properties.empty()) {
                out << "    properties:\n";
                for (const auto& prop : mapping.properties) {
                    out << "      - column: " << prop.column << "\n";
                    out << "        property: " << prop.property << "\n";
                    if (prop.transform.has_value()) {
                        out << "        transform: " << prop.transform.value() << "\n";
                    }
                    if (prop.datatype.has_value()) {
                        out << "        datatype: " << prop.datatype.value() << "\n";
                    }
                }
            }
        }
        out << "\n";
    }
    
    // Serialize relationship_mappings
    if (!relationship_mappings.empty()) {
        out << "relationship_mappings:\n";
        for (const auto& mapping : relationship_mappings) {
            out << "  - name: \"" << mapping.name << "\"\n";
            out << "    source: " << mapping.source << "\n";
            out << "    relationship: " << mapping.relationship << "\n";
            out << "    subject:\n";
            out << "      class: " << mapping.subject.class_name << "\n";
            out << "      column: " << mapping.subject.column << "\n";
            out << "      match_property: " << mapping.subject.match_property << "\n";
            out << "    object:\n";
            out << "      class: " << mapping.object.class_name << "\n";
            out << "      column: " << mapping.object.column << "\n";
            out << "      match_property: " << mapping.object.match_property << "\n";
            if (mapping.inverse_relationship.has_value()) {
                out << "    inverse_relationship: " << mapping.inverse_relationship.value() << "\n";
            }
        }
    }
    
    return out.str();
}

void DataMappingSpec::save_to_file(const std::string& filepath) const {
    std::ofstream file(filepath);
    if (!file.is_open()) {
        throw MappingSpecException("Could not open file for writing: " + filepath);
    }
    file << to_yaml();
}

void DataMappingSpec::expand_entity_types() {
    for (const auto& [class_name, entity] : entity_types) {
        // Create primary node mapping
        NodeMapping primary_mapping;
        primary_mapping.name = class_name + " (primary)";
        primary_mapping.source = entity.primary.source;
        primary_mapping.target_class = class_name;
        primary_mapping.mode = MappingMode::CREATE;
        primary_mapping.iri_column = entity.primary.iri_column;
        primary_mapping.filter = entity.primary.filter;
        primary_mapping.properties = entity.primary.properties;
        node_mappings.push_back(primary_mapping);
        
        // Create enrichment node mappings
        for (const auto& enrich : entity.enrichments) {
            NodeMapping enrich_mapping;
            enrich_mapping.name = class_name + " (" + enrich.name + ")";
            enrich_mapping.source = enrich.source;
            enrich_mapping.target_class = class_name;
            enrich_mapping.mode = MappingMode::ENRICH;
            enrich_mapping.match = enrich.match;
            enrich_mapping.properties = enrich.properties;
            node_mappings.push_back(enrich_mapping);
        }
    }
}

std::vector<NodeMapping> DataMappingSpec::get_all_node_mappings() const {
    std::vector<NodeMapping> all_mappings = node_mappings;
    
    // Add expanded entity_types
    for (const auto& [class_name, entity] : entity_types) {
        NodeMapping primary_mapping;
        primary_mapping.name = class_name + " (primary)";
        primary_mapping.source = entity.primary.source;
        primary_mapping.target_class = class_name;
        primary_mapping.mode = MappingMode::CREATE;
        primary_mapping.iri_column = entity.primary.iri_column;
        primary_mapping.filter = entity.primary.filter;
        primary_mapping.properties = entity.primary.properties;
        all_mappings.push_back(primary_mapping);
        
        for (const auto& enrich : entity.enrichments) {
            NodeMapping enrich_mapping;
            enrich_mapping.name = class_name + " (" + enrich.name + ")";
            enrich_mapping.source = enrich.source;
            enrich_mapping.target_class = class_name;
            enrich_mapping.mode = MappingMode::ENRICH;
            enrich_mapping.match = enrich.match;
            enrich_mapping.properties = enrich.properties;
            all_mappings.push_back(enrich_mapping);
        }
    }
    
    return all_mappings;
}

void DataMappingSpec::resolve_environment_variables() {
    // Regex to match ${VAR_NAME} pattern
    std::regex env_pattern(R"(\$\{([^}]+)\})");
    
    auto resolve = [&](std::string& str) {
        std::smatch match;
        std::string result = str;
        size_t offset = 0;
        
        while (std::regex_search(result.cbegin() + offset, result.cend(), match, env_pattern)) {
            std::string var_name = match[1].str();
            const char* env_value = std::getenv(var_name.c_str());
            
            if (env_value) {
                size_t match_start = offset + match.position(0);
                result = result.substr(0, match_start) + env_value + 
                         result.substr(match_start + match[0].length());
                offset = match_start + std::strlen(env_value);
            } else {
                offset += match.position(0) + match[0].length();
            }
        }
        
        str = result;
    };
    
    // Resolve in base_iri
    resolve(base_iri);
    
    // Resolve in sources
    for (auto& [name, source] : sources) {
        resolve(source.path);
        if (source.connection.has_value()) {
            resolve(source.connection->host);
            resolve(source.connection->database);
            resolve(source.connection->username);
            resolve(source.connection->password);
            resolve(source.connection->connection_string);
        }
    }
}

bool DataMappingSpec::has_class(const Ontology& ontology, const std::string& local_name) {
    // Search through declared classes
    for (const auto& axiom : ontology.getAxioms()) {
        if (auto decl = std::dynamic_pointer_cast<Declaration>(axiom)) {
            if (decl->getEntityType() == Declaration::EntityType::CLASS) {
                if (decl->getIRI().getLocalName() == local_name) {
                    return true;
                }
            }
        }
    }
    return false;
}

bool DataMappingSpec::has_property(const Ontology& ontology, const std::string& local_name) {
    // Search through declared properties (data and object)
    for (const auto& axiom : ontology.getAxioms()) {
        if (auto decl = std::dynamic_pointer_cast<Declaration>(axiom)) {
            if (decl->getEntityType() == Declaration::EntityType::DATA_PROPERTY ||
                decl->getEntityType() == Declaration::EntityType::OBJECT_PROPERTY) {
                if (decl->getIRI().getLocalName() == local_name) {
                    return true;
                }
            }
        }
    }
    return false;
}

} // namespace loader
} // namespace owl2
} // namespace ista
