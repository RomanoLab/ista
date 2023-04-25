#ifndef ENTITY_HPP
#define ENTITY_HPP

#include "iri.hpp"


struct Entity
{
    
};

struct Class : Entity
{
    IRI iri;
};


struct Datatype : Entity
{
    IRI iri;
};


struct ObjectProperty : Entity
{
    IRI iri;
};


struct DataProperty : Entity
{
    IRI iri;
};


struct AnnotationProperty
{
    IRI iri;
};


struct Individual
{

};


struct NamedInvidual : Individual, Entity
{

};

struct AnonymousIndividual : Individual
{

};

#endif