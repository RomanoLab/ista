#include "owl2.hpp"

ista::owl2::IRI::IRI(std::string base_iri)
{ 
    baseIRI = base_iri;
    fullIRI = "<" + base_iri + ">";
}

ista::owl2::IRI::IRI(std::string base_iri, std::string prefix_name)
{ 
    baseIRI = base_iri;
    fullIRI = "<" + base_iri + ">";
}