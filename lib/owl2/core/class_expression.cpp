#include "class_expression.hpp"
#include <sstream>

namespace ista {
namespace owl2 {

std::string NamedClass::toFunctionalSyntax() const {
    return "<" + class_.getIRI().getFullIRI() + ">";
}

std::string ObjectIntersectionOf::toFunctionalSyntax() const {
    std::ostringstream oss;
    oss << "ObjectIntersectionOf(";
    
    for (size_t i = 0; i < operands_.size(); ++i) {
        if (i > 0) {
            oss << " ";
        }
        oss << operands_[i]->toFunctionalSyntax();
    }
    
    oss << ")";
    return oss.str();
}

std::string ObjectUnionOf::toFunctionalSyntax() const {
    std::ostringstream oss;
    oss << "ObjectUnionOf(";
    
    for (size_t i = 0; i < operands_.size(); ++i) {
        if (i > 0) {
            oss << " ";
        }
        oss << operands_[i]->toFunctionalSyntax();
    }
    
    oss << ")";
    return oss.str();
}

std::string ObjectSomeValuesFrom::toFunctionalSyntax() const {
    std::ostringstream oss;
    oss << "ObjectSomeValuesFrom(";
    oss << "<" << property_.getIRI().getFullIRI() << "> ";
    oss << filler_->toFunctionalSyntax();
    oss << ")";
    return oss.str();
}

std::string ObjectAllValuesFrom::toFunctionalSyntax() const {
    std::ostringstream oss;
    oss << "ObjectAllValuesFrom(";
    oss << "<" << property_.getIRI().getFullIRI() << "> ";
    oss << filler_->toFunctionalSyntax();
    oss << ")";
    return oss.str();
}

} // namespace owl2
} // namespace ista
