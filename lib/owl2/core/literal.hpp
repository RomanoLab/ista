#ifndef ISTA_OWL2_LITERAL_HPP
#define ISTA_OWL2_LITERAL_HPP

#include <string>
#include <optional>
#include "iri.hpp"

namespace ista {
namespace owl2 {

/**
 * @brief Represents an OWL2 literal value
 * 
 * Literals are data values with optional datatype and language tags.
 */
class Literal {
public:
    /**
     * @brief Construct a plain literal with optional language tag
     * @param lexical_form The string value
     * @param language_tag Optional language tag (e.g., "en", "de")
     */
    explicit Literal(const std::string& lexical_form, 
                    const std::optional<std::string>& language_tag = std::nullopt);
    
    /**
     * @brief Construct a typed literal
     * @param lexical_form The string value
     * @param datatype IRI of the datatype
     */
    Literal(const std::string& lexical_form, const IRI& datatype);
    
    /**
     * @brief Get the lexical form (string representation)
     */
    std::string getLexicalForm() const { return lexical_form_; }
    
    /**
     * @brief Get the datatype IRI
     */
    std::optional<IRI> getDatatype() const { return datatype_; }
    
    /**
     * @brief Get the language tag
     */
    std::optional<std::string> getLanguageTag() const { return language_tag_; }
    
    /**
     * @brief Check if this is a typed literal
     */
    bool isTyped() const { return datatype_.has_value(); }
    
    /**
     * @brief Check if this has a language tag
     */
    bool hasLanguageTag() const { return language_tag_.has_value(); }
    
    /**
     * @brief Convert to string representation
     */
    std::string toString() const;
    
    // Comparison operators
    bool operator==(const Literal& other) const;
    bool operator!=(const Literal& other) const { return !(*this == other); }
    bool operator<(const Literal& other) const { return lexical_form_ < other.lexical_form_; }

private:
    std::string lexical_form_;
    std::optional<IRI> datatype_;
    std::optional<std::string> language_tag_;
};

// Common XSD datatypes as constants
namespace xsd {
    const IRI STRING("http://www.w3.org/2001/XMLSchema#string");
    const IRI INTEGER("http://www.w3.org/2001/XMLSchema#integer");
    const IRI INT("http://www.w3.org/2001/XMLSchema#int");
    const IRI LONG("http://www.w3.org/2001/XMLSchema#long");
    const IRI DOUBLE("http://www.w3.org/2001/XMLSchema#double");
    const IRI FLOAT("http://www.w3.org/2001/XMLSchema#float");
    const IRI BOOLEAN("http://www.w3.org/2001/XMLSchema#boolean");
    const IRI DATE_TIME("http://www.w3.org/2001/XMLSchema#dateTime");
    const IRI DATE("http://www.w3.org/2001/XMLSchema#date");
}

} // namespace owl2
} // namespace ista

#endif // ISTA_OWL2_LITERAL_HPP
