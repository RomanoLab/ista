#include "turtle_parser.hpp"
#include <fstream>
#include <sstream>
#include <cctype>
#include <algorithm>

namespace ista {
namespace owl2 {

// Public interface
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

// Parser implementation
TurtleParser::Parser::Parser(const std::string& content)
    : content_(content), pos_(0), line_(1), col_(1) {
    // Set default prefixes
    prefixes_["rdf"] = "http://www.w3.org/1999/02/22-rdf-syntax-ns#";
    prefixes_["rdfs"] = "http://www.w3.org/2000/01/rdf-schema#";
    prefixes_["xsd"] = "http://www.w3.org/2001/XMLSchema#";
    prefixes_["owl"] = "http://www.w3.org/2002/07/owl#";
}

Ontology TurtleParser::Parser::parse() {
    std::vector<Triple> triples;
    
    skipWhitespace();
    
    while (!isAtEnd()) {
        // Parse directives or triples
        if (peek() == '@') {
            parseDirective();
        } else if (peek() == '#') {
            skipComment();
        } else {
            auto stmt_triples = parseTriples();
            triples.insert(triples.end(), stmt_triples.begin(), stmt_triples.end());
        }
        
        skipWhitespace();
    }
    
    return triplesToOntology(triples);
}

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
        } else if (c == '#') {
            skipComment();
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
        if (!isAtEnd()) {
            advance(); // consume newline
        }
    }
}

bool TurtleParser::Parser::isAtEnd() const {
    return pos_ >= content_.length();
}

char TurtleParser::Parser::peek() const {
    if (isAtEnd()) return '\0';
    return content_[pos_];
}

char TurtleParser::Parser::advance() {
    if (isAtEnd()) return '\0';
    char c = content_[pos_++];
    if (c == '\n') {
        line_++;
        col_ = 1;
    } else {
        col_++;
    }
    return c;
}

bool TurtleParser::Parser::match(char expected) {
    if (isAtEnd()) return false;
    if (peek() != expected) return false;
    advance();
    return true;
}

bool TurtleParser::Parser::match(const std::string& expected) {
    size_t saved_pos = pos_;
    for (char c : expected) {
        if (isAtEnd() || peek() != c) {
            pos_ = saved_pos;
            return false;
        }
        advance();
    }
    return true;
}

void TurtleParser::Parser::parseDirective() {
    if (!match('@')) {
        error("Expected '@' at start of directive");
    }
    
    // Read directive name
    std::string directive;
    while (!isAtEnd() && isalpha(peek())) {
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
        if (!isNameChar(peek())) {
            error("Invalid character in prefix name");
        }
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
        error("Expected '.' at end of @prefix directive");
    }
    
    prefixes_[prefix] = iri;
}

void TurtleParser::Parser::parseBaseDirective() {
    skipWhitespace();
    
    base_uri_ = parseIRIRef();
    
    skipWhitespace();
    
    if (!match('.')) {
        error("Expected '.' at end of @base directive");
    }
}

std::vector<TurtleParser::Parser::Triple> TurtleParser::Parser::parseTriples() {
    std::vector<Triple> triples;
    
    std::string subject = parseSubject();
    skipWhitespace();
    
    // Parse predicate-object lists
    while (!isAtEnd() && peek() != '.') {
        std::string predicate = parsePredicate();
        skipWhitespace();
        
        // Parse objects
        parseObject(triples, subject, predicate);
        skipWhitespace();
        
        if (match(';')) {
            skipWhitespace();
            if (peek() == '.') break; // Trailing semicolon before period
        } else {
            break;
        }
    }
    
    if (!match('.')) {
        error("Expected '.' at end of triple");
    }
    
    return triples;
}

std::string TurtleParser::Parser::parseSubject() {
    char c = peek();
    
    if (c == '<') {
        return parseIRIRef();
    } else if (c == '_') {
        return parseBlankNode();
    } else if (c == '[') {
        return parseBlankNodePropertyList();
    } else if (c == '(') {
        return parseCollection();
    } else if (isNameStartChar(c)) {
        return parsePrefixedName();
    } else {
        error("Invalid subject");
        return "";
    }
}

std::string TurtleParser::Parser::parsePredicate() {
    if (match('a')) {
        // 'a' is shorthand for rdf:type
        skipWhitespace();
        if (isAtEnd() || !isspace(content_[pos_ - 1])) {
            // Make sure 'a' was followed by whitespace
            return expandPrefix("rdf:type");
        }
        pos_--; // Back up if it wasn't standalone 'a'
    }
    
    char c = peek();
    
    if (c == '<') {
        return parseIRIRef();
    } else if (isNameStartChar(c)) {
        return parsePrefixedName();
    } else {
        error("Invalid predicate");
        return "";
    }
}

void TurtleParser::Parser::parseObject(std::vector<Triple>& triples, 
                                       const std::string& subject, 
                                       const std::string& predicate) {
    do {
        skipWhitespace();
        
        Triple triple;
        triple.subject = subject;
        triple.predicate = predicate;
        triple.object_is_literal = false;
        
        char c = peek();
        
        if (c == '<') {
            triple.object = parseIRIRef();
        } else if (c == '_') {
            triple.object = parseBlankNode();
        } else if (c == '[') {
            triple.object = parseBlankNodePropertyList();
        } else if (c == '(') {
            triple.object = parseCollection();
        } else if (c == '"' || c == '\'') {
            triple.object_is_literal = true;
            triple.object = parseLiteral(triple.literal_datatype, triple.literal_language);
        } else if (isdigit(c) || c == '+' || c == '-' || c == '.') {
            // Numeric literal
            triple.object_is_literal = true;
            std::string num;
            while (!isAtEnd() && (isdigit(peek()) || peek() == '.' || peek() == 'e' || 
                                  peek() == 'E' || peek() == '+' || peek() == '-')) {
                num += advance();
            }
            triple.object = num;
            triple.literal_datatype = "http://www.w3.org/2001/XMLSchema#decimal";
        } else if (match("true") || match("false")) {
            triple.object_is_literal = true;
            triple.object = (content_[pos_ - 1] == 'e') ? "true" : "false";
            triple.literal_datatype = "http://www.w3.org/2001/XMLSchema#boolean";
        } else if (isNameStartChar(c)) {
            triple.object = parsePrefixedName();
        } else {
            error("Invalid object");
        }
        
        triples.push_back(triple);
        
        skipWhitespace();
    } while (match(','));
}

std::string TurtleParser::Parser::parseIRIRef() {
    if (!match('<')) {
        error("Expected '<' at start of IRI reference");
    }
    
    std::string iri;
    while (!isAtEnd() && peek() != '>') {
        char c = advance();
        if (c == '\\') {
            // Handle escape sequences
            if (!isAtEnd()) {
                char escaped = advance();
                if (escaped == 'u') {
                    // Unicode escape \uXXXX
                    std::string hex;
                    for (int i = 0; i < 4; i++) {
                        if (isAtEnd()) error("Incomplete unicode escape");
                        hex += advance();
                    }
                    // For simplicity, just keep the escape sequence
                    iri += "\\u" + hex;
                } else if (escaped == 'U') {
                    // Unicode escape \UXXXXXXXX
                    std::string hex;
                    for (int i = 0; i < 8; i++) {
                        if (isAtEnd()) error("Incomplete unicode escape");
                        hex += advance();
                    }
                    iri += "\\U" + hex;
                } else {
                    iri += escaped;
                }
            }
        } else {
            iri += c;
        }
    }
    
    if (!match('>')) {
        error("Expected '>' at end of IRI reference");
    }
    
    return resolveIRI(iri);
}

std::string TurtleParser::Parser::parsePrefixedName() {
    std::string prefix;
    std::string localName;
    
    // Parse prefix
    while (!isAtEnd() && peek() != ':' && isNameChar(peek())) {
        prefix += advance();
    }
    
    if (!match(':')) {
        error("Expected ':' in prefixed name");
    }
    
    // Parse local name
    while (!isAtEnd() && isNameChar(peek())) {
        localName += advance();
    }
    
    return expandPrefix(prefix + ":" + localName);
}

std::string TurtleParser::Parser::parseBlankNode() {
    if (!match('_')) {
        error("Expected '_' at start of blank node");
    }
    if (!match(':')) {
        error("Expected ':' after '_' in blank node");
    }
    
    std::string label;
    while (!isAtEnd() && isNameChar(peek())) {
        label += advance();
    }
    
    return "_:" + label;
}

std::string TurtleParser::Parser::parseLiteral(std::string& datatype, std::string& language) {
    char quote = peek();
    if (quote != '"' && quote != '\'') {
        error("Expected quote at start of literal");
    }
    advance();
    
    // Check for long literal (""" or ''')
    bool long_literal = false;
    if (peek() == quote && pos_ + 1 < content_.length() && content_[pos_ + 1] == quote) {
        long_literal = true;
        advance();
        advance();
    }
    
    std::string literal;
    while (!isAtEnd()) {
        char c = peek();
        
        if (long_literal) {
            // Check for closing """
            if (c == quote && pos_ + 2 < content_.length() && 
                content_[pos_ + 1] == quote && content_[pos_ + 2] == quote) {
                advance();
                advance();
                advance();
                break;
            }
        } else {
            if (c == quote) {
                advance();
                break;
            }
            if (c == '\n') {
                error("Newline in short literal");
            }
        }
        
        if (c == '\\') {
            advance();
            if (isAtEnd()) error("Incomplete escape sequence");
            char escaped = advance();
            switch (escaped) {
                case 't': literal += '\t'; break;
                case 'n': literal += '\n'; break;
                case 'r': literal += '\r'; break;
                case '"': literal += '"'; break;
                case '\'': literal += '\''; break;
                case '\\': literal += '\\'; break;
                default: literal += escaped; break;
            }
        } else {
            literal += advance();
        }
    }
    
    skipWhitespace();
    
    // Check for language tag or datatype
    if (match('@')) {
        // Language tag
        while (!isAtEnd() && (isalnum(peek()) || peek() == '-')) {
            language += advance();
        }
    } else if (match("^^")) {
        // Datatype
        skipWhitespace();
        datatype = (peek() == '<') ? parseIRIRef() : parsePrefixedName();
    }
    
    return literal;
}

std::string TurtleParser::Parser::parseCollection() {
    if (!match('(')) {
        error("Expected '(' at start of collection");
    }
    
    // TODO: Implement RDF collection parsing
    // For now, skip to closing ')'
    int depth = 1;
    while (!isAtEnd() && depth > 0) {
        if (peek() == '(') depth++;
        else if (peek() == ')') depth--;
        advance();
    }
    
    return "rdf:nil"; // Placeholder
}

std::string TurtleParser::Parser::parseBlankNodePropertyList() {
    if (!match('[')) {
        error("Expected '[' at start of blank node property list");
    }
    
    // TODO: Implement blank node property list parsing
    // For now, skip to closing ']'
    int depth = 1;
    while (!isAtEnd() && depth > 0) {
        if (peek() == '[') depth++;
        else if (peek() == ']') depth--;
        advance();
    }
    
    static int bnode_counter = 0;
    return "_:bnode" + std::to_string(bnode_counter++);
}

std::string TurtleParser::Parser::resolveIRI(const std::string& iri) {
    if (iri.find("://") != std::string::npos) {
        return iri; // Already absolute
    }
    
    if (!base_uri_.empty()) {
        return base_uri_ + iri;
    }
    
    return iri;
}

std::string TurtleParser::Parser::expandPrefix(const std::string& prefixed) {
    size_t colon = prefixed.find(':');
    if (colon == std::string::npos) {
        error("Invalid prefixed name: " + prefixed);
    }
    
    std::string prefix = prefixed.substr(0, colon);
    std::string localName = prefixed.substr(colon + 1);
    
    auto it = prefixes_.find(prefix);
    if (it == prefixes_.end()) {
        error("Undefined prefix: " + prefix);
    }
    
    return it->second + localName;
}

bool TurtleParser::Parser::isNameStartChar(char c) const {
    return isalpha(c) || c == '_';
}

bool TurtleParser::Parser::isNameChar(char c) const {
    return isalnum(c) || c == '_' || c == '-' || c == '.';
}

void TurtleParser::Parser::error(const std::string& message) {
    std::ostringstream oss;
    oss << "Parse error at line " << line_ << ", column " << col_ << ": " << message;
    throw TurtleParseException(oss.str());
}

Ontology TurtleParser::Parser::triplesToOntology(const std::vector<Triple>& triples) {
    Ontology ontology;
    
    // Convert RDF triples to OWL axioms
    for (const auto& triple : triples) {
        // TODO: Implement comprehensive triple-to-axiom conversion
        // This is a complex mapping that requires understanding the RDF/OWL mapping
        
        // For now, handle basic patterns:
        // - rdf:type owl:Class -> Declaration(Class)
        // - rdf:type owl:ObjectProperty -> Declaration(ObjectProperty)
        // - rdfs:subClassOf -> SubClassOf axiom
        // etc.
        
        // This is a placeholder - full implementation would be extensive
    }
    
    return ontology;
}

} // namespace owl2
} // namespace ista
