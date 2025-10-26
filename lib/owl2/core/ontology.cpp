#include "ontology.hpp"
#include "ontology_filter.hpp"
#include <algorithm>
#include <sstream>
#include <queue>
#include <unordered_map>

namespace ista {
namespace owl2 {

Ontology::Ontology() {
    initializeStandardPrefixes();
}

Ontology::Ontology(const IRI& ontology_iri)
    : ontology_iri_(ontology_iri) {
    initializeStandardPrefixes();
}

Ontology::Ontology(const IRI& ontology_iri, const IRI& version_iri)
    : ontology_iri_(ontology_iri), version_iri_(version_iri) {
    initializeStandardPrefixes();
}

void Ontology::addImport(const IRI& import_iri) {
    imports_.insert(import_iri);
}

void Ontology::removeImport(const IRI& import_iri) {
    imports_.erase(import_iri);
}

bool Ontology::hasImport(const IRI& import_iri) const {
    return imports_.find(import_iri) != imports_.end();
}

void Ontology::addOntologyAnnotation(const Annotation& annotation) {
    ontology_annotations_.push_back(annotation);
}

void Ontology::registerPrefix(const std::string& prefix, const std::string& namespace_uri) {
    prefix_to_namespace_[prefix] = namespace_uri;
    namespace_to_prefix_[namespace_uri] = prefix;
}

std::optional<std::string> Ontology::getNamespaceForPrefix(const std::string& prefix) const {
    auto it = prefix_to_namespace_.find(prefix);
    if (it != prefix_to_namespace_.end()) {
        return it->second;
    }
    return std::nullopt;
}

std::optional<std::string> Ontology::getPrefixForNamespace(const std::string& namespace_uri) const {
    auto it = namespace_to_prefix_.find(namespace_uri);
    if (it != namespace_to_prefix_.end()) {
        return it->second;
    }
    return std::nullopt;
}

void Ontology::removePrefix(const std::string& prefix) {
    auto it = prefix_to_namespace_.find(prefix);
    if (it != prefix_to_namespace_.end()) {
        namespace_to_prefix_.erase(it->second);
        prefix_to_namespace_.erase(it);
    }
}

void Ontology::clearPrefixes() {
    prefix_to_namespace_.clear();
    namespace_to_prefix_.clear();
}

void Ontology::initializeStandardPrefixes() {
    registerPrefix("owl", "http://www.w3.org/2002/07/owl#");
    registerPrefix("rdf", "http://www.w3.org/1999/02/22-rdf-syntax-ns#");
    registerPrefix("rdfs", "http://www.w3.org/2000/01/rdf-schema#");
    registerPrefix("xsd", "http://www.w3.org/2001/XMLSchema#");
}

bool Ontology::addAxiom(const AxiomPtr& axiom) {
    if (!axiom) {
        return false;
    }
    axioms_.push_back(axiom);
    return true;
}

bool Ontology::removeAxiom(const AxiomPtr& axiom) {
    auto it = std::find(axioms_.begin(), axioms_.end(), axiom);
    if (it != axioms_.end()) {
        axioms_.erase(it);
        return true;
    }
    return false;
}

bool Ontology::containsAxiom(const AxiomPtr& axiom) const {
    return std::find(axioms_.begin(), axioms_.end(), axiom) != axioms_.end();
}

std::vector<AxiomPtr> Ontology::getAxioms() const {
    return axioms_;
}

void Ontology::clearAxioms() {
    axioms_.clear();
}

std::vector<std::shared_ptr<Declaration>> Ontology::getDeclarationAxioms() const {
    std::vector<std::shared_ptr<Declaration>> result;
    for (const auto& axiom : axioms_) {
        if (auto decl = std::dynamic_pointer_cast<Declaration>(axiom)) {
            result.push_back(decl);
        }
    }
    return result;
}

std::vector<AxiomPtr> Ontology::getClassAxioms() const {
    std::vector<AxiomPtr> result;
    for (const auto& axiom : axioms_) {
        if (isClassAxiom(axiom)) {
            result.push_back(axiom);
        }
    }
    return result;
}

std::vector<AxiomPtr> Ontology::getObjectPropertyAxioms() const {
    std::vector<AxiomPtr> result;
    for (const auto& axiom : axioms_) {
        if (isObjectPropertyAxiom(axiom)) {
            result.push_back(axiom);
        }
    }
    return result;
}

std::vector<AxiomPtr> Ontology::getDataPropertyAxioms() const {
    std::vector<AxiomPtr> result;
    for (const auto& axiom : axioms_) {
        if (isDataPropertyAxiom(axiom)) {
            result.push_back(axiom);
        }
    }
    return result;
}

std::vector<AxiomPtr> Ontology::getAssertionAxioms() const {
    std::vector<AxiomPtr> result;
    for (const auto& axiom : axioms_) {
        if (isAssertionAxiom(axiom)) {
            result.push_back(axiom);
        }
    }
    return result;
}

std::vector<AxiomPtr> Ontology::getAnnotationAxioms() const {
    std::vector<AxiomPtr> result;
    for (const auto& axiom : axioms_) {
        if (isAnnotationAxiom(axiom)) {
            result.push_back(axiom);
        }
    }
    return result;
}


std::vector<std::shared_ptr<SubClassOf>> Ontology::getSubClassAxiomsForSubClass(const Class& cls) const {
    std::vector<std::shared_ptr<SubClassOf>> result;
    for (const auto& axiom : axioms_) {
        if (auto subclass = std::dynamic_pointer_cast<SubClassOf>(axiom)) {
            if (auto class_expr = std::dynamic_pointer_cast<NamedClass>(subclass->getSubClass())) {
                if (class_expr->getClass().getIRI() == cls.getIRI()) {
                    result.push_back(subclass);
                }
            }
        }
    }
    return result;
}

std::vector<std::shared_ptr<SubClassOf>> Ontology::getSubClassAxiomsForSuperClass(const Class& cls) const {
    std::vector<std::shared_ptr<SubClassOf>> result;
    for (const auto& axiom : axioms_) {
        if (auto subclass = std::dynamic_pointer_cast<SubClassOf>(axiom)) {
            if (auto class_expr = std::dynamic_pointer_cast<NamedClass>(subclass->getSuperClass())) {
                if (class_expr->getClass().getIRI() == cls.getIRI()) {
                    result.push_back(subclass);
                }
            }
        }
    }
    return result;
}

std::vector<std::shared_ptr<EquivalentClasses>> Ontology::getEquivalentClassesAxioms(const Class& cls) const {
    std::vector<std::shared_ptr<EquivalentClasses>> result;
    for (const auto& axiom : axioms_) {
        if (auto equiv = std::dynamic_pointer_cast<EquivalentClasses>(axiom)) {
            for (const auto& expr : equiv->getClassExpressions()) {
                if (auto class_expr = std::dynamic_pointer_cast<NamedClass>(expr)) {
                    if (class_expr->getClass().getIRI() == cls.getIRI()) {
                        result.push_back(equiv);
                        break;
                    }
                }
            }
        }
    }
    return result;
}

std::vector<std::shared_ptr<DisjointClasses>> Ontology::getDisjointClassesAxioms(const Class& cls) const {
    std::vector<std::shared_ptr<DisjointClasses>> result;
    for (const auto& axiom : axioms_) {
        if (auto disjoint = std::dynamic_pointer_cast<DisjointClasses>(axiom)) {
            for (const auto& expr : disjoint->getClassExpressions()) {
                if (auto class_expr = std::dynamic_pointer_cast<NamedClass>(expr)) {
                    if (class_expr->getClass().getIRI() == cls.getIRI()) {
                        result.push_back(disjoint);
                        break;
                    }
                }
            }
        }
    }
    return result;
}

std::vector<std::shared_ptr<SubObjectPropertyOf>> Ontology::getSubObjectPropertyAxioms(
    const ObjectProperty& property) const {
    std::vector<std::shared_ptr<SubObjectPropertyOf>> result;
    for (const auto& axiom : axioms_) {
        if (auto subprop = std::dynamic_pointer_cast<SubObjectPropertyOf>(axiom)) {
            result.push_back(subprop);
        }
    }
    return result;
}

std::vector<std::shared_ptr<SubDataPropertyOf>> Ontology::getSubDataPropertyAxioms(
    const DataProperty& property) const {
    std::vector<std::shared_ptr<SubDataPropertyOf>> result;
    for (const auto& axiom : axioms_) {
        if (auto subprop = std::dynamic_pointer_cast<SubDataPropertyOf>(axiom)) {
            if (subprop->getSubProperty().getIRI() == property.getIRI() ||
                subprop->getSuperProperty().getIRI() == property.getIRI()) {
                result.push_back(subprop);
            }
        }
    }
    return result;
}

std::vector<std::shared_ptr<ClassAssertion>> Ontology::getClassAssertions(
    const NamedIndividual& individual) const {
    std::vector<std::shared_ptr<ClassAssertion>> result;
    for (const auto& axiom : axioms_) {
        if (auto assertion = std::dynamic_pointer_cast<ClassAssertion>(axiom)) {
            if (std::holds_alternative<NamedIndividual>(assertion->getIndividual())) {
                const auto& ind = std::get<NamedIndividual>(assertion->getIndividual());
                if (ind.getIRI() == individual.getIRI()) {
                    result.push_back(assertion);
                }
            }
        }
    }
    return result;
}

std::vector<std::shared_ptr<ObjectPropertyAssertion>> Ontology::getObjectPropertyAssertions(
    const NamedIndividual& individual) const {
    std::vector<std::shared_ptr<ObjectPropertyAssertion>> result;
    for (const auto& axiom : axioms_) {
        if (auto assertion = std::dynamic_pointer_cast<ObjectPropertyAssertion>(axiom)) {
            if (std::holds_alternative<NamedIndividual>(assertion->getSource())) {
                const auto& ind = std::get<NamedIndividual>(assertion->getSource());
                if (ind.getIRI() == individual.getIRI()) {
                    result.push_back(assertion);
                }
            }
        }
    }
    return result;
}

std::vector<std::shared_ptr<DataPropertyAssertion>> Ontology::getDataPropertyAssertions(
    const NamedIndividual& individual) const {
    std::vector<std::shared_ptr<DataPropertyAssertion>> result;
    for (const auto& axiom : axioms_) {
        if (auto assertion = std::dynamic_pointer_cast<DataPropertyAssertion>(axiom)) {
            if (std::holds_alternative<NamedIndividual>(assertion->getSource())) {
                const auto& ind = std::get<NamedIndividual>(assertion->getSource());
                if (ind.getIRI() == individual.getIRI()) {
                    result.push_back(assertion);
                }
            }
        }
    }
    return result;
}


std::unordered_set<Class> Ontology::getClasses() const {
    std::unordered_set<Class> result;
    for (const auto& axiom : axioms_) {
        if (auto decl = std::dynamic_pointer_cast<Declaration>(axiom)) {
            if (decl->getEntityType() == Declaration::EntityType::CLASS) {
                result.insert(Class(decl->getIRI()));
            }
        }
    }
    return result;
}

std::unordered_set<ObjectProperty> Ontology::getObjectProperties() const {
    std::unordered_set<ObjectProperty> result;
    for (const auto& axiom : axioms_) {
        if (auto decl = std::dynamic_pointer_cast<Declaration>(axiom)) {
            if (decl->getEntityType() == Declaration::EntityType::OBJECT_PROPERTY) {
                result.insert(ObjectProperty(decl->getIRI()));
            }
        }
    }
    return result;
}

std::unordered_set<DataProperty> Ontology::getDataProperties() const {
    std::unordered_set<DataProperty> result;
    for (const auto& axiom : axioms_) {
        if (auto decl = std::dynamic_pointer_cast<Declaration>(axiom)) {
            if (decl->getEntityType() == Declaration::EntityType::DATA_PROPERTY) {
                result.insert(DataProperty(decl->getIRI()));
            }
        }
    }
    return result;
}

std::unordered_set<AnnotationProperty> Ontology::getAnnotationProperties() const {
    std::unordered_set<AnnotationProperty> result;
    for (const auto& axiom : axioms_) {
        if (auto decl = std::dynamic_pointer_cast<Declaration>(axiom)) {
            if (decl->getEntityType() == Declaration::EntityType::ANNOTATION_PROPERTY) {
                result.insert(AnnotationProperty(decl->getIRI()));
            }
        }
    }
    return result;
}

std::unordered_set<NamedIndividual> Ontology::getIndividuals() const {
    std::unordered_set<NamedIndividual> result;
    for (const auto& axiom : axioms_) {
        if (auto decl = std::dynamic_pointer_cast<Declaration>(axiom)) {
            if (decl->getEntityType() == Declaration::EntityType::NAMED_INDIVIDUAL) {
                result.insert(NamedIndividual(decl->getIRI()));
            }
        }
    }
    return result;
}

std::unordered_set<Datatype> Ontology::getDatatypes() const {
    std::unordered_set<Datatype> result;
    for (const auto& axiom : axioms_) {
        if (auto decl = std::dynamic_pointer_cast<Declaration>(axiom)) {
            if (decl->getEntityType() == Declaration::EntityType::DATATYPE) {
                result.insert(Datatype(decl->getIRI()));
            }
        }
    }
    return result;
}

bool Ontology::containsClass(const Class& cls) const {
    return getClasses().find(cls) != getClasses().end();
}

bool Ontology::containsObjectProperty(const ObjectProperty& property) const {
    return getObjectProperties().find(property) != getObjectProperties().end();
}

bool Ontology::containsDataProperty(const DataProperty& property) const {
    return getDataProperties().find(property) != getDataProperties().end();
}

bool Ontology::containsAnnotationProperty(const AnnotationProperty& property) const {
    return getAnnotationProperties().find(property) != getAnnotationProperties().end();
}

bool Ontology::containsIndividual(const NamedIndividual& individual) const {
    return getIndividuals().find(individual) != getIndividuals().end();
}

bool Ontology::containsDatatype(const Datatype& datatype) const {
    return getDatatypes().find(datatype) != getDatatypes().end();
}

size_t Ontology::getEntityCount() const {
    return getClassCount() + getObjectPropertyCount() + getDataPropertyCount() +
           getAnnotationProperties().size() + getIndividualCount() + getDatatypes().size();
}

std::string Ontology::getStatistics() const {
    std::ostringstream oss;
    oss << "Ontology Statistics:\n";
    if (ontology_iri_) {
        oss << "  IRI: " << ontology_iri_->getFullIRI() << "\n";
    }
    oss << "  Total Axioms: " << getAxiomCount() << "\n";
    oss << "  Total Entities: " << getEntityCount() << "\n";
    oss << "    Classes: " << getClassCount() << "\n";
    oss << "    Object Properties: " << getObjectPropertyCount() << "\n";
    oss << "    Data Properties: " << getDataPropertyCount() << "\n";
    oss << "    Annotation Properties: " << getAnnotationProperties().size() << "\n";
    oss << "    Individuals: " << getIndividualCount() << "\n";
    oss << "    Datatypes: " << getDatatypes().size() << "\n";
    oss << "  Imports: " << imports_.size() << "\n";
    return oss.str();
}


std::string Ontology::toFunctionalSyntax() const {
    return toFunctionalSyntax("    ");
}

std::string Ontology::toFunctionalSyntax(const std::string& indent) const {
    std::ostringstream oss;
    
    oss << "Ontology(";
    if (ontology_iri_) {
        oss << "<" << ontology_iri_->getFullIRI() << ">";
        if (version_iri_) {
            oss << " <" << version_iri_->getFullIRI() << ">";
        }
    }
    oss << "\n";
    
    for (const auto& [prefix, ns] : prefix_to_namespace_) {
        oss << indent << "Prefix(" << prefix << ":=<" << ns << ">)\n";
    }
    
    for (const auto& import_iri : imports_) {
        oss << indent << "Import(<" << import_iri.getFullIRI() << ">)\n";
    }
    
    for (const auto& annotation : ontology_annotations_) {
        oss << indent << annotation.toFunctionalSyntax() << "\n";
    }
    
    for (const auto& axiom : axioms_) {
        oss << indent << axiom->toFunctionalSyntax() << "\n";
    }
    
    oss << ")";
    return oss.str();
}

bool Ontology::isClassAxiom(const AxiomPtr& axiom) const {
    return std::dynamic_pointer_cast<SubClassOf>(axiom) ||
           std::dynamic_pointer_cast<EquivalentClasses>(axiom) ||
           std::dynamic_pointer_cast<DisjointClasses>(axiom) ||
           std::dynamic_pointer_cast<DisjointUnion>(axiom);
}

bool Ontology::isObjectPropertyAxiom(const AxiomPtr& axiom) const {
    return std::dynamic_pointer_cast<SubObjectPropertyOf>(axiom) ||
           std::dynamic_pointer_cast<EquivalentObjectProperties>(axiom) ||
           std::dynamic_pointer_cast<DisjointObjectProperties>(axiom) ||
           std::dynamic_pointer_cast<InverseObjectProperties>(axiom) ||
           std::dynamic_pointer_cast<ObjectPropertyDomain>(axiom) ||
           std::dynamic_pointer_cast<ObjectPropertyRange>(axiom) ||
           std::dynamic_pointer_cast<FunctionalObjectProperty>(axiom) ||
           std::dynamic_pointer_cast<InverseFunctionalObjectProperty>(axiom) ||
           std::dynamic_pointer_cast<ReflexiveObjectProperty>(axiom) ||
           std::dynamic_pointer_cast<IrreflexiveObjectProperty>(axiom) ||
           std::dynamic_pointer_cast<SymmetricObjectProperty>(axiom) ||
           std::dynamic_pointer_cast<AsymmetricObjectProperty>(axiom) ||
           std::dynamic_pointer_cast<TransitiveObjectProperty>(axiom);
}

bool Ontology::isDataPropertyAxiom(const AxiomPtr& axiom) const {
    return std::dynamic_pointer_cast<SubDataPropertyOf>(axiom) ||
           std::dynamic_pointer_cast<EquivalentDataProperties>(axiom) ||
           std::dynamic_pointer_cast<DisjointDataProperties>(axiom) ||
           std::dynamic_pointer_cast<DataPropertyDomain>(axiom) ||
           std::dynamic_pointer_cast<DataPropertyRange>(axiom) ||
           std::dynamic_pointer_cast<FunctionalDataProperty>(axiom);
}

bool Ontology::isAssertionAxiom(const AxiomPtr& axiom) const {
    return std::dynamic_pointer_cast<SameIndividual>(axiom) ||
           std::dynamic_pointer_cast<DifferentIndividuals>(axiom) ||
           std::dynamic_pointer_cast<ClassAssertion>(axiom) ||
           std::dynamic_pointer_cast<ObjectPropertyAssertion>(axiom) ||
           std::dynamic_pointer_cast<NegativeObjectPropertyAssertion>(axiom) ||
           std::dynamic_pointer_cast<DataPropertyAssertion>(axiom) ||
           std::dynamic_pointer_cast<NegativeDataPropertyAssertion>(axiom);
}

bool Ontology::isAnnotationAxiom(const AxiomPtr& axiom) const {
    return std::dynamic_pointer_cast<AnnotationAssertion>(axiom) ||
           std::dynamic_pointer_cast<SubAnnotationPropertyOf>(axiom) ||
           std::dynamic_pointer_cast<AnnotationPropertyDomain>(axiom) ||
           std::dynamic_pointer_cast<AnnotationPropertyRange>(axiom);
}

// ============================================================================
// Filtering and Subgraph Extraction Methods
// ============================================================================

std::shared_ptr<Ontology> Ontology::createSubgraph(const OntologyFilter& filter) const {
    auto result = filter.execute();
    return result.ontology;
}

std::unordered_set<NamedIndividual> Ontology::getIndividualsOfClass(const Class& cls) const {
    std::unordered_set<NamedIndividual> individuals;
    
    for (const auto& axiom : axioms_) {
        if (auto class_assertion = std::dynamic_pointer_cast<ClassAssertion>(axiom)) {
            // Check if the class matches
            if (auto named_class = std::dynamic_pointer_cast<NamedClass>(class_assertion->getClassExpression())) {
                if (named_class->getClass().getIRI() == cls.getIRI()) {
                    // Extract the individual
                    if (std::holds_alternative<NamedIndividual>(class_assertion->getIndividual())) {
                        individuals.insert(std::get<NamedIndividual>(class_assertion->getIndividual()));
                    }
                }
            }
        }
    }
    
    return individuals;
}

std::vector<NamedIndividual> Ontology::getNeighbors(const NamedIndividual& individual, int depth) const {
    if (depth < 0) {
        return {};
    }
    
    // Build adjacency list from object property assertions
    std::unordered_map<IRI, std::unordered_set<IRI>> adj_list;
    
    for (const auto& axiom : axioms_) {
        if (auto obj_prop = std::dynamic_pointer_cast<ObjectPropertyAssertion>(axiom)) {
            if (std::holds_alternative<NamedIndividual>(obj_prop->getSource()) &&
                std::holds_alternative<NamedIndividual>(obj_prop->getTarget())) {
                
                auto source = std::get<NamedIndividual>(obj_prop->getSource()).getIRI();
                auto target = std::get<NamedIndividual>(obj_prop->getTarget()).getIRI();
                
                // Bidirectional edges for undirected graph
                adj_list[source].insert(target);
                adj_list[target].insert(source);
            }
        }
    }
    
    // BFS traversal
    std::unordered_set<IRI> visited;
    std::queue<std::pair<IRI, int>> queue;  // (node, current_depth)
    
    IRI start_iri = individual.getIRI();
    queue.push({start_iri, 0});
    visited.insert(start_iri);
    
    while (!queue.empty()) {
        auto [current, current_depth] = queue.front();
        queue.pop();
        
        if (current_depth >= depth) {
            continue;
        }
        
        auto it = adj_list.find(current);
        if (it != adj_list.end()) {
            for (const auto& neighbor_iri : it->second) {
                if (visited.find(neighbor_iri) == visited.end()) {
                    visited.insert(neighbor_iri);
                    queue.push({neighbor_iri, current_depth + 1});
                }
            }
        }
    }
    
    // Remove the starting individual from results
    visited.erase(start_iri);
    
    // Convert to vector
    std::vector<NamedIndividual> neighbors;
    neighbors.reserve(visited.size());
    for (const auto& iri : visited) {
        neighbors.push_back(NamedIndividual(iri));
    }
    
    return neighbors;
}

bool Ontology::hasPath(const NamedIndividual& from, const NamedIndividual& to) const {
    // Build adjacency list
    std::unordered_map<IRI, std::unordered_set<IRI>> adj_list;
    
    for (const auto& axiom : axioms_) {
        if (auto obj_prop = std::dynamic_pointer_cast<ObjectPropertyAssertion>(axiom)) {
            if (std::holds_alternative<NamedIndividual>(obj_prop->getSource()) &&
                std::holds_alternative<NamedIndividual>(obj_prop->getTarget())) {
                
                auto source = std::get<NamedIndividual>(obj_prop->getSource()).getIRI();
                auto target = std::get<NamedIndividual>(obj_prop->getTarget()).getIRI();
                
                // Bidirectional edges
                adj_list[source].insert(target);
                adj_list[target].insert(source);
            }
        }
    }
    
    // BFS to check reachability
    std::unordered_set<IRI> visited;
    std::queue<IRI> queue;
    
    IRI start_iri = from.getIRI();
    IRI end_iri = to.getIRI();
    
    if (start_iri == end_iri) {
        return true;  // Trivial case
    }
    
    queue.push(start_iri);
    visited.insert(start_iri);
    
    while (!queue.empty()) {
        IRI current = queue.front();
        queue.pop();
        
        if (current == end_iri) {
            return true;
        }
        
        auto it = adj_list.find(current);
        if (it != adj_list.end()) {
            for (const auto& neighbor : it->second) {
                if (visited.find(neighbor) == visited.end()) {
                    visited.insert(neighbor);
                    queue.push(neighbor);
                }
            }
        }
    }
    
    return false;
}

} // namespace owl2
} // namespace ista
