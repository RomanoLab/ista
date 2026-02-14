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

void Ontology::rebuildIndices() const {
    if (indices_valid_) {
        return;
    }

    // Clear all caches
    declaration_index_.clear();
    class_iri_cache_.clear();
    object_property_iri_cache_.clear();
    data_property_iri_cache_.clear();
    annotation_property_iri_cache_.clear();
    individual_iri_cache_.clear();
    datatype_iri_cache_.clear();
    class_assertion_index_.clear();
    obj_prop_assertion_index_.clear();
    data_prop_assertion_index_.clear();

    // Build indices from axioms in a single pass
    for (const auto& axiom : axioms_) {
        if (auto decl = std::dynamic_pointer_cast<Declaration>(axiom)) {
            Declaration::EntityType entity_type = decl->getEntityType();
            declaration_index_[entity_type].push_back(decl);

            // Cache entity IRIs by type
            switch (entity_type) {
                case Declaration::EntityType::CLASS:
                    class_iri_cache_.insert(decl->getIRI());
                    break;
                case Declaration::EntityType::OBJECT_PROPERTY:
                    object_property_iri_cache_.insert(decl->getIRI());
                    break;
                case Declaration::EntityType::DATA_PROPERTY:
                    data_property_iri_cache_.insert(decl->getIRI());
                    break;
                case Declaration::EntityType::ANNOTATION_PROPERTY:
                    annotation_property_iri_cache_.insert(decl->getIRI());
                    break;
                case Declaration::EntityType::NAMED_INDIVIDUAL:
                    individual_iri_cache_.insert(decl->getIRI());
                    break;
                case Declaration::EntityType::DATATYPE:
                    datatype_iri_cache_.insert(decl->getIRI());
                    break;
            }
        } else if (auto ca = std::dynamic_pointer_cast<ClassAssertion>(axiom)) {
            class_assertion_index_.push_back(ca);
        } else if (auto opa = std::dynamic_pointer_cast<ObjectPropertyAssertion>(axiom)) {
            obj_prop_assertion_index_.push_back(opa);
        } else if (auto dpa = std::dynamic_pointer_cast<DataPropertyAssertion>(axiom)) {
            data_prop_assertion_index_.push_back(dpa);
        }
    }

    indices_valid_ = true;
}

void Ontology::beginBatchMode() {
    batch_mode_ = true;
}

void Ontology::endBatchMode() {
    batch_mode_ = false;
    indices_valid_ = false;
}

void Ontology::reserveAxioms(size_t count) {
    axioms_.reserve(axioms_.size() + count);
}

bool Ontology::addAxioms(std::vector<AxiomPtr>&& axioms) {
    bool any_added = false;
    axioms_.reserve(axioms_.size() + axioms.size());
    for (auto& axiom : axioms) {
        if (axiom) {
            axioms_.push_back(std::move(axiom));
            any_added = true;
        }
    }
    if (any_added) {
        invalidateIndices();
    }
    return any_added;
}

bool Ontology::addAxiom(const AxiomPtr& axiom) {
    if (!axiom) {
        return false;
    }
    axioms_.push_back(axiom);
    invalidateIndices();
    return true;
}

bool Ontology::removeAxiom(const AxiomPtr& axiom) {
    auto it = std::find(axioms_.begin(), axioms_.end(), axiom);
    if (it != axioms_.end()) {
        axioms_.erase(it);
        invalidateIndices();
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
    invalidateIndices();
}

std::vector<std::shared_ptr<Declaration>> Ontology::getDeclarationAxioms() const {
    rebuildIndices();
    std::vector<std::shared_ptr<Declaration>> result;
    for (const auto& [type, decls] : declaration_index_) {
        result.insert(result.end(), decls.begin(), decls.end());
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
    rebuildIndices();
    std::vector<std::shared_ptr<ClassAssertion>> result;
    for (const auto& assertion : class_assertion_index_) {
        Individual ind_variant = assertion->getIndividual();
        if (std::holds_alternative<NamedIndividual>(ind_variant)) {
            if (std::get<NamedIndividual>(ind_variant).getIRI() == individual.getIRI()) {
                result.push_back(assertion);
            }
        }
    }
    return result;
}

std::vector<std::shared_ptr<ObjectPropertyAssertion>> Ontology::getObjectPropertyAssertions(
    const NamedIndividual& individual) const {
    rebuildIndices();
    std::vector<std::shared_ptr<ObjectPropertyAssertion>> result;
    for (const auto& assertion : obj_prop_assertion_index_) {
        Individual source = assertion->getSource();
        if (std::holds_alternative<NamedIndividual>(source)) {
            if (std::get<NamedIndividual>(source).getIRI() == individual.getIRI()) {
                result.push_back(assertion);
            }
        }
    }
    return result;
}

std::vector<std::shared_ptr<DataPropertyAssertion>> Ontology::getDataPropertyAssertions(
    const NamedIndividual& individual) const {
    rebuildIndices();
    std::vector<std::shared_ptr<DataPropertyAssertion>> result;
    for (const auto& assertion : data_prop_assertion_index_) {
        Individual source = assertion->getSource();
        if (std::holds_alternative<NamedIndividual>(source)) {
            if (std::get<NamedIndividual>(source).getIRI() == individual.getIRI()) {
                result.push_back(assertion);
            }
        }
    }
    return result;
}


std::unordered_set<Class> Ontology::getClasses() const {
    rebuildIndices();
    std::unordered_set<Class> result;
    for (const auto& iri : class_iri_cache_) {
        result.insert(Class(iri));
    }
    return result;
}

std::unordered_set<ObjectProperty> Ontology::getObjectProperties() const {
    rebuildIndices();
    std::unordered_set<ObjectProperty> result;
    for (const auto& iri : object_property_iri_cache_) {
        result.insert(ObjectProperty(iri));
    }
    return result;
}

std::unordered_set<DataProperty> Ontology::getDataProperties() const {
    rebuildIndices();
    std::unordered_set<DataProperty> result;
    for (const auto& iri : data_property_iri_cache_) {
        result.insert(DataProperty(iri));
    }
    return result;
}

std::unordered_set<AnnotationProperty> Ontology::getAnnotationProperties() const {
    rebuildIndices();
    std::unordered_set<AnnotationProperty> result;
    for (const auto& iri : annotation_property_iri_cache_) {
        result.insert(AnnotationProperty(iri));
    }
    return result;
}

std::unordered_set<NamedIndividual> Ontology::getIndividuals() const {
    rebuildIndices();
    std::unordered_set<NamedIndividual> result;
    for (const auto& iri : individual_iri_cache_) {
        result.insert(NamedIndividual(iri));
    }
    return result;
}

std::unordered_set<Datatype> Ontology::getDatatypes() const {
    rebuildIndices();
    std::unordered_set<Datatype> result;
    for (const auto& iri : datatype_iri_cache_) {
        result.insert(Datatype(iri));
    }
    return result;
}

bool Ontology::containsClass(const Class& cls) const {
    rebuildIndices();
    return class_iri_cache_.find(cls.getIRI()) != class_iri_cache_.end();
}

bool Ontology::containsObjectProperty(const ObjectProperty& property) const {
    rebuildIndices();
    return object_property_iri_cache_.find(property.getIRI()) != object_property_iri_cache_.end();
}

bool Ontology::containsDataProperty(const DataProperty& property) const {
    rebuildIndices();
    return data_property_iri_cache_.find(property.getIRI()) != data_property_iri_cache_.end();
}

bool Ontology::containsAnnotationProperty(const AnnotationProperty& property) const {
    rebuildIndices();
    return annotation_property_iri_cache_.find(property.getIRI()) != annotation_property_iri_cache_.end();
}

bool Ontology::containsIndividual(const NamedIndividual& individual) const {
    rebuildIndices();
    return individual_iri_cache_.find(individual.getIRI()) != individual_iri_cache_.end();
}

bool Ontology::containsDatatype(const Datatype& datatype) const {
    rebuildIndices();
    return datatype_iri_cache_.find(datatype.getIRI()) != datatype_iri_cache_.end();
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
    rebuildIndices();
    std::unordered_set<NamedIndividual> individuals;

    for (const auto& assertion : class_assertion_index_) {
        if (auto named_class = std::dynamic_pointer_cast<NamedClass>(assertion->getClassExpression())) {
            if (named_class->getClass().getIRI() == cls.getIRI()) {
                if (std::holds_alternative<NamedIndividual>(assertion->getIndividual())) {
                    individuals.insert(std::get<NamedIndividual>(assertion->getIndividual()));
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

// ============================================================================
// Individual and Property Manipulation
// ============================================================================

NamedIndividual Ontology::createIndividual(const Class& cls, const IRI& individual_iri) {
    NamedIndividual individual(individual_iri);
    
    // Add declaration axiom for the individual
    auto decl = std::make_shared<Declaration>(Declaration::EntityType::NAMED_INDIVIDUAL, individual_iri);
    addAxiom(decl);
    
    // Add class assertion axiom
    auto class_expr = std::make_shared<NamedClass>(cls);
    auto class_assertion = std::make_shared<ClassAssertion>(class_expr, individual);
    addAxiom(class_assertion);
    
    return individual;
}

bool Ontology::addDataPropertyAssertion(const NamedIndividual& individual, 
                                         const DataProperty& property, 
                                         const Literal& value) {
    auto axiom = std::make_shared<DataPropertyAssertion>(property, individual, value);
    return addAxiom(axiom);
}

bool Ontology::addObjectPropertyAssertion(const NamedIndividual& subject,
                                           const ObjectProperty& property,
                                           const NamedIndividual& object) {
    auto axiom = std::make_shared<ObjectPropertyAssertion>(property, subject, object);
    return addAxiom(axiom);
}

bool Ontology::addClassAssertion(const NamedIndividual& individual, const Class& cls) {
    auto class_expr = std::make_shared<NamedClass>(cls);
    auto axiom = std::make_shared<ClassAssertion>(class_expr, individual);
    return addAxiom(axiom);
}

// ============================================================================
// Property-based Search
// ============================================================================

std::vector<NamedIndividual> Ontology::searchByDataProperty(const DataProperty& property,
                                                             const Literal& value) const {
    rebuildIndices();
    std::vector<NamedIndividual> results;

    for (const auto& assertion : data_prop_assertion_index_) {
        if (assertion->getProperty() == property) {
            if (assertion->getTarget() == value) {
                Individual source = assertion->getSource();
                if (std::holds_alternative<NamedIndividual>(source)) {
                    results.push_back(std::get<NamedIndividual>(source));
                }
            }
        }
    }

    return results;
}

std::vector<NamedIndividual> Ontology::searchByObjectProperty(const ObjectProperty& property,
                                                               const NamedIndividual& object) const {
    rebuildIndices();
    std::vector<NamedIndividual> results;

    for (const auto& assertion : obj_prop_assertion_index_) {
        ObjectPropertyExpression prop_expr = assertion->getProperty();
        if (std::holds_alternative<ObjectProperty>(prop_expr)) {
            if (std::get<ObjectProperty>(prop_expr) == property) {
                Individual target = assertion->getTarget();
                if (std::holds_alternative<NamedIndividual>(target)) {
                    if (std::get<NamedIndividual>(target) == object) {
                        Individual source = assertion->getSource();
                        if (std::holds_alternative<NamedIndividual>(source)) {
                            results.push_back(std::get<NamedIndividual>(source));
                        }
                    }
                }
            }
        }
    }

    return results;
}

// ============================================================================
// Property Assertion Queries
// ============================================================================

std::vector<std::pair<NamedIndividual, NamedIndividual>>
Ontology::getObjectPropertyAssertions(const ObjectProperty& property) const {
    rebuildIndices();
    std::vector<std::pair<NamedIndividual, NamedIndividual>> results;

    for (const auto& assertion : obj_prop_assertion_index_) {
        ObjectPropertyExpression prop_expr = assertion->getProperty();
        if (std::holds_alternative<ObjectProperty>(prop_expr)) {
            if (std::get<ObjectProperty>(prop_expr) == property) {
                Individual source = assertion->getSource();
                Individual target = assertion->getTarget();

                if (std::holds_alternative<NamedIndividual>(source) &&
                    std::holds_alternative<NamedIndividual>(target)) {
                    results.emplace_back(
                        std::get<NamedIndividual>(source),
                        std::get<NamedIndividual>(target)
                    );
                }
            }
        }
    }

    return results;
}

std::vector<std::pair<NamedIndividual, Literal>>
Ontology::getDataPropertyAssertions(const DataProperty& property) const {
    rebuildIndices();
    std::vector<std::pair<NamedIndividual, Literal>> results;

    for (const auto& assertion : data_prop_assertion_index_) {
        if (assertion->getProperty() == property) {
            Individual source = assertion->getSource();

            if (std::holds_alternative<NamedIndividual>(source)) {
                results.emplace_back(
                    std::get<NamedIndividual>(source),
                    assertion->getTarget()
                );
            }
        }
    }

    return results;
}

// ============================================================================
// Individual Class Queries
// ============================================================================

std::vector<Class> Ontology::getClassesForIndividual(const NamedIndividual& individual) const {
    rebuildIndices();
    std::vector<Class> results;

    for (const auto& assertion : class_assertion_index_) {
        Individual asserted_individual = assertion->getIndividual();

        if (std::holds_alternative<NamedIndividual>(asserted_individual)) {
            if (std::get<NamedIndividual>(asserted_individual) == individual) {
                ClassExpressionPtr class_expr = assertion->getClassExpression();

                if (auto named_class = std::dynamic_pointer_cast<NamedClass>(class_expr)) {
                    results.push_back(named_class->getClass());
                }
            }
        }
    }

    return results;
}

bool Ontology::isInstanceOf(const NamedIndividual& individual, const Class& cls) const {
    rebuildIndices();

    for (const auto& assertion : class_assertion_index_) {
        Individual asserted_individual = assertion->getIndividual();

        if (std::holds_alternative<NamedIndividual>(asserted_individual)) {
            if (std::get<NamedIndividual>(asserted_individual) == individual) {
                ClassExpressionPtr class_expr = assertion->getClassExpression();

                if (auto named_class = std::dynamic_pointer_cast<NamedClass>(class_expr)) {
                    if (named_class->getClass() == cls) {
                        return true;
                    }
                }
            }
        }
    }

    return false;
}

// ============================================================================
// Property Characteristics
// ============================================================================

bool Ontology::isFunctionalObjectProperty(const ObjectProperty& property) const {
    for (const auto& axiom : axioms_) {
        if (auto func_prop = std::dynamic_pointer_cast<FunctionalObjectProperty>(axiom)) {
            ObjectPropertyExpression prop_expr = func_prop->getProperty();
            if (std::holds_alternative<ObjectProperty>(prop_expr)) {
                if (std::get<ObjectProperty>(prop_expr) == property) {
                    return true;
                }
            }
        }
    }
    
    return false;
}

bool Ontology::isFunctionalDataProperty(const DataProperty& property) const {
    for (const auto& axiom : axioms_) {
        if (auto func_prop = std::dynamic_pointer_cast<FunctionalDataProperty>(axiom)) {
            if (func_prop->getProperty() == property) {
                return true;
            }
        }
    }
    
    return false;
}

} // namespace owl2
} // namespace ista
