#include "ontology_filter.hpp"
#include <queue>
#include <algorithm>
#include <random>
#include <stdexcept>

namespace ista {
namespace owl2 {

// ============================================================================
// Constructor
// ============================================================================

OntologyFilter::OntologyFilter(const Ontology& ontology)
    : ontology_(std::make_shared<const Ontology>(ontology)) {}

OntologyFilter::OntologyFilter(std::shared_ptr<const Ontology> ontology)
    : ontology_(ontology) {
    if (!ontology_) {
        throw std::invalid_argument("Ontology pointer cannot be null");
    }
}

// ============================================================================
// Public Filtering Methods
// ============================================================================

FilterResult OntologyFilter::filterByIndividuals(const std::unordered_set<IRI>& iris) const {
    return createFilteredOntology(iris);
}

FilterResult OntologyFilter::filterByClasses(const std::unordered_set<IRI>& class_iris) const {
    std::unordered_set<IRI> individuals;
    
    // Collect all individuals that are instances of the specified classes
    for (const auto& class_iri : class_iris) {
        auto class_individuals = getIndividualsOfClass(class_iri);
        individuals.insert(class_individuals.begin(), class_individuals.end());
    }
    
    return createFilteredOntology(individuals);
}

FilterResult OntologyFilter::filterByProperty(const IRI& property, const Literal& value) const {
    std::unordered_set<IRI> individuals;
    
    // Check DataPropertyAssertion axioms
    for (const auto& axiom : ontology_->getAxioms()) {
        if (auto data_prop = std::dynamic_pointer_cast<DataPropertyAssertion>(axiom)) {
            if (data_prop->getProperty().getIRI() == property &&
                data_prop->getTarget() == value) {
                // Extract the source individual
                if (std::holds_alternative<NamedIndividual>(data_prop->getSource())) {
                    individuals.insert(std::get<NamedIndividual>(data_prop->getSource()).getIRI());
                }
            }
        }
    }
    
    return createFilteredOntology(individuals);
}

FilterResult OntologyFilter::filterByObjectProperty(const IRI& property, const IRI& target) const {
    std::unordered_set<IRI> individuals;
    
    // Check ObjectPropertyAssertion axioms
    for (const auto& axiom : ontology_->getAxioms()) {
        if (auto obj_prop = std::dynamic_pointer_cast<ObjectPropertyAssertion>(axiom)) {
            // Check if property matches
            if (std::holds_alternative<ObjectProperty>(obj_prop->getProperty())) {
                auto prop = std::get<ObjectProperty>(obj_prop->getProperty());
                if (prop.getIRI() == property) {
                    // Check if target matches
                    if (std::holds_alternative<NamedIndividual>(obj_prop->getTarget())) {
                        auto target_ind = std::get<NamedIndividual>(obj_prop->getTarget());
                        if (target_ind.getIRI() == target) {
                            // Add the source individual
                            if (std::holds_alternative<NamedIndividual>(obj_prop->getSource())) {
                                individuals.insert(std::get<NamedIndividual>(obj_prop->getSource()).getIRI());
                            }
                        }
                    }
                }
            }
        }
    }
    
    return createFilteredOntology(individuals);
}

FilterResult OntologyFilter::extractNeighborhood(const IRI& seed, int depth) const {
    return extractNeighborhood(std::unordered_set<IRI>{seed}, depth);
}

FilterResult OntologyFilter::extractNeighborhood(const std::unordered_set<IRI>& seeds, int depth) const {
    if (depth < 0) {
        throw std::invalid_argument("Depth must be non-negative");
    }
    
    // Build adjacency list for efficient graph traversal
    auto adj_list = buildAdjacencyList();
    
    // Perform BFS traversal
    auto reachable = bfsTraversal(seeds, depth, adj_list);
    
    return createFilteredOntology(reachable);
}

FilterResult OntologyFilter::extractPath(const IRI& start, const IRI& end) const {
    // Build adjacency list
    auto adj_list = buildAdjacencyList();
    
    // Find path using BFS
    auto path_individuals = findPath(start, end, adj_list);
    
    return createFilteredOntology(path_individuals);
}

FilterResult OntologyFilter::randomSample(size_t n, unsigned int seed) const {
    auto all_individuals = getAllIndividuals();
    
    if (n >= all_individuals.size()) {
        // Return all individuals if n is larger than total
        return createFilteredOntology(all_individuals);
    }
    
    // Convert to vector for random sampling
    std::vector<IRI> individual_vec(all_individuals.begin(), all_individuals.end());
    
    // Shuffle and take first n elements
    std::mt19937 rng(seed);
    std::shuffle(individual_vec.begin(), individual_vec.end(), rng);
    
    std::unordered_set<IRI> sampled(individual_vec.begin(), individual_vec.begin() + n);
    
    return createFilteredOntology(sampled);
}

FilterResult OntologyFilter::applyFilter(const FilterCriteria& criteria) const {
    std::unordered_set<IRI> individuals;
    
    // Start with explicitly included individuals
    individuals.insert(criteria.include_individuals.begin(), 
                      criteria.include_individuals.end());
    
    // Add individuals from specified classes
    for (const auto& class_iri : criteria.include_classes) {
        auto class_individuals = getIndividualsOfClass(class_iri);
        individuals.insert(class_individuals.begin(), class_individuals.end());
    }
    
    // Apply neighborhood expansion if max_depth is specified
    if (criteria.max_depth >= 0 && !individuals.empty()) {
        auto adj_list = buildAdjacencyList();
        individuals = bfsTraversal(individuals, criteria.max_depth, adj_list);
    }
    
    // Remove excluded individuals
    for (const auto& excluded : criteria.exclude_individuals) {
        individuals.erase(excluded);
    }
    
    // Apply property value filters
    if (!criteria.property_value_filters.empty()) {
        std::unordered_set<IRI> filtered_individuals;
        for (const auto& ind_iri : individuals) {
            bool matches = true;
            for (const auto& [prop_iri, allowed_values] : criteria.property_value_filters) {
                // Check if individual has any of the allowed values for this property
                bool has_allowed_value = false;
                for (const auto& axiom : ontology_->getAxioms()) {
                    if (auto data_prop = std::dynamic_pointer_cast<DataPropertyAssertion>(axiom)) {
                        if (data_prop->getProperty().getIRI() == prop_iri) {
                            if (std::holds_alternative<NamedIndividual>(data_prop->getSource())) {
                                auto source = std::get<NamedIndividual>(data_prop->getSource());
                                if (source.getIRI() == ind_iri) {
                                    auto value = data_prop->getTarget().getLexicalForm();
                                    if (allowed_values.find(value) != allowed_values.end()) {
                                        has_allowed_value = true;
                                        break;
                                    }
                                }
                            }
                        }
                    }
                }
                if (!has_allowed_value) {
                    matches = false;
                    break;
                }
            }
            if (matches) {
                filtered_individuals.insert(ind_iri);
            }
        }
        individuals = filtered_individuals;
    }
    
    // Create the filtered ontology
    auto result = createFilteredOntology(individuals);
    
    // Apply custom filter if provided
    if (criteria.custom_filter) {
        auto filtered_axioms = std::make_shared<Ontology>();
        copyMetadata(*filtered_axioms);
        
        for (const auto& axiom : result.ontology->getAxioms()) {
            if (criteria.custom_filter(axiom)) {
                filtered_axioms->addAxiom(axiom);
            }
        }
        
        result.ontology = filtered_axioms;
        result.filtered_axiom_count = filtered_axioms->getAxiomCount();
    }
    
    return result;
}

// ============================================================================
// Builder Pattern Methods
// ============================================================================

OntologyFilter& OntologyFilter::withIndividuals(const std::unordered_set<IRI>& iris) {
    criteria_.include_individuals.insert(iris.begin(), iris.end());
    return *this;
}

OntologyFilter& OntologyFilter::withClasses(const std::unordered_set<IRI>& class_iris) {
    criteria_.include_classes.insert(class_iris.begin(), class_iris.end());
    return *this;
}

OntologyFilter& OntologyFilter::excludeIndividuals(const std::unordered_set<IRI>& iris) {
    criteria_.exclude_individuals.insert(iris.begin(), iris.end());
    return *this;
}

OntologyFilter& OntologyFilter::withMaxDepth(int depth) {
    criteria_.max_depth = depth;
    return *this;
}

OntologyFilter& OntologyFilter::includeClassHierarchy(bool include) {
    criteria_.include_class_hierarchy = include;
    return *this;
}

OntologyFilter& OntologyFilter::includePropertyHierarchy(bool include) {
    criteria_.include_property_hierarchy = include;
    return *this;
}

OntologyFilter& OntologyFilter::includeDeclarations(bool include) {
    criteria_.include_declarations = include;
    return *this;
}

FilterResult OntologyFilter::execute() const {
    return applyFilter(criteria_);
}

// ============================================================================
// Private Helper Methods
// ============================================================================

std::unordered_set<IRI> OntologyFilter::getAllIndividuals() const {
    std::unordered_set<IRI> individuals;
    
    for (const auto& ind : ontology_->getIndividuals()) {
        individuals.insert(ind.getIRI());
    }
    
    return individuals;
}

std::unordered_set<IRI> OntologyFilter::getIndividualsOfClass(const IRI& class_iri) const {
    std::unordered_set<IRI> individuals;
    
    for (const auto& axiom : ontology_->getAxioms()) {
        if (auto class_assertion = std::dynamic_pointer_cast<ClassAssertion>(axiom)) {
            // Check if class matches
            if (auto named_class = std::dynamic_pointer_cast<NamedClass>(class_assertion->getClassExpression())) {
                if (named_class->getClass().getIRI() == class_iri) {
                    // Add the individual
                    if (std::holds_alternative<NamedIndividual>(class_assertion->getIndividual())) {
                        individuals.insert(std::get<NamedIndividual>(class_assertion->getIndividual()).getIRI());
                    }
                }
            }
        }
    }
    
    return individuals;
}

std::unordered_map<IRI, std::unordered_set<IRI>> OntologyFilter::buildAdjacencyList() const {
    std::unordered_map<IRI, std::unordered_set<IRI>> adj_list;
    
    // Process ObjectPropertyAssertion axioms to build graph edges
    for (const auto& axiom : ontology_->getAxioms()) {
        if (auto obj_prop = std::dynamic_pointer_cast<ObjectPropertyAssertion>(axiom)) {
            // Extract source and target individuals
            if (std::holds_alternative<NamedIndividual>(obj_prop->getSource()) &&
                std::holds_alternative<NamedIndividual>(obj_prop->getTarget())) {
                
                auto source = std::get<NamedIndividual>(obj_prop->getSource()).getIRI();
                auto target = std::get<NamedIndividual>(obj_prop->getTarget()).getIRI();
                
                // Add bidirectional edges (undirected graph for neighborhood extraction)
                adj_list[source].insert(target);
                adj_list[target].insert(source);
            }
        }
    }
    
    return adj_list;
}

std::unordered_set<IRI> OntologyFilter::bfsTraversal(
    const std::unordered_set<IRI>& seeds,
    int depth,
    const std::unordered_map<IRI, std::unordered_set<IRI>>& adj_list) const {
    
    std::unordered_set<IRI> visited;
    std::queue<std::pair<IRI, int>> queue;  // (node, current_depth)
    
    // Initialize queue with seed nodes
    for (const auto& seed : seeds) {
        queue.push({seed, 0});
        visited.insert(seed);
    }
    
    // BFS traversal
    while (!queue.empty()) {
        auto [current, current_depth] = queue.front();
        queue.pop();
        
        // Stop if we've reached max depth
        if (current_depth >= depth) {
            continue;
        }
        
        // Visit neighbors
        auto it = adj_list.find(current);
        if (it != adj_list.end()) {
            for (const auto& neighbor : it->second) {
                if (visited.find(neighbor) == visited.end()) {
                    visited.insert(neighbor);
                    queue.push({neighbor, current_depth + 1});
                }
            }
        }
    }
    
    return visited;
}

std::unordered_set<IRI> OntologyFilter::findPath(
    const IRI& start,
    const IRI& end,
    const std::unordered_map<IRI, std::unordered_set<IRI>>& adj_list) const {
    
    // BFS to find shortest path
    std::unordered_map<IRI, IRI> parent;  // Track path
    std::unordered_set<IRI> visited;
    std::queue<IRI> queue;
    
    queue.push(start);
    visited.insert(start);
    parent.emplace(start, start);  // Mark start as its own parent
    
    bool found = false;
    
    while (!queue.empty() && !found) {
        auto current = queue.front();
        queue.pop();
        
        if (current == end) {
            found = true;
            break;
        }
        
        auto it = adj_list.find(current);
        if (it != adj_list.end()) {
            for (const auto& neighbor : it->second) {
                if (visited.find(neighbor) == visited.end()) {
                    visited.insert(neighbor);
                    parent.emplace(neighbor, current);
                    queue.push(neighbor);
                }
            }
        }
    }
    
    // Reconstruct path
    std::unordered_set<IRI> path_individuals;
    
    if (found) {
        IRI current = end;
        while (current != start) {
            path_individuals.insert(current);
            current = parent.at(current);
        }
        path_individuals.insert(start);
    }
    
    return path_individuals;
}

bool OntologyFilter::axiomReferencesIndividuals(
    const AxiomPtr& axiom,
    const std::unordered_set<IRI>& individuals) const {
    
    auto referenced = extractIndividualsFromAxiom(axiom);
    
    for (const auto& ind_iri : referenced) {
        if (individuals.find(ind_iri) != individuals.end()) {
            return true;
        }
    }
    
    return false;
}

std::unordered_set<IRI> OntologyFilter::extractIndividualsFromAxiom(const AxiomPtr& axiom) const {
    std::unordered_set<IRI> individuals;
    
    // ClassAssertion
    if (auto class_assertion = std::dynamic_pointer_cast<ClassAssertion>(axiom)) {
        if (std::holds_alternative<NamedIndividual>(class_assertion->getIndividual())) {
            individuals.insert(std::get<NamedIndividual>(class_assertion->getIndividual()).getIRI());
        }
    }
    // ObjectPropertyAssertion
    else if (auto obj_prop = std::dynamic_pointer_cast<ObjectPropertyAssertion>(axiom)) {
        if (std::holds_alternative<NamedIndividual>(obj_prop->getSource())) {
            individuals.insert(std::get<NamedIndividual>(obj_prop->getSource()).getIRI());
        }
        if (std::holds_alternative<NamedIndividual>(obj_prop->getTarget())) {
            individuals.insert(std::get<NamedIndividual>(obj_prop->getTarget()).getIRI());
        }
    }
    // DataPropertyAssertion
    else if (auto data_prop = std::dynamic_pointer_cast<DataPropertyAssertion>(axiom)) {
        if (std::holds_alternative<NamedIndividual>(data_prop->getSource())) {
            individuals.insert(std::get<NamedIndividual>(data_prop->getSource()).getIRI());
        }
    }
    // NegativeObjectPropertyAssertion
    else if (auto neg_obj_prop = std::dynamic_pointer_cast<NegativeObjectPropertyAssertion>(axiom)) {
        if (std::holds_alternative<NamedIndividual>(neg_obj_prop->getSource())) {
            individuals.insert(std::get<NamedIndividual>(neg_obj_prop->getSource()).getIRI());
        }
        if (std::holds_alternative<NamedIndividual>(neg_obj_prop->getTarget())) {
            individuals.insert(std::get<NamedIndividual>(neg_obj_prop->getTarget()).getIRI());
        }
    }
    // NegativeDataPropertyAssertion
    else if (auto neg_data_prop = std::dynamic_pointer_cast<NegativeDataPropertyAssertion>(axiom)) {
        if (std::holds_alternative<NamedIndividual>(neg_data_prop->getSource())) {
            individuals.insert(std::get<NamedIndividual>(neg_data_prop->getSource()).getIRI());
        }
    }
    // SameIndividual
    else if (auto same_ind = std::dynamic_pointer_cast<SameIndividual>(axiom)) {
        for (const auto& ind : same_ind->getIndividuals()) {
            if (std::holds_alternative<NamedIndividual>(ind)) {
                individuals.insert(std::get<NamedIndividual>(ind).getIRI());
            }
        }
    }
    // DifferentIndividuals
    else if (auto diff_ind = std::dynamic_pointer_cast<DifferentIndividuals>(axiom)) {
        for (const auto& ind : diff_ind->getIndividuals()) {
            if (std::holds_alternative<NamedIndividual>(ind)) {
                individuals.insert(std::get<NamedIndividual>(ind).getIRI());
            }
        }
    }
    
    return individuals;
}

FilterResult OntologyFilter::createFilteredOntology(const std::unordered_set<IRI>& individuals) const {
    FilterResult result;
    result.ontology = std::make_shared<Ontology>();
    result.original_axiom_count = ontology_->getAxiomCount();
    result.original_individual_count = getAllIndividuals().size();
    result.included_individuals = individuals;
    result.filtered_individual_count = individuals.size();
    
    // Copy metadata
    copyMetadata(*result.ontology);
    
    // Collect classes and properties referenced by included individuals
    std::unordered_set<IRI> referenced_classes;
    std::unordered_set<IRI> referenced_properties;
    std::unordered_set<IRI> referenced_entities;
    
    // Add all axioms that reference the included individuals
    for (const auto& axiom : ontology_->getAxioms()) {
        if (axiomReferencesIndividuals(axiom, individuals)) {
            result.ontology->addAxiom(axiom);
            
            // Track referenced entities for declarations
            if (auto class_assertion = std::dynamic_pointer_cast<ClassAssertion>(axiom)) {
                if (auto named_class = std::dynamic_pointer_cast<NamedClass>(class_assertion->getClassExpression())) {
                    referenced_classes.insert(named_class->getClass().getIRI());
                    referenced_entities.insert(named_class->getClass().getIRI());
                }
            }
            else if (auto obj_prop = std::dynamic_pointer_cast<ObjectPropertyAssertion>(axiom)) {
                if (std::holds_alternative<ObjectProperty>(obj_prop->getProperty())) {
                    auto prop = std::get<ObjectProperty>(obj_prop->getProperty());
                    referenced_properties.insert(prop.getIRI());
                    referenced_entities.insert(prop.getIRI());
                }
            }
            else if (auto data_prop = std::dynamic_pointer_cast<DataPropertyAssertion>(axiom)) {
                referenced_properties.insert(data_prop->getProperty().getIRI());
                referenced_entities.insert(data_prop->getProperty().getIRI());
            }
        }
    }
    
    // Add individual declarations
    for (const auto& ind_iri : individuals) {
        referenced_entities.insert(ind_iri);
    }
    
    // Add class hierarchy axioms if requested (default: true)
    if (criteria_.include_class_hierarchy) {
        addClassHierarchyAxioms(*result.ontology, referenced_classes);
    }
    
    // Add property hierarchy axioms if requested (default: true)
    if (criteria_.include_property_hierarchy) {
        addPropertyHierarchyAxioms(*result.ontology, referenced_properties);
    }
    
    // Add declarations if requested (default: true)
    if (criteria_.include_declarations) {
        addDeclarations(*result.ontology, referenced_entities);
    }
    
    result.filtered_axiom_count = result.ontology->getAxiomCount();
    
    return result;
}

void OntologyFilter::addClassHierarchyAxioms(
    Ontology& target,
    const std::unordered_set<IRI>& class_iris) const {
    
    for (const auto& axiom : ontology_->getAxioms()) {
        // SubClassOf axioms
        if (auto subclass = std::dynamic_pointer_cast<SubClassOf>(axiom)) {
            if (auto sub = std::dynamic_pointer_cast<NamedClass>(subclass->getSubClass())) {
                if (auto sup = std::dynamic_pointer_cast<NamedClass>(subclass->getSuperClass())) {
                    if (class_iris.find(sub->getClass().getIRI()) != class_iris.end() ||
                        class_iris.find(sup->getClass().getIRI()) != class_iris.end()) {
                        target.addAxiom(axiom);
                    }
                }
            }
        }
        // EquivalentClasses axioms
        else if (auto equiv = std::dynamic_pointer_cast<EquivalentClasses>(axiom)) {
            bool references_target_class = false;
            for (const auto& expr : equiv->getClassExpressions()) {
                if (auto named = std::dynamic_pointer_cast<NamedClass>(expr)) {
                    if (class_iris.find(named->getClass().getIRI()) != class_iris.end()) {
                        references_target_class = true;
                        break;
                    }
                }
            }
            if (references_target_class) {
                target.addAxiom(axiom);
            }
        }
        // DisjointClasses axioms
        else if (auto disjoint = std::dynamic_pointer_cast<DisjointClasses>(axiom)) {
            bool references_target_class = false;
            for (const auto& expr : disjoint->getClassExpressions()) {
                if (auto named = std::dynamic_pointer_cast<NamedClass>(expr)) {
                    if (class_iris.find(named->getClass().getIRI()) != class_iris.end()) {
                        references_target_class = true;
                        break;
                    }
                }
            }
            if (references_target_class) {
                target.addAxiom(axiom);
            }
        }
    }
}

void OntologyFilter::addPropertyHierarchyAxioms(
    Ontology& target,
    const std::unordered_set<IRI>& property_iris) const {
    
    for (const auto& axiom : ontology_->getAxioms()) {
        // SubObjectPropertyOf axioms
        if (auto subprop = std::dynamic_pointer_cast<SubObjectPropertyOf>(axiom)) {
            bool references_property = false;
            
            if (auto sub = subprop->getSubProperty()) {
                if (std::holds_alternative<ObjectProperty>(*sub)) {
                    auto prop = std::get<ObjectProperty>(*sub);
                    if (property_iris.find(prop.getIRI()) != property_iris.end()) {
                        references_property = true;
                    }
                }
            }
            
            if (std::holds_alternative<ObjectProperty>(subprop->getSuperProperty())) {
                auto prop = std::get<ObjectProperty>(subprop->getSuperProperty());
                if (property_iris.find(prop.getIRI()) != property_iris.end()) {
                    references_property = true;
                }
            }
            
            if (references_property) {
                target.addAxiom(axiom);
            }
        }
        // SubDataPropertyOf axioms
        else if (auto subprop = std::dynamic_pointer_cast<SubDataPropertyOf>(axiom)) {
            if (property_iris.find(subprop->getSubProperty().getIRI()) != property_iris.end() ||
                property_iris.find(subprop->getSuperProperty().getIRI()) != property_iris.end()) {
                target.addAxiom(axiom);
            }
        }
        // Property domain and range axioms
        else if (auto domain = std::dynamic_pointer_cast<ObjectPropertyDomain>(axiom)) {
            if (std::holds_alternative<ObjectProperty>(domain->getProperty())) {
                auto prop = std::get<ObjectProperty>(domain->getProperty());
                if (property_iris.find(prop.getIRI()) != property_iris.end()) {
                    target.addAxiom(axiom);
                }
            }
        }
        else if (auto range = std::dynamic_pointer_cast<ObjectPropertyRange>(axiom)) {
            if (std::holds_alternative<ObjectProperty>(range->getProperty())) {
                auto prop = std::get<ObjectProperty>(range->getProperty());
                if (property_iris.find(prop.getIRI()) != property_iris.end()) {
                    target.addAxiom(axiom);
                }
            }
        }
        else if (auto domain = std::dynamic_pointer_cast<DataPropertyDomain>(axiom)) {
            if (property_iris.find(domain->getProperty().getIRI()) != property_iris.end()) {
                target.addAxiom(axiom);
            }
        }
        else if (auto range = std::dynamic_pointer_cast<DataPropertyRange>(axiom)) {
            if (property_iris.find(range->getProperty().getIRI()) != property_iris.end()) {
                target.addAxiom(axiom);
            }
        }
    }
}

void OntologyFilter::addDeclarations(
    Ontology& target,
    const std::unordered_set<IRI>& entity_iris) const {
    
    for (const auto& axiom : ontology_->getAxioms()) {
        if (auto decl = std::dynamic_pointer_cast<Declaration>(axiom)) {
            if (entity_iris.find(decl->getIRI()) != entity_iris.end()) {
                target.addAxiom(axiom);
            }
        }
    }
}

void OntologyFilter::copyMetadata(Ontology& target) const {
    // Copy ontology IRI and version
    if (ontology_->getOntologyIRI()) {
        target.setOntologyIRI(*ontology_->getOntologyIRI());
    }
    if (ontology_->getVersionIRI()) {
        target.setVersionIRI(*ontology_->getVersionIRI());
    }
    
    // Copy prefixes
    for (const auto& [prefix, ns] : ontology_->getPrefixMap()) {
        target.registerPrefix(prefix, ns);
    }
    
    // Copy imports
    for (const auto& import_iri : ontology_->getImports()) {
        target.addImport(import_iri);
    }
    
    // Copy ontology annotations
    target.setOntologyAnnotations(ontology_->getOntologyAnnotations());
}

} // namespace owl2
} // namespace ista
