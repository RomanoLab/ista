#ifndef ISTA_OWL2_HPP
#define ISTA_OWL2_HPP

/**
 * @file owl2.hpp
 * @brief Main header for the ISTA OWL2 library
 * 
 * Include this header to access all OWL2 functionality.
 */

// Core OWL2 structures
#include "core/iri.hpp"
#include "core/entity.hpp"
#include "core/literal.hpp"
#include "core/data_range.hpp"
#include "core/class_expression.hpp"
#include "core/annotation.hpp"
#include "core/axiom.hpp"
#include "core/ontology.hpp"

// Serializers
#include "serializer/functional_serializer.hpp"
#include "serializer/rdfxml_serializer.hpp"

// Parsers
#include "parser/rdfxml_parser.hpp"

/**
 * @namespace ista::owl2
 * @brief OWL2 ontology manipulation library
 * 
 * This namespace contains all classes and functions for working with OWL2 ontologies.
 */

#endif // ISTA_OWL2_HPP
