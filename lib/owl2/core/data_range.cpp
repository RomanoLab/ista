#include "data_range.hpp"
#include <sstream>

namespace ista {
namespace owl2 {

std::string NamedDatatype::toFunctionalSyntax() const {
    return "<" + datatype_.getIRI().getFullIRI() + ">";
}

std::string DataIntersectionOf::toFunctionalSyntax() const {
    std::ostringstream oss;
    oss << "DataIntersectionOf(";
    
    for (size_t i = 0; i < operands_.size(); ++i) {
        if (i > 0) {
            oss << " ";
        }
        oss << operands_[i]->toFunctionalSyntax();
    }
    
    oss << ")";
    return oss.str();
}

std::string DataUnionOf::toFunctionalSyntax() const {
    std::ostringstream oss;
    oss << "DataUnionOf(";
    
    for (size_t i = 0; i < operands_.size(); ++i) {
        if (i > 0) {
            oss << " ";
        }
        oss << operands_[i]->toFunctionalSyntax();
    }
    
    oss << ")";
    return oss.str();
}

std::string DataComplementOf::toFunctionalSyntax() const {
    std::ostringstream oss;
    oss << "DataComplementOf(";
    oss << data_range_->toFunctionalSyntax();
    oss << ")";
    return oss.str();
}

std::string DataOneOf::toFunctionalSyntax() const {
    std::ostringstream oss;
    oss << "DataOneOf(";
    
    for (size_t i = 0; i < literals_.size(); ++i) {
        if (i > 0) {
            oss << " ";
        }
        oss << literals_[i].toString();
    }
    
    oss << ")";
    return oss.str();
}

std::string DatatypeRestriction::toFunctionalSyntax() const {
    std::ostringstream oss;
    oss << "DatatypeRestriction(";
    oss << "<" << datatype_.getIRI().getFullIRI() << ">";
    
    for (const auto& restriction : restrictions_) {
        oss << " <" << restriction.first.getFullIRI() << "> ";
        oss << restriction.second.toString();
    }
    
    oss << ")";
    return oss.str();
}

} // namespace owl2
} // namespace ista
