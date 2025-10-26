#ifndef ISTA_OWL2_RDFXML_SERIALIZER_HPP
#define ISTA_OWL2_RDFXML_SERIALIZER_HPP

#include "../core/ontology.hpp"
#include <string>
#include <sstream>
#include <unordered_map>

namespace ista {
namespace owl2 {

/**
 * @brief Serializer for OWL2 RDF/XML format
 * 
 * Writes ontologies to RDF/XML format compatible with tools like Protégé and owlready2.
 */
class RDFXMLSerializer {
public:
    /**
     * @brief Serialize ontology to RDF/XML string
     * @param ontology The ontology to serialize
     * @return String containing RDF/XML
     */
    static std::string serialize(const Ontology& ontology);
    
    /**
     * @brief Serialize ontology to file
     * @param ontology The ontology to serialize
     * @param filename Output file path
     * @return true if successful, false otherwise
     */
    static bool serializeToFile(const Ontology& ontology, const std::string& filename);

private:
    // Helper class for building RDF/XML
    class Builder {
    public:
        explicit Builder(const Ontology& ontology);
        std::string build();
        
    private:
        const Ontology& ontology_;
        std::ostringstream xml_;
        std::unordered_map<std::string, std::string> namespaces_;
        int blank_node_counter_;
        
        // XML generation helpers
        void writeXMLDeclaration();
        void writeRDFHeader();
        void writeOntologyHeader();
        void writeAxioms();
        void writeRDFFooter();
        
        // Axiom serialization
        void writeDeclaration(const std::shared_ptr<Declaration>& axiom);
        void writeSubClassOf(const std::shared_ptr<SubClassOf>& axiom);
        void writeEquivalentClasses(const std::shared_ptr<EquivalentClasses>& axiom);
        void writeDisjointClasses(const std::shared_ptr<DisjointClasses>& axiom);
        void writeClassAssertion(const std::shared_ptr<ClassAssertion>& axiom);
        void writeObjectPropertyAssertion(const std::shared_ptr<ObjectPropertyAssertion>& axiom);
        void writeDataPropertyAssertion(const std::shared_ptr<DataPropertyAssertion>& axiom);
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
        void writeAnnotationAssertion(const std::shared_ptr<AnnotationAssertion>& axiom);
        
        // Class expression serialization
        void writeClassExpression(const ClassExpressionPtr& expr, const std::string& indent);
        std::string getClassExpressionNodeID(const ClassExpressionPtr& expr);
        
        // Helper functions
        std::string escapeXML(const std::string& str) const;
        std::string getQName(const IRI& iri) const;
        std::string getNamespacePrefix(const std::string& ns) const;
        void registerStandardNamespaces();
        void registerOntologyNamespaces();
        std::string formatLiteral(const Literal& literal) const;
        std::string formatIndividual(const Individual& individual) const;
        std::string getBlankNodeID();
        void writeAnnotations(const std::vector<Annotation>& annotations, const std::string& indent);
    };
};

} // namespace owl2
} // namespace ista

#endif // ISTA_OWL2_RDFXML_SERIALIZER_HPP
