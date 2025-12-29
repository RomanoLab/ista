#ifndef ISTA_OWL2_MANCHESTER_PARSER_HPP
#define ISTA_OWL2_MANCHESTER_PARSER_HPP

#include "../core/ontology.hpp"
#include <string>
#include <stdexcept>

namespace ista {
namespace owl2 {

/**
 * @brief Exception thrown when Manchester Syntax parsing fails
 */
class ManchesterParseException : public std::runtime_error {
public:
    explicit ManchesterParseException(const std::string& message)
        : std::runtime_error(message) {}
};

/**
 * @brief Parser for OWL 2 Manchester Syntax
 * 
 * Parses ontologies from Manchester Syntax format, which is designed to be
 * more human-readable than other OWL syntaxes.
 * 
 * @note This is currently a stub implementation. Manchester Syntax parsing
 *       will be implemented in a future version.
 */
class ManchesterParser {
public:
    /**
     * @brief Parse Manchester Syntax from string
     * @param content Manchester Syntax content
     * @return Parsed ontology
     * @throws ManchesterParseException if parsing fails
     * @note Not yet implemented
     */
    static Ontology parseFromString(const std::string& content);
    
    /**
     * @brief Parse Manchester Syntax from file
     * @param filename Path to Manchester Syntax file
     * @return Parsed ontology
     * @throws ManchesterParseException if parsing fails
     * @note Not yet implemented
     */
    static Ontology parseFromFile(const std::string& filename);
};

} // namespace owl2
} // namespace ista

#endif // ISTA_OWL2_MANCHESTER_PARSER_HPP
