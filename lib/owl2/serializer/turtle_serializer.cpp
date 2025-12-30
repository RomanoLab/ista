#include "turtle_serializer.hpp"
#include <fstream>
#include <stdexcept>
#include <algorithm>
#include <cctype>
#include <variant>

namespace ista {
namespace owl2 {

// ============================================================================
// Public API
// ============================================================================

std::string TurtleSerializer::serialize(const Ontology& ontology) {
    Builder builder(ontology);
    return builder.build();
}

bool TurtleSerializer::serializeToFile(const Ontology& ontology, const std::string& filename) {
    try {
        std::string content = serialize(ontology);
        std::ofstream file(filename);
        if (!file.is_open()) {
            return false;
        }
        file << content;
        file.close();
        return true;
    } catch (...) {
        return false;
    }
}

std::string TurtleSerializer::serialize(const Ontology& ontology, 
                                       const std::map<std::string, std::string>& prefixes) {
    Builder builder(ontology, prefixes);
    return builder.build();
}

// ============================================================================
// Builder Implementation
// ============================================================================

TurtleSerializer::Builder::Builder(const Ontology& ontology)
    : ontology_(ontology), blank_node_counter_(0) {
    registerStandardNamespaces();
    registerOntologyNamespaces();
    detectNamespaces();
}

TurtleSerializer::Builder::Builder(const Ontology& ontology, 
                                   const std::map<std::string, std::string>& custom_prefixes)
    : ontology_(ontology), blank_node_counter_(0) {
    // Add custom prefixes first
    for (const auto& [prefix, ns] : custom_prefixes) {
        prefixes_[prefix] = ns;
        namespaces_[ns] = prefix;
    }
    registerStandardNamespaces();
    registerOntologyNamespaces();
    detectNamespaces();
}

std::string TurtleSerializer::Builder::build() {
    writePrefixes();
    writeOntologyHeader();
    writeAxioms();
    return ttl_.str();
}

void TurtleSerializer::Builder::writePrefixes() {
    // Write standard prefixes in canonical order
    std::vector<std::string> ordered_prefixes = {
        "rdf", "rdfs", "owl", "xsd"
    };
    
    for (const auto& prefix : ordered_prefixes) {
        if (prefixes_.find(prefix) != prefixes_.end()) {
            ttl_ << "@prefix " << prefix << ": <" << prefixes_[prefix] << "> .\n";
        }
    }
    
    // Write custom prefixes
    for (const auto& [prefix, ns] : prefixes_) {
        if (std::find(ordered_prefixes.begin(), ordered_prefixes.end(), prefix) == ordered_prefixes.end()) {
            ttl_ << "@prefix " << prefix << ": <" << ns << "> .\n";
        }
    }
    
    ttl_ << "\n";
}

void TurtleSerializer::Builder::writeOntologyHeader() {
    auto ontology_iri = ontology_.getOntologyIRI();
    if (ontology_iri.has_value()) {
        std::string ont_iri_str = formatIRI(ontology_iri.value());
        ttl_ << ont_iri_str << " a owl:Ontology";
        
        auto version_iri = ontology_.getVersionIRI();
        if (version_iri.has_value()) {
            ttl_ << " ;\n    owl:versionIRI " << formatIRI(version_iri.value());
        }
        
        // Write imports
        for (const auto& import_iri : ontology_.getImports()) {
            ttl_ << " ;\n    owl:imports " << formatIRI(import_iri);
        }
        
        // Write ontology annotations
        auto ont_annotations = ontology_.getOntologyAnnotations();
        for (const auto& annot : ont_annotations) {
            ttl_ << " ;\n    " << formatIRI(annot.getProperty().getIRI()) << " ";
            
            auto value = annot.getValue();
            if (std::holds_alternative<IRI>(value)) {
                ttl_ << formatIRI(std::get<IRI>(value));
            } else if (std::holds_alternative<Literal>(value)) {
                ttl_ << formatLiteral(std::get<Literal>(value));
            }
        }
        
        ttl_ << " .\n\n";
    }
}

void TurtleSerializer::Builder::writeAxioms() {
    auto axioms = ontology_.getAxioms();
    
    for (const auto& axiom : axioms) {
        std::string axiom_type = axiom->getAxiomType();
        
        // Focus on the most common axiom types for ontologies with individuals
        if (axiom_type == "Declaration") {
            writeDeclaration(std::dynamic_pointer_cast<Declaration>(axiom));
        }
        else if (axiom_type == "ClassAssertion") {
            writeClassAssertion(std::dynamic_pointer_cast<ClassAssertion>(axiom));
        }
        else if (axiom_type == "ObjectPropertyAssertion") {
            writeObjectPropertyAssertion(std::dynamic_pointer_cast<ObjectPropertyAssertion>(axiom));
        }
        else if (axiom_type == "DataPropertyAssertion") {
            writeDataPropertyAssertion(std::dynamic_pointer_cast<DataPropertyAssertion>(axiom));
        }
        else if (axiom_type == "SubClassOf") {
            writeSubClassOf(std::dynamic_pointer_cast<SubClassOf>(axiom));
        }
        else if (axiom_type == "AnnotationAssertion") {
            writeAnnotationAssertion(std::dynamic_pointer_cast<AnnotationAssertion>(axiom));
        }
        else if (axiom_type == "SubObjectPropertyOf") {
            writeSubObjectPropertyOf(std::dynamic_pointer_cast<SubObjectPropertyOf>(axiom));
        }
        else if (axiom_type == "SubDataPropertyOf") {
            writeSubDataPropertyOf(std::dynamic_pointer_cast<SubDataPropertyOf>(axiom));
        }
        else if (axiom_type == "ObjectPropertyDomain") {
            writeObjectPropertyDomain(std::dynamic_pointer_cast<ObjectPropertyDomain>(axiom));
        }
        else if (axiom_type == "ObjectPropertyRange") {
            writeObjectPropertyRange(std::dynamic_pointer_cast<ObjectPropertyRange>(axiom));
        }
        else if (axiom_type == "DataPropertyDomain") {
            writeDataPropertyDomain(std::dynamic_pointer_cast<DataPropertyDomain>(axiom));
        }
        else if (axiom_type == "DataPropertyRange") {
            writeDataPropertyRange(std::dynamic_pointer_cast<DataPropertyRange>(axiom));
        }
        else if (axiom_type == "FunctionalObjectProperty") {
            writeFunctionalObjectProperty(std::dynamic_pointer_cast<FunctionalObjectProperty>(axiom));
        }
        else if (axiom_type == "FunctionalDataProperty") {
            writeFunctionalDataProperty(std::dynamic_pointer_cast<FunctionalDataProperty>(axiom));
        }
        else if (axiom_type == "TransitiveObjectProperty") {
            writeTransitiveObjectProperty(std::dynamic_pointer_cast<TransitiveObjectProperty>(axiom));
        }
        // For other axiom types, we'll skip them for this simplified version
    }
}

// ============================================================================
// Axiom Serialization Methods (Most Common Types)
// ============================================================================

void TurtleSerializer::Builder::writeDeclaration(const std::shared_ptr<Declaration>& axiom) {
    if (!axiom) return;
    
    std::string subject = formatIRI(axiom->getIRI());
    std::string type;
    
    switch (axiom->getEntityType()) {
        case Declaration::EntityType::CLASS:
            type = "owl:Class";
            break;
        case Declaration::EntityType::OBJECT_PROPERTY:
            type = "owl:ObjectProperty";
            break;
        case Declaration::EntityType::DATA_PROPERTY:
            type = "owl:DatatypeProperty";
            break;
        case Declaration::EntityType::ANNOTATION_PROPERTY:
            type = "owl:AnnotationProperty";
            break;
        case Declaration::EntityType::NAMED_INDIVIDUAL:
            type = "owl:NamedIndividual";
            break;
        case Declaration::EntityType::DATATYPE:
            type = "rdfs:Datatype";
            break;
    }
    
    writeTriple(subject, "a", type);
}

void TurtleSerializer::Builder::writeClassAssertion(const std::shared_ptr<ClassAssertion>& axiom) {
    if (!axiom) return;
    
    std::string individual = formatIndividual(axiom->getIndividual());
    std::string cls = formatClassExpression(axiom->getClassExpression());
    writeTriple(individual, "a", cls);
}

void TurtleSerializer::Builder::writeObjectPropertyAssertion(const std::shared_ptr<ObjectPropertyAssertion>& axiom) {
    if (!axiom) return;
    
    auto prop_expr = axiom->getProperty();
    auto source = axiom->getSource();
    auto target = axiom->getTarget();
    
    std::string source_str = formatIndividual(source);
    std::string target_str = formatIndividual(target);
    
    // Handle simple object property (most common case)
    if (std::holds_alternative<ObjectProperty>(prop_expr)) {
        auto prop = std::get<ObjectProperty>(prop_expr);
        std::string property = formatIRI(prop.getIRI());
        writeTriple(source_str, property, target_str);
    }
}

void TurtleSerializer::Builder::writeDataPropertyAssertion(const std::shared_ptr<DataPropertyAssertion>& axiom) {
    if (!axiom) return;
    
    auto prop = axiom->getProperty();
    auto source = axiom->getSource();
    auto target = axiom->getTarget();
    
    std::string source_str = formatIndividual(source);
    std::string property = formatIRI(prop.getIRI());
    std::string value = formatLiteral(target);
    
    writeTriple(source_str, property, value);
}

void TurtleSerializer::Builder::writeSubClassOf(const std::shared_ptr<SubClassOf>& axiom) {
    if (!axiom) return;
    
    std::string subclass = formatClassExpression(axiom->getSubClass());
    std::string superclass = formatClassExpression(axiom->getSuperClass());
    writeTriple(subclass, "rdfs:subClassOf", superclass);
}

void TurtleSerializer::Builder::writeAnnotationAssertion(const std::shared_ptr<AnnotationAssertion>& axiom) {
    if (!axiom) return;
    
    auto prop = axiom->getProperty();
    auto subject = axiom->getSubject();
    auto value = axiom->getValue();
    
    // Format subject (can be IRI or AnonymousIndividual)
    std::string subject_str;
    if (std::holds_alternative<IRI>(subject)) {
        subject_str = formatIRI(std::get<IRI>(subject));
    } else {
        auto anon = std::get<AnonymousIndividual>(subject);
        subject_str = "_:" + anon.getNodeID();
    }
    
    std::string property = formatIRI(prop.getIRI());
    
    // Format value (can be IRI, Literal, or AnonymousIndividual)
    std::string value_str;
    if (std::holds_alternative<IRI>(value)) {
        value_str = formatIRI(std::get<IRI>(value));
    } else if (std::holds_alternative<Literal>(value)) {
        value_str = formatLiteral(std::get<Literal>(value));
    } else {
        auto anon = std::get<AnonymousIndividual>(value);
        value_str = "_:" + anon.getNodeID();
    }
    
    writeTriple(subject_str, property, value_str);
}

void TurtleSerializer::Builder::writeSubObjectPropertyOf(const std::shared_ptr<SubObjectPropertyOf>& axiom) {
    if (!axiom) return;
    
    auto sub_expr = axiom->getSubProperty();
    auto super_expr = axiom->getSuperProperty();
    
    // Handle simple case (most common)
    if (sub_expr.has_value() && std::holds_alternative<ObjectProperty>(sub_expr.value())) {
        auto sub_prop = std::get<ObjectProperty>(sub_expr.value());
        if (std::holds_alternative<ObjectProperty>(super_expr)) {
            auto super_prop = std::get<ObjectProperty>(super_expr);
            writeTriple(formatIRI(sub_prop.getIRI()), "rdfs:subPropertyOf", formatIRI(super_prop.getIRI()));
        }
    }
}

void TurtleSerializer::Builder::writeSubDataPropertyOf(const std::shared_ptr<SubDataPropertyOf>& axiom) {
    if (!axiom) return;
    
    std::string sub = formatIRI(axiom->getSubProperty().getIRI());
    std::string super = formatIRI(axiom->getSuperProperty().getIRI());
    writeTriple(sub, "rdfs:subPropertyOf", super);
}

void TurtleSerializer::Builder::writeObjectPropertyDomain(const std::shared_ptr<ObjectPropertyDomain>& axiom) {
    if (!axiom) return;
    
    auto prop_expr = axiom->getProperty();
    if (std::holds_alternative<ObjectProperty>(prop_expr)) {
        auto prop = std::get<ObjectProperty>(prop_expr);
        std::string property = formatIRI(prop.getIRI());
        std::string domain = formatClassExpression(axiom->getDomain());
        writeTriple(property, "rdfs:domain", domain);
    }
}

void TurtleSerializer::Builder::writeObjectPropertyRange(const std::shared_ptr<ObjectPropertyRange>& axiom) {
    if (!axiom) return;
    
    auto prop_expr = axiom->getProperty();
    if (std::holds_alternative<ObjectProperty>(prop_expr)) {
        auto prop = std::get<ObjectProperty>(prop_expr);
        std::string property = formatIRI(prop.getIRI());
        std::string range = formatClassExpression(axiom->getRange());
        writeTriple(property, "rdfs:range", range);
    }
}

void TurtleSerializer::Builder::writeDataPropertyDomain(const std::shared_ptr<DataPropertyDomain>& axiom) {
    if (!axiom) return;
    
    std::string property = formatIRI(axiom->getProperty().getIRI());
    std::string domain = formatClassExpression(axiom->getDomain());
    writeTriple(property, "rdfs:domain", domain);
}

void TurtleSerializer::Builder::writeDataPropertyRange(const std::shared_ptr<DataPropertyRange>& axiom) {
    if (!axiom) return;
    
    std::string property = formatIRI(axiom->getProperty().getIRI());
    std::string range = formatDataRange(axiom->getRange());
    writeTriple(property, "rdfs:range", range);
}

void TurtleSerializer::Builder::writeFunctionalObjectProperty(const std::shared_ptr<FunctionalObjectProperty>& axiom) {
    if (!axiom) return;
    
    auto prop_expr = axiom->getProperty();
    if (std::holds_alternative<ObjectProperty>(prop_expr)) {
        auto prop = std::get<ObjectProperty>(prop_expr);
        writeTriple(formatIRI(prop.getIRI()), "a", "owl:FunctionalProperty");
    }
}

void TurtleSerializer::Builder::writeFunctionalDataProperty(const std::shared_ptr<FunctionalDataProperty>& axiom) {
    if (!axiom) return;
    
    writeTriple(formatIRI(axiom->getProperty().getIRI()), "a", "owl:FunctionalProperty");
}

void TurtleSerializer::Builder::writeTransitiveObjectProperty(const std::shared_ptr<TransitiveObjectProperty>& axiom) {
    if (!axiom) return;
    
    auto prop_expr = axiom->getProperty();
    if (std::holds_alternative<ObjectProperty>(prop_expr)) {
        auto prop = std::get<ObjectProperty>(prop_expr);
        writeTriple(formatIRI(prop.getIRI()), "a", "owl:TransitiveProperty");
    }
}

// ============================================================================
// Formatting Methods
// ============================================================================

std::string TurtleSerializer::Builder::formatIRI(const IRI& iri) {
    std::string full_iri = iri.getFullIRI();
    
    // Try to use prefix notation
    for (const auto& [ns, prefix] : namespaces_) {
        if (full_iri.find(ns) == 0) {
            std::string local = full_iri.substr(ns.length());
            // Check if local part is valid for prefix notation
            if (!local.empty() && (std::isalpha(local[0]) || local[0] == '_')) {
                bool valid = true;
                for (char c : local) {
                    if (!std::isalnum(c) && c != '_' && c != '-' && c != '.') {
                        valid = false;
                        break;
                    }
                }
                if (valid) {
                    return prefix + ":" + local;
                }
            }
        }
    }
    
    // Fall back to full IRI in angle brackets
    return "<" + full_iri + ">";
}

std::string TurtleSerializer::Builder::formatLiteral(const Literal& literal) {
    std::string value = literal.getLexicalForm();
    std::string escaped = escapeTurtleString(value);
    
    std::ostringstream result;
    result << "\"" << escaped << "\"";
    
    // Add language tag if present
    auto lang_tag = literal.getLanguageTag();
    if (lang_tag.has_value()) {
        result << "@" << lang_tag.value();
    }
    // Add datatype if not xsd:string
    else {
        auto datatype_opt = literal.getDatatype();
        if (datatype_opt.has_value()) {
            std::string datatype = datatype_opt.value().getFullIRI();
            if (datatype != "http://www.w3.org/2001/XMLSchema#string") {
                result << "^^" << formatIRI(datatype_opt.value());
            }
        }
    }
    
    return result.str();
}

std::string TurtleSerializer::Builder::formatIndividual(const Individual& individual) {
    if (std::holds_alternative<NamedIndividual>(individual)) {
        auto named = std::get<NamedIndividual>(individual);
        return formatIRI(named.getIRI());
    } else {
        // Anonymous individual
        auto anon = std::get<AnonymousIndividual>(individual);
        return "_:" + anon.getNodeID();
    }
}

std::string TurtleSerializer::Builder::formatClassExpression(const ClassExpressionPtr& expr) {
    if (!expr) {
        return "owl:Thing";
    }
    
    std::string type = expr->getExpressionType();
    
    if (type == "NamedClass") {
        auto named = std::dynamic_pointer_cast<NamedClass>(expr);
        return formatIRI(named->getClass().getIRI());
    }
    
    // For complex class expressions, fall back to a blank node representation
    // Full implementation would handle ObjectIntersectionOf, ObjectUnionOf, etc.
    return "owl:Thing";
}

std::string TurtleSerializer::Builder::formatDataRange(const DataRangePtr& range) {
    if (!range) {
        return "rdfs:Literal";
    }
    
    std::string type = range->getDataRangeType();
    
    if (type == "NamedDatatype") {
        auto datatype = std::dynamic_pointer_cast<NamedDatatype>(range);
        return formatIRI(datatype->getDatatype().getIRI());
    }
    
    // Default for other data ranges
    return "rdfs:Literal";
}

// ============================================================================
// Helper Methods
// ============================================================================

void TurtleSerializer::Builder::registerStandardNamespaces() {
    if (prefixes_.find("rdf") == prefixes_.end()) {
        prefixes_["rdf"] = "http://www.w3.org/1999/02/22-rdf-syntax-ns#";
        namespaces_["http://www.w3.org/1999/02/22-rdf-syntax-ns#"] = "rdf";
    }
    if (prefixes_.find("rdfs") == prefixes_.end()) {
        prefixes_["rdfs"] = "http://www.w3.org/2000/01/rdf-schema#";
        namespaces_["http://www.w3.org/2000/01/rdf-schema#"] = "rdfs";
    }
    if (prefixes_.find("owl") == prefixes_.end()) {
        prefixes_["owl"] = "http://www.w3.org/2002/07/owl#";
        namespaces_["http://www.w3.org/2002/07/owl#"] = "owl";
    }
    if (prefixes_.find("xsd") == prefixes_.end()) {
        prefixes_["xsd"] = "http://www.w3.org/2001/XMLSchema#";
        namespaces_["http://www.w3.org/2001/XMLSchema#"] = "xsd";
    }
}

void TurtleSerializer::Builder::registerOntologyNamespaces() {
    // Register ontology IRI as base
    auto ont_iri = ontology_.getOntologyIRI();
    if (ont_iri.has_value()) {
        std::string ont_ns = ont_iri.value().getNamespace();
        if (!ont_ns.empty() && namespaces_.find(ont_ns) == namespaces_.end()) {
            prefixes_[""] = ont_ns;  // Default prefix
            namespaces_[ont_ns] = "";
        }
    }
}

void TurtleSerializer::Builder::detectNamespaces() {
    // Scan axioms to detect common namespaces
    std::unordered_map<std::string, int> namespace_counts;
    
    for (const auto& axiom : ontology_.getAxioms()) {
        std::string axiom_type = axiom->getAxiomType();
        
        if (axiom_type == "Declaration") {
            auto decl = std::dynamic_pointer_cast<Declaration>(axiom);
            std::string ns = decl->getIRI().getNamespace();
            if (!ns.empty()) {
                namespace_counts[ns]++;
            }
        }
    }
    
    // Register namespaces that appear frequently
    int counter = 1;
    for (const auto& [ns, count] : namespace_counts) {
        if (count > 5 && namespaces_.find(ns) == namespaces_.end()) {
            std::string prefix = "ns" + std::to_string(counter++);
            prefixes_[prefix] = ns;
            namespaces_[ns] = prefix;
        }
    }
}

std::string TurtleSerializer::Builder::getBlankNodeID() {
    return "b" + std::to_string(blank_node_counter_++);
}

std::string TurtleSerializer::Builder::escapeTurtleString(const std::string& str) {
    std::ostringstream escaped;
    for (char c : str) {
        switch (c) {
            case '\\': escaped << "\\\\"; break;
            case '"':  escaped << "\\\""; break;
            case '\n': escaped << "\\n"; break;
            case '\r': escaped << "\\r"; break;
            case '\t': escaped << "\\t"; break;
            default:   escaped << c; break;
        }
    }
    return escaped.str();
}

bool TurtleSerializer::Builder::needsQuotes(const std::string& str) {
    // Simple heuristic: needs quotes if it contains spaces or special characters
    for (char c : str) {
        if (std::isspace(c) || c == ',' || c == ';' || c == '.') {
            return true;
        }
    }
    return false;
}

void TurtleSerializer::Builder::writeTriple(const std::string& subject, 
                                            const std::string& predicate, 
                                            const std::string& object) {
    ttl_ << subject << " " << predicate << " " << object << " .\n";
}

void TurtleSerializer::Builder::writeAnnotations(const std::vector<Annotation>& annotations, 
                                                 const std::string& subject_iri) {
    // Annotations in Turtle are written as regular triples
    for (const auto& annot : annotations) {
        std::string property = formatIRI(annot.getProperty().getIRI());
        std::string value;
        
        auto annot_value = annot.getValue();
        if (std::holds_alternative<IRI>(annot_value)) {
            value = formatIRI(std::get<IRI>(annot_value));
        } else if (std::holds_alternative<Literal>(annot_value)) {
            value = formatLiteral(std::get<Literal>(annot_value));
        } else {
            auto anon = std::get<AnonymousIndividual>(annot_value);
            value = "_:" + anon.getNodeID();
        }
        
        writeTriple(subject_iri, property, value);
    }
}

} // namespace owl2
} // namespace ista
