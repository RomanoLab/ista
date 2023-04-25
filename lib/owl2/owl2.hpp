#ifndef OWL2_HPP
#define OWL2_HPP

#include <string>
#include <unordered_set>
#include <ostream>

#include "iri.hpp"
#include "axiom.hpp"


namespace ista
{

namespace owl2
{


struct Entity
{
    IRI entityIRI;

    Entity() = default;
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
    std::unordered_set<Axiom>* axioms;
};


}

}

#endif