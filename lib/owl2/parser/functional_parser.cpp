#include "functional_parser.hpp"
#include <fstream>
#include <sstream>
#include <cctype>
#include <algorithm>

namespace ista {
namespace owl2 {

// Public interface
Ontology FunctionalParser::parseFromString(const std::string& content) {
    Parser parser(content);
    return parser.parse();
}

Ontology FunctionalParser::parseFromFile(const std::string& filename) {
    std::ifstream file(filename);
    if (!file.is_open()) {
        throw FunctionalParseException("Could not open file: " + filename);
    }
    
    std::stringstream buffer;
    buffer << file.rdbuf();
    return parseFromString(buffer.str());
}

// Parser implementation
FunctionalParser::Parser::Parser(const std::string& content)
    : content_(content), pos_(0), line_(1), col_(1), current_ontology_(nullptr) {
}

Ontology FunctionalParser::Parser::parse() {
    Ontology ontology;
    current_ontology_ = &ontology;
    
    skipWhitespace();
    
    // Parse Prefix declarations
    while (!isAtEnd() && match("Prefix(")) {
        parsePrefixDeclaration();
        skipWhitespace();
    }
    
    // Parse Ontology
    if (match("Ontology(")) {
        parseOntology(ontology);
    } else {
        error("Expected 'Ontology(' at top level");
    }
    
    return ontology;
}

void FunctionalParser::Parser::skipWhitespace() {
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

void FunctionalParser::Parser::skipComment() {
    if (peek() == '#') {
        while (!isAtEnd() && peek() != '\n') {
            advance();
        }
        if (!isAtEnd()) {
            advance(); // consume newline
        }
    }
}

bool FunctionalParser::Parser::isAtEnd() const {
    return pos_ >= content_.length();
}

char FunctionalParser::Parser::peek() const {
    if (isAtEnd()) return '\0';
    return content_[pos_];
}

char FunctionalParser::Parser::advance() {
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

bool FunctionalParser::Parser::match(char expected) {
    if (isAtEnd()) return false;
    if (peek() != expected) return false;
    advance();
    return true;
}

bool FunctionalParser::Parser::match(const std::string& expected) {
    size_t saved_pos = pos_;
    size_t saved_line = line_;
    size_t saved_col = col_;
    
    for (char c : expected) {
        if (isAtEnd() || peek() != c) {
            pos_ = saved_pos;
            line_ = saved_line;
            col_ = saved_col;
            return false;
        }
        advance();
    }
    return true;
}

std::string FunctionalParser::Parser::readToken() {
    skipWhitespace();
    std::string token;
    
    while (!isAtEnd()) {
        char c = peek();
        if (isspace(c) || c == '(' || c == ')' || c == '<' || c == '"' || c == '#') {
            break;
        }
        token += advance();
    }
    
    return token;
}

std::string FunctionalParser::Parser::readQuotedString() {
    if (!match('"')) {
        error("Expected '\"' at start of quoted string");
    }
    
    std::string str;
    while (!isAtEnd() && peek() != '"') {
        if (peek() == '\\') {
            advance();
            if (!isAtEnd()) {
                char escaped = advance();
                switch (escaped) {
                    case 'n': str += '\n'; break;
                    case 't': str += '\t'; break;
                    case 'r': str += '\r'; break;
                    case '"': str += '"'; break;
                    case '\\': str += '\\'; break;
                    default: str += escaped; break;
                }
            }
        } else {
            str += advance();
        }
    }
    
    if (!match('"')) {
        error("Expected '\"' at end of quoted string");
    }
    
    return str;
}

std::string FunctionalParser::Parser::readIRI() {
    if (match('<')) {
        std::string iri;
        while (!isAtEnd() && peek() != '>') {
            iri += advance();
        }
        if (!match('>')) {
            error("Expected '>' at end of IRI");
        }
        return iri;
    } else {
        // Abbreviated IRI
        std::string abbreviated = readToken();
        return expandIRI(abbreviated);
    }
}

void FunctionalParser::Parser::parsePrefixDeclaration() {
    skipWhitespace();
    
    // Read prefix name (can be empty for default namespace)
    std::string prefix;
    if (peek() == ':') {
        advance();
    } else {
        while (!isAtEnd() && peek() != ':') {
            prefix += advance();
        }
        if (!match(':')) {
            error("Expected ':' after prefix name");
        }
    }
    
    skipWhitespace();
    expect('=');
    skipWhitespace();
    
    std::string iri = readIRI();
    
    skipWhitespace();
    expect(')');
    
    prefixes_[prefix] = iri;
}

void FunctionalParser::Parser::parseOntology(Ontology& ontology) {
    skipWhitespace();
    
    // Parse ontology IRI (optional)
    if (peek() == '<') {
        std::string ontologyIRI = readIRI();
        ontology.setOntologyIRI(IRI(ontologyIRI));
        
        skipWhitespace();
        
        // Parse version IRI (optional)
        if (peek() == '<') {
            std::string versionIRI = readIRI();
            ontology.setVersionIRI(IRI(versionIRI));
            skipWhitespace();
        }
    }
    
    // Parse imports
    while (!isAtEnd() && match("Import(")) {
        skipWhitespace();
        std::string importIRI = readIRI();
        ontology.addImport(IRI(importIRI));
        skipWhitespace();
        expect(')');
        skipWhitespace();
    }
    
    // Parse axioms
    while (!isAtEnd() && peek() != ')') {
        auto axiom = parseAxiom();
        if (axiom) {
            ontology.addAxiom(axiom);
        }
        skipWhitespace();
    }
    
    expect(')');
}

std::shared_ptr<Axiom> FunctionalParser::Parser::parseAxiom() {
    skipWhitespace();
    
    std::string keyword = readToken();
    
    if (keyword == "Declaration") {
        return parseDeclaration();
    } else if (keyword == "SubClassOf" || keyword == "EquivalentClasses" || 
               keyword == "DisjointClasses" || keyword == "DisjointUnion") {
        return parseClassAxiom(keyword);
    } else if (keyword == "SubObjectPropertyOf" || keyword == "EquivalentObjectProperties" ||
               keyword == "DisjointObjectProperties" || keyword == "InverseObjectProperties" ||
               keyword == "ObjectPropertyDomain" || keyword == "ObjectPropertyRange" ||
               keyword == "FunctionalObjectProperty" || keyword == "InverseFunctionalObjectProperty" ||
               keyword == "ReflexiveObjectProperty" || keyword == "IrreflexiveObjectProperty" ||
               keyword == "SymmetricObjectProperty" || keyword == "AsymmetricObjectProperty" ||
               keyword == "TransitiveObjectProperty") {
        return parseObjectPropertyAxiom(keyword);
    } else if (keyword == "SubDataPropertyOf" || keyword == "EquivalentDataProperties" ||
               keyword == "DisjointDataProperties" || keyword == "DataPropertyDomain" ||
               keyword == "DataPropertyRange" || keyword == "FunctionalDataProperty") {
        return parseDataPropertyAxiom(keyword);
    } else if (keyword == "ClassAssertion" || keyword == "ObjectPropertyAssertion" ||
               keyword == "NegativeObjectPropertyAssertion" || keyword == "DataPropertyAssertion" ||
               keyword == "NegativeDataPropertyAssertion" || keyword == "SameIndividual" ||
               keyword == "DifferentIndividuals") {
        return parseAssertionAxiom(keyword);
    } else if (keyword == "AnnotationAssertion" || keyword == "SubAnnotationPropertyOf" ||
               keyword == "AnnotationPropertyDomain" || keyword == "AnnotationPropertyRange") {
        return parseAnnotationAxiom(keyword);
    } else if (keyword == "DatatypeDefinition" || keyword == "HasKey") {
        // Skip for now - these are less common
        int depth = 1;
        expect('(');
        while (!isAtEnd() && depth > 0) {
            if (match('(')) depth++;
            else if (match(')')) depth--;
            else advance();
        }
        return nullptr;
    } else {
        error("Unknown axiom type: " + keyword);
        return nullptr;
    }
}

std::shared_ptr<Axiom> FunctionalParser::Parser::parseDeclaration() {
    expect('(');
    skipWhitespace();
    
    std::string entityType = readToken();
    expect('(');
    skipWhitespace();
    
    std::string iri = readIRI();
    
    skipWhitespace();
    expect(')');
    expect(')');
    
    if (entityType == "Class") {
        return std::make_shared<Declaration>(Class(IRI(iri)));
    } else if (entityType == "ObjectProperty") {
        return std::make_shared<Declaration>(ObjectProperty(IRI(iri)));
    } else if (entityType == "DataProperty") {
        return std::make_shared<Declaration>(DataProperty(IRI(iri)));
    } else if (entityType == "AnnotationProperty") {
        return std::make_shared<Declaration>(AnnotationProperty(IRI(iri)));
    } else if (entityType == "NamedIndividual") {
        return std::make_shared<Declaration>(NamedIndividual(IRI(iri)));
    } else if (entityType == "Datatype") {
        return std::make_shared<Declaration>(Datatype(IRI(iri)));
    } else {
        error("Unknown entity type in Declaration: " + entityType);
        return nullptr;
    }
}

std::shared_ptr<Axiom> FunctionalParser::Parser::parseClassAxiom(const std::string& axiomType) {
    expect('(');
    skipWhitespace();
    
    // Parse optional annotations
    std::vector<Annotation> annotations = parseAnnotations();
    
    if (axiomType == "SubClassOf") {
        auto subclass = parseClassExpression();
        skipWhitespace();
        auto superclass = parseClassExpression();
        skipWhitespace();
        expect(')');
        
        return std::make_shared<SubClassOf>(subclass, superclass, annotations);
    } else if (axiomType == "EquivalentClasses") {
        std::vector<std::shared_ptr<ClassExpression>> classes;
        while (peek() != ')') {
            classes.push_back(parseClassExpression());
            skipWhitespace();
        }
        expect(')');
        
        return std::make_shared<EquivalentClasses>(classes, annotations);
    } else if (axiomType == "DisjointClasses") {
        std::vector<std::shared_ptr<ClassExpression>> classes;
        while (peek() != ')') {
            classes.push_back(parseClassExpression());
            skipWhitespace();
        }
        expect(')');
        
        return std::make_shared<DisjointClasses>(classes, annotations);
    } else {
        error("Unhandled class axiom: " + axiomType);
        return nullptr;
    }
}

std::shared_ptr<Axiom> FunctionalParser::Parser::parseObjectPropertyAxiom(const std::string& axiomType) {
    expect('(');
    skipWhitespace();
    
    // Parse optional annotations
    std::vector<Annotation> annotations = parseAnnotations();
    
    if (axiomType == "ObjectPropertyDomain") {
        auto prop = parseObjectProperty();
        skipWhitespace();
        auto domain = parseClassExpression();
        skipWhitespace();
        expect(')');
        
        return std::make_shared<ObjectPropertyDomain>(prop, domain, annotations);
    } else if (axiomType == "ObjectPropertyRange") {
        auto prop = parseObjectProperty();
        skipWhitespace();
        auto range = parseClassExpression();
        skipWhitespace();
        expect(')');
        
        return std::make_shared<ObjectPropertyRange>(prop, range, annotations);
    } else if (axiomType == "FunctionalObjectProperty") {
        auto prop = parseObjectProperty();
        skipWhitespace();
        expect(')');
        
        return std::make_shared<FunctionalObjectProperty>(prop, annotations);
    } else if (axiomType == "InverseFunctionalObjectProperty") {
        auto prop = parseObjectProperty();
        skipWhitespace();
        expect(')');
        
        return std::make_shared<InverseFunctionalObjectProperty>(prop, annotations);
    } else if (axiomType == "ReflexiveObjectProperty") {
        auto prop = parseObjectProperty();
        skipWhitespace();
        expect(')');
        
        return std::make_shared<ReflexiveObjectProperty>(prop, annotations);
    } else if (axiomType == "IrreflexiveObjectProperty") {
        auto prop = parseObjectProperty();
        skipWhitespace();
        expect(')');
        
        return std::make_shared<IrreflexiveObjectProperty>(prop, annotations);
    } else if (axiomType == "SymmetricObjectProperty") {
        auto prop = parseObjectProperty();
        skipWhitespace();
        expect(')');
        
        return std::make_shared<SymmetricObjectProperty>(prop, annotations);
    } else if (axiomType == "AsymmetricObjectProperty") {
        auto prop = parseObjectProperty();
        skipWhitespace();
        expect(')');
        
        return std::make_shared<AsymmetricObjectProperty>(prop, annotations);
    } else if (axiomType == "TransitiveObjectProperty") {
        auto prop = parseObjectProperty();
        skipWhitespace();
        expect(')');
        
        return std::make_shared<TransitiveObjectProperty>(prop, annotations);
    } else {
        // For other axioms, skip for now
        int depth = 1;
        while (!isAtEnd() && depth > 0) {
            if (match('(')) depth++;
            else if (match(')')) depth--;
            else advance();
        }
        return nullptr;
    }
}

std::shared_ptr<Axiom> FunctionalParser::Parser::parseDataPropertyAxiom(const std::string& axiomType) {
    expect('(');
    skipWhitespace();
    
    // Parse optional annotations
    std::vector<Annotation> annotations = parseAnnotations();
    
    if (axiomType == "DataPropertyDomain") {
        auto prop = parseDataProperty();
        skipWhitespace();
        auto domain = parseClassExpression();
        skipWhitespace();
        expect(')');
        
        return std::make_shared<DataPropertyDomain>(prop, domain, annotations);
    } else if (axiomType == "DataPropertyRange") {
        auto prop = parseDataProperty();
        skipWhitespace();
        auto range = parseDataRange();
        skipWhitespace();
        expect(')');
        
        return std::make_shared<DataPropertyRange>(prop, range, annotations);
    } else if (axiomType == "FunctionalDataProperty") {
        auto prop = parseDataProperty();
        skipWhitespace();
        expect(')');
        
        return std::make_shared<FunctionalDataProperty>(prop, annotations);
    } else {
        // Skip other data property axioms for now
        int depth = 1;
        while (!isAtEnd() && depth > 0) {
            if (match('(')) depth++;
            else if (match(')')) depth--;
            else advance();
        }
        return nullptr;
    }
}

std::shared_ptr<Axiom> FunctionalParser::Parser::parseAssertionAxiom(const std::string& axiomType) {
    expect('(');
    skipWhitespace();
    
    // Parse optional annotations
    std::vector<Annotation> annotations = parseAnnotations();
    
    if (axiomType == "ClassAssertion") {
        auto classExpr = parseClassExpression();
        skipWhitespace();
        auto individual = parseNamedIndividual();
        skipWhitespace();
        expect(')');
        
        return std::make_shared<ClassAssertion>(classExpr, individual, annotations);
    } else if (axiomType == "ObjectPropertyAssertion") {
        auto prop = parseObjectProperty();
        skipWhitespace();
        auto source = parseNamedIndividual();
        skipWhitespace();
        auto target = parseNamedIndividual();
        skipWhitespace();
        expect(')');
        
        return std::make_shared<ObjectPropertyAssertion>(prop, source, target, annotations);
    } else if (axiomType == "DataPropertyAssertion") {
        auto prop = parseDataProperty();
        skipWhitespace();
        auto source = parseNamedIndividual();
        skipWhitespace();
        auto value = parseLiteral();
        skipWhitespace();
        expect(')');
        
        return std::make_shared<DataPropertyAssertion>(prop, source, value, annotations);
    } else {
        // Skip other assertion axioms for now
        int depth = 1;
        while (!isAtEnd() && depth > 0) {
            if (match('(')) depth++;
            else if (match(')')) depth--;
            else advance();
        }
        return nullptr;
    }
}

std::shared_ptr<Axiom> FunctionalParser::Parser::parseAnnotationAxiom(const std::string& axiomType) {
    expect('(');
    skipWhitespace();
    
    // Parse optional annotations
    std::vector<Annotation> annotations = parseAnnotations();
    
    if (axiomType == "AnnotationAssertion") {
        auto prop = parseAnnotationProperty();
        skipWhitespace();
        std::string subject = readIRI();
        skipWhitespace();
        
        // Parse annotation value (IRI or literal)
        std::string value;
        if (peek() == '<') {
            value = readIRI();
        } else if (peek() == '"') {
            value = readQuotedString();
        } else {
            value = readToken();
        }
        
        skipWhitespace();
        expect(')');
        
        return std::make_shared<AnnotationAssertion>(prop, IRI(subject), value, annotations);
    } else {
        // Skip other annotation axioms for now
        int depth = 1;
        while (!isAtEnd() && depth > 0) {
            if (match('(')) depth++;
            else if (match(')')) depth--;
            else advance();
        }
        return nullptr;
    }
}

Class FunctionalParser::Parser::parseClass() {
    std::string iri = readIRI();
    return Class(IRI(iri));
}

ObjectProperty FunctionalParser::Parser::parseObjectProperty() {
    std::string iri = readIRI();
    return ObjectProperty(IRI(iri));
}

DataProperty FunctionalParser::Parser::parseDataProperty() {
    std::string iri = readIRI();
    return DataProperty(IRI(iri));
}

AnnotationProperty FunctionalParser::Parser::parseAnnotationProperty() {
    std::string iri = readIRI();
    return AnnotationProperty(IRI(iri));
}

NamedIndividual FunctionalParser::Parser::parseNamedIndividual() {
    std::string iri = readIRI();
    return NamedIndividual(IRI(iri));
}

Datatype FunctionalParser::Parser::parseDatatype() {
    std::string iri = readIRI();
    return Datatype(IRI(iri));
}

std::shared_ptr<ClassExpression> FunctionalParser::Parser::parseClassExpression() {
    skipWhitespace();
    
    if (match("ObjectSomeValuesFrom(")) {
        skipWhitespace();
        auto prop = parseObjectProperty();
        skipWhitespace();
        auto filler = parseClassExpression();
        skipWhitespace();
        expect(')');
        
        return std::make_shared<ObjectSomeValuesFrom>(prop, filler);
    } else if (match("ObjectAllValuesFrom(")) {
        skipWhitespace();
        auto prop = parseObjectProperty();
        skipWhitespace();
        auto filler = parseClassExpression();
        skipWhitespace();
        expect(')');
        
        return std::make_shared<ObjectAllValuesFrom>(prop, filler);
    } else if (match("ObjectIntersectionOf(")) {
        skipWhitespace();
        std::vector<std::shared_ptr<ClassExpression>> operands;
        while (peek() != ')') {
            operands.push_back(parseClassExpression());
            skipWhitespace();
        }
        expect(')');
        
        return std::make_shared<ObjectIntersectionOf>(operands);
    } else if (match("ObjectUnionOf(")) {
        skipWhitespace();
        std::vector<std::shared_ptr<ClassExpression>> operands;
        while (peek() != ')') {
            operands.push_back(parseClassExpression());
            skipWhitespace();
        }
        expect(')');
        
        return std::make_shared<ObjectUnionOf>(operands);
    } else {
        // Simple class
        auto cls = parseClass();
        return std::make_shared<NamedClass>(cls);
    }
}

std::shared_ptr<DataRange> FunctionalParser::Parser::parseDataRange() {
    skipWhitespace();
    
    // For now, just handle named datatypes
    auto datatype = parseDatatype();
    return std::make_shared<NamedDatatype>(datatype);
}

Literal FunctionalParser::Parser::parseLiteral() {
    skipWhitespace();
    
    std::string lexicalForm = readQuotedString();
    
    skipWhitespace();
    
    // Check for datatype or language tag
    if (match("^^")) {
        skipWhitespace();
        std::string datatypeIRI = readIRI();
        return Literal(lexicalForm, IRI(datatypeIRI));
    } else if (match('@')) {
        std::string langTag;
        while (!isAtEnd() && (isalnum(peek()) || peek() == '-')) {
            langTag += advance();
        }
        return Literal(lexicalForm, langTag);
    } else {
        return Literal(lexicalForm);
    }
}

std::vector<Annotation> FunctionalParser::Parser::parseAnnotations() {
    std::vector<Annotation> annotations;
    
    while (match("Annotation(")) {
        annotations.push_back(parseAnnotation());
        skipWhitespace();
    }
    
    return annotations;
}

Annotation FunctionalParser::Parser::parseAnnotation() {
    skipWhitespace();
    
    auto prop = parseAnnotationProperty();
    skipWhitespace();
    
    // Parse annotation value
    std::string value;
    if (peek() == '<') {
        value = readIRI();
    } else if (peek() == '"') {
        value = readQuotedString();
    } else {
        value = readToken();
    }
    
    skipWhitespace();
    expect(')');
    
    return Annotation(prop, value);
}

void FunctionalParser::Parser::expect(char c) {
    skipWhitespace();
    if (!match(c)) {
        std::ostringstream oss;
        oss << "Expected '" << c << "' but found '" << peek() << "'";
        error(oss.str());
    }
}

void FunctionalParser::Parser::expect(const std::string& keyword) {
    skipWhitespace();
    if (!match(keyword)) {
        error("Expected '" + keyword + "'");
    }
}

std::string FunctionalParser::Parser::expandIRI(const std::string& abbreviated) {
    size_t colon = abbreviated.find(':');
    if (colon == std::string::npos) {
        return abbreviated;
    }
    
    std::string prefix = abbreviated.substr(0, colon);
    std::string localName = abbreviated.substr(colon + 1);
    
    auto it = prefixes_.find(prefix);
    if (it != prefixes_.end()) {
        return it->second + localName;
    }
    
    return abbreviated;
}

void FunctionalParser::Parser::error(const std::string& message) {
    std::ostringstream oss;
    oss << "Parse error at line " << line_ << ", column " << col_ << ": " << message;
    throw FunctionalParseException(oss.str());
}

} // namespace owl2
} // namespace ista
