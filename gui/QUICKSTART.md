# Quick Start Guide - ISTA Knowledge Graph Editor

Get up and running with the ISTA GUI in 5 minutes.

## Step 1: Download Dependencies

```bash
cd gui
./setup_dependencies.sh
```

This downloads Dear ImGui and GLFW into the `external/` directory.

## Step 2: Build

```bash
cd ..  # Back to project root
mkdir -p build && cd build
cmake ..
cmake --build .
```

## Step 3: Run

```bash
./gui/ista_gui
```

## Step 4: Load an Ontology

1. Click **File > Load Ontology** (or press Ctrl+O)
2. Enter the path to your `.owl` file (must be RDF/XML format)
3. Click **Load**

Your ontology will appear as an interactive graph!

## Basic Controls

| Action | Control |
|--------|---------|
| Pan view | Right-click + drag |
| Zoom | Mouse wheel |
| Select node | Left-click |
| Move node | Left-click + drag |
| Reset view | View > Reset View |

## Example Ontology

Try loading one of the example ontologies from the ISTA project (if available), or create a simple one:

```xml
<?xml version="1.0"?>
<rdf:RDF xmlns="http://example.org/medical#"
     xml:base="http://example.org/medical"
     xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
     xmlns:owl="http://www.w3.org/2002/07/owl#"
     xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#">
    
    <owl:Ontology rdf:about="http://example.org/medical"/>
    
    <!-- Classes -->
    <owl:Class rdf:about="http://example.org/medical#Patient"/>
    <owl:Class rdf:about="http://example.org/medical#Disease"/>
    
    <!-- Object Properties -->
    <owl:ObjectProperty rdf:about="http://example.org/medical#hasDiagnosis"/>
    
    <!-- Individuals -->
    <owl:NamedIndividual rdf:about="http://example.org/medical#patient001">
        <rdf:type rdf:resource="http://example.org/medical#Patient"/>
    </owl:NamedIndividual>
    
    <owl:NamedIndividual rdf:about="http://example.org/medical#diabetes">
        <rdf:type rdf:resource="http://example.org/medical#Disease"/>
    </owl:NamedIndividual>
</rdf:RDF>
```

Save this as `medical_example.owl` and load it in the GUI!

## Troubleshooting

**"Failed to initialize GLFW"**
- Make sure you ran `./setup_dependencies.sh`
- Check that `external/glfw/` and `external/imgui/` directories exist

**Build errors**
- Ensure you have a C++20 compiler (GCC 10+, Clang 10+, MSVC 2019+)
- Check CMake version: `cmake --version` (need 3.15+)

**Blank screen after loading**
- Your ontology might not have any classes or individuals
- Try toggling visibility in View menu

## Next Steps

- Explore the [full README](README.md) for detailed documentation
- Check the main [ISTA README](../README.md) for C++ library usage
- Look at example ontologies in the project

## Getting Help

- Open an issue on the ISTA GitHub repository
- Check the troubleshooting section in the full README
- Review the Dear ImGui documentation for UI customization
