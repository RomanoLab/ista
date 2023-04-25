#ifndef IRI_HPP
#define IRI_HPP

#include <string>

struct IRI
{
    std::string fullIRI;
    std::string prefixName;
    std::string abbreviatedIRI;
    std::string baseIRI;
    
    IRI(std::string base_iri);
    
    IRI(std::string base_iri, std::string prefix_name);
};


#endif