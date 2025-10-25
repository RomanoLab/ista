#include "axiom.hpp"
#include <sstream>

namespace ista {
namespace owl2 {

// ============================================================================
// BASE AXIOM CLASS
// ============================================================================

std::string Axiom::formatAnnotations() const {
    if (annotations_.empty()) {
        return "";
    }
    
    std::string result = " ";
    for (const auto& annotation : annotations_) {
        result += annotation.toFunctionalSyntax() + " ";
    }
    return result;
}

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

std::string formatObjectPropertyExpression(const ObjectPropertyExpression& ope) {
    return std::visit([](const auto& prop) -> std::string {
        using T = std::decay_t<decltype(prop)>;
        if constexpr (std::is_same_v<T, ObjectProperty>) {
            return "<" + prop.getIRI().toString() + ">";
        } else {
            return "ObjectInverseOf(<" + prop.first.getIRI().toString() + ">)";
        }
    }, ope);
}

std::string formatIndividual(const Individual& individual) {
    return std::visit([](const auto& ind) -> std::string {
        using T = std::decay_t<decltype(ind)>;
        if constexpr (std::is_same_v<T, NamedIndividual>) {
            return "<" + ind.getIRI().toString() + ">";
        } else {
            return "_:" + ind.getNodeID();
        }
    }, individual);
}

std::string formatAnnotationSubject(const AnnotationSubject& subject) {
    return std::visit([](const auto& subj) -> std::string {
        using T = std::decay_t<decltype(subj)>;
        if constexpr (std::is_same_v<T, IRI>) {
            return "<" + subj.toString() + ">";
        } else {
            return "_:" + subj.getNodeID();
        }
    }, subject);
}

std::string formatAnnotationValue(const AnnotationValue& value) {
    return std::visit([](const auto& val) -> std::string {
        using T = std::decay_t<decltype(val)>;
        if constexpr (std::is_same_v<T, IRI>) {
            return "<" + val.toString() + ">";
        } else if constexpr (std::is_same_v<T, Literal>) {
            return val.toString();
        } else {
            return "_:" + val.getNodeID();
        }
    }, value);
}

// ============================================================================
// DECLARATION AXIOMS
// ============================================================================

std::string Declaration::toFunctionalSyntax() const {
    std::string entity_type_str;
    switch (entity_type_) {
        case EntityType::CLASS:
            entity_type_str = "Class";
            break;
        case EntityType::DATATYPE:
            entity_type_str = "Datatype";
            break;
        case EntityType::OBJECT_PROPERTY:
            entity_type_str = "ObjectProperty";
            break;
        case EntityType::DATA_PROPERTY:
            entity_type_str = "DataProperty";
            break;
        case EntityType::ANNOTATION_PROPERTY:
            entity_type_str = "AnnotationProperty";
            break;
        case EntityType::NAMED_INDIVIDUAL:
            entity_type_str = "NamedIndividual";
            break;
    }
    
    return "Declaration(" + formatAnnotations() + entity_type_str + "(<" + iri_.toString() + ">))";
}

// ============================================================================
// CLASS AXIOMS
// ============================================================================

std::string SubClassOf::toFunctionalSyntax() const {
    return "SubClassOf(" + formatAnnotations() + 
           subclass_->toFunctionalSyntax() + " " +
           superclass_->toFunctionalSyntax() + ")";
}

std::string EquivalentClasses::toFunctionalSyntax() const {
    std::string result = "EquivalentClasses(" + formatAnnotations();
    for (const auto& ce : class_expressions_) {
        result += ce->toFunctionalSyntax() + " ";
    }
    result.pop_back();
    return result + ")";
}

std::string DisjointClasses::toFunctionalSyntax() const {
    std::string result = "DisjointClasses(" + formatAnnotations();
    for (const auto& ce : class_expressions_) {
        result += ce->toFunctionalSyntax() + " ";
    }
    result.pop_back();
    return result + ")";
}

std::string DisjointUnion::toFunctionalSyntax() const {
    std::string result = "DisjointUnion(" + formatAnnotations() +
                        "<" + class_.getIRI().toString() + "> ";
    for (const auto& ce : class_expressions_) {
        result += ce->toFunctionalSyntax() + " ";
    }
    result.pop_back();
    return result + ")";
}

// ============================================================================
// OBJECT PROPERTY AXIOMS
// ============================================================================

std::string SubObjectPropertyOf::toFunctionalSyntax() const {
    std::string result = "SubObjectPropertyOf(" + formatAnnotations();
    
    if (isPropertyChain()) {
        result += "ObjectPropertyChain(";
        for (const auto& prop : property_chain_) {
            result += formatObjectPropertyExpression(prop) + " ";
        }
        result.pop_back();
        result += ") ";
    } else {
        result += formatObjectPropertyExpression(*sub_property_) + " ";
    }
    
    result += formatObjectPropertyExpression(super_property_) + ")";
    return result;
}

std::string EquivalentObjectProperties::toFunctionalSyntax() const {
    std::string result = "EquivalentObjectProperties(" + formatAnnotations();
    for (const auto& prop : properties_) {
        result += formatObjectPropertyExpression(prop) + " ";
    }
    result.pop_back();
    return result + ")";
}

std::string DisjointObjectProperties::toFunctionalSyntax() const {
    std::string result = "DisjointObjectProperties(" + formatAnnotations();
    for (const auto& prop : properties_) {
        result += formatObjectPropertyExpression(prop) + " ";
    }
    result.pop_back();
    return result + ")";
}

std::string InverseObjectProperties::toFunctionalSyntax() const {
    return "InverseObjectProperties(" + formatAnnotations() +
           formatObjectPropertyExpression(property1_) + " " +
           formatObjectPropertyExpression(property2_) + ")";
}

std::string ObjectPropertyDomain::toFunctionalSyntax() const {
    return "ObjectPropertyDomain(" + formatAnnotations() +
           formatObjectPropertyExpression(property_) + " " +
           domain_->toFunctionalSyntax() + ")";
}

std::string ObjectPropertyRange::toFunctionalSyntax() const {
    return "ObjectPropertyRange(" + formatAnnotations() +
           formatObjectPropertyExpression(property_) + " " +
           range_->toFunctionalSyntax() + ")";
}

std::string FunctionalObjectProperty::toFunctionalSyntax() const {
    return "FunctionalObjectProperty(" + formatAnnotations() +
           formatObjectPropertyExpression(property_) + ")";
}

std::string InverseFunctionalObjectProperty::toFunctionalSyntax() const {
    return "InverseFunctionalObjectProperty(" + formatAnnotations() +
           formatObjectPropertyExpression(property_) + ")";
}

std::string ReflexiveObjectProperty::toFunctionalSyntax() const {
    return "ReflexiveObjectProperty(" + formatAnnotations() +
           formatObjectPropertyExpression(property_) + ")";
}

std::string IrreflexiveObjectProperty::toFunctionalSyntax() const {
    return "IrreflexiveObjectProperty(" + formatAnnotations() +
           formatObjectPropertyExpression(property_) + ")";
}

std::string SymmetricObjectProperty::toFunctionalSyntax() const {
    return "SymmetricObjectProperty(" + formatAnnotations() +
           formatObjectPropertyExpression(property_) + ")";
}

std::string AsymmetricObjectProperty::toFunctionalSyntax() const {
    return "AsymmetricObjectProperty(" + formatAnnotations() +
           formatObjectPropertyExpression(property_) + ")";
}

std::string TransitiveObjectProperty::toFunctionalSyntax() const {
    return "TransitiveObjectProperty(" + formatAnnotations() +
           formatObjectPropertyExpression(property_) + ")";
}

// ============================================================================
// DATA PROPERTY AXIOMS
// ============================================================================

std::string SubDataPropertyOf::toFunctionalSyntax() const {
    return "SubDataPropertyOf(" + formatAnnotations() +
           "<" + sub_property_.getIRI().toString() + "> " +
           "<" + super_property_.getIRI().toString() + ">)";
}

std::string EquivalentDataProperties::toFunctionalSyntax() const {
    std::string result = "EquivalentDataProperties(" + formatAnnotations();
    for (const auto& prop : properties_) {
        result += "<" + prop.getIRI().toString() + "> ";
    }
    result.pop_back();
    return result + ")";
}

std::string DisjointDataProperties::toFunctionalSyntax() const {
    std::string result = "DisjointDataProperties(" + formatAnnotations();
    for (const auto& prop : properties_) {
        result += "<" + prop.getIRI().toString() + "> ";
    }
    result.pop_back();
    return result + ")";
}

std::string DataPropertyDomain::toFunctionalSyntax() const {
    return "DataPropertyDomain(" + formatAnnotations() +
           "<" + property_.getIRI().toString() + "> " +
           domain_->toFunctionalSyntax() + ")";
}

std::string DataPropertyRange::toFunctionalSyntax() const {
    return "DataPropertyRange(" + formatAnnotations() +
           "<" + property_.getIRI().toString() + "> " +
           range_->toFunctionalSyntax() + ")";
}

std::string FunctionalDataProperty::toFunctionalSyntax() const {
    return "FunctionalDataProperty(" + formatAnnotations() +
           "<" + property_.getIRI().toString() + ">)";
}

// ============================================================================
// DATATYPE DEFINITION AXIOM
// ============================================================================

std::string DatatypeDefinition::toFunctionalSyntax() const {
    return "DatatypeDefinition(" + formatAnnotations() +
           "<" + datatype_.getIRI().toString() + "> " +
           data_range_->toFunctionalSyntax() + ")";
}

// ============================================================================
// KEYS AXIOM
// ============================================================================

std::string HasKey::toFunctionalSyntax() const {
    std::string result = "HasKey(" + formatAnnotations() +
                        class_expression_->toFunctionalSyntax() + " (";
    
    for (const auto& prop : object_properties_) {
        result += formatObjectPropertyExpression(prop) + " ";
    }
    for (const auto& prop : data_properties_) {
        result += "<" + prop.getIRI().toString() + "> ";
    }
    
    if (!object_properties_.empty() || !data_properties_.empty()) {
        result.pop_back();
    }
    
    return result + "))";
}

// ============================================================================
// ASSERTION AXIOMS
// ============================================================================

std::string SameIndividual::toFunctionalSyntax() const {
    std::string result = "SameIndividual(" + formatAnnotations();
    for (const auto& ind : individuals_) {
        result += formatIndividual(ind) + " ";
    }
    result.pop_back();
    return result + ")";
}

std::string DifferentIndividuals::toFunctionalSyntax() const {
    std::string result = "DifferentIndividuals(" + formatAnnotations();
    for (const auto& ind : individuals_) {
        result += formatIndividual(ind) + " ";
    }
    result.pop_back();
    return result + ")";
}

std::string ClassAssertion::toFunctionalSyntax() const {
    return "ClassAssertion(" + formatAnnotations() +
           class_expression_->toFunctionalSyntax() + " " +
           formatIndividual(individual_) + ")";
}

std::string ObjectPropertyAssertion::toFunctionalSyntax() const {
    return "ObjectPropertyAssertion(" + formatAnnotations() +
           formatObjectPropertyExpression(property_) + " " +
           formatIndividual(source_) + " " +
           formatIndividual(target_) + ")";
}

std::string NegativeObjectPropertyAssertion::toFunctionalSyntax() const {
    return "NegativeObjectPropertyAssertion(" + formatAnnotations() +
           formatObjectPropertyExpression(property_) + " " +
           formatIndividual(source_) + " " +
           formatIndividual(target_) + ")";
}

std::string DataPropertyAssertion::toFunctionalSyntax() const {
    return "DataPropertyAssertion(" + formatAnnotations() +
           "<" + property_.getIRI().toString() + "> " +
           formatIndividual(source_) + " " +
           target_.toString() + ")";
}

std::string NegativeDataPropertyAssertion::toFunctionalSyntax() const {
    return "NegativeDataPropertyAssertion(" + formatAnnotations() +
           "<" + property_.getIRI().toString() + "> " +
           formatIndividual(source_) + " " +
           target_.toString() + ")";
}

// ============================================================================
// ANNOTATION AXIOMS
// ============================================================================

std::string AnnotationAssertion::toFunctionalSyntax() const {
    return "AnnotationAssertion(" + formatAnnotations() +
           "<" + property_.getIRI().toString() + "> " +
           formatAnnotationSubject(subject_) + " " +
           formatAnnotationValue(value_) + ")";
}

std::string SubAnnotationPropertyOf::toFunctionalSyntax() const {
    return "SubAnnotationPropertyOf(" + formatAnnotations() +
           "<" + sub_property_.getIRI().toString() + "> " +
           "<" + super_property_.getIRI().toString() + ">)";
}

std::string AnnotationPropertyDomain::toFunctionalSyntax() const {
    return "AnnotationPropertyDomain(" + formatAnnotations() +
           "<" + property_.getIRI().toString() + "> " +
           "<" + domain_.toString() + ">)";
}

std::string AnnotationPropertyRange::toFunctionalSyntax() const {
    return "AnnotationPropertyRange(" + formatAnnotations() +
           "<" + property_.getIRI().toString() + "> " +
           "<" + range_.toString() + ">)";
}

} // namespace owl2
} // namespace ista
