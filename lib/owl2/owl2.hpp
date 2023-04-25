#ifndef OWL2_HPP
#define OWL2_HPP

#include <string>
#include <unordered_set>

namespace ista
{

namespace owl2
{


struct IRI
{
    std::string fullIRI;
    std::string prefixName;
    std::string abbreviatedIRI;
    std::string baseIRI;
    
    IRI(std::string base_iri);
    
    IRI(std::string base_iri, std::string prefix_name);
};


struct Axiom
{

};


struct Annotation
{

};


class Ontology
{   
public:
    Ontology(IRI ontology_iri, IRI version_iri);

    IRI ontology_iri;
    IRI version_iri;
private:
    std::unordered_set* axioms;
};


}

}

#endif