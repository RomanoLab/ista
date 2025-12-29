# ISTA Knowledge Graph Editor GUI

A lightweight, cross-platform graphical interface for populating OWL 2 knowledge graphs using the ISTA library.

## Features

- **OWL 2 Ontology Loading**: Load and visualize OWL 2 ontologies in RDF/XML format
- **Interactive Graph Visualization**: View classes, individuals, and their relationships as an interactive directed graph
- **Knowledge Graph Schema Rendering**: Visualize class hierarchies and ontological structure
- **Data Source Integration**: (Planned) Select and map data sources (CSV, Excel) to ontology classes for population
- **Cross-Platform**: Runs on Windows, macOS, and Linux
- **Lightweight**: Minimal dependencies using Dear ImGui and GLFW

## Technology Stack

- **C++20**: Modern C++ for high performance
- **Dear ImGui**: Lightweight immediate-mode GUI framework
- **GLFW**: Cross-platform window and input handling
- **OpenGL 3.3**: Hardware-accelerated graphics rendering
- **ISTA OWL2**: Native C++ OWL 2 ontology manipulation library

## Prerequisites

### Required
- CMake 3.15 or higher
- C++20 compatible compiler (GCC 10+, Clang 10+, MSVC 2019+)
- OpenGL 3.3 or higher support

### Dependencies (automatically downloaded)
- Dear ImGui (v1.90.4)
- GLFW (v3.4)

## Installation

### 1. Download Dependencies

Run the setup script to download Dear ImGui and GLFW:

```bash
cd gui
./setup_dependencies.sh
```

This will clone Dear ImGui and GLFW into the `external/` directory.

### 2. Build the Application

From the project root:

```bash
mkdir -p build && cd build
cmake .. -DBUILD_GUI=ON
cmake --build .
```

The executable will be located at: `build/gui/ista_gui`

### Build Options

- `BUILD_GUI=ON/OFF`: Enable/disable GUI build (default: ON)
- `BUILD_PYTHON_BINDINGS=ON/OFF`: Enable/disable Python bindings (default: ON)

To disable GUI build:
```bash
cmake .. -DBUILD_GUI=OFF
```

## Usage

### Launch the GUI

```bash
./build/gui/ista_gui
```

Or load an ontology file directly:

```bash
./build/gui/ista_gui path/to/ontology.owl
```

### Basic Workflow

1. **Load Ontology**
   - Click `File > Load Ontology` or press `Ctrl+O`
   - Enter the path to your RDF/XML ontology file
   - The graph visualization will display classes and individuals

2. **Navigate the Graph**
   - **Pan**: Right-click and drag
   - **Zoom**: Mouse wheel
   - **Select Node**: Left-click on a node
   - **Drag Node**: Left-click and drag

3. **View Options**
   - `View > Show Class Hierarchy`: Toggle class nodes visibility
   - `View > Show Individuals`: Toggle individual nodes visibility
   - `View > Reset View`: Reset pan and zoom

4. **Save Changes**
   - Click `File > Save Ontology` or press `Ctrl+S`
   - Use `File > Save As...` to save to a new location

### Planned Features

- **Data Source Panel**: Add CSV/Excel files as data sources
- **Class Mapping**: Map data source columns to ontology classes and properties
- **Batch Population**: Automatically populate individuals from data sources
- **Filtering**: Filter graph view by class or property
- **Search**: Find specific classes or individuals
- **Export**: Export graph visualizations as images

## Graph Visualization

### Node Types

- **Blue Circles (Large)**: OWL 2 Classes
- **Green Circles (Small)**: Named Individuals
- **Gold**: Selected node

### Edge Types

- **Blue Arrows**: Subclass relationships (rdfs:subClassOf)
- **Gray Arrows**: Object property assertions

### Interaction

- **Selection**: Click on a node to view its properties in the Properties panel
- **Dragging**: Rearrange nodes by dragging them
- **Panning**: Navigate large graphs by right-click dragging
- **Zooming**: Use mouse wheel to zoom in/out

## Architecture

### Directory Structure

```
gui/
├── include/
│   └── kg_editor.hpp          # Main editor class header
├── src/
│   ├── main.cpp               # Application entry point
│   └── kg_editor.cpp          # Editor implementation
├── CMakeLists.txt             # Build configuration
├── setup_dependencies.sh      # Dependency download script
└── README.md                  # This file
```

### Key Classes

**KnowledgeGraphEditor**: Main application class
- Manages GUI window and rendering
- Handles ontology loading/saving
- Controls graph visualization
- Manages user interactions

**GraphNode**: Represents a visual node (class or individual)
- Position and velocity for layout algorithms
- Selection and interaction state
- Display label and IRI

**GraphEdge**: Represents a visual edge (relationship)
- Source and target nodes
- Property label
- Edge type (subclass, property, etc.)

## Platform-Specific Notes

### macOS
- Requires macOS 10.13 or later for OpenGL 3.3 support
- The application uses Cocoa, IOKit, and CoreVideo frameworks
- If you encounter OpenGL warnings, they can be safely ignored (OpenGL deprecated but still functional)

### Linux
- Requires X11 development libraries: `sudo apt-get install libx11-dev libxrandr-dev libxinerama-dev libxcursor-dev libxi-dev`
- May require `libgl1-mesa-dev` for OpenGL headers

### Windows
- Requires Visual Studio 2019 or later
- CMake will generate Visual Studio solution files
- OpenGL libraries are included with graphics drivers

## Troubleshooting

### "Failed to initialize GLFW"
- Ensure you have OpenGL 3.3 or higher support
- Update graphics drivers
- Check that GLFW was downloaded correctly

### "Dear ImGui not found"
- Run `./setup_dependencies.sh` to download dependencies
- Check that `external/imgui/` directory exists and contains `imgui.cpp`

### Build Errors
- Ensure C++20 compiler support
- Check CMake version (3.15+)
- Verify all dependencies are present in `external/` directory

### Performance Issues
- Large ontologies (1000+ classes) may experience slowdown
- Disable class hierarchy view if not needed
- Use hierarchical layout instead of force-directed for better performance

## Development

### Adding Features

To extend the GUI:

1. Add new methods to `KnowledgeGraphEditor` class in `include/kg_editor.hpp`
2. Implement in `src/kg_editor.cpp`
3. Add UI elements in the appropriate `render_*` method
4. Follow ImGui patterns for immediate-mode UI

### Layout Algorithms

Current layouts:
- **Hierarchical**: Classes at top, individuals below (implemented)
- **Force-Directed**: Physics-based node positioning (planned)

To implement new layouts, add methods similar to `apply_hierarchical_layout()`.

## License

This GUI application is part of the ISTA project and follows the same license as the main ISTA library.

## Contributing

Contributions are welcome! Please ensure:
- Code follows existing style conventions
- C++20 features are used appropriately
- Cross-platform compatibility is maintained
- Changes are documented

## References

- [Dear ImGui](https://github.com/ocornut/imgui) - Bloat-free GUI library
- [GLFW](https://www.glfw.org/) - Multi-platform library for OpenGL
- [ISTA Library](../README.md) - OWL 2 ontology manipulation
- [OWL 2 Specification](https://www.w3.org/TR/owl2-overview/)

## Future Enhancements

### Short-term
- File dialog integration (native file picker)
- Data source management (CSV import)
- Column-to-property mapping interface
- Batch individual creation from CSV

### Medium-term
- Force-directed graph layout
- Graph filtering and search
- Undo/redo support
- Export visualizations as PNG/SVG

### Long-term
- SPARQL query interface
- Reasoner integration (visualize inferred axioms)
- Collaborative editing
- Plugin system for custom data sources
