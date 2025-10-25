#ifndef ISTA_OWL2_DATA_RANGE_HPP
#define ISTA_OWL2_DATA_RANGE_HPP

#include "entity.hpp"
#include "literal.hpp"
#include <vector>
#include <memory>
#include <utility>

namespace ista {
namespace owl2 {

/**
 * @brief Base class for all OWL2 data ranges
 * 
 * Data ranges describe sets of data values.
 */
class DataRange {
public:
    virtual ~DataRange() = default;
    
    /**
     * @brief Convert to OWL2 Functional Syntax
     */
    virtual std::string toFunctionalSyntax() const = 0;
    
    /**
     * @brief Get the type of this data range
     */
    virtual std::string getDataRangeType() const = 0;
};

using DataRangePtr = std::shared_ptr<DataRange>;

/**
 * @brief Named datatype (wraps a Datatype entity)
 */
class NamedDatatype : public DataRange {
public:
    explicit NamedDatatype(const Datatype& datatype) : datatype_(datatype) {}
    
    Datatype getDatatype() const { return datatype_; }
    
    std::string toFunctionalSyntax() const override;
    std::string getDataRangeType() const override { return "NamedDatatype"; }

private:
    Datatype datatype_;
};

/**
 * @brief Intersection of data ranges
 */
class DataIntersectionOf : public DataRange {
public:
    explicit DataIntersectionOf(const std::vector<DataRangePtr>& operands)
        : operands_(operands) {}
    
    std::vector<DataRangePtr> getOperands() const { return operands_; }
    
    std::string toFunctionalSyntax() const override;
    std::string getDataRangeType() const override { return "DataIntersectionOf"; }

private:
    std::vector<DataRangePtr> operands_;
};

/**
 * @brief Union of data ranges
 */
class DataUnionOf : public DataRange {
public:
    explicit DataUnionOf(const std::vector<DataRangePtr>& operands)
        : operands_(operands) {}
    
    std::vector<DataRangePtr> getOperands() const { return operands_; }
    
    std::string toFunctionalSyntax() const override;
    std::string getDataRangeType() const override { return "DataUnionOf"; }

private:
    std::vector<DataRangePtr> operands_;
};

/**
 * @brief Complement of a data range
 */
class DataComplementOf : public DataRange {
public:
    explicit DataComplementOf(const DataRangePtr& data_range)
        : data_range_(data_range) {}
    
    DataRangePtr getDataRange() const { return data_range_; }
    
    std::string toFunctionalSyntax() const override;
    std::string getDataRangeType() const override { return "DataComplementOf"; }

private:
    DataRangePtr data_range_;
};

/**
 * @brief Enumeration of literals
 */
class DataOneOf : public DataRange {
public:
    explicit DataOneOf(const std::vector<Literal>& literals)
        : literals_(literals) {}
    
    std::vector<Literal> getLiterals() const { return literals_; }
    
    std::string toFunctionalSyntax() const override;
    std::string getDataRangeType() const override { return "DataOneOf"; }

private:
    std::vector<Literal> literals_;
};

/**
 * @brief Facet restriction on a datatype
 * 
 * Represents constraining facets like minInclusive, maxExclusive, etc.
 */
class DatatypeRestriction : public DataRange {
public:
    using FacetRestriction = std::pair<IRI, Literal>;
    
    DatatypeRestriction(const Datatype& datatype, 
                       const std::vector<FacetRestriction>& restrictions)
        : datatype_(datatype), restrictions_(restrictions) {}
    
    Datatype getDatatype() const { return datatype_; }
    std::vector<FacetRestriction> getRestrictions() const { return restrictions_; }
    
    std::string toFunctionalSyntax() const override;
    std::string getDataRangeType() const override { return "DatatypeRestriction"; }

private:
    Datatype datatype_;
    std::vector<FacetRestriction> restrictions_;
};

// Common XSD facets
namespace facets {
    const IRI MIN_INCLUSIVE("http://www.w3.org/2001/XMLSchema#minInclusive");
    const IRI MAX_INCLUSIVE("http://www.w3.org/2001/XMLSchema#maxInclusive");
    const IRI MIN_EXCLUSIVE("http://www.w3.org/2001/XMLSchema#minExclusive");
    const IRI MAX_EXCLUSIVE("http://www.w3.org/2001/XMLSchema#maxExclusive");
    const IRI LENGTH("http://www.w3.org/2001/XMLSchema#length");
    const IRI MIN_LENGTH("http://www.w3.org/2001/XMLSchema#minLength");
    const IRI MAX_LENGTH("http://www.w3.org/2001/XMLSchema#maxLength");
    const IRI PATTERN("http://www.w3.org/2001/XMLSchema#pattern");
}

} // namespace owl2
} // namespace ista

#endif // ISTA_OWL2_DATA_RANGE_HPP
