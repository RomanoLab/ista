#ifndef ASSERTION_HPP
#define ASSERTION_HPP

#include "entity.hpp"


struct Assertion
{

};

struct SameIndividual : Assertion
{

};

struct DifferentIndividuals : Assertion
{

};

struct ClassAssertion : Assertion
{

};

struct ObjectPropertyAssertion : Assertion
{

};

struct NegativeObjectPropertyAssertion : Assertion
{

};

struct DataPropertyAssertion : Assertion
{

};

struct NegativeDataPropertyAssertion : Assertion
{

};

#endif