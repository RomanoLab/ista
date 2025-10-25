#include "functional_serializer.hpp"
#include <sstream>

namespace ista {
namespace owl2 {

std::string FunctionalSyntaxSerializer::serialize(const Ontology& ontology) {
    return ontology.toFunctionalSyntax();
}

std::string FunctionalSyntaxSerializer::serialize(const Ontology& ontology, const std::string& indent) {
    return ontology.toFunctionalSyntax(indent);
}

bool FunctionalSyntaxSerializer::serializeToFile(const Ontology& ontology, const std::string& filename) {
    try {
        std::ofstream file(filename);
        if (!file.is_open()) {
            return false;
        }
        
        std::string content = serialize(ontology);
        file << content;
        file.close();
        
        return true;
    } catch (const std::exception& e) {
        return false;
    }
}

} // namespace owl2
} // namespace ista
