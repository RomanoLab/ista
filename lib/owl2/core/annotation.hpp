#ifndef ISTA_OWL2_ANNOTATION_HPP
#define ISTA_OWL2_ANNOTATION_HPP

#include "entity.hpp"
#include "literal.hpp"
#include <variant>
#include <memory>
#include <vector>

namespace ista {
namespace owl2 {

/**
 * @brief Represents an OWL2 annotation value
 * 
 * An annotation value can be an IRI, a Literal, or an AnonymousIndividual.
 */
using AnnotationValue = std::variant<IRI, Literal, AnonymousIndividual>;

/**
 * @brief Represents an OWL2 annotation
 * 
 * Annotations provide metadata about ontology elements using annotation properties.
 */
class Annotation {
public:
    /**
     * @brief Construct an annotation with a property and value
     * @param property The annotation property
     * @param value The annotation value (IRI, Literal, or AnonymousIndividual)
     */
    Annotation(const AnnotationProperty& property, const AnnotationValue& value)
        : property_(property), value_(value) {}
    
    /**
     * @brief Construct an annotation with nested annotations
     * @param property The annotation property
     * @param value The annotation value
     * @param annotations Nested annotations on this annotation
     */
    Annotation(const AnnotationProperty& property, 
              const AnnotationValue& value,
              const std::vector<Annotation>& annotations)
        : property_(property), value_(value), annotations_(annotations) {}
    
    /**
     * @brief Get the annotation property
     */
    AnnotationProperty getProperty() const { return property_; }
    
    /**
     * @brief Get the annotation value
     */
    AnnotationValue getValue() const { return value_; }
    
    /**
     * @brief Get nested annotations
     */
    std::vector<Annotation> getAnnotations() const { return annotations_; }
    
    /**
     * @brief Check if this annotation has nested annotations
     */
    bool hasAnnotations() const { return !annotations_.empty(); }
    
    /**
     * @brief Set the annotation property
     */
    void setProperty(const AnnotationProperty& property) { property_ = property; }
    
    /**
     * @brief Set the annotation value
     */
    void setValue(const AnnotationValue& value) { value_ = value; }
    
    /**
     * @brief Add a nested annotation
     */
    void addAnnotation(const Annotation& annotation) {
        annotations_.push_back(annotation);
    }
    
    /**
     * @brief Convert to OWL2 Functional Syntax
     */
    std::string toFunctionalSyntax() const;
    
    /**
     * @brief Get the value as a string representation
     */
    std::string getValueAsString() const;
    
    // Comparison operators
    bool operator==(const Annotation& other) const;
    bool operator!=(const Annotation& other) const { return !(*this == other); }

private:
    AnnotationProperty property_;
    AnnotationValue value_;
    std::vector<Annotation> annotations_;
};

using AnnotationPtr = std::shared_ptr<Annotation>;

/**
 * @brief Helper function to create an annotation with an IRI value
 */
inline Annotation makeAnnotation(const AnnotationProperty& property, const IRI& value) {
    return Annotation(property, value);
}

/**
 * @brief Helper function to create an annotation with a Literal value
 */
inline Annotation makeAnnotation(const AnnotationProperty& property, const Literal& value) {
    return Annotation(property, value);
}

/**
 * @brief Helper function to create an annotation with an AnonymousIndividual value
 */
inline Annotation makeAnnotation(const AnnotationProperty& property, const AnonymousIndividual& value) {
    return Annotation(property, value);
}

} // namespace owl2
} // namespace ista

#endif // ISTA_OWL2_ANNOTATION_HPP
