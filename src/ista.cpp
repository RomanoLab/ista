#include <iostream>

#include "owl2/owl2.hpp"

int main(int argc, char* argv[])
{
    IRI my_test_iri = IRI("https://comptox.ai/comptox.rdf");
    
    std::cout << "Hello, Ista!\n";
    std::cout << my_test_iri.fullIRI << "\n";
    return 0;
}