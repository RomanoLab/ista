#ifndef ISTA_OWL2_CLASS_EXPRESSION_HPP
#define ISTA_OWL2_CLASS_EXPRESSION_HPP

#include "entity.hpp"
#include "literal.hpp"
#include <vector>
#include <memory>

namespace ista {
namespace owl2 {

// Forward declarations
class DataRange;
using DataRangePtr = std::shared_ptr<DataRange>;

class ClassExpression {
public:
    virtual ~ClassExpression() = default;
    virtual std::string toFunctionalSyntax() const = 0;
    virtual std::string getExpressionType() const = 0;
};

using ClassExpressionPtr = std::shared_ptr<ClassExpression>;

class NamedClass : public ClassExpression {
public:
    explicit NamedClass(const Class& cls) : class_(cls) {}
    Class getClass() const { return class_; }
    std::string toFunctionalSyntax() const override;
    std::string getExpressionType() const override { return "NamedClass"; }
private:
    Class class_;
};

class ObjectIntersectionOf : public ClassExpression {
public:
    explicit ObjectIntersectionOf(const std::vector<ClassExpressionPtr>& operands)
        : operands_(operands) {}
    std::vector<ClassExpressionPtr> getOperands() const { return operands_; }
    std::string toFunctionalSyntax() const override;
    std::string getExpressionType() const override { return "ObjectIntersectionOf"; }
private:
    std::vector<ClassExpressionPtr> operands_;
};

class ObjectUnionOf : public ClassExpression {
public:
    explicit ObjectUnionOf(const std::vector<ClassExpressionPtr>& operands)
        : operands_(operands) {}
    std::vector<ClassExpressionPtr> getOperands() const { return operands_; }
    std::string toFunctionalSyntax() const override;
    std::string getExpressionType() const override { return "ObjectUnionOf"; }
private:
    std::vector<ClassExpressionPtr> operands_;
};

class ObjectSomeValuesFrom : public ClassExpression {
public:
    ObjectSomeValuesFrom(const ObjectProperty& property, const ClassExpressionPtr& filler)
        : property_(property), filler_(filler) {}
    ObjectProperty getProperty() const { return property_; }
    ClassExpressionPtr getFiller() const { return filler_; }
    std::string toFunctionalSyntax() const override;
    std::string getExpressionType() const override { return "ObjectSomeValuesFrom"; }
private:
    ObjectProperty property_;
    ClassExpressionPtr filler_;
};

class ObjectAllValuesFrom : public ClassExpression {
public:
    ObjectAllValuesFrom(const ObjectProperty& property, const ClassExpressionPtr& filler)
        : property_(property), filler_(filler) {}
    ObjectProperty getProperty() const { return property_; }
    ClassExpressionPtr getFiller() const { return filler_; }
    std::string toFunctionalSyntax() const override;
    std::string getExpressionType() const override { return "ObjectAllValuesFrom"; }
private:
    ObjectProperty property_;
    ClassExpressionPtr filler_;
};

} // namespace owl2
} // namespace ista

#endif
