#ifndef ISTA_OWL2_RDFXML_PARSER_HPP
#define ISTA_OWL2_RDFXML_PARSER_HPP

#include "../core/ontology.hpp"
#include <string>
#include <stdexcept>
#include <unordered_map>
#include <memory>

namespace ista {
namespace owl2 {

/**
 * @brief Exception thrown when RDF/XML parsing fails
 */
class RDFXMLParseException : public std::runtime_error {
public:
    explicit RDFXMLParseException(const std::string& message)
        : std::runtime_error("RDF/XML Parse Error: " + message) {}
};

/**
 * @brief Parser for OWL2 ontologies in RDF/XML format
 * 
 * This parser handles a subset of OWL2 constructs that aligns with the 
 * RDFXMLSerializer capabilities. It parses:
 * - Ontology metadata (IRI, version IRI, imports)
 * - Namespace prefixes
 * - Entity declarations (Class, ObjectProperty, DataProperty, AnnotationProperty, NamedIndividual, Datatype)
 * - Simple axioms:
 *   - SubClassOf (rdfs:subClassOf)
 *   - EquivalentClasses (owl:equivalentClass)
 *   - DisjointClasses (owl:AllDisjointClasses)
 *   - ClassAssertion (rdf:type)
 *   - ObjectPropertyDomain (rdfs:domain)
 *   - ObjectPropertyRange (rdfs:range)
 *   - DataPropertyDomain (rdfs:domain)
 *   - DataPropertyRange (rdfs:range)
 *   - FunctionalObjectProperty (rdf:type owl:FunctionalProperty)
 *   - FunctionalDataProperty (rdf:type owl:FunctionalProperty)
 *   - InverseFunctionalObjectProperty (rdf:type owl:InverseFunctionalProperty)
 *   - TransitiveObjectProperty (rdf:type owl:TransitiveProperty)
 *   - SymmetricObjectProperty (rdf:type owl:SymmetricProperty)
 *   - AsymmetricObjectProperty (rdf:type owl:AsymmetricProperty)
 *   - ReflexiveObjectProperty (rdf:type owl:ReflexiveProperty)
 *   - IrreflexiveObjectProperty (rdf:type owl:IrreflexiveProperty)
 *   - SubObjectPropertyOf (rdfs:subPropertyOf)
 *   - SubDataPropertyOf (rdfs:subPropertyOf)
 *   - ObjectPropertyAssertion (property assertions on individuals)
 *   - DataPropertyAssertion (property assertions on individuals)
 *   - AnnotationAssertion (annotation property assertions)
 * - Class expressions in restrictions:
 *   - ObjectSomeValuesFrom (owl:someValuesFrom)
 *   - ObjectAllValuesFrom (owl:allValuesFrom)
 *   - ObjectIntersectionOf (owl:intersectionOf)
 *   - ObjectUnionOf (owl:unionOf)
 * 
 * @note This parser uses pugixml for XML parsing.
 */
class RDFXMLParser {
public:
    /**
     * @brief Parse an OWL2 ontology from RDF/XML content
     * @param rdfxml_content RDF/XML string content
     * @return Parsed ontology
     * @throws RDFXMLParseException if parsing fails
     */
    static Ontology parse(const std::string& rdfxml_content);
    
    /**
     * @brief Parse an OWL2 ontology from an RDF/XML file
     * @param filename Path to RDF/XML file
     * @return Parsed ontology
     * @throws RDFXMLParseException if file cannot be read or parsing fails
     */
    static Ontology parseFromFile(const std::string& filename);

private:
    class Parser;
};

} // namespace owl2
} // namespace ista

#endif // ISTA_OWL2_RDFXML_PARSER_HPP
