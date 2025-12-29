#include "manchester_parser.hpp"
#include <fstream>
#include <sstream>

namespace ista {
namespace owl2 {

Ontology ManchesterParser::parseFromString(const std::string& content) {
    // TODO: Implement Manchester Syntax parser
    throw ManchesterParseException(
        "Manchester Syntax parser is not yet implemented. "
        "This feature is planned for a future release."
    );
}

Ontology ManchesterParser::parseFromFile(const std::string& filename) {
    std::ifstream file(filename);
    if (!file.is_open()) {
        throw ManchesterParseException("Could not open file: " + filename);
    }
    
    std::stringstream buffer;
    buffer << file.rdbuf();
    return parseFromString(buffer.str());
}

} // namespace owl2
} // namespace ista
