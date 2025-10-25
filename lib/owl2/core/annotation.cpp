#include "annotation.hpp"
#include <sstream>

namespace ista {
namespace owl2 {

std::string Annotation::toFunctionalSyntax() const {
    std::ostringstream oss;
    oss << "Annotation(";
    
    // Add nested annotations if present
    if (!annotations_.empty()) {
        for (const auto& ann : annotations_) {
            oss << ann.toFunctionalSyntax() << " ";
        }
    }
    
    // Add the annotation property
    oss << "<" << property_.getIRI().getFullIRI() << "> ";
    
    // Add the annotation value
    oss << getValueAsString();
    
    oss << ")";
    return oss.str();
}

std::string Annotation::getValueAsString() const {
    return std::visit([](auto&& arg) -> std::string {
        using T = std::decay_t<decltype(arg)>;
        if constexpr (std::is_same_v<T, IRI>) {
            return "<" + arg.getFullIRI() + ">";
        } else if constexpr (std::is_same_v<T, Literal>) {
            return arg.toString();
        } else if constexpr (std::is_same_v<T, AnonymousIndividual>) {
            return "_:" + arg.getNodeID();
        }
    }, value_);
}

bool Annotation::operator==(const Annotation& other) const {
    if (property_ != other.property_) {
        return false;
    }
    
    // Compare values
    if (value_.index() != other.value_.index()) {
        return false;
    }
    
    bool values_equal = std::visit([](auto&& arg1, auto&& arg2) -> bool {
        using T1 = std::decay_t<decltype(arg1)>;
        using T2 = std::decay_t<decltype(arg2)>;
        if constexpr (std::is_same_v<T1, T2>) {
            return arg1 == arg2;
        } else {
            return false;
        }
    }, value_, other.value_);
    
    if (!values_equal) {
        return false;
    }
    
    // Compare nested annotations
    if (annotations_.size() != other.annotations_.size()) {
        return false;
    }
    
    for (size_t i = 0; i < annotations_.size(); ++i) {
        if (annotations_[i] != other.annotations_[i]) {
            return false;
        }
    }
    
    return true;
}

} // namespace owl2
} // namespace ista
