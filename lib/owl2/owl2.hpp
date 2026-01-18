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
#include "serializer/manchester_serializer.hpp"
#include "serializer/owlxml_serializer.hpp"
#include "serializer/turtle_serializer.hpp"

// Parsers
#include "parser/rdfxml_parser.hpp"
#include "parser/functional_parser.hpp"
#include "parser/manchester_parser.hpp"
#include "parser/owlxml_parser.hpp"
#include "parser/turtle_parser.hpp"

// Data Loading
#include "loader/transform_engine.hpp"
#include "loader/yaml_parser.hpp"
#include "loader/mapping_spec.hpp"
#include "loader/data_loader.hpp"
#include "loader/database_reader.hpp"

// Optional database reader implementations
#ifdef ISTA_HAS_SQLITE
#include "loader/sqlite_reader.hpp"
#endif
#ifdef ISTA_HAS_MYSQL
#include "loader/mysql_reader.hpp"
#endif
#ifdef ISTA_HAS_POSTGRES
#include "loader/postgres_reader.hpp"
#endif

/**
 * @namespace ista::owl2
 * @brief OWL2 ontology manipulation library
 * 
 * This namespace contains all classes and functions for working with OWL2 ontologies.
 */

#endif // ISTA_OWL2_HPP
