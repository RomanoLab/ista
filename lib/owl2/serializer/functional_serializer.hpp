#ifndef ISTA_OWL2_FUNCTIONAL_SERIALIZER_HPP
#define ISTA_OWL2_FUNCTIONAL_SERIALIZER_HPP

#include "../core/ontology.hpp"
#include <string>
#include <fstream>

namespace ista {
namespace owl2 {

/**
 * @brief Serializer for OWL2 Functional Syntax
 * 
 * Writes ontologies to OWL2 Functional Syntax format.
 */
class FunctionalSyntaxSerializer {
public:
    /**
     * @brief Serialize ontology to string
     * @param ontology The ontology to serialize
     * @return String containing OWL2 Functional Syntax
     */
    static std::string serialize(const Ontology& ontology);
    
    /**
     * @brief Serialize ontology to file
     * @param ontology The ontology to serialize
     * @param filename Output file path
     * @return true if successful, false otherwise
     */
    static bool serializeToFile(const Ontology& ontology, const std::string& filename);
    
    /**
     * @brief Serialize with custom indentation
     * @param ontology The ontology to serialize
     * @param indent Indentation string (e.g., "  " or "	")
     * @return String containing OWL2 Functional Syntax
     */
    static std::string serialize(const Ontology& ontology, const std::string& indent);
};

} // namespace owl2
} // namespace ista

#endif // ISTA_OWL2_FUNCTIONAL_SERIALIZER_HPP
