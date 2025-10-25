#include "iri.hpp"
#include <algorithm>

namespace ista {
namespace owl2 {

IRI::IRI(const std::string& iri_string) 
    : full_iri_(iri_string) {
    // Try to extract namespace and local name
    // Look for common separators: # or the last /
    size_t hash_pos = iri_string.find_last_of('#');
    size_t slash_pos = iri_string.find_last_of('/');
    
    size_t separator_pos = std::string::npos;
    if (hash_pos != std::string::npos) {
        separator_pos = hash_pos;
    } else if (slash_pos != std::string::npos) {
        separator_pos = slash_pos;
    }
    
    if (separator_pos != std::string::npos && separator_pos < iri_string.length() - 1) {
        namespace_uri_ = iri_string.substr(0, separator_pos + 1);
        local_name_ = iri_string.substr(separator_pos + 1);
    } else {
        namespace_uri_ = iri_string;
    }
}

IRI::IRI(const std::string& prefix, const std::string& local_name, const std::string& namespace_uri)
    : prefix_(prefix),
      local_name_(local_name),
      namespace_uri_(namespace_uri) {
    full_iri_ = namespace_uri + local_name;
}

std::string IRI::getAbbreviated() const {
    if (prefix_.has_value() && local_name_.has_value()) {
        return prefix_.value() + ":" + local_name_.value();
    }
    return full_iri_;
}

} // namespace owl2
} // namespace ista
