#include "literal.hpp"

namespace ista {
namespace owl2 {

Literal::Literal(const std::string& lexical_form, 
                 const std::optional<std::string>& language_tag)
    : lexical_form_(lexical_form),
      language_tag_(language_tag) {
}

Literal::Literal(const std::string& lexical_form, const IRI& datatype)
    : lexical_form_(lexical_form),
      datatype_(datatype) {
}

std::string Literal::toString() const {
    std::string result = "\"" + lexical_form_ + "\"";
    
    if (language_tag_.has_value()) {
        result += "@" + language_tag_.value();
    } else if (datatype_.has_value()) {
        result += "^^" + datatype_.value().getFullIRI();
    }
    
    return result;
}

bool Literal::operator==(const Literal& other) const {
    if (lexical_form_ != other.lexical_form_) {
        return false;
    }
    
    if (language_tag_.has_value() != other.language_tag_.has_value()) {
        return false;
    }
    if (language_tag_.has_value() && language_tag_.value() != other.language_tag_.value()) {
        return false;
    }
    
    if (datatype_.has_value() != other.datatype_.has_value()) {
        return false;
    }
    if (datatype_.has_value() && datatype_.value() != other.datatype_.value()) {
        return false;
    }
    
    return true;
}

} // namespace owl2
} // namespace ista
