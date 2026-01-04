#include "lib/owl2/owl2.hpp"
#include "lib/owl2/parser/rdfxml_parser.hpp"
#include <iostream>

int main(int argc, char** argv) {
    if (argc < 2) {
        std::cerr << "Usage: " << argv[0] << " <ontology.rdf>" << std::endl;
        return 1;
    }

    try {
        std::cout << "Loading ontology: " << argv[1] << std::endl;
        ista::owl2::RDFXMLParser parser;
        auto ontology = parser.parse(argv[1]);
        
        std::cout << "\n=== Ontology Statistics ===" << std::endl;
        std::cout << "Classes: " << ontology->getClasses().size() << std::endl;
        std::cout << "Individuals: " << ontology->getIndividuals().size() << std::endl;
        std::cout << "Object Properties: " << ontology->getObjectPropertyCount() << std::endl;
        std::cout << "Data Properties: " << ontology->getDataPropertyCount() << std::endl;
        
        std::cout << "\n=== Object Property Axioms ===" << std::endl;
        auto obj_prop_axioms = ontology->getObjectPropertyAxioms();
        std::cout << "Total: " << obj_prop_axioms.size() << std::endl;
        for (const auto& axiom : obj_prop_axioms) {
            std::cout << "  Type: " << axiom->getAxiomType() << std::endl;
        }
        
        std::cout << "\n=== Assertion Axioms ===" << std::endl;
        auto assertion_axioms = ontology->getAssertionAxioms();
        std::cout << "Total: " << assertion_axioms.size() << std::endl;
        int obj_prop_count = 0;
        for (const auto& axiom : assertion_axioms) {
            if (axiom->getAxiomType() == "ObjectPropertyAssertion") {
                obj_prop_count++;
            }
        }
        std::cout << "ObjectPropertyAssertion count: " << obj_prop_count << std::endl;
        
        std::cout << "\n=== Classes ===" << std::endl;
        for (const auto& cls : ontology->getClasses()) {
            std::cout << "  " << cls.getIRI().toString() << std::endl;
        }
        
        std::cout << "\n=== Individuals ===" << std::endl;
        for (const auto& ind : ontology->getIndividuals()) {
            std::cout << "  " << ind.getIRI().toString() << std::endl;
        }
        
        return 0;
    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << std::endl;
        return 1;
    }
}
