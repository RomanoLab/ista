#ifndef ISTA_OWL2_ONTOLOGY_FILTER_HPP
#define ISTA_OWL2_ONTOLOGY_FILTER_HPP

#include "ontology.hpp"
#include "entity.hpp"
#include "literal.hpp"
#include <unordered_set>
#include <unordered_map>
#include <vector>
#include <functional>
#include <optional>
#include <memory>

namespace ista {
namespace owl2 {

// Forward declaration
class Ontology;

/**
 * @brief Criteria for filtering ontology content
 * 
 * This struct holds all the filtering options that can be applied
 * to an ontology to extract a subgraph.
 */
struct FilterCriteria {
    // Individuals to include explicitly
    std::unordered_set<IRI> include_individuals;
    
    // Classes whose instances should be included
    std::unordered_set<IRI> include_classes;
    
    // Individuals to exclude explicitly
    std::unordered_set<IRI> exclude_individuals;
    
    // Property filters: property IRI → allowed values
    std::unordered_map<IRI, std::unordered_set<std::string>> property_value_filters;
    
    // Maximum depth for neighborhood extraction (0 = only seed nodes)
    int max_depth = -1;  // -1 means no limit
    
    // Whether to include class hierarchy axioms for included individuals
    bool include_class_hierarchy = true;
    
    // Whether to include property hierarchy axioms
    bool include_property_hierarchy = true;
    
    // Whether to include all declarations for referenced entities
    bool include_declarations = true;
    
    // Custom filter function for additional filtering logic
    std::function<bool(const AxiomPtr&)> custom_filter;
    
    FilterCriteria() = default;
};

/**
 * @brief Result of a filtering operation
 * 
 * Contains the filtered ontology and metadata about the filtering process.
 */
struct FilterResult {
    // The filtered ontology
    std::shared_ptr<Ontology> ontology;
    
    // Statistics about the filtering
    size_t original_axiom_count = 0;
    size_t filtered_axiom_count = 0;
    size_t original_individual_count = 0;
    size_t filtered_individual_count = 0;
    
    // Individuals that were included
    std::unordered_set<IRI> included_individuals;
    
    FilterResult() : ontology(std::make_shared<Ontology>()) {}
    explicit FilterResult(std::shared_ptr<Ontology> onto) : ontology(onto) {}
};

/**
 * @brief High-performance ontology filtering and subgraph extraction
 * 
 * This class provides methods to filter ontologies based on various criteria,
 * extracting subgraphs efficiently using hash-based lookups and graph algorithms.
 * 
 * Usage:
 *   OntologyFilter filter(ontology);
 *   auto result = filter.filterByIndividuals({iri1, iri2});
 *   // result.ontology contains the filtered ontology
 */
class OntologyFilter {
public:
    /**
     * @brief Construct a filter for the given ontology
     * @param ontology The ontology to filter
     */
    explicit OntologyFilter(const Ontology& ontology);
    
    /**
     * @brief Construct a filter with shared ownership of ontology
     * @param ontology Shared pointer to the ontology to filter
     */
    explicit OntologyFilter(std::shared_ptr<const Ontology> ontology);
    
    /**
     * @brief Extract a subgraph containing specific individuals
     * 
     * Includes all axioms that reference the specified individuals,
     * along with their class assertions and property assertions.
     * 
     * @param iris Set of individual IRIs to include
     * @return FilterResult containing the filtered ontology
     */
    FilterResult filterByIndividuals(const std::unordered_set<IRI>& iris) const;
    
    /**
     * @brief Filter by class membership
     * 
     * Includes all individuals that are instances of the specified classes
     * (according to ClassAssertion axioms), along with their related axioms.
     * 
     * @param class_iris Set of class IRIs
     * @return FilterResult containing the filtered ontology
     */
    FilterResult filterByClasses(const std::unordered_set<IRI>& class_iris) const;
    
    /**
     * @brief Filter by property value
     * 
     * Includes individuals that have the specified property with the given value.
     * For DataPropertyAssertion axioms, matches against the literal value.
     * For ObjectPropertyAssertion axioms, matches against the target individual's IRI.
     * 
     * @param property The property IRI to filter by
     * @param value The literal value to match
     * @return FilterResult containing the filtered ontology
     */
    FilterResult filterByProperty(const IRI& property, const Literal& value) const;
    
    /**
     * @brief Filter by object property target
     * 
     * Includes individuals that have the specified object property
     * pointing to the given target individual.
     * 
     * @param property The object property IRI
     * @param target The target individual IRI
     * @return FilterResult containing the filtered ontology
     */
    FilterResult filterByObjectProperty(const IRI& property, const IRI& target) const;
    
    /**
     * @brief Extract k-hop neighborhood around seed individual(s)
     * 
     * Uses BFS to traverse the ontology graph, following property assertions
     * up to the specified depth. Depth 0 includes only the seed node(s).
     * 
     * @param seed The seed individual IRI
     * @param depth Maximum number of hops (property edges) to traverse
     * @return FilterResult containing the neighborhood subgraph
     */
    FilterResult extractNeighborhood(const IRI& seed, int depth) const;
    
    /**
     * @brief Extract k-hop neighborhood around multiple seed individuals
     * 
     * @param seeds Set of seed individual IRIs
     * @param depth Maximum number of hops to traverse
     * @return FilterResult containing the neighborhood subgraph
     */
    FilterResult extractNeighborhood(const std::unordered_set<IRI>& seeds, int depth) const;
    
    /**
     * @brief Extract path(s) between two individuals
     * 
     * Uses BFS to find if a path exists between start and end individuals
     * through property assertions. Includes all axioms on the shortest path(s).
     * 
     * @param start Starting individual IRI
     * @param end Target individual IRI
     * @return FilterResult containing the path subgraph (empty if no path exists)
     */
    FilterResult extractPath(const IRI& start, const IRI& end) const;
    
    /**
     * @brief Random sampling of individuals
     * 
     * Randomly selects n individuals and extracts their axioms.
     * Useful for creating training/test splits or sampling large ontologies.
     * 
     * @param n Number of individuals to sample
     * @param seed Random seed for reproducibility
     * @return FilterResult containing the sampled subgraph
     */
    FilterResult randomSample(size_t n, unsigned int seed = 42) const;
    
    /**
     * @brief Apply custom filter criteria
     * 
     * Provides maximum flexibility by allowing arbitrary filtering logic
     * through the FilterCriteria struct.
     * 
     * @param criteria The filter criteria to apply
     * @return FilterResult containing the filtered ontology
     */
    FilterResult applyFilter(const FilterCriteria& criteria) const;
    
    /**
     * @brief Builder pattern: start building a filter
     * 
     * Returns *this for method chaining.
     */
    OntologyFilter& withIndividuals(const std::unordered_set<IRI>& iris);
    OntologyFilter& withClasses(const std::unordered_set<IRI>& class_iris);
    OntologyFilter& excludeIndividuals(const std::unordered_set<IRI>& iris);
    OntologyFilter& withMaxDepth(int depth);
    OntologyFilter& includeClassHierarchy(bool include);
    OntologyFilter& includePropertyHierarchy(bool include);
    OntologyFilter& includeDeclarations(bool include);
    
    /**
     * @brief Execute the built filter
     * @return FilterResult containing the filtered ontology
     */
    FilterResult execute() const;
    
    /**
     * @brief Get the source ontology
     */
    std::shared_ptr<const Ontology> getOntology() const { return ontology_; }

private:
    std::shared_ptr<const Ontology> ontology_;
    FilterCriteria criteria_;
    
    // Internal helper methods
    
    /**
     * @brief Get all individuals mentioned in the ontology
     */
    std::unordered_set<IRI> getAllIndividuals() const;
    
    /**
     * @brief Get individuals that are instances of a class
     */
    std::unordered_set<IRI> getIndividualsOfClass(const IRI& class_iri) const;
    
    /**
     * @brief Build adjacency list for graph traversal
     * Returns map: individual IRI → set of connected individual IRIs
     */
    std::unordered_map<IRI, std::unordered_set<IRI>> buildAdjacencyList() const;
    
    /**
     * @brief BFS traversal from seed nodes up to depth
     */
    std::unordered_set<IRI> bfsTraversal(
        const std::unordered_set<IRI>& seeds,
        int depth,
        const std::unordered_map<IRI, std::unordered_set<IRI>>& adj_list) const;
    
    /**
     * @brief BFS to find path between two nodes
     * Returns set of all individuals on shortest path(s)
     */
    std::unordered_set<IRI> findPath(
        const IRI& start,
        const IRI& end,
        const std::unordered_map<IRI, std::unordered_set<IRI>>& adj_list) const;
    
    /**
     * @brief Check if an axiom references any of the target individuals
     */
    bool axiomReferencesIndividuals(
        const AxiomPtr& axiom,
        const std::unordered_set<IRI>& individuals) const;
    
    /**
     * @brief Extract IRIs of individuals mentioned in an axiom
     */
    std::unordered_set<IRI> extractIndividualsFromAxiom(const AxiomPtr& axiom) const;
    
    /**
     * @brief Create filtered ontology from set of individuals
     * Includes all axioms that reference these individuals
     */
    FilterResult createFilteredOntology(const std::unordered_set<IRI>& individuals) const;
    
    /**
     * @brief Add class hierarchy axioms for the given classes
     */
    void addClassHierarchyAxioms(
        Ontology& target,
        const std::unordered_set<IRI>& class_iris) const;
    
    /**
     * @brief Add property hierarchy axioms
     */
    void addPropertyHierarchyAxioms(
        Ontology& target,
        const std::unordered_set<IRI>& property_iris) const;
    
    /**
     * @brief Add declarations for referenced entities
     */
    void addDeclarations(
        Ontology& target,
        const std::unordered_set<IRI>& entity_iris) const;
    
    /**
     * @brief Copy ontology metadata (IRI, version, prefixes, imports)
     */
    void copyMetadata(Ontology& target) const;
};

} // namespace owl2
} // namespace ista

#endif // ISTA_OWL2_ONTOLOGY_FILTER_HPP
