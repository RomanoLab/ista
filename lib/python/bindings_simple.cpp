/**
 * @file bindings_simple.cpp
 * @brief Simplified Pybind11 bindings for the libista OWL2 library
 * 
 * This module exposes core OWL2 functionality to Python without variant types.
 * It provides a simpler, more accessible API for basic ontology manipulation.
 */

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/operators.h>
#include <pybind11/functional.h>

#include "../owl2/owl2.hpp"
#include "../owl2/parser/rdfxml_parser.hpp"
#include "../owl2/parser/csv_parser.hpp"
#include "../owl2/parser/turtle_parser.hpp"
#include "../owl2/parser/functional_parser.hpp"
#include "../owl2/parser/manchester_parser.hpp"
#include "../owl2/parser/owlxml_parser.hpp"
#include "../owl2/serializer/turtle_serializer.hpp"
#include "../owl2/serializer/manchester_serializer.hpp"
#include "../owl2/serializer/owlxml_serializer.hpp"
#include "../owl2/core/ontology_filter.hpp"

namespace py = pybind11;
using namespace ista::owl2;

PYBIND11_MODULE(_libista_owl2, m) {
    m.doc() = "Simplified Python bindings for the libista OWL2 library";

    // ========================================================================
    // IRI Class
    // ========================================================================
    py::class_<IRI>(m, "IRI", "Internationalized Resource Identifier")
        .def(py::init<const std::string&>(),
             py::arg("iri_string"),
             "Construct IRI from full IRI string")
        .def(py::init<const std::string&, const std::string&, const std::string&>(),
             py::arg("prefix"),
             py::arg("local_name"),
             py::arg("namespace_uri"),
             "Construct IRI from prefix, local name, and namespace URI")
        .def("get_full_iri", &IRI::getFullIRI,
             "Get the full IRI string")
        .def("get_prefix", &IRI::getPrefix,
             "Get the namespace prefix (if available)")
        .def("get_local_name", &IRI::getLocalName,
             "Get the local name (if available)")
        .def("get_namespace", &IRI::getNamespace,
             "Get the namespace URI")
        .def("get_abbreviated", &IRI::getAbbreviated,
             "Get abbreviated form (prefix:localName) if available")
        .def("is_abbreviated", &IRI::isAbbreviated,
             "Check if this IRI is abbreviated")
        .def("to_string", &IRI::toString,
             "Convert to string (returns full IRI)")
        .def("__str__", &IRI::toString)
        .def("__repr__", [](const IRI& iri) {
            return "<IRI '" + iri.toString() + "'>";
        })
        .def(py::self == py::self)
        .def(py::self != py::self)
        .def(py::self < py::self)
        .def("__hash__", [](const IRI& iri) {
            return std::hash<IRI>()(iri);
        });

    // ========================================================================
    // Entity Classes
    // ========================================================================
    py::class_<Entity, std::shared_ptr<Entity>>(m, "Entity", "Base class for all OWL2 entities")
        .def("get_iri", &Entity::getIRI,
             "Get the IRI of this entity")
        .def("get_entity_type", &Entity::getEntityType,
             "Get the type of this entity")
        .def(py::self == py::self)
        .def(py::self != py::self)
        .def(py::self < py::self);

    py::class_<Class, Entity, std::shared_ptr<Class>>(m, "Class", "OWL2 Class")
        .def(py::init<const IRI&>(),
             py::arg("iri"),
             "Construct a Class with the given IRI")
        .def("__repr__", [](const Class& cls) {
            return "<Class '" + cls.getIRI().toString() + "'>";
        });

    py::class_<ObjectProperty, Entity, std::shared_ptr<ObjectProperty>>(m, "ObjectProperty", "OWL2 Object Property")
        .def(py::init<const IRI&>(),
             py::arg("iri"),
             "Construct an ObjectProperty with the given IRI")
        .def("__repr__", [](const ObjectProperty& op) {
            return "<ObjectProperty '" + op.getIRI().toString() + "'>";
        });

    py::class_<DataProperty, Entity, std::shared_ptr<DataProperty>>(m, "DataProperty", "OWL2 Data Property")
        .def(py::init<const IRI&>(),
             py::arg("iri"),
             "Construct a DataProperty with the given IRI")
        .def("__repr__", [](const DataProperty& dp) {
            return "<DataProperty '" + dp.getIRI().toString() + "'>";
        });

    py::class_<NamedIndividual, Entity, std::shared_ptr<NamedIndividual>>(m, "NamedIndividual", "OWL2 Named Individual")
        .def(py::init<const IRI&>(),
             py::arg("iri"),
             "Construct a NamedIndividual with the given IRI")
        .def("__repr__", [](const NamedIndividual& ni) {
            return "<NamedIndividual '" + ni.getIRI().toString() + "'>";
        })
        .def("__hash__", [](const NamedIndividual& ni) {
            return std::hash<IRI>()(ni.getIRI());
        });

    // ========================================================================
    // Literal Class
    // ========================================================================
    py::class_<Literal>(m, "Literal", "OWL2 Literal value")
        .def(py::init<const std::string&, const std::optional<std::string>&>(),
             py::arg("lexical_form"),
             py::arg("language_tag") = std::nullopt,
             "Construct a plain literal with optional language tag")
        .def(py::init<const std::string&, const IRI&>(),
             py::arg("lexical_form"),
             py::arg("datatype"),
             "Construct a typed literal")
        .def("get_lexical_form", &Literal::getLexicalForm,
             "Get the lexical form (string representation)")
        .def("get_datatype", &Literal::getDatatype,
             "Get the datatype IRI")
        .def("get_language_tag", &Literal::getLanguageTag,
             "Get the language tag")
        .def("is_typed", &Literal::isTyped,
             "Check if this is a typed literal")
        .def("has_language_tag", &Literal::hasLanguageTag,
             "Check if this has a language tag")
        .def("to_string", &Literal::toString,
             "Convert to string representation")
        .def("__str__", &Literal::toString)
        .def("__repr__", [](const Literal& lit) {
            return "<Literal '" + lit.toString() + "'>";
        })
        .def(py::self == py::self)
        .def(py::self != py::self)
        .def(py::self < py::self);

    // XSD datatypes namespace
    auto xsd = m.def_submodule("xsd", "XSD datatype constants");
    xsd.attr("STRING") = xsd::STRING;
    xsd.attr("INTEGER") = xsd::INTEGER;
    xsd.attr("INT") = xsd::INT;
    xsd.attr("LONG") = xsd::LONG;
    xsd.attr("DOUBLE") = xsd::DOUBLE;
    xsd.attr("FLOAT") = xsd::FLOAT;
    xsd.attr("BOOLEAN") = xsd::BOOLEAN;
    xsd.attr("DATE_TIME") = xsd::DATE_TIME;
    xsd.attr("DATE") = xsd::DATE;

    // ========================================================================
    // Class Expression Classes
    // ========================================================================
    py::class_<ClassExpression, std::shared_ptr<ClassExpression>>(m, "ClassExpression", "Base class for all OWL2 class expressions")
        .def("to_functional_syntax", &ClassExpression::toFunctionalSyntax,
             "Convert to OWL2 Functional Syntax")
        .def("get_expression_type", &ClassExpression::getExpressionType,
             "Get the type of this class expression");

    py::class_<NamedClass, ClassExpression, std::shared_ptr<NamedClass>>(m, "NamedClass", "Named class expression")
        .def(py::init<const Class&>(),
             py::arg("cls"),
             "Construct a NamedClass")
        .def("get_class", &NamedClass::getClass,
             "Get the class");

    // ========================================================================
    // Axiom Classes
    // ========================================================================
    py::class_<Axiom, std::shared_ptr<Axiom>>(m, "Axiom", "Base class for all OWL2 axioms")
        .def("to_functional_syntax", &Axiom::toFunctionalSyntax,
             "Convert to OWL2 Functional Syntax")
        .def("get_axiom_type", &Axiom::getAxiomType,
             "Get the type of this axiom");

    // Declaration Axiom
    py::enum_<Declaration::EntityType>(m, "EntityType", "Entity type for declaration axioms")
        .value("CLASS", Declaration::EntityType::CLASS)
        .value("DATATYPE", Declaration::EntityType::DATATYPE)
        .value("OBJECT_PROPERTY", Declaration::EntityType::OBJECT_PROPERTY)
        .value("DATA_PROPERTY", Declaration::EntityType::DATA_PROPERTY)
        .value("ANNOTATION_PROPERTY", Declaration::EntityType::ANNOTATION_PROPERTY)
        .value("NAMED_INDIVIDUAL", Declaration::EntityType::NAMED_INDIVIDUAL)
        .export_values();

    py::class_<Declaration, Axiom, std::shared_ptr<Declaration>>(m, "Declaration", "Declaration axiom")
        .def(py::init<Declaration::EntityType, const IRI&>(),
             py::arg("entity_type"),
             py::arg("iri"),
             "Construct a Declaration axiom")
        .def("get_entity_type", &Declaration::getEntityType,
             "Get the entity type")
        .def("get_iri", &Declaration::getIRI,
             "Get the IRI");

    // SubClassOf Axiom
    py::class_<SubClassOf, Axiom, std::shared_ptr<SubClassOf>>(m, "SubClassOf", "SubClassOf axiom")
        .def(py::init<const ClassExpressionPtr&, const ClassExpressionPtr&>(),
             py::arg("subclass"),
             py::arg("superclass"),
             "Construct a SubClassOf axiom")
        .def("get_sub_class", &SubClassOf::getSubClass,
             "Get the subclass")
        .def("get_super_class", &SubClassOf::getSuperClass,
             "Get the superclass");

    // ClassAssertion Axiom - using lambda to accept NamedIndividual directly
    py::class_<ClassAssertion, Axiom, std::shared_ptr<ClassAssertion>>(m, "ClassAssertion", "ClassAssertion axiom")
        .def(py::init([](const Class& cls, const NamedIndividual& individual) {
                 return std::make_shared<ClassAssertion>(
                     std::make_shared<NamedClass>(cls), 
                     Individual(individual));
             }),
             py::arg("cls"),
             py::arg("individual"),
             "Construct a ClassAssertion axiom with a Class and NamedIndividual")
        .def("get_class_expression", &ClassAssertion::getClassExpression,
             "Get the class expression");
        // Note: getIndividual() returns variant, so we skip it

    // ObjectPropertyDomain Axiom - using lambda to accept ObjectProperty directly
    py::class_<ObjectPropertyDomain, Axiom, std::shared_ptr<ObjectPropertyDomain>>(m, "ObjectPropertyDomain", "ObjectPropertyDomain axiom")
        .def(py::init([](const ObjectProperty& property, const ClassExpressionPtr& domain) {
                 return std::make_shared<ObjectPropertyDomain>(ObjectPropertyExpression(property), domain);
             }),
             py::arg("property"),
             py::arg("domain"),
             "Construct an ObjectPropertyDomain axiom")
        .def("get_domain", &ObjectPropertyDomain::getDomain,
             "Get the domain");
        // Note: getProperty() returns variant, so we skip it

    // ObjectPropertyRange Axiom - using lambda to accept ObjectProperty directly
    py::class_<ObjectPropertyRange, Axiom, std::shared_ptr<ObjectPropertyRange>>(m, "ObjectPropertyRange", "ObjectPropertyRange axiom")
        .def(py::init([](const ObjectProperty& property, const ClassExpressionPtr& range) {
                 return std::make_shared<ObjectPropertyRange>(ObjectPropertyExpression(property), range);
             }),
             py::arg("property"),
             py::arg("range"),
             "Construct an ObjectPropertyRange axiom")
        .def("get_range", &ObjectPropertyRange::getRange,
             "Get the range");
        // Note: getProperty() returns variant, so we skip it

    // DataPropertyDomain Axiom
    py::class_<DataPropertyDomain, Axiom, std::shared_ptr<DataPropertyDomain>>(m, "DataPropertyDomain", "DataPropertyDomain axiom")
        .def(py::init<const DataProperty&, const ClassExpressionPtr&>(),
             py::arg("property"),
             py::arg("domain"),
             "Construct a DataPropertyDomain axiom")
        .def("get_property", &DataPropertyDomain::getProperty,
             "Get the property")
        .def("get_domain", &DataPropertyDomain::getDomain,
             "Get the domain");

    // DataPropertyRange Axiom - simplified to skip DataRange for now
    py::class_<DataPropertyRange, Axiom, std::shared_ptr<DataPropertyRange>>(m, "DataPropertyRange", "DataPropertyRange axiom");
        // Note: Constructor requires DataRangePtr which is complex, so we skip it for now

    // FunctionalObjectProperty Axiom - using lambda to accept ObjectProperty directly
    py::class_<FunctionalObjectProperty, Axiom, std::shared_ptr<FunctionalObjectProperty>>(m, "FunctionalObjectProperty", "FunctionalObjectProperty axiom")
        .def(py::init([](const ObjectProperty& property) {
                 return std::make_shared<FunctionalObjectProperty>(ObjectPropertyExpression(property));
             }),
             py::arg("property"),
             "Construct a FunctionalObjectProperty axiom");
        // Note: getProperty() returns variant, so we skip it

    // FunctionalDataProperty Axiom
    py::class_<FunctionalDataProperty, Axiom, std::shared_ptr<FunctionalDataProperty>>(m, "FunctionalDataProperty", "FunctionalDataProperty axiom")
        .def(py::init<const DataProperty&>(),
             py::arg("property"),
             "Construct a FunctionalDataProperty axiom")
        .def("get_property", &FunctionalDataProperty::getProperty,
             "Get the property");

    // ObjectPropertyAssertion - using lambda to accept NamedIndividual directly
    py::class_<ObjectPropertyAssertion, Axiom, std::shared_ptr<ObjectPropertyAssertion>>(m, "ObjectPropertyAssertion", "ObjectPropertyAssertion axiom")
        .def(py::init([](const ObjectProperty& property, const NamedIndividual& source, const NamedIndividual& target) {
                 return std::make_shared<ObjectPropertyAssertion>(
                     ObjectPropertyExpression(property),
                     Individual(source),
                     Individual(target));
             }),
             py::arg("property"),
             py::arg("source"),
             py::arg("target"),
             "Construct an ObjectPropertyAssertion axiom");

    // DataPropertyAssertion - using lambda to accept NamedIndividual directly
    py::class_<DataPropertyAssertion, Axiom, std::shared_ptr<DataPropertyAssertion>>(m, "DataPropertyAssertion", "DataPropertyAssertion axiom")
        .def(py::init([](const DataProperty& property, const NamedIndividual& source, const Literal& value) {
                 return std::make_shared<DataPropertyAssertion>(
                     property,
                     Individual(source),
                     value);
             }),
             py::arg("property"),
             py::arg("source"),
             py::arg("value"),
             "Construct a DataPropertyAssertion axiom");

    // ========================================================================
    // Ontology Class
    // ========================================================================
    py::class_<Ontology, std::shared_ptr<Ontology>>(m, "Ontology", "OWL2 Ontology")
        .def(py::init<>(),
             "Construct an empty ontology")
        .def(py::init<const IRI&>(),
             py::arg("ontology_iri"),
             "Construct an ontology with the given IRI")
        .def(py::init<const IRI&, const IRI&>(),
             py::arg("ontology_iri"),
             py::arg("version_iri"),
             "Construct an ontology with IRI and version IRI")
        
        // Metadata management
        .def("get_ontology_iri", &Ontology::getOntologyIRI,
             "Get the ontology IRI")
        .def("set_ontology_iri", &Ontology::setOntologyIRI,
             py::arg("iri"),
             "Set the ontology IRI")
        .def("get_version_iri", &Ontology::getVersionIRI,
             "Get the version IRI")
        .def("set_version_iri", &Ontology::setVersionIRI,
             py::arg("iri"),
             "Set the version IRI")
        .def("get_imports", &Ontology::getImports,
             "Get the imports")
        .def("add_import", &Ontology::addImport,
             py::arg("import_iri"),
             "Add an import")
        .def("remove_import", &Ontology::removeImport,
             py::arg("import_iri"),
             "Remove an import")
        .def("has_import", &Ontology::hasImport,
             py::arg("import_iri"),
             "Check if this ontology has the given import")
        
        // Prefix management
        .def("register_prefix", &Ontology::registerPrefix,
             py::arg("prefix"),
             py::arg("namespace_uri"),
             "Register a namespace prefix")
        .def("get_namespace_for_prefix", &Ontology::getNamespaceForPrefix,
             py::arg("prefix"),
             "Get the namespace URI for a prefix")
        .def("get_prefix_for_namespace", &Ontology::getPrefixForNamespace,
             py::arg("namespace_uri"),
             "Get the prefix for a namespace URI")
        .def("get_prefix_map", &Ontology::getPrefixMap,
             "Get the complete prefix map")
        .def("remove_prefix", &Ontology::removePrefix,
             py::arg("prefix"),
             "Remove a prefix")
        .def("clear_prefixes", &Ontology::clearPrefixes,
             "Clear all prefixes")
        
        // Axiom management
        .def("add_axiom", &Ontology::addAxiom,
             py::arg("axiom"),
             "Add an axiom to the ontology")
        .def("remove_axiom", &Ontology::removeAxiom,
             py::arg("axiom"),
             "Remove an axiom from the ontology")
        .def("contains_axiom", &Ontology::containsAxiom,
             py::arg("axiom"),
             "Check if the ontology contains the given axiom")
        .def("get_axioms", &Ontology::getAxioms,
             "Get all axioms in the ontology")
        .def("clear_axioms", &Ontology::clearAxioms,
             "Clear all axioms from the ontology")
        
        // Entity queries
        .def("get_classes", &Ontology::getClasses,
             "Get all classes in the ontology")
        .def("get_object_properties", &Ontology::getObjectProperties,
             "Get all object properties in the ontology")
        .def("get_data_properties", &Ontology::getDataProperties,
             "Get all data properties in the ontology")
        .def("get_individuals", &Ontology::getIndividuals,
             "Get all named individuals in the ontology")
        .def("contains_class", &Ontology::containsClass,
             py::arg("cls"),
             "Check if the ontology contains the given class")
        .def("contains_object_property", &Ontology::containsObjectProperty,
             py::arg("property"),
             "Check if the ontology contains the given object property")
        .def("contains_data_property", &Ontology::containsDataProperty,
             py::arg("property"),
             "Check if the ontology contains the given data property")
        .def("contains_individual", &Ontology::containsIndividual,
             py::arg("individual"),
             "Check if the ontology contains the given individual")
        
        // Statistics
        .def("get_axiom_count", &Ontology::getAxiomCount,
             "Get the number of axioms in the ontology")
        .def("get_entity_count", &Ontology::getEntityCount,
             "Get the total number of entities in the ontology")
        .def("get_class_count", &Ontology::getClassCount,
             "Get the number of classes in the ontology")
        .def("get_object_property_count", &Ontology::getObjectPropertyCount,
             "Get the number of object properties in the ontology")
        .def("get_data_property_count", &Ontology::getDataPropertyCount,
             "Get the number of data properties in the ontology")
        .def("get_individual_count", &Ontology::getIndividualCount,
             "Get the number of individuals in the ontology")
        .def("get_statistics", &Ontology::getStatistics,
             "Get statistics about the ontology as a string")
        
        // Serialization
        .def("to_functional_syntax", py::overload_cast<>(&Ontology::toFunctionalSyntax, py::const_),
             "Convert the ontology to OWL2 Functional Syntax")
        .def("to_functional_syntax", py::overload_cast<const std::string&>(&Ontology::toFunctionalSyntax, py::const_),
             py::arg("indent"),
             "Convert the ontology to OWL2 Functional Syntax with custom indentation")
        
        // Individual and property manipulation
        .def("create_individual", &Ontology::createIndividual,
             py::arg("cls"),
             py::arg("individual_iri"),
             "Create a new individual of the specified class\n\n"
             "This creates a NamedIndividual and adds a ClassAssertion axiom.\n\n"
             "Args:\n"
             "    cls: The class to instantiate\n"
             "    individual_iri: The IRI for the new individual\n\n"
             "Returns:\n"
             "    The created NamedIndividual")
        .def("add_data_property_assertion", &Ontology::addDataPropertyAssertion,
             py::arg("individual"),
             py::arg("property"),
             py::arg("value"),
             "Add a data property assertion\n\n"
             "Creates and adds a DataPropertyAssertion axiom.\n\n"
             "Args:\n"
             "    individual: The subject individual\n"
             "    property: The data property\n"
             "    value: The literal value\n\n"
             "Returns:\n"
             "    True if the axiom was added successfully")
        .def("add_object_property_assertion", &Ontology::addObjectPropertyAssertion,
             py::arg("subject"),
             py::arg("property"),
             py::arg("object"),
             "Add an object property assertion\n\n"
             "Creates and adds an ObjectPropertyAssertion axiom.\n\n"
             "Args:\n"
             "    subject: The subject individual\n"
             "    property: The object property\n"
             "    object: The object individual\n\n"
             "Returns:\n"
             "    True if the axiom was added successfully")
        .def("add_class_assertion", &Ontology::addClassAssertion,
             py::arg("individual"),
             py::arg("cls"),
             "Add a class assertion to an existing individual\n\n"
             "Args:\n"
             "    individual: The individual\n"
             "    cls: The class to assert\n\n"
             "Returns:\n"
             "    True if the axiom was added successfully")
        
        // Property-based search
        .def("search_by_data_property", &Ontology::searchByDataProperty,
             py::arg("property"),
             py::arg("value"),
             "Search for individuals by data property value\n\n"
             "Args:\n"
             "    property: The data property to search\n"
             "    value: The literal value to match\n\n"
             "Returns:\n"
             "    List of individuals with matching data property assertions")
        .def("search_by_object_property", &Ontology::searchByObjectProperty,
             py::arg("property"),
             py::arg("object"),
             "Search for individuals by object property value\n\n"
             "Args:\n"
             "    property: The object property to search\n"
             "    object: The object individual to match\n\n"
             "Returns:\n"
             "    List of subject individuals with matching object property assertions")
        
        // Property assertion queries
        .def("get_object_property_assertions_for_individual", 
             py::overload_cast<const NamedIndividual&>(&Ontology::getObjectPropertyAssertions, py::const_),
             py::arg("individual"),
             "Get all object property assertions for an individual\n\n"
             "Args:\n"
             "    individual: The individual\n\n"
             "Returns:\n"
             "    List of ObjectPropertyAssertion axioms")
        .def("get_object_property_assertions_for_property",
             py::overload_cast<const ObjectProperty&>(&Ontology::getObjectPropertyAssertions, py::const_),
             py::arg("property"),
             "Get all object property assertions for a property\n\n"
             "Args:\n"
             "    property: The object property\n\n"
             "Returns:\n"
             "    List of (subject, object) pairs")
        .def("get_data_property_assertions_for_individual",
             py::overload_cast<const NamedIndividual&>(&Ontology::getDataPropertyAssertions, py::const_),
             py::arg("individual"),
             "Get all data property assertions for an individual\n\n"
             "Args:\n"
             "    individual: The individual\n\n"
             "Returns:\n"
             "    List of DataPropertyAssertion axioms")
        .def("get_data_property_assertions_for_property",
             py::overload_cast<const DataProperty&>(&Ontology::getDataPropertyAssertions, py::const_),
             py::arg("property"),
             "Get all data property assertions for a property\n\n"
             "Args:\n"
             "    property: The data property\n\n"
             "Returns:\n"
             "    List of (subject, value) pairs")
        
        // Individual class queries
        .def("get_classes_for_individual", &Ontology::getClassesForIndividual,
             py::arg("individual"),
             "Get all classes that an individual is asserted to be an instance of\n\n"
             "Args:\n"
             "    individual: The individual to query\n\n"
             "Returns:\n"
             "    List of classes")
        .def("is_instance_of", &Ontology::isInstanceOf,
             py::arg("individual"),
             py::arg("cls"),
             "Check if an individual is an instance of a class\n\n"
             "Args:\n"
             "    individual: The individual to check\n"
             "    cls: The class to check membership of\n\n"
             "Returns:\n"
             "    True if there is a ClassAssertion axiom")
        
        // Property characteristics
        .def("is_functional_object_property", &Ontology::isFunctionalObjectProperty,
             py::arg("property"),
             "Check if an object property is functional\n\n"
             "Args:\n"
             "    property: The object property to check\n\n"
             "Returns:\n"
             "    True if there is a FunctionalObjectProperty axiom")
        .def("is_functional_data_property", &Ontology::isFunctionalDataProperty,
             py::arg("property"),
             "Check if a data property is functional\n\n"
             "Args:\n"
             "    property: The data property to check\n\n"
             "Returns:\n"
             "    True if there is a FunctionalDataProperty axiom")
        
        // Filtering and subgraph extraction methods
        .def("create_subgraph", &Ontology::createSubgraph,
             py::arg("filter"),
             "Create a filtered subgraph using an OntologyFilter")
        .def("get_individuals_of_class", &Ontology::getIndividualsOfClass,
             py::arg("cls"),
             "Get all individuals that are instances of the given class")
        .def("get_neighbors", &Ontology::getNeighbors,
             py::arg("individual"),
             py::arg("depth") = 1,
             "Get neighboring individuals within specified depth (default: 1 hop)")
        .def("has_path", &Ontology::hasPath,
             py::arg("from_individual"),
             py::arg("to_individual"),
             "Check if a path exists between two individuals through property assertions")
        
        .def("__repr__", [](const Ontology& onto) {
            auto iri = onto.getOntologyIRI();
            if (iri.has_value()) {
                return "<Ontology '" + iri.value().toString() + "' with " + 
                       std::to_string(onto.getAxiomCount()) + " axioms>";
            }
            return "<Ontology with " + std::to_string(onto.getAxiomCount()) + " axioms>";
        });

    // ========================================================================
    // Ontology Filtering
    // ========================================================================
    
    // FilterCriteria struct
    py::class_<FilterCriteria>(m, "FilterCriteria", "Criteria for filtering ontology content")
        .def(py::init<>(), "Construct empty filter criteria")
        .def_readwrite("include_individuals", &FilterCriteria::include_individuals,
                      "Set of individual IRIs to include explicitly")
        .def_readwrite("include_classes", &FilterCriteria::include_classes,
                      "Set of class IRIs whose instances should be included")
        .def_readwrite("exclude_individuals", &FilterCriteria::exclude_individuals,
                      "Set of individual IRIs to exclude explicitly")
        .def_readwrite("property_value_filters", &FilterCriteria::property_value_filters,
                      "Map of property IRI to allowed values")
        .def_readwrite("max_depth", &FilterCriteria::max_depth,
                      "Maximum depth for neighborhood extraction (-1 = no limit)")
        .def_readwrite("include_class_hierarchy", &FilterCriteria::include_class_hierarchy,
                      "Whether to include class hierarchy axioms")
        .def_readwrite("include_property_hierarchy", &FilterCriteria::include_property_hierarchy,
                      "Whether to include property hierarchy axioms")
        .def_readwrite("include_declarations", &FilterCriteria::include_declarations,
                      "Whether to include declarations for referenced entities")
        .def_readwrite("custom_filter", &FilterCriteria::custom_filter,
                      "Custom filter function for additional filtering logic");
    
    // FilterResult struct
    py::class_<FilterResult>(m, "FilterResult", "Result of a filtering operation")
        .def(py::init<>(), "Construct empty filter result")
        .def_readwrite("ontology", &FilterResult::ontology,
                      "The filtered ontology")
        .def_readwrite("original_axiom_count", &FilterResult::original_axiom_count,
                      "Number of axioms in original ontology")
        .def_readwrite("filtered_axiom_count", &FilterResult::filtered_axiom_count,
                      "Number of axioms in filtered ontology")
        .def_readwrite("original_individual_count", &FilterResult::original_individual_count,
                      "Number of individuals in original ontology")
        .def_readwrite("filtered_individual_count", &FilterResult::filtered_individual_count,
                      "Number of individuals in filtered ontology")
        .def_readwrite("included_individuals", &FilterResult::included_individuals,
                      "Set of individual IRIs that were included")
        .def("__repr__", [](const FilterResult& result) {
            return "<FilterResult: " + std::to_string(result.filtered_axiom_count) + 
                   " axioms, " + std::to_string(result.filtered_individual_count) + " individuals>";
        });
    
    // OntologyFilter class
    py::class_<OntologyFilter>(m, "OntologyFilter", "High-performance ontology filtering and subgraph extraction")
        .def(py::init<const Ontology&>(),
             py::arg("ontology"),
             "Construct a filter for the given ontology")
        .def(py::init<std::shared_ptr<const Ontology>>(),
             py::arg("ontology"),
             "Construct a filter with shared ownership of ontology")
        
        // Filtering methods
        .def("filter_by_individuals", &OntologyFilter::filterByIndividuals,
             py::arg("iris"),
             "Extract a subgraph containing specific individuals")
        .def("filter_by_classes", &OntologyFilter::filterByClasses,
             py::arg("class_iris"),
             "Filter by class membership - includes all instances of specified classes")
        .def("filter_by_property", &OntologyFilter::filterByProperty,
             py::arg("property"),
             py::arg("value"),
             "Filter by data property value")
        .def("filter_by_object_property", &OntologyFilter::filterByObjectProperty,
             py::arg("property"),
             py::arg("target"),
             "Filter by object property target")
        .def("extract_neighborhood", 
             py::overload_cast<const IRI&, int>(&OntologyFilter::extractNeighborhood, py::const_),
             py::arg("seed"),
             py::arg("depth"),
             "Extract k-hop neighborhood around a seed individual")
        .def("extract_neighborhood", 
             py::overload_cast<const std::unordered_set<IRI>&, int>(&OntologyFilter::extractNeighborhood, py::const_),
             py::arg("seeds"),
             py::arg("depth"),
             "Extract k-hop neighborhood around multiple seed individuals")
        .def("extract_path", &OntologyFilter::extractPath,
             py::arg("start"),
             py::arg("end"),
             "Extract path(s) between two individuals")
        .def("random_sample", &OntologyFilter::randomSample,
             py::arg("n"),
             py::arg("seed") = 42,
             "Random sampling of n individuals")
        .def("apply_filter", &OntologyFilter::applyFilter,
             py::arg("criteria"),
             "Apply custom filter criteria")
        
        // Builder pattern methods
        .def("with_individuals", &OntologyFilter::withIndividuals,
             py::arg("iris"),
             "Builder: add individuals to include")
        .def("with_classes", &OntologyFilter::withClasses,
             py::arg("class_iris"),
             "Builder: add classes whose instances should be included")
        .def("exclude_individuals", &OntologyFilter::excludeIndividuals,
             py::arg("iris"),
             "Builder: add individuals to exclude")
        .def("with_max_depth", &OntologyFilter::withMaxDepth,
             py::arg("depth"),
             "Builder: set maximum depth for neighborhood extraction")
        .def("include_class_hierarchy", &OntologyFilter::includeClassHierarchy,
             py::arg("include"),
             "Builder: set whether to include class hierarchy axioms")
        .def("include_property_hierarchy", &OntologyFilter::includePropertyHierarchy,
             py::arg("include"),
             "Builder: set whether to include property hierarchy axioms")
        .def("include_declarations", &OntologyFilter::includeDeclarations,
             py::arg("include"),
             "Builder: set whether to include declarations")
        .def("execute", &OntologyFilter::execute,
             "Execute the built filter")
        
        .def("get_ontology", &OntologyFilter::getOntology,
             "Get the source ontology")
        .def("__repr__", [](const OntologyFilter& filter) {
            return "<OntologyFilter>";
        });

    // ========================================================================
    // Functional Syntax Serializer
    // ========================================================================
    py::class_<FunctionalSyntaxSerializer>(m, "FunctionalSyntaxSerializer", "Serializer for OWL2 Functional Syntax")
        .def_static("serialize", py::overload_cast<const Ontology&>(&FunctionalSyntaxSerializer::serialize),
                   py::arg("ontology"),
                   "Serialize ontology to string")
        .def_static("serialize", py::overload_cast<const Ontology&, const std::string&>(&FunctionalSyntaxSerializer::serialize),
                   py::arg("ontology"),
                   py::arg("indent"),
                   "Serialize ontology to string with custom indentation")
        .def_static("serialize_to_file", &FunctionalSyntaxSerializer::serializeToFile,
                   py::arg("ontology"),
                   py::arg("filename"),
                   "Serialize ontology to file");

    // ========================================================================
    // RDF/XML Serializer
    // ========================================================================
    py::class_<RDFXMLSerializer>(m, "RDFXMLSerializer", "Serializer for OWL2 RDF/XML format")
        .def_static("serialize", &RDFXMLSerializer::serialize,
                   py::arg("ontology"),
                   "Serialize ontology to RDF/XML string")
        .def_static("serialize_to_file", &RDFXMLSerializer::serializeToFile,
                   py::arg("ontology"),
                   py::arg("filename"),
                   "Serialize ontology to RDF/XML file");

    // ========================================================================
    // RDF/XML Parser
    // ========================================================================
    py::class_<RDFXMLParser>(m, "RDFXMLParser", "Parser for OWL2 RDF/XML format")
        .def_static("parse", &RDFXMLParser::parse,
                   py::arg("rdfxml_content"),
                   "Parse ontology from RDF/XML string")
        .def_static("parse_from_file", &RDFXMLParser::parseFromFile,
                   py::arg("filename"),
                   "Parse ontology from RDF/XML file");
    
    // Parser exception
    py::register_exception<RDFXMLParseException>(m, "RDFXMLParseException");

    // ========================================================================
    // Turtle Parser
    // ========================================================================
    py::class_<TurtleParser>(m, "TurtleParser", "Parser for Turtle format")
        .def_static("parse", &TurtleParser::parseFromString,
                   py::arg("turtle_content"),
                   "Parse ontology from Turtle string")
        .def_static("parse_from_file", &TurtleParser::parseFromFile,
                   py::arg("filename"),
                   "Parse ontology from Turtle file");
    
    py::register_exception<TurtleParseException>(m, "TurtleParseException");

    // ========================================================================
    // Functional Syntax Parser
    // ========================================================================
    py::class_<FunctionalParser>(m, "FunctionalParser", "Parser for OWL2 Functional Syntax")
        .def_static("parse", &FunctionalParser::parseFromString,
                   py::arg("functional_content"),
                   "Parse ontology from Functional Syntax string")
        .def_static("parse_from_file", &FunctionalParser::parseFromFile,
                   py::arg("filename"),
                   "Parse ontology from Functional Syntax file");
    
    py::register_exception<FunctionalParseException>(m, "FunctionalParseException");

    // ========================================================================
    // Manchester Syntax Parser
    // ========================================================================
    py::class_<ManchesterParser>(m, "ManchesterParser", "Parser for Manchester Syntax")
        .def_static("parse", &ManchesterParser::parseFromString,
                   py::arg("manchester_content"),
                   "Parse ontology from Manchester Syntax string")
        .def_static("parse_from_file", &ManchesterParser::parseFromFile,
                   py::arg("filename"),
                   "Parse ontology from Manchester Syntax file");
    
    py::register_exception<ManchesterParseException>(m, "ManchesterParseException");

    // ========================================================================
    // OWL/XML Parser
    // ========================================================================
    py::class_<OWLXMLParser>(m, "OWLXMLParser", "Parser for OWL/XML format")
        .def_static("parse", &OWLXMLParser::parseFromString,
                   py::arg("owlxml_content"),
                   "Parse ontology from OWL/XML string")
        .def_static("parse_from_file", &OWLXMLParser::parseFromFile,
                   py::arg("filename"),
                   "Parse ontology from OWL/XML file");
    
    py::register_exception<OWLXMLParseException>(m, "OWLXMLParseException");

    // ========================================================================
    // Turtle Serializer
    // ========================================================================
    py::class_<TurtleSerializer>(m, "TurtleSerializer", "Serializer for Turtle format")
        .def_static("serialize", py::overload_cast<const Ontology&>(&TurtleSerializer::serialize),
                   py::arg("ontology"),
                   "Serialize ontology to Turtle string")
        .def_static("serialize_to_file", &TurtleSerializer::serializeToFile,
                   py::arg("ontology"),
                   py::arg("filename"),
                   "Serialize ontology to Turtle file");

    // ========================================================================
    // Manchester Syntax Serializer
    // ========================================================================
    py::class_<ManchesterSerializer>(m, "ManchesterSerializer", "Serializer for Manchester Syntax")
        .def_static("serialize", &ManchesterSerializer::serialize,
                   py::arg("ontology"),
                   "Serialize ontology to Manchester Syntax string")
        .def_static("serialize_to_file", &ManchesterSerializer::serializeToFile,
                   py::arg("ontology"),
                   py::arg("filename"),
                   "Serialize ontology to Manchester Syntax file");

    // ========================================================================
    // OWL/XML Serializer
    // ========================================================================
    py::class_<OWLXMLSerializer>(m, "OWLXMLSerializer", "Serializer for OWL/XML format")
        .def_static("serialize", &OWLXMLSerializer::serialize,
                   py::arg("ontology"),
                   "Serialize ontology to OWL/XML string")
        .def_static("serialize_to_file", &OWLXMLSerializer::serializeToFile,
                   py::arg("ontology"),
                   py::arg("filename"),
                   "Serialize ontology to OWL/XML file");

    // ========================================================================
    // CSV Parser
    // ========================================================================
    
    // NodeTypeConfig struct
    py::class_<NodeTypeConfig>(m, "NodeTypeConfig", "Configuration for parsing node types from CSV")
        .def(py::init<>(), "Construct empty node type config")
        .def_readwrite("iri_column_name", &NodeTypeConfig::iri_column_name,
                      "Column name for unique identifiers")
        .def_readwrite("has_headers", &NodeTypeConfig::has_headers,
                      "Whether the CSV has header row")
        .def_readwrite("data_property_map", &NodeTypeConfig::data_property_map,
                      "Map from column names to property IRIs")
        .def_readwrite("data_transforms", &NodeTypeConfig::data_transforms,
                      "Transform functions for column data")
        .def_readwrite("filter_column", &NodeTypeConfig::filter_column,
                      "Column name for filtering")
        .def_readwrite("filter_value", &NodeTypeConfig::filter_value,
                      "Value to match for filtering")
        .def_readwrite("merge_mode", &NodeTypeConfig::merge_mode,
                      "Whether to merge with existing individuals")
        .def_readwrite("merge_property_iri", &NodeTypeConfig::merge_property_iri,
                      "Property to match on when merging")
        .def_readwrite("merge_column_name", &NodeTypeConfig::merge_column_name,
                      "Column name to use for merging");
    
    // RelationshipTypeConfig struct
    py::class_<RelationshipTypeConfig>(m, "RelationshipTypeConfig", "Configuration for parsing relationships from CSV")
        .def(py::init<>(), "Construct empty relationship type config")
        .def_readwrite("has_headers", &RelationshipTypeConfig::has_headers,
                      "Whether the CSV has header row")
        .def_readwrite("subject_class_iri", &RelationshipTypeConfig::subject_class_iri,
                      "IRI of subject class")
        .def_readwrite("subject_column_name", &RelationshipTypeConfig::subject_column_name,
                      "Column name for subject values")
        .def_readwrite("subject_match_property_iri", &RelationshipTypeConfig::subject_match_property_iri,
                      "Property to match subjects on")
        .def_readwrite("object_class_iri", &RelationshipTypeConfig::object_class_iri,
                      "IRI of object class")
        .def_readwrite("object_column_name", &RelationshipTypeConfig::object_column_name,
                      "Column name for object values")
        .def_readwrite("object_match_property_iri", &RelationshipTypeConfig::object_match_property_iri,
                      "Property to match objects on")
        .def_readwrite("filter_column", &RelationshipTypeConfig::filter_column,
                      "Column name for filtering")
        .def_readwrite("filter_value", &RelationshipTypeConfig::filter_value,
                      "Value to match for filtering")
        .def_readwrite("data_transforms", &RelationshipTypeConfig::data_transforms,
                      "Transform functions for column data");
    
    // CSVParser class
    py::class_<CSVParser>(m, "CSVParser", "High-performance CSV parser for OWL2 ontologies")
        .def(py::init<Ontology&, const std::string&>(),
             py::arg("ontology"),
             py::arg("base_iri"),
             "Construct a CSV parser for the given ontology")
        .def("parse_node_type", &CSVParser::parse_node_type,
             py::arg("filename"),
             py::arg("class_iri"),
             py::arg("config"),
             py::arg("delimiter") = ',',
             "Parse CSV file to create individuals of a class")
        .def("parse_relationship_type", &CSVParser::parse_relationship_type,
             py::arg("filename"),
             py::arg("property_iri"),
             py::arg("config"),
             py::arg("delimiter") = ',',
             "Parse CSV file to create relationships between individuals")
        .def("set_iri_generator", &CSVParser::set_iri_generator,
             py::arg("generator"),
             "Set custom IRI generator function")
        .def("get_ontology", &CSVParser::get_ontology,
             py::return_value_policy::reference,
             "Get the ontology being populated")
        .def("__repr__", [](const CSVParser& parser) {
            return "<CSVParser>";
        });
    
    // Parser exception
    py::register_exception<CSVParseException>(m, "CSVParseException");

    // ========================================================================
    // Version information
    // ========================================================================
    m.attr("__version__") = "0.1.0-simple";
}
