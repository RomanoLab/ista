#ifndef ENTITY_HPP
#define ENTITY_HPP

#include "iri.hpp"


struct Entity
{
    IRI iri;
};

struct Class : Entity
{
    
};


struct Datatype : Entity
{
    
};


struct ObjectProperty : Entity
{
    
};


struct DataProperty : Entity
{
    
};


struct AnnotationProperty
{
    
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