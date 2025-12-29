#ifndef ISTA_OWL2_FUNCTIONAL_PARSER_HPP
#define ISTA_OWL2_FUNCTIONAL_PARSER_HPP

#include "../core/ontology.hpp"
#include <string>
#include <vector>
#include <map>
#include <memory>
#include <stdexcept>

namespace ista {
namespace owl2 {

/**
 * @brief Exception thrown when Functional Syntax parsing fails
 */
class FunctionalParseException : public std::runtime_error {
public:
    explicit FunctionalParseException(const std::string& message)
        : std::runtime_error(message) {}
};

/**
 * @brief Parser for OWL 2 Functional Syntax
 * 
 * Parses ontologies from OWL 2 Functional Syntax format, which uses
 * a Lisp-like syntax with parentheses and keywords.
 * 
 * Supports:
 * - Ontology declarations
 * - Prefix declarations
 * - Import statements
 * - All OWL 2 axiom types
 * - Class expressions
 * - Data ranges
 * - Annotations
 */
class FunctionalParser {
public:
    /**
     * @brief Parse Functional Syntax from string
     * @param content Functional Syntax content
     * @return Parsed ontology
     * @throws FunctionalParseException if parsing fails
     */
    static Ontology parseFromString(const std::string& content);
    
    /**
     * @brief Parse Functional Syntax from file
     * @param filename Path to Functional Syntax file
     * @return Parsed ontology
     * @throws FunctionalParseException if parsing fails
     */
    static Ontology parseFromFile(const std::string& filename);

private:
    /**
     * @brief Internal parser implementation
     */
    class Parser {
    public:
        explicit Parser(const std::string& content);
        Ontology parse();

    private:
        std::string content_;
        size_t pos_;
        size_t line_;
        size_t col_;
        std::map<std::string, std::string> prefixes_;
        
        // Tokenization
        void skipWhitespace();
        void skipComment();
        bool isAtEnd() const;
        char peek() const;
        char advance();
        bool match(char expected);
        bool match(const std::string& expected);
        
        // Token reading
        std::string readToken();
        std::string readQuotedString();
        std::string readIRI();
        
        // High-level parsing
        void parseOntologyDocument();
        void parsePrefixDeclaration();
        void parseOntology(Ontology& ontology);
        
        // Axiom parsing
        std::shared_ptr<Axiom> parseAxiom();
        std::shared_ptr<Axiom> parseDeclaration();
        std::shared_ptr<Axiom> parseClassAxiom(const std::string& axiomType);
        std::shared_ptr<Axiom> parseObjectPropertyAxiom(const std::string& axiomType);
        std::shared_ptr<Axiom> parseDataPropertyAxiom(const std::string& axiomType);
        std::shared_ptr<Axiom> parseAssertionAxiom(const std::string& axiomType);
        std::shared_ptr<Axiom> parseAnnotationAxiom(const std::string& axiomType);
        
        // Entity parsing
        Class parseClass();
        ObjectProperty parseObjectProperty();
        DataProperty parseDataProperty();
        AnnotationProperty parseAnnotationProperty();
        NamedIndividual parseNamedIndividual();
        Datatype parseDatatype();
        
        // Expression parsing
        std::shared_ptr<ClassExpression> parseClassExpression();
        std::shared_ptr<DataRange> parseDataRange();
        Literal parseLiteral();
        
        // Annotation parsing
        std::vector<Annotation> parseAnnotations();
        Annotation parseAnnotation();
        
        // Utilities
        void expect(char c);
        void expect(const std::string& keyword);
        std::string expandIRI(const std::string& abbreviated);
        void error(const std::string& message);
        
        // Parser state
        Ontology* current_ontology_;
    };
};

} // namespace owl2
} // namespace ista

#endif // ISTA_OWL2_FUNCTIONAL_PARSER_HPP
