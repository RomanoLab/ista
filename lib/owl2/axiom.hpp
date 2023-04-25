#ifndef AXIOM_HPP
#define AXIOM_HPP

#include <string>

#include "entity.hpp"

struct Axiom
{
    
    virtual std::string toFunctional() = 0;
};

struct Declaration : Axiom
{
    
};

struct ClassAxiom : Axiom
{

};

struct ObjectPropertyAxiom : Axiom
{

};

struct DataPropertyAxiom : Axiom
{

};

struct DatatypeDefinition : Axiom
{

};

struct HasKey : Axiom
{

};

struct Assertion : Axiom
{

};

struct AnnotationAxiom : Axiom
{

};

#endif