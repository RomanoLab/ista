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

#include "../owl2/owl2.hpp"
#include "../owl2/parser/rdfxml_parser.hpp"

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
        .def(py::init([](const ClassExpressionPtr& class_expression, const NamedIndividual& individual) {
                 return std::make_shared<ClassAssertion>(class_expression, Individual(individual));
             }),
             py::arg("class_expression"),
             py::arg("individual"),
             "Construct a ClassAssertion axiom with a NamedIndividual")
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
        .def("__repr__", [](const Ontology& onto) {
            auto iri = onto.getOntologyIRI();
            if (iri.has_value()) {
                return "<Ontology '" + iri.value().toString() + "' with " + 
                       std::to_string(onto.getAxiomCount()) + " axioms>";
            }
            return "<Ontology with " + std::to_string(onto.getAxiomCount()) + " axioms>";
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
    // Version information
    // ========================================================================
    m.attr("__version__") = "0.1.0-simple";
}
