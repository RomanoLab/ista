#ifndef ISTA_OWL2_ENTITY_HPP
#define ISTA_OWL2_ENTITY_HPP

#include "iri.hpp"
#include <memory>

namespace ista {
namespace owl2 {

/**
 * @brief Base class for all OWL2 entities
 * 
 * Entities are the named components of an ontology.
 */
class Entity {
public:
    explicit Entity(const IRI& iri) : iri_(iri) {}
    virtual ~Entity() = default;
    
    IRI getIRI() const { return iri_; }
    
    virtual std::string getEntityType() const = 0;
    
    bool operator==(const Entity& other) const { 
        return iri_ == other.iri_; 
    }
    bool operator!=(const Entity& other) const { 
        return !(*this == other); 
    }
    bool operator<(const Entity& other) const { 
        return iri_ < other.iri_; 
    }

protected:
    IRI iri_;
};

/**
 * @brief OWL2 Class
 */
class Class : public Entity {
public:
    explicit Class(const IRI& iri) : Entity(iri) {}
    
    std::string getEntityType() const override { return "Class"; }
};

/**
 * @brief OWL2 Datatype
 */
class Datatype : public Entity {
public:
    explicit Datatype(const IRI& iri) : Entity(iri) {}
    
    std::string getEntityType() const override { return "Datatype"; }
};

/**
 * @brief OWL2 Object Property
 */
class ObjectProperty : public Entity {
public:
    explicit ObjectProperty(const IRI& iri) : Entity(iri) {}
    
    std::string getEntityType() const override { return "ObjectProperty"; }
};

/**
 * @brief OWL2 Data Property
 */
class DataProperty : public Entity {
public:
    explicit DataProperty(const IRI& iri) : Entity(iri) {}
    
    std::string getEntityType() const override { return "DataProperty"; }
};

/**
 * @brief OWL2 Annotation Property
 */
class AnnotationProperty : public Entity {
public:
    explicit AnnotationProperty(const IRI& iri) : Entity(iri) {}
    
    std::string getEntityType() const override { return "AnnotationProperty"; }
};

/**
 * @brief OWL2 Named Individual
 */
class NamedIndividual : public Entity {
public:
    explicit NamedIndividual(const IRI& iri) : Entity(iri) {}
    
    std::string getEntityType() const override { return "NamedIndividual"; }
};

/**
 * @brief OWL2 Anonymous Individual (blank node)
 */
class AnonymousIndividual {
public:
    explicit AnonymousIndividual(const std::string& node_id) : node_id_(node_id) {}
    
    std::string getNodeID() const { return node_id_; }
    
    bool operator==(const AnonymousIndividual& other) const {
        return node_id_ == other.node_id_;
    }
    bool operator!=(const AnonymousIndividual& other) const {
        return !(*this == other);
    }
    bool operator<(const AnonymousIndividual& other) const {
        return node_id_ < other.node_id_;
    }

private:
    std::string node_id_;
};

// Convenience type aliases
using ClassPtr = std::shared_ptr<Class>;
using DatatypePtr = std::shared_ptr<Datatype>;
using ObjectPropertyPtr = std::shared_ptr<ObjectProperty>;
using DataPropertyPtr = std::shared_ptr<DataProperty>;
using AnnotationPropertyPtr = std::shared_ptr<AnnotationProperty>;
using NamedIndividualPtr = std::shared_ptr<NamedIndividual>;
using AnonymousIndividualPtr = std::shared_ptr<AnonymousIndividual>;

} // namespace owl2
} // namespace ista

// Hash functions for entities
namespace std {
    template<>
    struct hash<ista::owl2::Class> {
        size_t operator()(const ista::owl2::Class& c) const {
            return hash<ista::owl2::IRI>()(c.getIRI());
        }
    };
    
    template<>
    struct hash<ista::owl2::Datatype> {
        size_t operator()(const ista::owl2::Datatype& dt) const {
            return hash<ista::owl2::IRI>()(dt.getIRI());
        }
    };
    
    template<>
    struct hash<ista::owl2::ObjectProperty> {
        size_t operator()(const ista::owl2::ObjectProperty& op) const {
            return hash<ista::owl2::IRI>()(op.getIRI());
        }
    };
    
    template<>
    struct hash<ista::owl2::DataProperty> {
        size_t operator()(const ista::owl2::DataProperty& dp) const {
            return hash<ista::owl2::IRI>()(dp.getIRI());
        }
    };
    
    template<>
    struct hash<ista::owl2::AnnotationProperty> {
        size_t operator()(const ista::owl2::AnnotationProperty& ap) const {
            return hash<ista::owl2::IRI>()(ap.getIRI());
        }
    };
    
    template<>
    struct hash<ista::owl2::NamedIndividual> {
        size_t operator()(const ista::owl2::NamedIndividual& ni) const {
            return hash<ista::owl2::IRI>()(ni.getIRI());
        }
    };
    
    template<>
    struct hash<ista::owl2::AnonymousIndividual> {
        size_t operator()(const ista::owl2::AnonymousIndividual& ai) const {
            return hash<string>()(ai.getNodeID());
        }
    };
}

#endif // ISTA_OWL2_ENTITY_HPP
