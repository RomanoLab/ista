#include "turtle_parser.hpp"
#include <fstream>
#include <sstream>
#include <cctype>
#include <algorithm>

namespace ista {
namespace owl2 {

// ============================================================================
// Public API
// ============================================================================

Ontology TurtleParser::parseFromString(const std::string& content) {
    Parser parser(content);
    return parser.parse();
}

Ontology TurtleParser::parseFromFile(const std::string& filename) {
    std::ifstream file(filename);
    if (!file.is_open()) {
        throw TurtleParseException("Could not open file: " + filename);
    }
    
    std::stringstream buffer;
    buffer << file.rdbuf();
    return parseFromString(buffer.str());
}

// ============================================================================
// Parser Implementation
// ============================================================================

TurtleParser::Parser::Parser(const std::string& content)
    : content_(content), pos_(0), line_(1), col_(1) {
    // Standard prefixes
    prefixes_["rdf"] = "http://www.w3.org/1999/02/22-rdf-syntax-ns#";
    prefixes_["rdfs"] = "http://www.w3.org/2000/01/rdf-schema#";
    prefixes_["owl"] = "http://www.w3.org/2002/07/owl#";
    prefixes_["xsd"] = "http://www.w3.org/2001/XMLSchema#";
}

Ontology TurtleParser::Parser::parse() {
    std::vector<Triple> triples;
    
    while (!isAtEnd()) {
        skipWhitespace();
        
        if (isAtEnd()) break;
        
        char c = peek();
        
        // Handle directives
        if (c == '@') {
            parseDirective();
        }
        // Handle comments
        else if (c == '#') {
            skipComment();
        }
        // Handle triples
        else {
            auto triple_batch = parseTriples();
            triples.insert(triples.end(), triple_batch.begin(), triple_batch.end());
        }
        
        skipWhitespace();
    }
    
    return triplesToOntology(triples);
}

// ============================================================================
// Directive Parsing
// ============================================================================

void TurtleParser::Parser::parseDirective() {
    advance(); // Skip '@'
    
    std::string directive;
    while (!isAtEnd() && isNameChar(peek())) {
        directive += advance();
    }
    
    if (directive == "prefix") {
        parsePrefixDirective();
    } else if (directive == "base") {
        parseBaseDirective();
    } else {
        error("Unknown directive: @" + directive);
    }
}

void TurtleParser::Parser::parsePrefixDirective() {
    skipWhitespace();
    
    // Parse prefix name
    std::string prefix;
    while (!isAtEnd() && peek() != ':') {
        prefix += advance();
    }
    
    if (!match(':')) {
        error("Expected ':' after prefix name");
    }
    
    skipWhitespace();
    
    // Parse IRI
    std::string iri = parseIRIRef();
    
    skipWhitespace();
    if (!match('.')) {
        error("Expected '.' after @prefix directive");
    }
    
    prefixes_[prefix] = iri;
}

void TurtleParser::Parser::parseBaseDirective() {
    skipWhitespace();
    
    base_uri_ = parseIRIRef();
    
    skipWhitespace();
    if (!match('.')) {
        error("Expected '.' after @base directive");
    }
}

// ============================================================================
// Triple Parsing
// BREADCRUMB: Does not handle semicolon grouping (;) or comma lists (,)
// Each triple must be on its own line ending with '.'
// ============================================================================

std::vector<TurtleParser::Parser::Triple> TurtleParser::Parser::parseTriples() {
    std::vector<Triple> triples;
    
    std::string subject = parseSubject();
    skipWhitespace();
    
    std::string predicate = parsePredicate();
    skipWhitespace();
    
    parseObject(triples, subject, predicate);
    
    skipWhitespace();
    if (!match('.')) {
        error("Expected '.' at end of triple");
    }
    
    return triples;
}

std::string TurtleParser::Parser::parseSubject() {
    skipWhitespace();
    
    char c = peek();
    
    if (c == '<') {
        return parseIRIRef();
    } else if (c == '_') {
        return parseBlankNode();
    } else if (isNameStartChar(c) || c == ':') {
        // Allow ':' for default prefix (e.g., ":test")
        return parsePrefixedName();
    } else {
        error("Expected subject (IRI, blank node, or prefixed name)");
        return "";
    }
}

std::string TurtleParser::Parser::parsePredicate() {
    skipWhitespace();
    
    // Handle 'a' shortcut for rdf:type
    if (peek() == 'a' && (pos_ + 1 >= content_.size() || std::isspace(content_[pos_ + 1]))) {
        advance();
        return prefixes_["rdf"] + "type";
    }
    
    char c = peek();
    
    if (c == '<') {
        return parseIRIRef();
    } else if (isNameStartChar(c) || c == ':') {
        // Allow ':' for default prefix (e.g., ":hasAge")
        return parsePrefixedName();
    } else {
        error("Expected predicate (IRI or prefixed name)");
        return "";
    }
}

void TurtleParser::Parser::parseObject(std::vector<Triple>& triples, 
                                       const std::string& subject, 
                                       const std::string& predicate) {
    skipWhitespace();
    
    Triple triple;
    triple.subject = subject;
    triple.predicate = predicate;
    triple.object_is_literal = false;
    
    char c = peek();
    
    // BREADCRUMB: Does not handle blank node property lists []
    // BREADCRUMB: Does not handle RDF collections ()
    
    if (c == '"') {
        // Literal
        triple.object_is_literal = true;
        triple.object = parseLiteral(triple.literal_datatype, triple.literal_language);
    } else if (c == '<') {
        // IRI reference
        triple.object = parseIRIRef();
    } else if (c == '_') {
        // Blank node
        triple.object = parseBlankNode();
    } else if (isNameStartChar(c) || c == ':' || std::isdigit(c)) {
        // Prefixed name (including default prefix :) or numeric literal
        if (std::isdigit(c) || c == '+' || c == '-' || c == '.') {
            // BREADCRUMB: Numeric literal parsing is simplified
            // May not handle all edge cases (scientific notation, etc.)
            triple.object_is_literal = true;
            std::string num;
            while (!isAtEnd() && (std::isdigit(peek()) || peek() == '.' || peek() == 'e' || peek() == 'E' || 
                                  peek() == '+' || peek() == '-')) {
                num += advance();
            }
            triple.object = num;
            
            // Determine datatype
            if (num.find('.') != std::string::npos || num.find('e') != std::string::npos || num.find('E') != std::string::npos) {
                triple.literal_datatype = prefixes_["xsd"] + "double";
            } else {
                triple.literal_datatype = prefixes_["xsd"] + "integer";
            }
        } else {
            triple.object = parsePrefixedName();
        }
    } else {
        error("Expected object (IRI, blank node, literal, or prefixed name)");
    }
    
    triples.push_back(triple);
}

// ============================================================================
// Term Parsing
// ============================================================================

std::string TurtleParser::Parser::parseIRIRef() {
    if (!match('<')) {
        error("Expected '<' to start IRI reference");
        return "";
    }
    
    std::string iri;
    while (!isAtEnd() && peek() != '>') {
        char c = advance();
        
        // BREADCRUMB: Does not handle IRI escape sequences like \u or \U
        if (c == '\\') {
            error("IRI escape sequences not yet supported");
        }
        
        iri += c;
    }
    
    if (!match('>')) {
        error("Expected '>' to end IRI reference");
    }
    
    return resolveIRI(iri);
}

std::string TurtleParser::Parser::parsePrefixedName() {
    std::string prefix;
    
    // Parse prefix (optional)
    while (!isAtEnd() && peek() != ':' && isNameChar(peek())) {
        prefix += advance();
    }
    
    if (!match(':')) {
        error("Expected ':' in prefixed name");
        return "";
    }
    
    // Parse local name
    std::string local;
    while (!isAtEnd() && isNameChar(peek())) {
        local += advance();
    }
    
    return expandPrefix(prefix + ":" + local);
}

std::string TurtleParser::Parser::parseBlankNode() {
    if (!match('_')) {
        error("Expected '_' to start blank node");
        return "";
    }
    if (!match(':')) {
        error("Expected ':' after '_' in blank node");
        return "";
    }
    
    std::string id;
    while (!isAtEnd() && isNameChar(peek())) {
        id += advance();
    }
    
    return "_:" + id;
}

std::string TurtleParser::Parser::parseLiteral(std::string& datatype, std::string& language) {
    // BREADCRUMB: Does not handle triple-quoted strings (""")
    // BREADCRUMB: Does not handle all escape sequences
    
    if (!match('"')) {
        error("Expected '\"' to start literal");
        return "";
    }
    
    std::string value;
    while (!isAtEnd() && peek() != '"') {
        char c = advance();
        
        if (c == '\\') {
            // Handle escape sequences
            if (isAtEnd()) {
                error("Unexpected end in escape sequence");
                return "";
            }
            char escaped = advance();
            switch (escaped) {
                case 't': value += '\t'; break;
                case 'n': value += '\n'; break;
                case 'r': value += '\r'; break;
                case '"': value += '"'; break;
                case '\\': value += '\\'; break;
                // BREADCRUMB: Does not handle \u or \U Unicode escapes
                default:
                    error(std::string("Unknown escape sequence: \\") + escaped);
            }
        } else {
            value += c;
        }
    }
    
    if (!match('"')) {
        error("Expected '\"' to end literal");
    }
    
    skipWhitespace();
    
    // Check for language tag
    if (peek() == '@') {
        advance();
        while (!isAtEnd() && (std::isalpha(peek()) || peek() == '-')) {
            language += advance();
        }
    }
    // Check for datatype
    else if (peek() == '^') {
        advance();
        if (!match('^')) {
            error("Expected '^^' for datatype");
        }
        skipWhitespace();
        
        if (peek() == '<') {
            datatype = parseIRIRef();
        } else {
            datatype = parsePrefixedName();
        }
    }
    
    return value;
}

// ============================================================================
// Utilities
// ============================================================================

void TurtleParser::Parser::skipWhitespace() {
    while (!isAtEnd()) {
        char c = peek();
        if (c == ' ' || c == '\t' || c == '\r' || c == '\n') {
            if (c == '\n') {
                line_++;
                col_ = 1;
            } else {
                col_++;
            }
            pos_++;
        } else {
            break;
        }
    }
}

void TurtleParser::Parser::skipComment() {
    if (peek() == '#') {
        while (!isAtEnd() && peek() != '\n') {
            advance();
        }
    }
}

bool TurtleParser::Parser::isAtEnd() const {
    return pos_ >= content_.size();
}

char TurtleParser::Parser::peek() const {
    if (isAtEnd()) return '\0';
    return content_[pos_];
}

char TurtleParser::Parser::advance() {
    if (isAtEnd()) return '\0';
    char c = content_[pos_++];
    col_++;
    return c;
}

bool TurtleParser::Parser::match(char expected) {
    if (isAtEnd() || peek() != expected) {
        return false;
    }
    advance();
    return true;
}

bool TurtleParser::Parser::match(const std::string& expected) {
    if (pos_ + expected.size() > content_.size()) {
        return false;
    }
    
    for (size_t i = 0; i < expected.size(); i++) {
        if (content_[pos_ + i] != expected[i]) {
            return false;
        }
    }
    
    pos_ += expected.size();
    col_ += expected.size();
    return true;
}

std::string TurtleParser::Parser::resolveIRI(const std::string& iri) {
    // If it's already absolute, return as-is
    if (iri.find("http://") == 0 || iri.find("https://") == 0 || iri.find("file://") == 0) {
        return iri;
    }
    
    // Resolve relative to base
    if (!base_uri_.empty()) {
        return base_uri_ + iri;
    }
    
    return iri;
}

std::string TurtleParser::Parser::expandPrefix(const std::string& prefixed) {
    size_t colon = prefixed.find(':');
    if (colon == std::string::npos) {
        return prefixed;
    }
    
    std::string prefix = prefixed.substr(0, colon);
    std::string local = prefixed.substr(colon + 1);
    
    auto it = prefixes_.find(prefix);
    if (it != prefixes_.end()) {
        return it->second + local;
    }
    
    return prefixed;
}

bool TurtleParser::Parser::isNameStartChar(char c) const {
    return std::isalpha(c) || c == '_';
}

bool TurtleParser::Parser::isNameChar(char c) const {
    return std::isalnum(c) || c == '_' || c == '-' || c == '.';
}

void TurtleParser::Parser::error(const std::string& message) {
    std::ostringstream oss;
    oss << "Parse error at line " << line_ << ", column " << col_ << ": " << message;
    throw TurtleParseException(oss.str());
}

// ============================================================================
// Convert RDF Triples to OWL Ontology
// BREADCRUMB: This is a simplified RDF-to-OWL conversion
// Does not handle all OWL constructs, blank node patterns, or restrictions
// ============================================================================

Ontology TurtleParser::Parser::triplesToOntology(const std::vector<Triple>& triples) {
    Ontology ont;
    
    // First pass: collect ontology IRI if present
    for (const auto& t : triples) {
        if (t.predicate == prefixes_["rdf"] + "type" && 
            t.object == prefixes_["owl"] + "Ontology") {
            ont = Ontology(IRI(t.subject));
            break;
        }
    }
    
    // Second pass: process triples
    for (const auto& t : triples) {
        try {
            // Skip blank node subjects for now
            // BREADCRUMB: Blank nodes need special handling for complex axioms
            if (t.subject.find("_:") == 0) {
                continue;
            }
            
            IRI subject_iri(t.subject);
            IRI predicate_iri(t.predicate);
            
            // Handle rdf:type
            if (t.predicate == prefixes_["rdf"] + "type") {
                if (t.object == prefixes_["owl"] + "Class") {
                    ont.addAxiom(std::make_shared<Declaration>(Declaration::EntityType::CLASS, subject_iri));
                } else if (t.object == prefixes_["owl"] + "ObjectProperty") {
                    ont.addAxiom(std::make_shared<Declaration>(Declaration::EntityType::OBJECT_PROPERTY, subject_iri));
                } else if (t.object == prefixes_["owl"] + "DatatypeProperty") {
                    ont.addAxiom(std::make_shared<Declaration>(Declaration::EntityType::DATA_PROPERTY, subject_iri));
                } else if (t.object == prefixes_["owl"] + "AnnotationProperty") {
                    ont.addAxiom(std::make_shared<Declaration>(Declaration::EntityType::ANNOTATION_PROPERTY, subject_iri));
                } else if (t.object == prefixes_["owl"] + "NamedIndividual") {
                    ont.addAxiom(std::make_shared<Declaration>(Declaration::EntityType::NAMED_INDIVIDUAL, subject_iri));
                } else if (t.object.find("_:") != 0) {
                    // Class assertion
                    NamedIndividual individual(subject_iri);
                    Class cls(IRI(t.object));
                    auto class_expr = std::make_shared<NamedClass>(cls);
                    ont.addAxiom(std::make_shared<ClassAssertion>(class_expr, individual));
                }
            }
            // Handle rdfs:subClassOf
            else if (t.predicate == prefixes_["rdfs"] + "subClassOf" && t.object.find("_:") != 0) {
                Class subclass(subject_iri);
                Class superclass(IRI(t.object));
                auto sub_expr = std::make_shared<NamedClass>(subclass);
                auto super_expr = std::make_shared<NamedClass>(superclass);
                ont.addAxiom(std::make_shared<SubClassOf>(sub_expr, super_expr));
            }
            // Handle rdfs:subPropertyOf
            else if (t.predicate == prefixes_["rdfs"] + "subPropertyOf" && t.object.find("_:") != 0) {
                // Try object property first
                ObjectProperty sub_prop(subject_iri);
                ObjectProperty super_prop(IRI(t.object));
                ObjectPropertyExpression sub_expr = sub_prop;
                ObjectPropertyExpression super_expr = super_prop;
                ont.addAxiom(std::make_shared<SubObjectPropertyOf>(sub_expr, super_expr));
            }
            // Handle rdfs:domain
            else if (t.predicate == prefixes_["rdfs"] + "domain" && t.object.find("_:") != 0) {
                Class domain_class(IRI(t.object));
                auto domain_expr = std::make_shared<NamedClass>(domain_class);
                
                // Try as object property
                ObjectProperty obj_prop(subject_iri);
                ObjectPropertyExpression prop_expr = obj_prop;
                ont.addAxiom(std::make_shared<ObjectPropertyDomain>(prop_expr, domain_expr));
            }
            // Handle rdfs:range
            else if (t.predicate == prefixes_["rdfs"] + "range" && t.object.find("_:") != 0) {
                Class range_class(IRI(t.object));
                auto range_expr = std::make_shared<NamedClass>(range_class);
                
                // Try as object property
                ObjectProperty obj_prop(subject_iri);
                ObjectPropertyExpression prop_expr = obj_prop;
                ont.addAxiom(std::make_shared<ObjectPropertyRange>(prop_expr, range_expr));
            }
            // Handle data property assertions
            else if (t.object_is_literal) {
                NamedIndividual individual(subject_iri);
                DataProperty prop(predicate_iri);
                
                // Create the literal value based on available information
                Literal literal_value = !t.literal_language.empty() 
                    ? Literal(t.object, t.literal_language)
                    : !t.literal_datatype.empty()
                        ? Literal(t.object, IRI(t.literal_datatype))
                        : Literal(t.object);
                
                ont.addAxiom(std::make_shared<DataPropertyAssertion>(prop, individual, literal_value));
            }
            // Handle object property assertions
            else if (t.object.find("_:") != 0) {
                NamedIndividual subject_ind(subject_iri);
                NamedIndividual object_ind(IRI(t.object));
                ObjectProperty prop(predicate_iri);
                ObjectPropertyExpression prop_expr = prop;
                
                ont.addAxiom(std::make_shared<ObjectPropertyAssertion>(prop_expr, subject_ind, object_ind));
            }
        } catch (const std::exception& e) {
            // BREADCRUMB: Silently skip malformed triples for now
            // In production, might want to log warnings
            continue;
        }
    }
    
    return ont;
}

} // namespace owl2
} // namespace ista
