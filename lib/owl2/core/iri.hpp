#ifndef ISTA_OWL2_IRI_HPP
#define ISTA_OWL2_IRI_HPP

#include <string>
#include <unordered_map>
#include <optional>

namespace ista {
namespace owl2 {

/**
 * @brief Internationalized Resource Identifier (IRI)
 * 
 * Represents IRIs used throughout OWL2 ontologies. Supports both full and abbreviated forms.
 */
class IRI {
public:
    /**
     * @brief Construct IRI from full IRI string
     * @param iri_string Full IRI (e.g., "http://example.org/ontology#Class1")
     */
    explicit IRI(const std::string& iri_string);
    
    /**
     * @brief Construct IRI from prefix and local name
     * @param prefix Namespace prefix (e.g., "ex")
     * @param local_name Local name within namespace (e.g., "Class1")
     * @param namespace_uri Full namespace URI (e.g., "http://example.org/ontology#")
     */
    IRI(const std::string& prefix, const std::string& local_name, const std::string& namespace_uri);
    
    /**
     * @brief Get the full IRI string
     * @return Full IRI
     */
    std::string getFullIRI() const { return full_iri_; }
    
    /**
     * @brief Get the namespace prefix (if available)
     * @return Optional prefix
     */
    std::optional<std::string> getPrefix() const { return prefix_; }
    
    /**
     * @brief Get the local name (if available)
     * @return Optional local name
     */
    std::optional<std::string> getLocalName() const { return local_name_; }
    
    /**
     * @brief Get the namespace URI
     * @return Namespace URI
     */
    std::string getNamespace() const { return namespace_uri_; }
    
    /**
     * @brief Get abbreviated form (prefix:localName) if available
     * @return Abbreviated IRI or full IRI if no abbreviation exists
     */
    std::string getAbbreviated() const;
    
    /**
     * @brief Check if this IRI is abbreviated
     */
    bool isAbbreviated() const { return prefix_.has_value() && local_name_.has_value(); }
    
    // Comparison operators
    bool operator==(const IRI& other) const { return full_iri_ == other.full_iri_; }
    bool operator!=(const IRI& other) const { return full_iri_ != other.full_iri_; }
    bool operator<(const IRI& other) const { return full_iri_ < other.full_iri_; }
    
    /**
     * @brief Convert to string (returns full IRI)
     */
    std::string toString() const { return full_iri_; }

private:
    std::string full_iri_;
    std::string namespace_uri_;
    std::optional<std::string> prefix_;
    std::optional<std::string> local_name_;
};

} // namespace owl2
} // namespace ista

// Hash function for IRI to use in unordered containers
namespace std {
    template<>
    struct hash<ista::owl2::IRI> {
        size_t operator()(const ista::owl2::IRI& iri) const {
            return hash<string>()(iri.getFullIRI());
        }
    };
}

#endif // ISTA_OWL2_IRI_HPP
