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
