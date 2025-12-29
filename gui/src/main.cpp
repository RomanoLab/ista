/**
 * @file main.cpp
 * @brief Main entry point for the ISTA Knowledge Graph Editor GUI
 */

#include "../include/kg_editor.hpp"
#include <iostream>

int main(int argc, char** argv) {
    std::cout << "Starting ISTA Knowledge Graph Editor..." << std::endl;

    ista::gui::KnowledgeGraphEditor editor;

    if (!editor.initialize()) {
        std::cerr << "Failed to initialize editor" << std::endl;
        return 1;
    }

    // If a file path was provided as argument, load it
    if (argc > 1) {
        std::string filepath(argv[1]);
        std::cout << "Loading ontology from command line: " << filepath << std::endl;
        editor.load_ontology(filepath);
    }

    int result = editor.run();
    
    editor.shutdown();
    
    std::cout << "ISTA Knowledge Graph Editor closed" << std::endl;
    return result;
}
