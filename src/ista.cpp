#include <iostream>

#include "owl2/owl2.hpp"

int main(int argc, char* argv[])
{
    ista::owl2::IRI my_test_iri = ista::owl2::IRI("https://comptox.ai/comptox.rdf");
    
    std::cout << "Hello, Ista!\n";
    return 0;
}