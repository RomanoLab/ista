#ifndef ISTA_OWL2_TURTLE_SERIALIZER_HPP
#define ISTA_OWL2_TURTLE_SERIALIZER_HPP

#include "../core/ontology.hpp"
#include <string>
#include <map>
#include <sstream>
#include <unordered_map>
#include <set>

namespace ista {
namespace owl2 {

/**
 * @brief Serializer for Turtle (Terse RDF Triple Language) format
 * 
 * Writes ontologies to Turtle format, which is a compact, human-readable
 * RDF serialization. Turtle is particularly efficient for large ontologies
 * with many individuals, producing smaller files than RDF/XML or OWL/XML.
 * 
 * @par Implementation Status
 * **Fully Implemented:**
 * - Prefix declarations (@prefix)
 * - IRI references (prefix:local and <full-iri>)
 * - Literals (plain, typed with ^^, language-tagged with @)
 * - Triples (subject predicate object .)
 * - Declaration axioms (classes, properties, individuals)
 * - Class assertions (individual rdf:type Class)
 * - Object/Data property assertions
 * - Annotation assertions
 * - SubClassOf, SubPropertyOf axioms
 * - Property domain/range axioms
 * - Property characteristics (functional, transitive)
 * - Blank nodes for anonymous individuals
 * - Ontology metadata (versionIRI, imports)
 * 
 * **Not Yet Implemented:**
 * - Subject-predicate grouping with semicolons (;)
 * - Object lists with commas (,)
 * - Collection syntax with parentheses ()
 * - Blank node property lists with brackets []
 * - Complex class expressions (currently output as owl:Thing)
 * - Property chains and other complex axioms
 * 
 * **Current Limitations:**
 * - Each triple is written on a separate line (no grouping)
 * - Named class expressions only (restrictions fall back to owl:Thing)
 * - Simple object/data properties only (no inverse property paths)
 * 
 * Despite these limitations, the serializer handles the most common use cases
 * for ontologies with individuals and is particularly well-suited for ABox data.
 * 
 * @see https://www.w3.org/TR/turtle/
 */
class TurtleSerializer {
public:
    /**
     * @brief Serialize ontology to Turtle string
     * @param ontology The ontology to serialize
     * @return String containing Turtle format
     */
    static std::string serialize(const Ontology& ontology);
    
    /**
     * @brief Serialize ontology to Turtle file
     * @param ontology The ontology to serialize
     * @param filename Output file path
     * @return true if successful, false otherwise
     */
    static bool serializeToFile(const Ontology& ontology, const std::string& filename);
    
    /**
     * @brief Serialize with custom prefix mappings
     * @param ontology The ontology to serialize
     * @param prefixes Map of prefix to namespace URI
     * @return String containing Turtle format
     */
    static std::string serialize(const Ontology& ontology, 
                                 const std::map<std::string, std::string>& prefixes);

private:
    /**
     * @brief Helper class for building Turtle output
     */
    class Builder {
    public:
        explicit Builder(const Ontology& ontology);
        Builder(const Ontology& ontology, const std::map<std::string, std::string>& custom_prefixes);
        
        std::string build();
        
    private:
        const Ontology& ontology_;
        std::ostringstream ttl_;
        std::unordered_map<std::string, std::string> namespaces_;  // ns -> prefix
        std::unordered_map<std::string, std::string> prefixes_;    // prefix -> ns
        int blank_node_counter_;
        std::set<std::string> written_subjects_;  // Track subjects already written
        
        // Building phases
        void writePrefixes();
        void writeOntologyHeader();
        void writeAxioms();
        
        // Axiom serialization
        void writeDeclaration(const std::shared_ptr<Declaration>& axiom);
        void writeSubClassOf(const std::shared_ptr<SubClassOf>& axiom);
        void writeEquivalentClasses(const std::shared_ptr<EquivalentClasses>& axiom);
        void writeDisjointClasses(const std::shared_ptr<DisjointClasses>& axiom);
        void writeClassAssertion(const std::shared_ptr<ClassAssertion>& axiom);
        void writeObjectPropertyAssertion(const std::shared_ptr<ObjectPropertyAssertion>& axiom);
        void writeDataPropertyAssertion(const std::shared_ptr<DataPropertyAssertion>& axiom);
        void writeNegativeObjectPropertyAssertion(const std::shared_ptr<NegativeObjectPropertyAssertion>& axiom);
        void writeNegativeDataPropertyAssertion(const std::shared_ptr<NegativeDataPropertyAssertion>& axiom);
        void writeSubObjectPropertyOf(const std::shared_ptr<SubObjectPropertyOf>& axiom);
        void writeSubDataPropertyOf(const std::shared_ptr<SubDataPropertyOf>& axiom);
        void writeObjectPropertyDomain(const std::shared_ptr<ObjectPropertyDomain>& axiom);
        void writeObjectPropertyRange(const std::shared_ptr<ObjectPropertyRange>& axiom);
        void writeDataPropertyDomain(const std::shared_ptr<DataPropertyDomain>& axiom);
        void writeDataPropertyRange(const std::shared_ptr<DataPropertyRange>& axiom);
        void writeFunctionalObjectProperty(const std::shared_ptr<FunctionalObjectProperty>& axiom);
        void writeFunctionalDataProperty(const std::shared_ptr<FunctionalDataProperty>& axiom);
        void writeInverseFunctionalObjectProperty(const std::shared_ptr<InverseFunctionalObjectProperty>& axiom);
        void writeTransitiveObjectProperty(const std::shared_ptr<TransitiveObjectProperty>& axiom);
        void writeSymmetricObjectProperty(const std::shared_ptr<SymmetricObjectProperty>& axiom);
        void writeAsymmetricObjectProperty(const std::shared_ptr<AsymmetricObjectProperty>& axiom);
        void writeReflexiveObjectProperty(const std::shared_ptr<ReflexiveObjectProperty>& axiom);
        void writeIrreflexiveObjectProperty(const std::shared_ptr<IrreflexiveObjectProperty>& axiom);
        void writeInverseObjectProperties(const std::shared_ptr<InverseObjectProperties>& axiom);
        void writeEquivalentObjectProperties(const std::shared_ptr<EquivalentObjectProperties>& axiom);
        void writeEquivalentDataProperties(const std::shared_ptr<EquivalentDataProperties>& axiom);
        void writeDisjointObjectProperties(const std::shared_ptr<DisjointObjectProperties>& axiom);
        void writeDisjointDataProperties(const std::shared_ptr<DisjointDataProperties>& axiom);
        void writeAnnotationAssertion(const std::shared_ptr<AnnotationAssertion>& axiom);
        void writeSubAnnotationPropertyOf(const std::shared_ptr<SubAnnotationPropertyOf>& axiom);
        void writeAnnotationPropertyDomain(const std::shared_ptr<AnnotationPropertyDomain>& axiom);
        void writeAnnotationPropertyRange(const std::shared_ptr<AnnotationPropertyRange>& axiom);
        
        // Entity and expression serialization
        std::string formatIRI(const IRI& iri);
        std::string formatLiteral(const Literal& literal);
        std::string formatIndividual(const Individual& individual);
        std::string formatClassExpression(const ClassExpressionPtr& expr);
        std::string formatDataRange(const DataRangePtr& range);
        
        // Helpers
        void registerStandardNamespaces();
        void registerOntologyNamespaces();
        void detectNamespaces();
        std::string getBlankNodeID();
        std::string escapeTurtleString(const std::string& str);
        bool needsQuotes(const std::string& str);
        void writeTriple(const std::string& subject, const std::string& predicate, const std::string& object);
        void writeAnnotations(const std::vector<Annotation>& annotations, const std::string& subject_iri);
    };
};

} // namespace owl2
} // namespace ista

#endif // ISTA_OWL2_TURTLE_SERIALIZER_HPP
