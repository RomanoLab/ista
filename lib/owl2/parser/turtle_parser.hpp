#ifndef ISTA_OWL2_TURTLE_PARSER_HPP
#define ISTA_OWL2_TURTLE_PARSER_HPP

#include "../core/ontology.hpp"
#include <string>
#include <map>
#include <vector>
#include <stdexcept>

namespace ista {
namespace owl2 {

/**
 * @brief Exception thrown when Turtle parsing fails
 */
class TurtleParseException : public std::runtime_error {
public:
    explicit TurtleParseException(const std::string& message)
        : std::runtime_error(message) {}
};

/**
 * @brief Parser for Turtle (Terse RDF Triple Language) format
 * 
 * Parses ontologies from Turtle format, which is a compact, human-readable
 * RDF serialization.
 * 
 * @par Implementation Status
 * **BASIC IMPLEMENTATION COMPLETE** - Handles common Turtle patterns (~80% coverage).
 * 
 * **Fully Implemented:**
 * - @prefix and @base directives
 * - IRI references in angle brackets <...>
 * - Prefixed names (prefix:local)
 * - Literals (plain, typed with ^^, language-tagged with @)
 * - Basic escape sequences in strings (\\t \\n \\r \\" \\\\)
 * - Blank nodes (_:id)
 * - Comments (#)
 * - Numeric literals (integers and decimals)
 * - 'a' shortcut for rdf:type
 * - Simple triples (subject predicate object .)
 * - RDF-to-OWL conversion for common axioms:
 *   - Declarations (owl:Class, owl:ObjectProperty, etc.)
 *   - Class assertions (individual rdf:type Class)
 *   - Object/Data property assertions
 *   - SubClassOf, SubPropertyOf
 *   - Property domain/range
 * 
 * **Not Yet Implemented (see BREADCRUMB comments in code):**
 * - Subject-predicate grouping with semicolons (;)
 * - Object lists with commas (,)
 * - RDF collections with parentheses ()
 * - Blank node property lists with brackets []
 * - Triple-quoted strings (""")
 * - Unicode escape sequences (\\u \\U)
 * - IRI escape sequences
 * - Scientific notation for numbers
 * - Complex OWL constructs (restrictions, unions, intersections)
 * - Blank node patterns for complex axioms
 * 
 * **Current Limitations:**
 * - Each triple must end with '.' (no grouping)
 * - Blank nodes in complex patterns are skipped
 * - Some malformed triples are silently ignored
 * - Limited OWL axiom reconstruction from RDF triples
 * 
 * Despite limitations, the parser successfully handles Turtle files generated
 * by TurtleSerializer and many standard Turtle ontologies.
 * 
 * @see https://www.w3.org/TR/turtle/
 */
class TurtleParser {
public:
    /**
     * @brief Parse Turtle from string
     * @param content Turtle content
     * @return Parsed ontology
     * @throws TurtleParseException if parsing fails
     */
    static Ontology parseFromString(const std::string& content);
    
    /**
     * @brief Parse Turtle from file
     * @param filename Path to Turtle file
     * @return Parsed ontology
     * @throws TurtleParseException if parsing fails
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
        std::string base_uri_;
        
        // Tokenization
        void skipWhitespace();
        void skipComment();
        bool isAtEnd() const;
        char peek() const;
        char advance();
        bool match(char expected);
        bool match(const std::string& expected);
        
        // Parsing directives
        void parseDirective();
        void parsePrefixDirective();
        void parseBaseDirective();
        
        // Parsing triples
        struct Triple {
            std::string subject;
            std::string predicate;
            std::string object;
            bool object_is_literal;
            std::string literal_datatype;
            std::string literal_language;
        };
        
        std::vector<Triple> parseTriples();
        std::string parseSubject();
        std::string parsePredicate();
        void parseObject(std::vector<Triple>& triples, const std::string& subject, 
                        const std::string& predicate);
        
        // Parsing terms
        std::string parseIRIRef();
        std::string parsePrefixedName();
        std::string parseBlankNode();
        std::string parseLiteral(std::string& datatype, std::string& language);
        std::string parseCollection();
        std::string parseBlankNodePropertyList();
        
        // Utilities
        std::string resolveIRI(const std::string& iri);
        std::string expandPrefix(const std::string& prefixed);
        bool isNameStartChar(char c) const;
        bool isNameChar(char c) const;
        void error(const std::string& message);
        
        // Convert RDF triples to OWL ontology
        Ontology triplesToOntology(const std::vector<Triple>& triples);
    };
};

} // namespace owl2
} // namespace ista

#endif // ISTA_OWL2_TURTLE_PARSER_HPP
