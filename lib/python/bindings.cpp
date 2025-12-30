/**
 * @file bindings.cpp
 * @brief Pybind11 bindings for the libista OWL2 library
 * 
 * This module exposes the core OWL2 functionality to Python.
 */

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/functional.h>
#include <pybind11/operators.h>

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

namespace py = pybind11;
using namespace ista::owl2;

PYBIND11_MODULE(_libista_owl2, m) {
    m.doc() = "Python bindings for the libista OWL2 library";

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

    py::class_<Datatype, Entity, std::shared_ptr<Datatype>>(m, "Datatype", "OWL2 Datatype")
        .def(py::init<const IRI&>(),
             py::arg("iri"),
             "Construct a Datatype with the given IRI")
        .def("__repr__", [](const Datatype& dt) {
            return "<Datatype '" + dt.getIRI().toString() + "'>";
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

    py::class_<AnnotationProperty, Entity, std::shared_ptr<AnnotationProperty>>(m, "AnnotationProperty", "OWL2 Annotation Property")
        .def(py::init<const IRI&>(),
             py::arg("iri"),
             "Construct an AnnotationProperty with the given IRI")
        .def("__repr__", [](const AnnotationProperty& ap) {
            return "<AnnotationProperty '" + ap.getIRI().toString() + "'>";
        });

    py::class_<NamedIndividual, Entity, std::shared_ptr<NamedIndividual>>(m, "NamedIndividual", "OWL2 Named Individual")
        .def(py::init<const IRI&>(),
             py::arg("iri"),
             "Construct a NamedIndividual with the given IRI")
        .def("__repr__", [](const NamedIndividual& ni) {
            return "<NamedIndividual '" + ni.getIRI().toString() + "'>";
        });

    py::class_<AnonymousIndividual, std::shared_ptr<AnonymousIndividual>>(m, "AnonymousIndividual", "OWL2 Anonymous Individual (blank node)")
        .def(py::init<const std::string&>(),
             py::arg("node_id"),
             "Construct an AnonymousIndividual with the given node ID")
        .def("get_node_id", &AnonymousIndividual::getNodeID,
             "Get the node ID")
        .def("__repr__", [](const AnonymousIndividual& ai) {
            return "<AnonymousIndividual '" + ai.getNodeID() + "'>";
        })
        .def(py::self == py::self)
        .def(py::self != py::self)
        .def(py::self < py::self);

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
    // Annotation Classes
    // ========================================================================
    // Note: Annotation constructors/methods that take AnnotationValue (std::variant)
    // can't be directly exposed due to pybind11 limitations. We provide factory functions instead.
    py::class_<Annotation>(m, "Annotation", "OWL2 Annotation")
        // Factory functions for creating annotations with different value types
        .def(py::init([](const AnnotationProperty& prop, const IRI& value) {
                 return Annotation(prop, AnnotationValue(value));
             }),
             py::arg("property"),
             py::arg("value"),
             "Construct an annotation with an IRI value")
        .def(py::init([](const AnnotationProperty& prop, const Literal& value) {
                 return Annotation(prop, AnnotationValue(value));
             }),
             py::arg("property"),
             py::arg("value"),
             "Construct an annotation with a Literal value")
        .def("get_property", &Annotation::getProperty,
             "Get the annotation property")
        // getValue returns variant - skip it
        .def("get_annotations", &Annotation::getAnnotations,
             "Get nested annotations")
        .def("has_annotations", &Annotation::hasAnnotations,
             "Check if this annotation has nested annotations")
        .def("set_property", &Annotation::setProperty,
             py::arg("property"),
             "Set the annotation property")
        // setValue takes variant - skip it
        .def("add_annotation", &Annotation::addAnnotation,
             py::arg("annotation"),
             "Add a nested annotation")
        .def("to_functional_syntax", &Annotation::toFunctionalSyntax,
             "Convert to OWL2 Functional Syntax")
        .def("get_value_as_string", &Annotation::getValueAsString,
             "Get the value as a string representation")
        .def(py::self == py::self)
        .def(py::self != py::self);

    // ========================================================================
    // Data Range Classes
    // ========================================================================
    py::class_<DataRange, std::shared_ptr<DataRange>>(m, "DataRange", "Base class for all OWL2 data ranges")
        .def("to_functional_syntax", &DataRange::toFunctionalSyntax,
             "Convert to OWL2 Functional Syntax")
        .def("get_data_range_type", &DataRange::getDataRangeType,
             "Get the type of this data range");

    py::class_<NamedDatatype, DataRange, std::shared_ptr<NamedDatatype>>(m, "NamedDatatype", "Named datatype")
        .def(py::init<const Datatype&>(),
             py::arg("datatype"),
             "Construct a NamedDatatype")
        .def("get_datatype", &NamedDatatype::getDatatype,
             "Get the datatype");

    py::class_<DataIntersectionOf, DataRange, std::shared_ptr<DataIntersectionOf>>(m, "DataIntersectionOf", "Intersection of data ranges")
        .def(py::init<const std::vector<DataRangePtr>&>(),
             py::arg("operands"),
             "Construct a DataIntersectionOf")
        .def("get_operands", &DataIntersectionOf::getOperands,
             "Get the operands");

    py::class_<DataUnionOf, DataRange, std::shared_ptr<DataUnionOf>>(m, "DataUnionOf", "Union of data ranges")
        .def(py::init<const std::vector<DataRangePtr>&>(),
             py::arg("operands"),
             "Construct a DataUnionOf")
        .def("get_operands", &DataUnionOf::getOperands,
             "Get the operands");

    py::class_<DataComplementOf, DataRange, std::shared_ptr<DataComplementOf>>(m, "DataComplementOf", "Complement of a data range")
        .def(py::init<const DataRangePtr&>(),
             py::arg("data_range"),
             "Construct a DataComplementOf")
        .def("get_data_range", &DataComplementOf::getDataRange,
             "Get the data range");

    py::class_<DataOneOf, DataRange, std::shared_ptr<DataOneOf>>(m, "DataOneOf", "Enumeration of literals")
        .def(py::init<const std::vector<Literal>&>(),
             py::arg("literals"),
             "Construct a DataOneOf")
        .def("get_literals", &DataOneOf::getLiterals,
             "Get the literals");

    py::class_<DatatypeRestriction, DataRange, std::shared_ptr<DatatypeRestriction>>(m, "DatatypeRestriction", "Facet restriction on a datatype")
        .def(py::init<const Datatype&, const std::vector<std::pair<IRI, Literal>>&>(),
             py::arg("datatype"),
             py::arg("restrictions"),
             "Construct a DatatypeRestriction")
        .def("get_datatype", &DatatypeRestriction::getDatatype,
             "Get the datatype")
        .def("get_restrictions", &DatatypeRestriction::getRestrictions,
             "Get the restrictions");

    // XSD facets namespace
    auto facets = m.def_submodule("facets", "XSD facet constants");
    facets.attr("MIN_INCLUSIVE") = facets::MIN_INCLUSIVE;
    facets.attr("MAX_INCLUSIVE") = facets::MAX_INCLUSIVE;
    facets.attr("MIN_EXCLUSIVE") = facets::MIN_EXCLUSIVE;
    facets.attr("MAX_EXCLUSIVE") = facets::MAX_EXCLUSIVE;
    facets.attr("LENGTH") = facets::LENGTH;
    facets.attr("MIN_LENGTH") = facets::MIN_LENGTH;
    facets.attr("MAX_LENGTH") = facets::MAX_LENGTH;
    facets.attr("PATTERN") = facets::PATTERN;

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

    py::class_<ObjectIntersectionOf, ClassExpression, std::shared_ptr<ObjectIntersectionOf>>(m, "ObjectIntersectionOf", "Intersection of class expressions")
        .def(py::init<const std::vector<ClassExpressionPtr>&>(),
             py::arg("operands"),
             "Construct an ObjectIntersectionOf")
        .def("get_operands", &ObjectIntersectionOf::getOperands,
             "Get the operands");

    py::class_<ObjectUnionOf, ClassExpression, std::shared_ptr<ObjectUnionOf>>(m, "ObjectUnionOf", "Union of class expressions")
        .def(py::init<const std::vector<ClassExpressionPtr>&>(),
             py::arg("operands"),
             "Construct an ObjectUnionOf")
        .def("get_operands", &ObjectUnionOf::getOperands,
             "Get the operands");

    py::class_<ObjectSomeValuesFrom, ClassExpression, std::shared_ptr<ObjectSomeValuesFrom>>(m, "ObjectSomeValuesFrom", "Existential restriction")
        .def(py::init<const ObjectProperty&, const ClassExpressionPtr&>(),
             py::arg("property"),
             py::arg("filler"),
             "Construct an ObjectSomeValuesFrom")
        .def("get_property", &ObjectSomeValuesFrom::getProperty,
             "Get the property")
        .def("get_filler", &ObjectSomeValuesFrom::getFiller,
             "Get the filler");

    py::class_<ObjectAllValuesFrom, ClassExpression, std::shared_ptr<ObjectAllValuesFrom>>(m, "ObjectAllValuesFrom", "Universal restriction")
        .def(py::init<const ObjectProperty&, const ClassExpressionPtr&>(),
             py::arg("property"),
             py::arg("filler"),
             "Construct an ObjectAllValuesFrom")
        .def("get_property", &ObjectAllValuesFrom::getProperty,
             "Get the property")
        .def("get_filler", &ObjectAllValuesFrom::getFiller,
             "Get the filler");

    // ========================================================================
    // Axiom Classes
    // ========================================================================
    py::class_<Axiom, std::shared_ptr<Axiom>>(m, "Axiom", "Base class for all OWL2 axioms")
        .def("to_functional_syntax", &Axiom::toFunctionalSyntax,
             "Convert to OWL2 Functional Syntax")
        .def("get_axiom_type", &Axiom::getAxiomType,
             "Get the type of this axiom")
        .def("get_annotations", &Axiom::getAnnotations,
             "Get annotations on this axiom")
        .def("has_annotations", &Axiom::hasAnnotations,
             "Check if this axiom has annotations")
        .def("add_annotation", &Axiom::addAnnotation,
             py::arg("annotation"),
             "Add an annotation to this axiom")
        .def("set_annotations", &Axiom::setAnnotations,
             py::arg("annotations"),
             "Set all annotations");

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

    // Class Axioms
    py::class_<SubClassOf, Axiom, std::shared_ptr<SubClassOf>>(m, "SubClassOf", "SubClassOf axiom")
        .def(py::init<const ClassExpressionPtr&, const ClassExpressionPtr&>(),
             py::arg("subclass"),
             py::arg("superclass"),
             "Construct a SubClassOf axiom")
        .def("get_sub_class", &SubClassOf::getSubClass,
             "Get the subclass")
        .def("get_super_class", &SubClassOf::getSuperClass,
             "Get the superclass");

    py::class_<EquivalentClasses, Axiom, std::shared_ptr<EquivalentClasses>>(m, "EquivalentClasses", "EquivalentClasses axiom")
        .def(py::init<const std::vector<ClassExpressionPtr>&>(),
             py::arg("class_expressions"),
             "Construct an EquivalentClasses axiom")
        .def("get_class_expressions", &EquivalentClasses::getClassExpressions,
             "Get the class expressions");

    py::class_<DisjointClasses, Axiom, std::shared_ptr<DisjointClasses>>(m, "DisjointClasses", "DisjointClasses axiom")
        .def(py::init<const std::vector<ClassExpressionPtr>&>(),
             py::arg("class_expressions"),
             "Construct a DisjointClasses axiom")
        .def("get_class_expressions", &DisjointClasses::getClassExpressions,
             "Get the class expressions");

    py::class_<DisjointUnion, Axiom, std::shared_ptr<DisjointUnion>>(m, "DisjointUnion", "DisjointUnion axiom")
        .def(py::init<const Class&, const std::vector<ClassExpressionPtr>&>(),
             py::arg("cls"),
             py::arg("class_expressions"),
             "Construct a DisjointUnion axiom")
        .def("get_class", &DisjointUnion::getClass,
             "Get the class")
        .def("get_class_expressions", &DisjointUnion::getClassExpressions,
             "Get the class expressions");

    // Object Property Axioms
    py::class_<SubObjectPropertyOf, Axiom, std::shared_ptr<SubObjectPropertyOf>>(m, "SubObjectPropertyOf", "SubObjectPropertyOf axiom")
        .def(py::init<const ObjectPropertyExpression&, const ObjectPropertyExpression&>(),
             py::arg("sub_property"),
             py::arg("super_property"),
             "Construct a SubObjectPropertyOf axiom")
        .def(py::init<const std::vector<ObjectPropertyExpression>&, const ObjectPropertyExpression&>(),
             py::arg("property_chain"),
             py::arg("super_property"),
             "Construct a SubObjectPropertyOf axiom with property chain")
        .def("get_sub_property", &SubObjectPropertyOf::getSubProperty,
             "Get the sub property")
        .def("get_super_property", &SubObjectPropertyOf::getSuperProperty,
             "Get the super property")
        .def("get_property_chain", &SubObjectPropertyOf::getPropertyChain,
             "Get the property chain")
        .def("is_property_chain", &SubObjectPropertyOf::isPropertyChain,
             "Check if this is a property chain axiom");

    py::class_<EquivalentObjectProperties, Axiom, std::shared_ptr<EquivalentObjectProperties>>(m, "EquivalentObjectProperties", "EquivalentObjectProperties axiom")
        .def(py::init<const std::vector<ObjectPropertyExpression>&>(),
             py::arg("properties"),
             "Construct an EquivalentObjectProperties axiom")
        .def("get_properties", &EquivalentObjectProperties::getProperties,
             "Get the properties");

    py::class_<DisjointObjectProperties, Axiom, std::shared_ptr<DisjointObjectProperties>>(m, "DisjointObjectProperties", "DisjointObjectProperties axiom")
        .def(py::init<const std::vector<ObjectPropertyExpression>&>(),
             py::arg("properties"),
             "Construct a DisjointObjectProperties axiom")
        .def("get_properties", &DisjointObjectProperties::getProperties,
             "Get the properties");

    py::class_<InverseObjectProperties, Axiom, std::shared_ptr<InverseObjectProperties>>(m, "InverseObjectProperties", "InverseObjectProperties axiom")
        .def(py::init<const ObjectPropertyExpression&, const ObjectPropertyExpression&>(),
             py::arg("property1"),
             py::arg("property2"),
             "Construct an InverseObjectProperties axiom")
        .def("get_property1", &InverseObjectProperties::getProperty1,
             "Get the first property")
        .def("get_property2", &InverseObjectProperties::getProperty2,
             "Get the second property");

    py::class_<ObjectPropertyDomain, Axiom, std::shared_ptr<ObjectPropertyDomain>>(m, "ObjectPropertyDomain", "ObjectPropertyDomain axiom")
        .def(py::init<const ObjectPropertyExpression&, const ClassExpressionPtr&>(),
             py::arg("property"),
             py::arg("domain"),
             "Construct an ObjectPropertyDomain axiom")
        .def("get_property", &ObjectPropertyDomain::getProperty,
             "Get the property")
        .def("get_domain", &ObjectPropertyDomain::getDomain,
             "Get the domain");

    py::class_<ObjectPropertyRange, Axiom, std::shared_ptr<ObjectPropertyRange>>(m, "ObjectPropertyRange", "ObjectPropertyRange axiom")
        .def(py::init<const ObjectPropertyExpression&, const ClassExpressionPtr&>(),
             py::arg("property"),
             py::arg("range"),
             "Construct an ObjectPropertyRange axiom")
        .def("get_property", &ObjectPropertyRange::getProperty,
             "Get the property")
        .def("get_range", &ObjectPropertyRange::getRange,
             "Get the range");

    py::class_<FunctionalObjectProperty, Axiom, std::shared_ptr<FunctionalObjectProperty>>(m, "FunctionalObjectProperty", "FunctionalObjectProperty axiom")
        .def(py::init<const ObjectPropertyExpression&>(),
             py::arg("property"),
             "Construct a FunctionalObjectProperty axiom")
        .def("get_property", &FunctionalObjectProperty::getProperty,
             "Get the property");

    py::class_<InverseFunctionalObjectProperty, Axiom, std::shared_ptr<InverseFunctionalObjectProperty>>(m, "InverseFunctionalObjectProperty", "InverseFunctionalObjectProperty axiom")
        .def(py::init<const ObjectPropertyExpression&>(),
             py::arg("property"),
             "Construct an InverseFunctionalObjectProperty axiom")
        .def("get_property", &InverseFunctionalObjectProperty::getProperty,
             "Get the property");

    py::class_<ReflexiveObjectProperty, Axiom, std::shared_ptr<ReflexiveObjectProperty>>(m, "ReflexiveObjectProperty", "ReflexiveObjectProperty axiom")
        .def(py::init<const ObjectPropertyExpression&>(),
             py::arg("property"),
             "Construct a ReflexiveObjectProperty axiom")
        .def("get_property", &ReflexiveObjectProperty::getProperty,
             "Get the property");

    py::class_<IrreflexiveObjectProperty, Axiom, std::shared_ptr<IrreflexiveObjectProperty>>(m, "IrreflexiveObjectProperty", "IrreflexiveObjectProperty axiom")
        .def(py::init<const ObjectPropertyExpression&>(),
             py::arg("property"),
             "Construct an IrreflexiveObjectProperty axiom")
        .def("get_property", &IrreflexiveObjectProperty::getProperty,
             "Get the property");

    py::class_<SymmetricObjectProperty, Axiom, std::shared_ptr<SymmetricObjectProperty>>(m, "SymmetricObjectProperty", "SymmetricObjectProperty axiom")
        .def(py::init<const ObjectPropertyExpression&>(),
             py::arg("property"),
             "Construct a SymmetricObjectProperty axiom")
        .def("get_property", &SymmetricObjectProperty::getProperty,
             "Get the property");

    py::class_<AsymmetricObjectProperty, Axiom, std::shared_ptr<AsymmetricObjectProperty>>(m, "AsymmetricObjectProperty", "AsymmetricObjectProperty axiom")
        .def(py::init<const ObjectPropertyExpression&>(),
             py::arg("property"),
             "Construct an AsymmetricObjectProperty axiom")
        .def("get_property", &AsymmetricObjectProperty::getProperty,
             "Get the property");

    py::class_<TransitiveObjectProperty, Axiom, std::shared_ptr<TransitiveObjectProperty>>(m, "TransitiveObjectProperty", "TransitiveObjectProperty axiom")
        .def(py::init<const ObjectPropertyExpression&>(),
             py::arg("property"),
             "Construct a TransitiveObjectProperty axiom")
        .def("get_property", &TransitiveObjectProperty::getProperty,
             "Get the property");

    // Data Property Axioms
    py::class_<SubDataPropertyOf, Axiom, std::shared_ptr<SubDataPropertyOf>>(m, "SubDataPropertyOf", "SubDataPropertyOf axiom")
        .def(py::init<const DataProperty&, const DataProperty&>(),
             py::arg("sub_property"),
             py::arg("super_property"),
             "Construct a SubDataPropertyOf axiom")
        .def("get_sub_property", &SubDataPropertyOf::getSubProperty,
             "Get the sub property")
        .def("get_super_property", &SubDataPropertyOf::getSuperProperty,
             "Get the super property");

    py::class_<EquivalentDataProperties, Axiom, std::shared_ptr<EquivalentDataProperties>>(m, "EquivalentDataProperties", "EquivalentDataProperties axiom")
        .def(py::init<const std::vector<DataProperty>&>(),
             py::arg("properties"),
             "Construct an EquivalentDataProperties axiom")
        .def("get_properties", &EquivalentDataProperties::getProperties,
             "Get the properties");

    py::class_<DisjointDataProperties, Axiom, std::shared_ptr<DisjointDataProperties>>(m, "DisjointDataProperties", "DisjointDataProperties axiom")
        .def(py::init<const std::vector<DataProperty>&>(),
             py::arg("properties"),
             "Construct a DisjointDataProperties axiom")
        .def("get_properties", &DisjointDataProperties::getProperties,
             "Get the properties");

    py::class_<DataPropertyDomain, Axiom, std::shared_ptr<DataPropertyDomain>>(m, "DataPropertyDomain", "DataPropertyDomain axiom")
        .def(py::init<const DataProperty&, const ClassExpressionPtr&>(),
             py::arg("property"),
             py::arg("domain"),
             "Construct a DataPropertyDomain axiom")
        .def("get_property", &DataPropertyDomain::getProperty,
             "Get the property")
        .def("get_domain", &DataPropertyDomain::getDomain,
             "Get the domain");

    py::class_<DataPropertyRange, Axiom, std::shared_ptr<DataPropertyRange>>(m, "DataPropertyRange", "DataPropertyRange axiom")
        .def(py::init<const DataProperty&, const DataRangePtr&>(),
             py::arg("property"),
             py::arg("range"),
             "Construct a DataPropertyRange axiom")
        .def("get_property", &DataPropertyRange::getProperty,
             "Get the property")
        .def("get_range", &DataPropertyRange::getRange,
             "Get the range");

    py::class_<FunctionalDataProperty, Axiom, std::shared_ptr<FunctionalDataProperty>>(m, "FunctionalDataProperty", "FunctionalDataProperty axiom")
        .def(py::init<const DataProperty&>(),
             py::arg("property"),
             "Construct a FunctionalDataProperty axiom")
        .def("get_property", &FunctionalDataProperty::getProperty,
             "Get the property");

    // Datatype Definition Axiom
    py::class_<DatatypeDefinition, Axiom, std::shared_ptr<DatatypeDefinition>>(m, "DatatypeDefinition", "DatatypeDefinition axiom")
        .def(py::init<const Datatype&, const DataRangePtr&>(),
             py::arg("datatype"),
             py::arg("data_range"),
             "Construct a DatatypeDefinition axiom")
        .def("get_datatype", &DatatypeDefinition::getDatatype,
             "Get the datatype")
        .def("get_data_range", &DatatypeDefinition::getDataRange,
             "Get the data range");

    // HasKey Axiom
    py::class_<HasKey, Axiom, std::shared_ptr<HasKey>>(m, "HasKey", "HasKey axiom")
        .def(py::init<const ClassExpressionPtr&, const std::vector<ObjectPropertyExpression>&, const std::vector<DataProperty>&>(),
             py::arg("class_expression"),
             py::arg("object_properties"),
             py::arg("data_properties"),
             "Construct a HasKey axiom")
        .def("get_class_expression", &HasKey::getClassExpression,
             "Get the class expression")
        .def("get_object_properties", &HasKey::getObjectProperties,
             "Get the object properties")
        .def("get_data_properties", &HasKey::getDataProperties,
             "Get the data properties");

    // Assertion Axioms
    py::class_<SameIndividual, Axiom, std::shared_ptr<SameIndividual>>(m, "SameIndividual", "SameIndividual axiom")
        .def(py::init<const std::vector<Individual>&>(),
             py::arg("individuals"),
             "Construct a SameIndividual axiom")
        .def("get_individuals", &SameIndividual::getIndividuals,
             "Get the individuals");

    py::class_<DifferentIndividuals, Axiom, std::shared_ptr<DifferentIndividuals>>(m, "DifferentIndividuals", "DifferentIndividuals axiom")
        .def(py::init<const std::vector<Individual>&>(),
             py::arg("individuals"),
             "Construct a DifferentIndividuals axiom")
        .def("get_individuals", &DifferentIndividuals::getIndividuals,
             "Get the individuals");

    py::class_<ClassAssertion, Axiom, std::shared_ptr<ClassAssertion>>(m, "ClassAssertion", "ClassAssertion axiom")
        .def(py::init<const ClassExpressionPtr&, const Individual&>(),
             py::arg("class_expression"),
             py::arg("individual"),
             "Construct a ClassAssertion axiom")
        .def("get_class_expression", &ClassAssertion::getClassExpression,
             "Get the class expression")
        .def("get_individual", &ClassAssertion::getIndividual,
             "Get the individual");

    py::class_<ObjectPropertyAssertion, Axiom, std::shared_ptr<ObjectPropertyAssertion>>(m, "ObjectPropertyAssertion", "ObjectPropertyAssertion axiom")
        .def(py::init<const ObjectPropertyExpression&, const Individual&, const Individual&>(),
             py::arg("property"),
             py::arg("source"),
             py::arg("target"),
             "Construct an ObjectPropertyAssertion axiom")
        .def("get_property", &ObjectPropertyAssertion::getProperty,
             "Get the property")
        .def("get_source", &ObjectPropertyAssertion::getSource,
             "Get the source individual")
        .def("get_target", &ObjectPropertyAssertion::getTarget,
             "Get the target individual");

    py::class_<NegativeObjectPropertyAssertion, Axiom, std::shared_ptr<NegativeObjectPropertyAssertion>>(m, "NegativeObjectPropertyAssertion", "NegativeObjectPropertyAssertion axiom")
        .def(py::init<const ObjectPropertyExpression&, const Individual&, const Individual&>(),
             py::arg("property"),
             py::arg("source"),
             py::arg("target"),
             "Construct a NegativeObjectPropertyAssertion axiom")
        .def("get_property", &NegativeObjectPropertyAssertion::getProperty,
             "Get the property")
        .def("get_source", &NegativeObjectPropertyAssertion::getSource,
             "Get the source individual")
        .def("get_target", &NegativeObjectPropertyAssertion::getTarget,
             "Get the target individual");

    py::class_<DataPropertyAssertion, Axiom, std::shared_ptr<DataPropertyAssertion>>(m, "DataPropertyAssertion", "DataPropertyAssertion axiom")
        .def(py::init<const DataProperty&, const Individual&, const Literal&>(),
             py::arg("property"),
             py::arg("source"),
             py::arg("target"),
             "Construct a DataPropertyAssertion axiom")
        .def("get_property", &DataPropertyAssertion::getProperty,
             "Get the property")
        .def("get_source", &DataPropertyAssertion::getSource,
             "Get the source individual")
        .def("get_target", &DataPropertyAssertion::getTarget,
             "Get the target literal");

    py::class_<NegativeDataPropertyAssertion, Axiom, std::shared_ptr<NegativeDataPropertyAssertion>>(m, "NegativeDataPropertyAssertion", "NegativeDataPropertyAssertion axiom")
        .def(py::init<const DataProperty&, const Individual&, const Literal&>(),
             py::arg("property"),
             py::arg("source"),
             py::arg("target"),
             "Construct a NegativeDataPropertyAssertion axiom")
        .def("get_property", &NegativeDataPropertyAssertion::getProperty,
             "Get the property")
        .def("get_source", &NegativeDataPropertyAssertion::getSource,
             "Get the source individual")
        .def("get_target", &NegativeDataPropertyAssertion::getTarget,
             "Get the target literal");

    // Annotation Axioms
    py::class_<AnnotationAssertion, Axiom, std::shared_ptr<AnnotationAssertion>>(m, "AnnotationAssertion", "AnnotationAssertion axiom")
        .def(py::init<const AnnotationProperty&, const AnnotationSubject&, const AnnotationValue&>(),
             py::arg("property"),
             py::arg("subject"),
             py::arg("value"),
             "Construct an AnnotationAssertion axiom")
        .def("get_property", &AnnotationAssertion::getProperty,
             "Get the property")
        .def("get_subject", &AnnotationAssertion::getSubject,
             "Get the subject")
        .def("get_value", &AnnotationAssertion::getValue,
             "Get the value");

    py::class_<SubAnnotationPropertyOf, Axiom, std::shared_ptr<SubAnnotationPropertyOf>>(m, "SubAnnotationPropertyOf", "SubAnnotationPropertyOf axiom")
        .def(py::init<const AnnotationProperty&, const AnnotationProperty&>(),
             py::arg("sub_property"),
             py::arg("super_property"),
             "Construct a SubAnnotationPropertyOf axiom")
        .def("get_sub_property", &SubAnnotationPropertyOf::getSubProperty,
             "Get the sub property")
        .def("get_super_property", &SubAnnotationPropertyOf::getSuperProperty,
             "Get the super property");

    py::class_<AnnotationPropertyDomain, Axiom, std::shared_ptr<AnnotationPropertyDomain>>(m, "AnnotationPropertyDomain", "AnnotationPropertyDomain axiom")
        .def(py::init<const AnnotationProperty&, const IRI&>(),
             py::arg("property"),
             py::arg("domain"),
             "Construct an AnnotationPropertyDomain axiom")
        .def("get_property", &AnnotationPropertyDomain::getProperty,
             "Get the property")
        .def("get_domain", &AnnotationPropertyDomain::getDomain,
             "Get the domain");

    py::class_<AnnotationPropertyRange, Axiom, std::shared_ptr<AnnotationPropertyRange>>(m, "AnnotationPropertyRange", "AnnotationPropertyRange axiom")
        .def(py::init<const AnnotationProperty&, const IRI&>(),
             py::arg("property"),
             py::arg("range"),
             "Construct an AnnotationPropertyRange axiom")
        .def("get_property", &AnnotationPropertyRange::getProperty,
             "Get the property")
        .def("get_range", &AnnotationPropertyRange::getRange,
             "Get the range");

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
        .def("get_ontology_annotations", &Ontology::getOntologyAnnotations,
             "Get the ontology annotations")
        .def("add_ontology_annotation", &Ontology::addOntologyAnnotation,
             py::arg("annotation"),
             "Add an ontology annotation")
        .def("set_ontology_annotations", &Ontology::setOntologyAnnotations,
             py::arg("annotations"),
             "Set all ontology annotations")
        .def("clear_ontology_annotations", &Ontology::clearOntologyAnnotations,
             "Clear all ontology annotations")
        
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
        
        // Axiom queries by type
        .def("get_declaration_axioms", &Ontology::getDeclarationAxioms,
             "Get all declaration axioms")
        .def("get_class_axioms", &Ontology::getClassAxioms,
             "Get all class axioms")
        .def("get_object_property_axioms", &Ontology::getObjectPropertyAxioms,
             "Get all object property axioms")
        .def("get_data_property_axioms", &Ontology::getDataPropertyAxioms,
             "Get all data property axioms")
        .def("get_assertion_axioms", &Ontology::getAssertionAxioms,
             "Get all assertion axioms")
        .def("get_annotation_axioms", &Ontology::getAnnotationAxioms,
             "Get all annotation axioms")
        
        // Specific axiom queries
        .def("get_sub_class_axioms_for_sub_class", &Ontology::getSubClassAxiomsForSubClass,
             py::arg("cls"),
             "Get all SubClassOf axioms where the given class is the subclass")
        .def("get_sub_class_axioms_for_super_class", &Ontology::getSubClassAxiomsForSuperClass,
             py::arg("cls"),
             "Get all SubClassOf axioms where the given class is the superclass")
        .def("get_equivalent_classes_axioms", &Ontology::getEquivalentClassesAxioms,
             py::arg("cls"),
             "Get all EquivalentClasses axioms containing the given class")
        .def("get_disjoint_classes_axioms", &Ontology::getDisjointClassesAxioms,
             py::arg("cls"),
             "Get all DisjointClasses axioms containing the given class")
        .def("get_sub_object_property_axioms", &Ontology::getSubObjectPropertyAxioms,
             py::arg("property"),
             "Get all SubObjectPropertyOf axioms for the given property")
        .def("get_sub_data_property_axioms", &Ontology::getSubDataPropertyAxioms,
             py::arg("property"),
             "Get all SubDataPropertyOf axioms for the given property")
        .def("get_class_assertions", &Ontology::getClassAssertions,
             py::arg("individual"),
             "Get all ClassAssertion axioms for the given individual")
        .def("get_object_property_assertions", &Ontology::getObjectPropertyAssertions,
             py::arg("individual"),
             "Get all ObjectPropertyAssertion axioms for the given individual")
        .def("get_data_property_assertions", &Ontology::getDataPropertyAssertions,
             py::arg("individual"),
             "Get all DataPropertyAssertion axioms for the given individual")
        
        // Entity queries
        .def("get_classes", &Ontology::getClasses,
             "Get all classes in the ontology")
        .def("get_object_properties", &Ontology::getObjectProperties,
             "Get all object properties in the ontology")
        .def("get_data_properties", &Ontology::getDataProperties,
             "Get all data properties in the ontology")
        .def("get_annotation_properties", &Ontology::getAnnotationProperties,
             "Get all annotation properties in the ontology")
        .def("get_individuals", &Ontology::getIndividuals,
             "Get all named individuals in the ontology")
        .def("get_datatypes", &Ontology::getDatatypes,
             "Get all datatypes in the ontology")
        .def("contains_class", &Ontology::containsClass,
             py::arg("cls"),
             "Check if the ontology contains the given class")
        .def("contains_object_property", &Ontology::containsObjectProperty,
             py::arg("property"),
             "Check if the ontology contains the given object property")
        .def("contains_data_property", &Ontology::containsDataProperty,
             py::arg("property"),
             "Check if the ontology contains the given data property")
        .def("contains_annotation_property", &Ontology::containsAnnotationProperty,
             py::arg("property"),
             "Check if the ontology contains the given annotation property")
        .def("contains_individual", &Ontology::containsIndividual,
             py::arg("individual"),
             "Check if the ontology contains the given individual")
        .def("contains_datatype", &Ontology::containsDatatype,
             py::arg("datatype"),
             "Check if the ontology contains the given datatype")
        
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

    // Exception for parser errors
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
    py::class_<NodeTypeConfig>(m, "NodeTypeConfig", "Configuration for parsing node types from CSV files")
        .def(py::init<>(),
             "Construct a NodeTypeConfig")
        .def_readwrite("iri_column_name", &NodeTypeConfig::iri_column_name,
                      "Column name that contains unique identifiers for creating IRIs")
        .def_readwrite("has_headers", &NodeTypeConfig::has_headers,
                      "Whether the file has a header row")
        .def_readwrite("data_property_map", &NodeTypeConfig::data_property_map,
                      "Map from CSV column names to data property IRIs")
        .def_readwrite("data_transforms", &NodeTypeConfig::data_transforms,
                      "Optional transform functions for column data")
        .def_readwrite("filter_column", &NodeTypeConfig::filter_column,
                      "Optional filter column name")
        .def_readwrite("filter_value", &NodeTypeConfig::filter_value,
                      "Optional filter value")
        .def_readwrite("merge_mode", &NodeTypeConfig::merge_mode,
                      "Whether to merge with existing individuals")
        .def_readwrite("merge_property_iri", &NodeTypeConfig::merge_property_iri,
                      "Optional property IRI for merging")
        .def_readwrite("merge_column_name", &NodeTypeConfig::merge_column_name,
                      "Column name for merge matching");

    py::class_<RelationshipTypeConfig>(m, "RelationshipTypeConfig", "Configuration for parsing relationship types from CSV files")
        .def(py::init<>(),
             "Construct a RelationshipTypeConfig")
        .def_readwrite("has_headers", &RelationshipTypeConfig::has_headers,
                      "Whether the file has a header row")
        .def_readwrite("subject_class_iri", &RelationshipTypeConfig::subject_class_iri,
                      "Optional subject class IRI")
        .def_readwrite("subject_column_name", &RelationshipTypeConfig::subject_column_name,
                      "Subject column name")
        .def_readwrite("subject_match_property_iri", &RelationshipTypeConfig::subject_match_property_iri,
                      "Optional subject match property IRI")
        .def_readwrite("object_class_iri", &RelationshipTypeConfig::object_class_iri,
                      "Optional object class IRI")
        .def_readwrite("object_column_name", &RelationshipTypeConfig::object_column_name,
                      "Object column name")
        .def_readwrite("object_match_property_iri", &RelationshipTypeConfig::object_match_property_iri,
                      "Optional object match property IRI")
        .def_readwrite("filter_column", &RelationshipTypeConfig::filter_column,
                      "Optional filter column name")
        .def_readwrite("filter_value", &RelationshipTypeConfig::filter_value,
                      "Optional filter value")
        .def_readwrite("data_transforms", &RelationshipTypeConfig::data_transforms,
                      "Optional transform functions for column data");

    py::class_<CSVParser>(m, "CSVParser", "High-performance CSV parser for populating OWL2 ontologies")
        .def(py::init<Ontology&, const std::string&>(),
             py::arg("ontology"),
             py::arg("base_iri"),
             "Construct a CSV parser")
        .def("parse_node_type", &CSVParser::parse_node_type,
             py::arg("filename"),
             py::arg("class_iri"),
             py::arg("config"),
             py::arg("delimiter") = ',',
             "Parse a CSV file to create individuals of a specific class")
        .def("parse_relationship_type", &CSVParser::parse_relationship_type,
             py::arg("filename"),
             py::arg("property_iri"),
             py::arg("config"),
             py::arg("delimiter") = ',',
             "Parse a CSV file to create relationships between individuals")
        .def("set_iri_generator", &CSVParser::set_iri_generator,
             py::arg("generator"),
             "Set a custom IRI generator function")
        .def("get_ontology", &CSVParser::get_ontology,
             py::return_value_policy::reference,
             "Get the ontology being populated");

    // Exception for CSV parser errors
    py::register_exception<CSVParseException>(m, "CSVParseException");

    // ========================================================================
    // Helper functions
    // ========================================================================
    // Note: The following helper functions take std::variant types by const ref,
    // which pybind11 can't handle directly. These are commented out:
    //   - format_object_property_expression (ObjectPropertyExpression is a variant)
    //   - format_individual (Individual is a variant)
    //   - format_annotation_subject (AnnotationSubject is a variant)
    //   - format_annotation_value (AnnotationValue is a variant)
    // These are internal utilities used by serializers - users don't need them.

    // ========================================================================
    // Version information
    // ========================================================================
    m.attr("__version__") = "0.1.0";
}
