#include "csv_parser.hpp"
#include <algorithm>
#include <cctype>
#include <iostream>

namespace ista {
namespace owl2 {

CSVParser::CSVParser(Ontology& ontology, const std::string& base_iri)
    : ontology_(ontology), base_iri_(base_iri) {
    
    // Default IRI generator: base_iri + "#" + value
    iri_generator_ = [](const std::string& base, const std::string& value, const std::string& class_name) {
        // Clean the value (remove whitespace, special chars)
        std::string clean_value = value;
        clean_value.erase(std::remove_if(clean_value.begin(), clean_value.end(),
            [](unsigned char c) { return std::isspace(c); }), clean_value.end());
        
        return base + "#" + clean_value;
    };
}

void CSVParser::set_iri_generator(std::function<std::string(const std::string&, const std::string&, const std::string&)> generator) {
    iri_generator_ = generator;
}

std::vector<std::string> CSVParser::parse_csv_line(const std::string& line, char delimiter) {
    std::vector<std::string> result;
    std::string current_field;
    bool in_quotes = false;
    
    for (size_t i = 0; i < line.length(); ++i) {
        char c = line[i];
        
        if (c == '"') {
            // Handle quoted fields
            if (in_quotes && i + 1 < line.length() && line[i + 1] == '"') {
                // Escaped quote
                current_field += '"';
                ++i;
            } else {
                // Toggle quote mode
                in_quotes = !in_quotes;
            }
        } else if (c == delimiter && !in_quotes) {
            // End of field
            result.push_back(current_field);
            current_field.clear();
        } else {
            current_field += c;
        }
    }
    
    // Add the last field
    result.push_back(current_field);
    
    return result;
}

IRI CSVParser::create_individual_iri(const std::string& value, const std::string& class_name) {
    std::string iri_string = iri_generator_(base_iri_, value, class_name);
    return IRI(iri_string);
}

std::shared_ptr<NamedIndividual> CSVParser::find_individual_by_property(
    const IRI& property_iri,
    const std::string& value) {
    
    // Create cache key
    std::string cache_key = property_iri.toString() + ":" + value;
    
    // Check cache first
    auto cache_it = individual_cache_.find(cache_key);
    if (cache_it != individual_cache_.end()) {
        return cache_it->second;
    }
    
    // Search through all data property assertions
    for (const auto& axiom : ontology_.getAxioms()) {
        if (auto dpa = std::dynamic_pointer_cast<DataPropertyAssertion>(axiom)) {
            // Check if property matches
            if (dpa->getProperty().getIRI() == property_iri &&
                dpa->getTarget().getLexicalForm() == value) {
                // Get the individual from the source
                Individual source = dpa->getSource();
                // The Individual is a variant, we need to extract NamedIndividual
                if (std::holds_alternative<NamedIndividual>(source)) {
                    auto individual = std::make_shared<NamedIndividual>(std::get<NamedIndividual>(source));
                    individual_cache_[cache_key] = individual;
                    return individual;
                }
            }
        }
    }
    
    return nullptr;
}

std::string CSVParser::apply_transform(
    const std::string& column_name,
    const std::string& value,
    const std::unordered_map<std::string, std::function<std::string(const std::string&)>>& transforms) {
    
    auto it = transforms.find(column_name);
    if (it != transforms.end()) {
        return it->second(value);
    }
    return value;
}

size_t CSVParser::parse_node_type(
    const std::string& filename,
    const IRI& class_iri,
    const NodeTypeConfig& config,
    char delimiter) {
    
    std::ifstream file(filename);
    if (!file.is_open()) {
        throw CSVParseException("Could not open file: " + filename);
    }
    
    size_t count = 0;
    std::string line;
    std::vector<std::string> headers;
    std::unordered_map<std::string, size_t> header_indices;
    
    // Read header if present
    if (config.has_headers) {
        if (!std::getline(file, line)) {
            throw CSVParseException("Empty file or could not read header");
        }
        headers = parse_csv_line(line, delimiter);
        
        // Build header index map
        for (size_t i = 0; i < headers.size(); ++i) {
            header_indices[headers[i]] = i;
        }
        
        // Verify required columns exist
        if (header_indices.find(config.iri_column_name) == header_indices.end()) {
            throw CSVParseException("IRI column '" + config.iri_column_name + "' not found in headers");
        }
    }
    
    // Create the class entity
    Class class_entity(class_iri);
    
    // Add declaration for the class if not already present
    bool class_declared = false;
    for (const auto& axiom : ontology_.getAxioms()) {
        if (auto decl = std::dynamic_pointer_cast<Declaration>(axiom)) {
            if (decl->getEntityType() == Declaration::EntityType::CLASS && 
                decl->getIRI() == class_iri) {
                class_declared = true;
                break;
            }
        }
    }
    if (!class_declared) {
        ontology_.addAxiom(std::make_shared<Declaration>(Declaration::EntityType::CLASS, class_iri));
    }
    
    // Process each row
    while (std::getline(file, line)) {
        // Skip empty lines
        if (line.empty() || std::all_of(line.begin(), line.end(), ::isspace)) {
            continue;
        }
        
        auto fields = parse_csv_line(line, delimiter);
        
        // Skip if not enough fields
        if (fields.size() != headers.size()) {
            std::cerr << "Warning: Row has " << fields.size() << " fields but expected " 
                      << headers.size() << ". Skipping." << std::endl;
            continue;
        }
        
        // Apply filter if specified
        if (!config.filter_column.empty()) {
            auto filter_it = header_indices.find(config.filter_column);
            if (filter_it != header_indices.end()) {
                std::string filter_value = fields[filter_it->second];
                if (filter_value != config.filter_value) {
                    continue; // Skip this row
                }
            }
        }
        
        // Get IRI column value
        std::string iri_value = fields[header_indices.at(config.iri_column_name)];
        iri_value = apply_transform(config.iri_column_name, iri_value, config.data_transforms);
        
        // Check for merge mode
        std::shared_ptr<NamedIndividual> individual;
        
        if (config.merge_mode && !config.merge_column_name.empty() && config.merge_property_iri.has_value()) {
            // Try to find existing individual
            std::string merge_value = fields[header_indices.at(config.merge_column_name)];
            merge_value = apply_transform(config.merge_column_name, merge_value, config.data_transforms);
            individual = find_individual_by_property(config.merge_property_iri.value(), merge_value);
        }
        
        // Create new individual if not found or not in merge mode
        if (!individual) {
            std::string class_name = class_iri.getLocalName().value_or("Individual");
            IRI individual_iri = create_individual_iri(iri_value, class_name);
            individual = std::make_shared<NamedIndividual>(individual_iri);
            
            // Add declaration
            ontology_.addAxiom(std::make_shared<Declaration>(Declaration::EntityType::NAMED_INDIVIDUAL, individual_iri));
            
            // Add class assertion
            auto class_expr = std::make_shared<NamedClass>(class_entity);
            ontology_.addAxiom(std::make_shared<ClassAssertion>(class_expr, Individual(*individual)));
            
            count++;
        }
        
        // Add data properties
        for (const auto& [column_name, property_iri] : config.data_property_map) {
            auto col_it = header_indices.find(column_name);
            if (col_it != header_indices.end()) {
                std::string value = fields[col_it->second];
                
                // Skip empty values
                if (value.empty()) {
                    continue;
                }
                
                // Apply transform if specified
                value = apply_transform(column_name, value, config.data_transforms);
                
                // Create data property
                DataProperty data_property(property_iri);
                
                // Declare property if not already declared
                bool prop_declared = false;
                for (const auto& axiom : ontology_.getAxioms()) {
                    if (auto decl = std::dynamic_pointer_cast<Declaration>(axiom)) {
                        if (decl->getEntityType() == Declaration::EntityType::DATA_PROPERTY && 
                            decl->getIRI() == property_iri) {
                            prop_declared = true;
                            break;
                        }
                    }
                }
                if (!prop_declared) {
                    ontology_.addAxiom(std::make_shared<Declaration>(Declaration::EntityType::DATA_PROPERTY, property_iri));
                }
                
                // Add data property assertion
                Literal literal(value);
                ontology_.addAxiom(std::make_shared<DataPropertyAssertion>(
                    data_property, Individual(*individual), literal));
            }
        }
    }
    
    file.close();
    return count;
}

size_t CSVParser::parse_relationship_type(
    const std::string& filename,
    const IRI& property_iri,
    const RelationshipTypeConfig& config,
    char delimiter) {
    
    std::ifstream file(filename);
    if (!file.is_open()) {
        throw CSVParseException("Could not open file: " + filename);
    }
    
    size_t count = 0;
    std::string line;
    std::vector<std::string> headers;
    std::unordered_map<std::string, size_t> header_indices;
    
    // Read header if present
    if (config.has_headers) {
        if (!std::getline(file, line)) {
            throw CSVParseException("Empty file or could not read header");
        }
        headers = parse_csv_line(line, delimiter);
        
        // Build header index map
        for (size_t i = 0; i < headers.size(); ++i) {
            header_indices[headers[i]] = i;
        }
        
        // Verify required columns exist
        if (header_indices.find(config.subject_column_name) == header_indices.end()) {
            throw CSVParseException("Subject column '" + config.subject_column_name + "' not found");
        }
        if (header_indices.find(config.object_column_name) == header_indices.end()) {
            throw CSVParseException("Object column '" + config.object_column_name + "' not found");
        }
    }
    
    // Declare object property if not already declared
    ObjectProperty object_property(property_iri);
    bool prop_declared = false;
    for (const auto& axiom : ontology_.getAxioms()) {
        if (auto decl = std::dynamic_pointer_cast<Declaration>(axiom)) {
            if (decl->getEntityType() == Declaration::EntityType::OBJECT_PROPERTY && 
                decl->getIRI() == property_iri) {
                prop_declared = true;
                break;
            }
        }
    }
    if (!prop_declared) {
        ontology_.addAxiom(std::make_shared<Declaration>(Declaration::EntityType::OBJECT_PROPERTY, property_iri));
    }
    
    // Process each row
    while (std::getline(file, line)) {
        // Skip empty lines
        if (line.empty() || std::all_of(line.begin(), line.end(), ::isspace)) {
            continue;
        }
        
        auto fields = parse_csv_line(line, delimiter);
        
        // Skip if not enough fields
        if (fields.size() != headers.size()) {
            continue;
        }
        
        // Apply filter if specified
        if (!config.filter_column.empty()) {
            auto filter_it = header_indices.find(config.filter_column);
            if (filter_it != header_indices.end()) {
                std::string filter_value = fields[filter_it->second];
                if (filter_value != config.filter_value) {
                    continue;
                }
            }
        }
        
        // Get subject and object values
        std::string subject_value = fields[header_indices.at(config.subject_column_name)];
        std::string object_value = fields[header_indices.at(config.object_column_name)];
        
        // Apply transforms
        subject_value = apply_transform(config.subject_column_name, subject_value, config.data_transforms);
        object_value = apply_transform(config.object_column_name, object_value, config.data_transforms);
        
        // Validate configuration
        if (!config.subject_match_property_iri.has_value() || !config.object_match_property_iri.has_value()) {
            std::cerr << "Warning: Missing match property IRIs for relationship parsing" << std::endl;
            continue;
        }
        
        // Find subject and object individuals
        auto subject_individual = find_individual_by_property(config.subject_match_property_iri.value(), subject_value);
        auto object_individual = find_individual_by_property(config.object_match_property_iri.value(), object_value);
        
        if (!subject_individual) {
            std::cerr << "Warning: Could not find subject individual with property value: " 
                      << subject_value << std::endl;
            continue;
        }
        
        if (!object_individual) {
            std::cerr << "Warning: Could not find object individual with property value: " 
                      << object_value << std::endl;
            continue;
        }
        
        // Create object property assertion
        ontology_.addAxiom(std::make_shared<ObjectPropertyAssertion>(
            ObjectPropertyExpression(object_property), 
            Individual(*subject_individual), 
            Individual(*object_individual)));
        
        count++;
    }
    
    file.close();
    return count;
}

} // namespace owl2
} // namespace ista
