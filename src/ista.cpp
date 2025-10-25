#include <iostream>
#include "owl2/owl2.hpp"

using namespace ista::owl2;

int main(int argc, char* argv[]) {
    std::cout << "=== ISTA OWL2 Library Example ===" << std::endl << std::endl;
    
    // Create an ontology
    IRI ontology_iri("http://example.org/university");
    IRI version_iri("http://example.org/university/1.0");
    Ontology onto(ontology_iri, version_iri);
    
    // Register a prefix for abbreviated IRIs
    onto.registerPrefix("uni", "http://example.org/university#");
    onto.registerPrefix("ex", "http://example.org/university#");
    
    std::cout << "Created ontology: " << ontology_iri.toString() << std::endl;
    std::cout << "Version: " << version_iri.toString() << std::endl << std::endl;
    
    // Create some classes
    Class person(IRI("ex", "Person", "http://example.org/university#"));
    Class student(IRI("ex", "Student", "http://example.org/university#"));
    Class professor(IRI("ex", "Professor", "http://example.org/university#"));
    
    // Declare the classes
    onto.addAxiom(std::make_shared<Declaration>(Declaration::EntityType::CLASS, person.getIRI()));
    onto.addAxiom(std::make_shared<Declaration>(Declaration::EntityType::CLASS, student.getIRI()));
    onto.addAxiom(std::make_shared<Declaration>(Declaration::EntityType::CLASS, professor.getIRI()));
    
    std::cout << "Declared " << onto.getClassCount() << " classes" << std::endl;
    
    // Add subclass axioms
    auto student_subclass = std::make_shared<NamedClass>(student);
    auto person_superclass = std::make_shared<NamedClass>(person);
    onto.addAxiom(std::make_shared<SubClassOf>(student_subclass, person_superclass));
    
    auto professor_subclass = std::make_shared<NamedClass>(professor);
    onto.addAxiom(std::make_shared<SubClassOf>(professor_subclass, person_superclass));
    
    std::cout << "Added subclass relationships" << std::endl;
    
    // Create an object property
    ObjectProperty teachesProperty(IRI("ex", "teaches", "http://example.org/university#"));
    onto.addAxiom(std::make_shared<Declaration>(Declaration::EntityType::OBJECT_PROPERTY, teachesProperty.getIRI()));
    
    // Add domain and range restrictions
    onto.addAxiom(std::make_shared<ObjectPropertyDomain>(teachesProperty, professor_subclass));
    onto.addAxiom(std::make_shared<ObjectPropertyRange>(teachesProperty, student_subclass));
    
    std::cout << "Created object property with domain and range" << std::endl << std::endl;
    
    // Create a data property
    DataProperty ageProperty(IRI("ex", "age", "http://example.org/university#"));
    onto.addAxiom(std::make_shared<Declaration>(Declaration::EntityType::DATA_PROPERTY, ageProperty.getIRI()));
    
    // Make it functional
    onto.addAxiom(std::make_shared<FunctionalDataProperty>(ageProperty));
    
    std::cout << "Created functional data property" << std::endl;
    
    // Create individuals
    NamedIndividual john(IRI("ex", "John", "http://example.org/university#"));
    NamedIndividual mary(IRI("ex", "Mary", "http://example.org/university#"));
    
    onto.addAxiom(std::make_shared<Declaration>(Declaration::EntityType::NAMED_INDIVIDUAL, john.getIRI()));
    onto.addAxiom(std::make_shared<Declaration>(Declaration::EntityType::NAMED_INDIVIDUAL, mary.getIRI()));
    
    // Assert John is a Professor
    onto.addAxiom(std::make_shared<ClassAssertion>(professor_subclass, john));
    
    // Assert Mary is a Student
    onto.addAxiom(std::make_shared<ClassAssertion>(student_subclass, mary));
    
    // Assert John teaches Mary
    onto.addAxiom(std::make_shared<ObjectPropertyAssertion>(teachesProperty, john, mary));
    
    // Assert ages
    Literal johnAge("45", xsd::INTEGER);
    Literal maryAge("22", xsd::INTEGER);
    onto.addAxiom(std::make_shared<DataPropertyAssertion>(ageProperty, john, johnAge));
    onto.addAxiom(std::make_shared<DataPropertyAssertion>(ageProperty, mary, maryAge));
    
    std::cout << "Created individuals with assertions" << std::endl << std::endl;
    
    // Print statistics
    std::cout << "=== Ontology Statistics ===" << std::endl;
    std::cout << onto.getStatistics() << std::endl;
    
    // Serialize to functional syntax
    std::cout << std::endl << "=== Functional Syntax Output ===" << std::endl;
    std::string functional_syntax = onto.toFunctionalSyntax();
    std::cout << functional_syntax << std::endl;
    
    // Try to save to file
    FunctionalSyntaxSerializer serializer;
    if (serializer.serializeToFile(onto, "university.ofn")) {
        std::cout << "Ontology saved to university.ofn" << std::endl;
    } else {
        std::cout << "Failed to save ontology to file" << std::endl;
    }
    
    return 0;
}
