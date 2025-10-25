#ifndef ISTA_OWL2_AXIOM_HPP
#define ISTA_OWL2_AXIOM_HPP

#include "entity.hpp"
#include "class_expression.hpp"
#include "data_range.hpp"
#include "literal.hpp"
#include "annotation.hpp"
#include <vector>
#include <memory>
#include <optional>
#include <variant>

namespace ista {
namespace owl2 {

/**
 * @brief Base class for all OWL2 axioms
 *
 * All axioms can have annotations attached to them.
 */
class Axiom {
public:
    virtual ~Axiom() = default;

    /**
     * @brief Convert to OWL2 Functional Syntax
     */
    virtual std::string toFunctionalSyntax() const = 0;

    /**
     * @brief Get the type of this axiom
     */
    virtual std::string getAxiomType() const = 0;

    /**
     * @brief Get annotations on this axiom
     */
    std::vector<Annotation> getAnnotations() const { return annotations_; }

    /**
     * @brief Check if this axiom has annotations
     */
    bool hasAnnotations() const { return !annotations_.empty(); }

    /**
     * @brief Add an annotation to this axiom
     */
    void addAnnotation(const Annotation& annotation) {
        annotations_.push_back(annotation);
    }

    /**
     * @brief Set all annotations
     */
    void setAnnotations(const std::vector<Annotation>& annotations) {
        annotations_ = annotations;
    }

protected:
    std::vector<Annotation> annotations_;

    /**
     * @brief Helper to format annotations in functional syntax
     */
    std::string formatAnnotations() const;
};

using AxiomPtr = std::shared_ptr<Axiom>;

// ============================================================================
// DECLARATION AXIOMS
// ============================================================================

/**
 * @brief Declares an entity in the ontology
 */
class Declaration : public Axiom {
public:
    enum class EntityType {
        CLASS,
        DATATYPE,
        OBJECT_PROPERTY,
        DATA_PROPERTY,
        ANNOTATION_PROPERTY,
        NAMED_INDIVIDUAL
    };

    Declaration(EntityType type, const IRI& iri)
        : entity_type_(type), iri_(iri) {}

    EntityType getEntityType() const { return entity_type_; }
    IRI getIRI() const { return iri_; }

    std::string toFunctionalSyntax() const override;
    std::string getAxiomType() const override { return "Declaration"; }

private:
    EntityType entity_type_;
    IRI iri_;
};

// ============================================================================
// CLASS AXIOMS
// ============================================================================

/**
 * @brief SubClassOf axiom: C1 ⊑ C2
 */
class SubClassOf : public Axiom {
public:
    SubClassOf(const ClassExpressionPtr& subclass,
               const ClassExpressionPtr& superclass)
        : subclass_(subclass), superclass_(superclass) {}

    ClassExpressionPtr getSubClass() const { return subclass_; }
    ClassExpressionPtr getSuperClass() const { return superclass_; }

    std::string toFunctionalSyntax() const override;
    std::string getAxiomType() const override { return "SubClassOf"; }

private:
    ClassExpressionPtr subclass_;
    ClassExpressionPtr superclass_;
};

/**
 * @brief EquivalentClasses axiom: C1 ≡ C2 ≡ ... ≡ Cn
 */
class EquivalentClasses : public Axiom {
public:
    explicit EquivalentClasses(const std::vector<ClassExpressionPtr>& class_expressions)
        : class_expressions_(class_expressions) {}

    std::vector<ClassExpressionPtr> getClassExpressions() const {
        return class_expressions_;
    }

    std::string toFunctionalSyntax() const override;
    std::string getAxiomType() const override { return "EquivalentClasses"; }

private:
    std::vector<ClassExpressionPtr> class_expressions_;
};

/**
 * @brief DisjointClasses axiom: all pairs are disjoint
 */
class DisjointClasses : public Axiom {
public:
    explicit DisjointClasses(const std::vector<ClassExpressionPtr>& class_expressions)
        : class_expressions_(class_expressions) {}

    std::vector<ClassExpressionPtr> getClassExpressions() const {
        return class_expressions_;
    }

    std::string toFunctionalSyntax() const override;
    std::string getAxiomType() const override { return "DisjointClasses"; }

private:
    std::vector<ClassExpressionPtr> class_expressions_;
};

/**
 * @brief DisjointUnion axiom: C ≡ C1 ⊔ ... ⊔ Cn where all Ci are pairwise disjoint
 */
class DisjointUnion : public Axiom {
public:
    DisjointUnion(const Class& cls,
                  const std::vector<ClassExpressionPtr>& class_expressions)
        : class_(cls), class_expressions_(class_expressions) {}

    Class getClass() const { return class_; }
    std::vector<ClassExpressionPtr> getClassExpressions() const {
        return class_expressions_;
    }

    std::string toFunctionalSyntax() const override;
    std::string getAxiomType() const override { return "DisjointUnion"; }

private:
    Class class_;
    std::vector<ClassExpressionPtr> class_expressions_;
};

// ============================================================================
// OBJECT PROPERTY AXIOMS
// ============================================================================

/**
 * @brief Object property expression - can be a property or its inverse
 */
using ObjectPropertyExpression = std::variant<ObjectProperty, std::pair<ObjectProperty, bool>>;

/**
 * @brief SubObjectPropertyOf axiom
 */
class SubObjectPropertyOf : public Axiom {
public:
    SubObjectPropertyOf(const ObjectPropertyExpression& sub_property,
                        const ObjectPropertyExpression& super_property)
        : sub_property_(sub_property), super_property_(super_property) {}

    // Constructor for property chains
    SubObjectPropertyOf(const std::vector<ObjectPropertyExpression>& property_chain,
                        const ObjectPropertyExpression& super_property)
        : property_chain_(property_chain), super_property_(super_property) {}

    std::optional<ObjectPropertyExpression> getSubProperty() const { return sub_property_; }
    ObjectPropertyExpression getSuperProperty() const { return super_property_; }
    std::vector<ObjectPropertyExpression> getPropertyChain() const { return property_chain_; }
    bool isPropertyChain() const { return !property_chain_.empty(); }

    std::string toFunctionalSyntax() const override;
    std::string getAxiomType() const override { return "SubObjectPropertyOf"; }

private:
    std::optional<ObjectPropertyExpression> sub_property_;
    std::vector<ObjectPropertyExpression> property_chain_;
    ObjectPropertyExpression super_property_;
};

/**
 * @brief EquivalentObjectProperties axiom
 */
class EquivalentObjectProperties : public Axiom {
public:
    explicit EquivalentObjectProperties(
        const std::vector<ObjectPropertyExpression>& properties)
        : properties_(properties) {}

    std::vector<ObjectPropertyExpression> getProperties() const { return properties_; }

    std::string toFunctionalSyntax() const override;
    std::string getAxiomType() const override { return "EquivalentObjectProperties"; }

private:
    std::vector<ObjectPropertyExpression> properties_;
};

/**
 * @brief DisjointObjectProperties axiom
 */
class DisjointObjectProperties : public Axiom {
public:
    explicit DisjointObjectProperties(
        const std::vector<ObjectPropertyExpression>& properties)
        : properties_(properties) {}

    std::vector<ObjectPropertyExpression> getProperties() const { return properties_; }

    std::string toFunctionalSyntax() const override;
    std::string getAxiomType() const override { return "DisjointObjectProperties"; }

private:
    std::vector<ObjectPropertyExpression> properties_;
};

/**
 * @brief InverseObjectProperties axiom
 */
class InverseObjectProperties : public Axiom {
public:
    InverseObjectProperties(const ObjectPropertyExpression& property1,
                           const ObjectPropertyExpression& property2)
        : property1_(property1), property2_(property2) {}

    ObjectPropertyExpression getProperty1() const { return property1_; }
    ObjectPropertyExpression getProperty2() const { return property2_; }

    std::string toFunctionalSyntax() const override;
    std::string getAxiomType() const override { return "InverseObjectProperties"; }

private:
    ObjectPropertyExpression property1_;
    ObjectPropertyExpression property2_;
};

/**
 * @brief ObjectPropertyDomain axiom
 */
class ObjectPropertyDomain : public Axiom {
public:
    ObjectPropertyDomain(const ObjectPropertyExpression& property,
                        const ClassExpressionPtr& domain)
        : property_(property), domain_(domain) {}

    ObjectPropertyExpression getProperty() const { return property_; }
    ClassExpressionPtr getDomain() const { return domain_; }

    std::string toFunctionalSyntax() const override;
    std::string getAxiomType() const override { return "ObjectPropertyDomain"; }

private:
    ObjectPropertyExpression property_;
    ClassExpressionPtr domain_;
};

/**
 * @brief ObjectPropertyRange axiom
 */
class ObjectPropertyRange : public Axiom {
public:
    ObjectPropertyRange(const ObjectPropertyExpression& property,
                       const ClassExpressionPtr& range)
        : property_(property), range_(range) {}

    ObjectPropertyExpression getProperty() const { return property_; }
    ClassExpressionPtr getRange() const { return range_; }

    std::string toFunctionalSyntax() const override;
    std::string getAxiomType() const override { return "ObjectPropertyRange"; }

private:
    ObjectPropertyExpression property_;
    ClassExpressionPtr range_;
};

/**
 * @brief FunctionalObjectProperty axiom
 */
class FunctionalObjectProperty : public Axiom {
public:
    explicit FunctionalObjectProperty(const ObjectPropertyExpression& property)
        : property_(property) {}

    ObjectPropertyExpression getProperty() const { return property_; }

    std::string toFunctionalSyntax() const override;
    std::string getAxiomType() const override { return "FunctionalObjectProperty"; }

private:
    ObjectPropertyExpression property_;
};

/**
 * @brief InverseFunctionalObjectProperty axiom
 */
class InverseFunctionalObjectProperty : public Axiom {
public:
    explicit InverseFunctionalObjectProperty(const ObjectPropertyExpression& property)
        : property_(property) {}

    ObjectPropertyExpression getProperty() const { return property_; }

    std::string toFunctionalSyntax() const override;
    std::string getAxiomType() const override { return "InverseFunctionalObjectProperty"; }

private:
    ObjectPropertyExpression property_;
};

/**
 * @brief ReflexiveObjectProperty axiom
 */
class ReflexiveObjectProperty : public Axiom {
public:
    explicit ReflexiveObjectProperty(const ObjectPropertyExpression& property)
        : property_(property) {}

    ObjectPropertyExpression getProperty() const { return property_; }

    std::string toFunctionalSyntax() const override;
    std::string getAxiomType() const override { return "ReflexiveObjectProperty"; }

private:
    ObjectPropertyExpression property_;
};

/**
 * @brief IrreflexiveObjectProperty axiom
 */
class IrreflexiveObjectProperty : public Axiom {
public:
    explicit IrreflexiveObjectProperty(const ObjectPropertyExpression& property)
        : property_(property) {}

    ObjectPropertyExpression getProperty() const { return property_; }

    std::string toFunctionalSyntax() const override;
    std::string getAxiomType() const override { return "IrreflexiveObjectProperty"; }

private:
    ObjectPropertyExpression property_;
};

/**
 * @brief SymmetricObjectProperty axiom
 */
class SymmetricObjectProperty : public Axiom {
public:
    explicit SymmetricObjectProperty(const ObjectPropertyExpression& property)
        : property_(property) {}

    ObjectPropertyExpression getProperty() const { return property_; }

    std::string toFunctionalSyntax() const override;
    std::string getAxiomType() const override { return "SymmetricObjectProperty"; }

private:
    ObjectPropertyExpression property_;
};

/**
 * @brief AsymmetricObjectProperty axiom
 */
class AsymmetricObjectProperty : public Axiom {
public:
    explicit AsymmetricObjectProperty(const ObjectPropertyExpression& property)
        : property_(property) {}

    ObjectPropertyExpression getProperty() const { return property_; }

    std::string toFunctionalSyntax() const override;
    std::string getAxiomType() const override { return "AsymmetricObjectProperty"; }

private:
    ObjectPropertyExpression property_;
};

/**
 * @brief TransitiveObjectProperty axiom
 */
class TransitiveObjectProperty : public Axiom {
public:
    explicit TransitiveObjectProperty(const ObjectPropertyExpression& property)
        : property_(property) {}

    ObjectPropertyExpression getProperty() const { return property_; }

    std::string toFunctionalSyntax() const override;
    std::string getAxiomType() const override { return "TransitiveObjectProperty"; }

private:
    ObjectPropertyExpression property_;
};

// ============================================================================
// DATA PROPERTY AXIOMS
// ============================================================================

/**
 * @brief SubDataPropertyOf axiom
 */
class SubDataPropertyOf : public Axiom {
public:
    SubDataPropertyOf(const DataProperty& sub_property,
                     const DataProperty& super_property)
        : sub_property_(sub_property), super_property_(super_property) {}

    DataProperty getSubProperty() const { return sub_property_; }
    DataProperty getSuperProperty() const { return super_property_; }

    std::string toFunctionalSyntax() const override;
    std::string getAxiomType() const override { return "SubDataPropertyOf"; }

private:
    DataProperty sub_property_;
    DataProperty super_property_;
};

/**
 * @brief EquivalentDataProperties axiom
 */
class EquivalentDataProperties : public Axiom {
public:
    explicit EquivalentDataProperties(const std::vector<DataProperty>& properties)
        : properties_(properties) {}

    std::vector<DataProperty> getProperties() const { return properties_; }

    std::string toFunctionalSyntax() const override;
    std::string getAxiomType() const override { return "EquivalentDataProperties"; }

private:
    std::vector<DataProperty> properties_;
};

/**
 * @brief DisjointDataProperties axiom
 */
class DisjointDataProperties : public Axiom {
public:
    explicit DisjointDataProperties(const std::vector<DataProperty>& properties)
        : properties_(properties) {}

    std::vector<DataProperty> getProperties() const { return properties_; }

    std::string toFunctionalSyntax() const override;
    std::string getAxiomType() const override { return "DisjointDataProperties"; }

private:
    std::vector<DataProperty> properties_;
};

/**
 * @brief DataPropertyDomain axiom
 */
class DataPropertyDomain : public Axiom {
public:
    DataPropertyDomain(const DataProperty& property,
                      const ClassExpressionPtr& domain)
        : property_(property), domain_(domain) {}

    DataProperty getProperty() const { return property_; }
    ClassExpressionPtr getDomain() const { return domain_; }

    std::string toFunctionalSyntax() const override;
    std::string getAxiomType() const override { return "DataPropertyDomain"; }

private:
    DataProperty property_;
    ClassExpressionPtr domain_;
};

/**
 * @brief DataPropertyRange axiom
 */
class DataPropertyRange : public Axiom {
public:
    DataPropertyRange(const DataProperty& property,
                     const DataRangePtr& range)
        : property_(property), range_(range) {}

    DataProperty getProperty() const { return property_; }
    DataRangePtr getRange() const { return range_; }

    std::string toFunctionalSyntax() const override;
    std::string getAxiomType() const override { return "DataPropertyRange"; }

private:
    DataProperty property_;
    DataRangePtr range_;
};

/**
 * @brief FunctionalDataProperty axiom
 */
class FunctionalDataProperty : public Axiom {
public:
    explicit FunctionalDataProperty(const DataProperty& property)
        : property_(property) {}

    DataProperty getProperty() const { return property_; }

    std::string toFunctionalSyntax() const override;
    std::string getAxiomType() const override { return "FunctionalDataProperty"; }

private:
    DataProperty property_;
};

// ============================================================================
// DATATYPE DEFINITION AXIOM
// ============================================================================

/**
 * @brief DatatypeDefinition axiom
 */
class DatatypeDefinition : public Axiom {
public:
    DatatypeDefinition(const Datatype& datatype, const DataRangePtr& data_range)
        : datatype_(datatype), data_range_(data_range) {}

    Datatype getDatatype() const { return datatype_; }
    DataRangePtr getDataRange() const { return data_range_; }

    std::string toFunctionalSyntax() const override;
    std::string getAxiomType() const override { return "DatatypeDefinition"; }

private:
    Datatype datatype_;
    DataRangePtr data_range_;
};

// ============================================================================
// KEYS AXIOM
// ============================================================================

/**
 * @brief HasKey axiom
 */
class HasKey : public Axiom {
public:
    HasKey(const ClassExpressionPtr& class_expression,
           const std::vector<ObjectPropertyExpression>& object_properties,
           const std::vector<DataProperty>& data_properties)
        : class_expression_(class_expression),
          object_properties_(object_properties),
          data_properties_(data_properties) {}

    ClassExpressionPtr getClassExpression() const { return class_expression_; }
    std::vector<ObjectPropertyExpression> getObjectProperties() const {
        return object_properties_;
    }
    std::vector<DataProperty> getDataProperties() const { return data_properties_; }

    std::string toFunctionalSyntax() const override;
    std::string getAxiomType() const override { return "HasKey"; }

private:
    ClassExpressionPtr class_expression_;
    std::vector<ObjectPropertyExpression> object_properties_;
    std::vector<DataProperty> data_properties_;
};

// ============================================================================
// ASSERTION AXIOMS
// ============================================================================

/**
 * @brief Individual - can be named or anonymous
 */
using Individual = std::variant<NamedIndividual, AnonymousIndividual>;

/**
 * @brief SameIndividual axiom
 */
class SameIndividual : public Axiom {
public:
    explicit SameIndividual(const std::vector<Individual>& individuals)
        : individuals_(individuals) {}

    std::vector<Individual> getIndividuals() const { return individuals_; }

    std::string toFunctionalSyntax() const override;
    std::string getAxiomType() const override { return "SameIndividual"; }

private:
    std::vector<Individual> individuals_;
};

/**
 * @brief DifferentIndividuals axiom
 */
class DifferentIndividuals : public Axiom {
public:
    explicit DifferentIndividuals(const std::vector<Individual>& individuals)
        : individuals_(individuals) {}

    std::vector<Individual> getIndividuals() const { return individuals_; }

    std::string toFunctionalSyntax() const override;
    std::string getAxiomType() const override { return "DifferentIndividuals"; }

private:
    std::vector<Individual> individuals_;
};

/**
 * @brief ClassAssertion axiom
 */
class ClassAssertion : public Axiom {
public:
    ClassAssertion(const ClassExpressionPtr& class_expression,
                  const Individual& individual)
        : class_expression_(class_expression), individual_(individual) {}

    ClassExpressionPtr getClassExpression() const { return class_expression_; }
    Individual getIndividual() const { return individual_; }

    std::string toFunctionalSyntax() const override;
    std::string getAxiomType() const override { return "ClassAssertion"; }

private:
    ClassExpressionPtr class_expression_;
    Individual individual_;
};

/**
 * @brief ObjectPropertyAssertion axiom
 */
class ObjectPropertyAssertion : public Axiom {
public:
    ObjectPropertyAssertion(const ObjectPropertyExpression& property,
                           const Individual& source,
                           const Individual& target)
        : property_(property), source_(source), target_(target) {}

    ObjectPropertyExpression getProperty() const { return property_; }
    Individual getSource() const { return source_; }
    Individual getTarget() const { return target_; }

    std::string toFunctionalSyntax() const override;
    std::string getAxiomType() const override { return "ObjectPropertyAssertion"; }

private:
    ObjectPropertyExpression property_;
    Individual source_;
    Individual target_;
};

/**
 * @brief NegativeObjectPropertyAssertion axiom
 */
class NegativeObjectPropertyAssertion : public Axiom {
public:
    NegativeObjectPropertyAssertion(const ObjectPropertyExpression& property,
                                   const Individual& source,
                                   const Individual& target)
        : property_(property), source_(source), target_(target) {}

    ObjectPropertyExpression getProperty() const { return property_; }
    Individual getSource() const { return source_; }
    Individual getTarget() const { return target_; }

    std::string toFunctionalSyntax() const override;
    std::string getAxiomType() const override { return "NegativeObjectPropertyAssertion"; }

private:
    ObjectPropertyExpression property_;
    Individual source_;
    Individual target_;
};

/**
 * @brief DataPropertyAssertion axiom
 */
class DataPropertyAssertion : public Axiom {
public:
    DataPropertyAssertion(const DataProperty& property,
                         const Individual& source,
                         const Literal& target)
        : property_(property), source_(source), target_(target) {}

    DataProperty getProperty() const { return property_; }
    Individual getSource() const { return source_; }
    Literal getTarget() const { return target_; }

    std::string toFunctionalSyntax() const override;
    std::string getAxiomType() const override { return "DataPropertyAssertion"; }

private:
    DataProperty property_;
    Individual source_;
    Literal target_;
};

/**
 * @brief NegativeDataPropertyAssertion axiom
 */
class NegativeDataPropertyAssertion : public Axiom {
public:
    NegativeDataPropertyAssertion(const DataProperty& property,
                                 const Individual& source,
                                 const Literal& target)
        : property_(property), source_(source), target_(target) {}

    DataProperty getProperty() const { return property_; }
    Individual getSource() const { return source_; }
    Literal getTarget() const { return target_; }

    std::string toFunctionalSyntax() const override;
    std::string getAxiomType() const override { return "NegativeDataPropertyAssertion"; }

private:
    DataProperty property_;
    Individual source_;
    Literal target_;
};

// ============================================================================
// ANNOTATION AXIOMS
// ============================================================================

/**
 * @brief Annotation subject - can be IRI or anonymous individual
 */
using AnnotationSubject = std::variant<IRI, AnonymousIndividual>;

/**
 * @brief AnnotationAssertion axiom
 */
class AnnotationAssertion : public Axiom {
public:
    AnnotationAssertion(const AnnotationProperty& property,
                       const AnnotationSubject& subject,
                       const AnnotationValue& value)
        : property_(property), subject_(subject), value_(value) {}

    AnnotationProperty getProperty() const { return property_; }
    AnnotationSubject getSubject() const { return subject_; }
    AnnotationValue getValue() const { return value_; }

    std::string toFunctionalSyntax() const override;
    std::string getAxiomType() const override { return "AnnotationAssertion"; }

private:
    AnnotationProperty property_;
    AnnotationSubject subject_;
    AnnotationValue value_;
};

/**
 * @brief SubAnnotationPropertyOf axiom
 */
class SubAnnotationPropertyOf : public Axiom {
public:
    SubAnnotationPropertyOf(const AnnotationProperty& sub_property,
                           const AnnotationProperty& super_property)
        : sub_property_(sub_property), super_property_(super_property) {}

    AnnotationProperty getSubProperty() const { return sub_property_; }
    AnnotationProperty getSuperProperty() const { return super_property_; }

    std::string toFunctionalSyntax() const override;
    std::string getAxiomType() const override { return "SubAnnotationPropertyOf"; }

private:
    AnnotationProperty sub_property_;
    AnnotationProperty super_property_;
};

/**
 * @brief AnnotationPropertyDomain axiom
 */
class AnnotationPropertyDomain : public Axiom {
public:
    AnnotationPropertyDomain(const AnnotationProperty& property, const IRI& domain)
        : property_(property), domain_(domain) {}

    AnnotationProperty getProperty() const { return property_; }
    IRI getDomain() const { return domain_; }

    std::string toFunctionalSyntax() const override;
    std::string getAxiomType() const override { return "AnnotationPropertyDomain"; }

private:
    AnnotationProperty property_;
    IRI domain_;
};

/**
 * @brief AnnotationPropertyRange axiom
 */
class AnnotationPropertyRange : public Axiom {
public:
    AnnotationPropertyRange(const AnnotationProperty& property, const IRI& range)
        : property_(property), range_(range) {}

    AnnotationProperty getProperty() const { return property_; }
    IRI getRange() const { return range_; }

    std::string toFunctionalSyntax() const override;
    std::string getAxiomType() const override { return "AnnotationPropertyRange"; }

private:
    AnnotationProperty property_;
    IRI range_;
};

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

/**
 * @brief Format an object property expression in functional syntax
 */
std::string formatObjectPropertyExpression(const ObjectPropertyExpression& ope);

/**
 * @brief Format an individual in functional syntax
 */
std::string formatIndividual(const Individual& individual);

/**
 * @brief Format an annotation subject in functional syntax
 */
std::string formatAnnotationSubject(const AnnotationSubject& subject);

/**
 * @brief Format an annotation value in functional syntax
 */
std::string formatAnnotationValue(const AnnotationValue& value);

} // namespace owl2
} // namespace ista

#endif // ISTA_OWL2_AXIOM_HPP
