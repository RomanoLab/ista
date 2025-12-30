#ifndef ISTA_OWL2_ONTOLOGY_HPP
#define ISTA_OWL2_ONTOLOGY_HPP

#include "iri.hpp"
#include "entity.hpp"
#include "axiom.hpp"
#include "annotation.hpp"
#include <string>
#include <unordered_set>
#include <unordered_map>
#include <vector>
#include <memory>
#include <optional>

namespace ista {
namespace owl2 {

class Ontology {
public:
    Ontology();
    explicit Ontology(const IRI& ontology_iri);
    Ontology(const IRI& ontology_iri, const IRI& version_iri);
    ~Ontology() = default;

    // Metadata management
    std::optional<IRI> getOntologyIRI() const { return ontology_iri_; }
    void setOntologyIRI(const IRI& iri) { ontology_iri_ = iri; }
    std::optional<IRI> getVersionIRI() const { return version_iri_; }
    void setVersionIRI(const IRI& iri) { version_iri_ = iri; }
    std::unordered_set<IRI> getImports() const { return imports_; }
    void addImport(const IRI& import_iri);
    void removeImport(const IRI& import_iri);
    bool hasImport(const IRI& import_iri) const;
    std::vector<Annotation> getOntologyAnnotations() const { return ontology_annotations_; }
    void addOntologyAnnotation(const Annotation& annotation);
    void setOntologyAnnotations(const std::vector<Annotation>& annotations) {
        ontology_annotations_ = annotations;
    }
    void clearOntologyAnnotations() { ontology_annotations_.clear(); }

    // Prefix management
    void registerPrefix(const std::string& prefix, const std::string& namespace_uri);
    std::optional<std::string> getNamespaceForPrefix(const std::string& prefix) const;
    std::optional<std::string> getPrefixForNamespace(const std::string& namespace_uri) const;
    std::unordered_map<std::string, std::string> getPrefixMap() const {
        return prefix_to_namespace_;
    }
    void removePrefix(const std::string& prefix);
    void clearPrefixes();

    // Axiom management
    bool addAxiom(const AxiomPtr& axiom);
    bool removeAxiom(const AxiomPtr& axiom);
    bool containsAxiom(const AxiomPtr& axiom) const;
    std::vector<AxiomPtr> getAxioms() const;
    void clearAxioms();

    // Axiom queries by type
    std::vector<std::shared_ptr<Declaration>> getDeclarationAxioms() const;
    std::vector<AxiomPtr> getClassAxioms() const;
    std::vector<AxiomPtr> getObjectPropertyAxioms() const;
    std::vector<AxiomPtr> getDataPropertyAxioms() const;
    std::vector<AxiomPtr> getAssertionAxioms() const;
    std::vector<AxiomPtr> getAnnotationAxioms() const;

    // Specific axiom queries
    std::vector<std::shared_ptr<SubClassOf>> getSubClassAxiomsForSubClass(const Class& cls) const;
    std::vector<std::shared_ptr<SubClassOf>> getSubClassAxiomsForSuperClass(const Class& cls) const;
    std::vector<std::shared_ptr<EquivalentClasses>> getEquivalentClassesAxioms(const Class& cls) const;
    std::vector<std::shared_ptr<DisjointClasses>> getDisjointClassesAxioms(const Class& cls) const;
    std::vector<std::shared_ptr<SubObjectPropertyOf>> getSubObjectPropertyAxioms(
        const ObjectProperty& property) const;
    std::vector<std::shared_ptr<SubDataPropertyOf>> getSubDataPropertyAxioms(
        const DataProperty& property) const;
    std::vector<std::shared_ptr<ClassAssertion>> getClassAssertions(
        const NamedIndividual& individual) const;
    std::vector<std::shared_ptr<ObjectPropertyAssertion>> getObjectPropertyAssertions(
        const NamedIndividual& individual) const;
    std::vector<std::shared_ptr<DataPropertyAssertion>> getDataPropertyAssertions(
        const NamedIndividual& individual) const;

    // Entity queries
    std::unordered_set<Class> getClasses() const;
    std::unordered_set<ObjectProperty> getObjectProperties() const;
    std::unordered_set<DataProperty> getDataProperties() const;
    std::unordered_set<AnnotationProperty> getAnnotationProperties() const;
    std::unordered_set<NamedIndividual> getIndividuals() const;
    std::unordered_set<Datatype> getDatatypes() const;
    bool containsClass(const Class& cls) const;
    bool containsObjectProperty(const ObjectProperty& property) const;
    bool containsDataProperty(const DataProperty& property) const;
    bool containsAnnotationProperty(const AnnotationProperty& property) const;
    bool containsIndividual(const NamedIndividual& individual) const;
    bool containsDatatype(const Datatype& datatype) const;

    // Statistics
    size_t getAxiomCount() const { return axioms_.size(); }
    size_t getEntityCount() const;
    size_t getClassCount() const { return getClasses().size(); }
    size_t getObjectPropertyCount() const { return getObjectProperties().size(); }
    size_t getDataPropertyCount() const { return getDataProperties().size(); }
    size_t getIndividualCount() const { return getIndividuals().size(); }
    std::string getStatistics() const;

    // Serialization
    std::string toFunctionalSyntax() const;
    std::string toFunctionalSyntax(const std::string& indent) const;

    // Individual and Property Manipulation
    /**
     * @brief Create a new individual of the specified class
     * 
     * This creates a NamedIndividual and adds a ClassAssertion axiom to the ontology.
     * 
     * @param cls The class to instantiate
     * @param individual_iri The IRI for the new individual
     * @return The created NamedIndividual
     */
    NamedIndividual createIndividual(const Class& cls, const IRI& individual_iri);
    
    /**
     * @brief Add a data property assertion
     * 
     * Creates and adds a DataPropertyAssertion axiom.
     * 
     * @param individual The subject individual
     * @param property The data property
     * @param value The literal value
     * @return true if the axiom was added successfully
     */
    bool addDataPropertyAssertion(const NamedIndividual& individual, 
                                   const DataProperty& property, 
                                   const Literal& value);
    
    /**
     * @brief Add an object property assertion
     * 
     * Creates and adds an ObjectPropertyAssertion axiom.
     * 
     * @param subject The subject individual
     * @param property The object property
     * @param object The object individual
     * @return true if the axiom was added successfully
     */
    bool addObjectPropertyAssertion(const NamedIndividual& subject,
                                     const ObjectProperty& property,
                                     const NamedIndividual& object);
    
    /**
     * @brief Add a class assertion to an existing individual
     * 
     * @param individual The individual
     * @param cls The class to assert
     * @return true if the axiom was added successfully
     */
    bool addClassAssertion(const NamedIndividual& individual, const Class& cls);
    
    // Property-based Search
    /**
     * @brief Search for individuals by data property value
     * 
     * @param property The data property to search
     * @param value The literal value to match
     * @return Vector of individuals with matching data property assertions
     */
    std::vector<NamedIndividual> searchByDataProperty(const DataProperty& property, 
                                                       const Literal& value) const;
    
    /**
     * @brief Search for individuals by object property value
     * 
     * @param property The object property to search
     * @param object The object individual to match
     * @return Vector of subject individuals with matching object property assertions
     */
    std::vector<NamedIndividual> searchByObjectProperty(const ObjectProperty& property,
                                                         const NamedIndividual& object) const;
    
    // Property Assertion Queries
    /**
     * @brief Get all object property assertions for a property
     * 
     * @param property The object property
     * @return Vector of (subject, object) pairs
     */
    std::vector<std::pair<NamedIndividual, NamedIndividual>> 
    getObjectPropertyAssertions(const ObjectProperty& property) const;
    
    /**
     * @brief Get all data property assertions for a property
     * 
     * @param property The data property
     * @return Vector of (subject, value) pairs
     */
    std::vector<std::pair<NamedIndividual, Literal>> 
    getDataPropertyAssertions(const DataProperty& property) const;
    
    // Individual Class Queries
    /**
     * @brief Get all classes that an individual is asserted to be an instance of
     * 
     * @param individual The individual to query
     * @return Vector of classes
     */
    std::vector<Class> getClassesForIndividual(const NamedIndividual& individual) const;
    
    /**
     * @brief Check if an individual is an instance of a class
     * 
     * @param individual The individual to check
     * @param cls The class to check membership of
     * @return true if there is a ClassAssertion axiom
     */
    bool isInstanceOf(const NamedIndividual& individual, const Class& cls) const;
    
    // Property Characteristics
    /**
     * @brief Check if an object property is functional
     * 
     * @param property The object property to check
     * @return true if there is a FunctionalObjectProperty axiom
     */
    bool isFunctionalObjectProperty(const ObjectProperty& property) const;
    
    /**
     * @brief Check if a data property is functional
     * 
     * @param property The data property to check
     * @return true if there is a FunctionalDataProperty axiom
     */
    bool isFunctionalDataProperty(const DataProperty& property) const;

    // Filtering and Subgraph Extraction
    /**
     * @brief Create a filtered subgraph using OntologyFilter
     * @param filter The OntologyFilter to apply (must reference this ontology)
     * @return Shared pointer to the filtered ontology
     */
    std::shared_ptr<Ontology> createSubgraph(const class OntologyFilter& filter) const;
    
    /**
     * @brief Get all individuals that are instances of a class
     * @param cls The class to query
     * @return Set of individuals that have ClassAssertion axioms for this class
     */
    std::unordered_set<NamedIndividual> getIndividualsOfClass(const Class& cls) const;
    
    /**
     * @brief Get neighboring individuals within specified depth
     * 
     * Uses BFS to traverse the ontology graph via object property assertions.
     * 
     * @param individual The starting individual
     * @param depth Maximum number of hops (default 1)
     * @return Vector of individuals reachable within depth hops
     */
    std::vector<NamedIndividual> getNeighbors(const NamedIndividual& individual, int depth = 1) const;
    
    /**
     * @brief Check if a path exists between two individuals
     * 
     * Uses BFS to determine reachability through object property assertions.
     * 
     * @param from Starting individual
     * @param to Target individual
     * @return true if a path exists, false otherwise
     */
    bool hasPath(const NamedIndividual& from, const NamedIndividual& to) const;

private:
    std::optional<IRI> ontology_iri_;
    std::optional<IRI> version_iri_;
    std::unordered_set<IRI> imports_;
    std::vector<Annotation> ontology_annotations_;
    std::unordered_map<std::string, std::string> prefix_to_namespace_;
    std::unordered_map<std::string, std::string> namespace_to_prefix_;
    std::vector<AxiomPtr> axioms_;

    void initializeStandardPrefixes();
    bool isClassAxiom(const AxiomPtr& axiom) const;
    bool isObjectPropertyAxiom(const AxiomPtr& axiom) const;
    bool isDataPropertyAxiom(const AxiomPtr& axiom) const;
    bool isAssertionAxiom(const AxiomPtr& axiom) const;
    bool isAnnotationAxiom(const AxiomPtr& axiom) const;
};

using OntologyPtr = std::shared_ptr<Ontology>;

} // namespace owl2
} // namespace ista

#endif // ISTA_OWL2_ONTOLOGY_HPP
