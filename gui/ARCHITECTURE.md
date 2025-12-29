# ISTA GUI Architecture

This document describes the architecture and design decisions for the ISTA Knowledge Graph Editor GUI.

## Design Goals

1. **Lightweight**: Minimal dependencies, fast startup, low resource usage
2. **Cross-Platform**: Single codebase for Windows, macOS, and Linux
3. **Native C++**: No Java, leverage existing C++20 ISTA library
4. **Open Source**: Use only open-source, permissively-licensed libraries
5. **Biomedical Focus**: Design choices suitable for biomedical knowledge graphs

## Technology Stack

### Core Technologies

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| GUI Framework | Dear ImGui v1.90.4 | Lightweight, immediate-mode, minimal dependencies |
| Windowing | GLFW v3.4 | Cross-platform, OpenGL integration, simple API |
| Graphics | OpenGL 3.3 Core | Widely supported, hardware-accelerated |
| Language | C++20 | Matches ISTA library, modern features |
| Build System | CMake 3.15+ | Cross-platform, integrates with existing build |
| OWL2 Library | libista | Native integration, high performance |

### Why Dear ImGui?

**Advantages:**
- **Bloat-free**: Single-header core, ~40KB compiled
- **No complex UI hierarchy**: Immediate-mode is simple and predictable
- **Perfect for tools**: Designed for content creation and visualization tools
- **Renderer agnostic**: Can swap OpenGL for DirectX, Vulkan, Metal
- **Active development**: Regular updates, large community
- **MIT licensed**: Commercial-friendly

**Alternatives Considered:**
- **Qt**: Too heavy (100+ MB), LGPL licensing complexity, Java-like feel
- **wxWidgets**: Large dependency tree, dated API
- **GTK/gtkmm**: LGPL licensing, Linux-centric
- **Nuklear**: Similar to ImGui but less mature
- **Custom**: Too much development time

### Why GLFW?

**Advantages:**
- **Minimal**: Just window/input handling, no GUI widgets
- **Cross-platform**: Same API on all platforms
- **OpenGL focused**: Designed for graphics applications
- **Small**: <1MB compiled
- **zlib licensed**: Very permissive

**Alternatives Considered:**
- **SDL2**: Heavier, game-focused
- **GLUT**: Outdated, limited features
- **Native APIs**: Platform-specific code complexity

## Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│                   ista_gui (main)                   │
└─────────────────────┬───────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────┐
│              KnowledgeGraphEditor                   │
│  ┌──────────────────────────────────────────────┐  │
│  │  Window & Rendering (GLFW + OpenGL)          │  │
│  └──────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────┐  │
│  │  UI Panels (Dear ImGui)                      │  │
│  │  • Menu Bar                                  │  │
│  │  • Graph Visualization                       │  │
│  │  • Properties Panel                          │  │
│  │  • Data Source Panel                         │  │
│  └──────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────┐  │
│  │  Graph Model (GraphNode, GraphEdge)          │  │
│  └──────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────┐  │
│  │  Ontology Interface (libista)                │  │
│  └──────────────────────────────────────────────┘  │
└─────────────────────┬───────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────┐
│                   libista (OWL2)                    │
│  • Ontology                                         │
│  • RDFXMLParser                                     │
│  • RDFXMLSerializer                                 │
│  • Classes, Properties, Individuals                 │
│  • Axioms                                           │
└─────────────────────────────────────────────────────┘
```

## Key Classes

### KnowledgeGraphEditor

The main application class that orchestrates all functionality.

**Responsibilities:**
- Initialize and manage GLFW window
- Set up Dear ImGui context
- Run main application loop
- Coordinate UI rendering
- Manage ontology loading/saving
- Handle user interactions
- Maintain application state

**Key Methods:**
```cpp
bool initialize()           // Setup window and ImGui
int run()                   // Main application loop
void shutdown()             // Cleanup resources
bool load_ontology()        // Load OWL2 file
bool save_ontology()        // Save OWL2 file
void build_graph_from_ontology()  // Convert ontology to visual graph
```

### GraphNode

Represents a visual node in the graph (class or individual).

**Data:**
- `id`: Unique identifier (IRI string)
- `label`: Display label (abbreviated IRI)
- `x, y`: Position in graph canvas
- `vx, vy`: Velocity for physics-based layout
- `is_class`: True for classes, false for individuals
- `selected`: Selection state

### GraphEdge

Represents a visual edge (relationship) between nodes.

**Data:**
- `from`: Source node ID
- `to`: Target node ID
- `label`: Property label
- `is_subclass`: True for subClassOf, false for other properties

## UI Panels

### Menu Bar
- File operations (load, save, exit)
- View options (toggle class hierarchy, individuals, reset view)
- Data source management
- Help and about

### Graph Visualization Panel
- Canvas for rendering the graph
- Grid background
- Interactive nodes and edges
- Pan (right-click drag)
- Zoom (mouse wheel)
- Node selection (left-click)
- Node dragging (left-click drag)

### Properties Panel
- Display selected node information
- Show IRI, type, and related axioms
- (Future) Edit properties and relationships

### Data Source Panel
- List added data sources (CSV, Excel)
- Show mapping status (which class each source populates)
- (Future) Configure column mappings

## Rendering Pipeline

### Frame Rendering (60 FPS)

1. **Poll Events** (GLFW)
   - Window resize, mouse input, keyboard input

2. **Start ImGui Frame**
   - Begin new frame
   - Set up docking space

3. **Render UI Components**
   - Menu bar
   - Graph view (custom drawing)
   - Properties panel
   - Data source panel
   - Modal dialogs (load, save, about)

4. **ImGui Rendering**
   - Generate draw commands
   - Submit to OpenGL

5. **OpenGL Rendering**
   - Clear framebuffer
   - Render ImGui draw data
   - Swap buffers

6. **Repeat**

### Graph Drawing

Uses ImGui's `ImDrawList` API for custom 2D rendering:

```cpp
// Get draw list
ImDrawList* draw_list = ImGui::GetWindowDrawList();

// Draw grid
draw_list->AddLine(p1, p2, color);

// Draw edges with arrows
draw_list->AddLine(from, to, edge_color, thickness);
draw_list->AddTriangleFilled(arrow_tip, arrow_left, arrow_right, color);

// Draw nodes
draw_list->AddCircleFilled(center, radius, node_color);
draw_list->AddCircle(center, radius, border_color);

// Draw labels
draw_list->AddText(position, color, text);
```

## Graph Layout Algorithms

### Hierarchical Layout (Implemented)

Simple top-down layout:
- Classes at top level
- Individuals below classes
- Evenly spaced horizontally

**Pros:** Fast, predictable, works well for taxonomies
**Cons:** Doesn't show complex relationships well

### Force-Directed Layout (Planned)

Physics simulation with:
- **Repulsion**: Nodes push each other apart
- **Attraction**: Connected nodes pull together
- **Damping**: Reduce oscillation

**Pros:** Natural clustering, shows relationships
**Cons:** Slower, non-deterministic

## Data Flow

### Loading an Ontology

```
User selects file
    ↓
RDFXMLParser::parseFromFile()
    ↓
Create Ontology object
    ↓
build_graph_from_ontology()
    ↓
extract_class_hierarchy()
    ↓
extract_individuals()
    ↓
apply_hierarchical_layout()
    ↓
Render graph
```

### Saving an Ontology

```
User clicks save
    ↓
RDFXMLSerializer::serializeToFile()
    ↓
Write to disk
    ↓
Update filepath and modified flag
```

## State Management

### Application State

Stored in `KnowledgeGraphEditor` class:
- `ontology_`: Current loaded ontology (unique_ptr)
- `current_filepath_`: Last saved/loaded file path
- `ontology_modified_`: Dirty flag for unsaved changes

### View State

- `view_offset_x/y_`: Pan position
- `zoom_level_`: Zoom factor (0.1 to 5.0)
- `show_class_hierarchy_`: Toggle class visibility
- `show_individuals_`: Toggle individual visibility

### Selection State

- `selected_node_`: Currently selected node
- `dragged_node_`: Node being dragged

## Future Enhancements

### Data Population Workflow (Planned)

```
User adds CSV file
    ↓
File appears in data source panel
    ↓
User selects class to populate
    ↓
Column mapping dialog opens
    ↓
User maps CSV columns to:
    - Individual IRI generation
    - Data properties
    - Object properties
    ↓
User clicks "Populate"
    ↓
CSV parsed row by row
    ↓
New individuals created
    ↓
Graph updates in real-time
    ↓
User saves ontology
```

### Advanced Features (Planned)

- **SPARQL Query Panel**: Query loaded ontology
- **Reasoner Integration**: Show inferred axioms
- **Undo/Redo**: Command pattern for reversible operations
- **Multi-file Projects**: Load multiple ontologies with imports
- **Export Visualizations**: Save graph as PNG/SVG
- **Custom Stylesheets**: Configure colors, fonts, layouts

## Performance Considerations

### Current Optimizations

- **Immediate Mode UI**: No persistent widget tree overhead
- **Selective Rendering**: Only visible nodes drawn
- **Static Layout**: Layout computed once when loading

### Scalability Limits

| Metric | Current | Target |
|--------|---------|--------|
| Classes | 1000+ | 10,000 |
| Individuals | 1000+ | 100,000 |
| Edges | 5000+ | 500,000 |
| FPS | 60 | 60 |

### Future Optimizations

- **Frustum Culling**: Only draw visible nodes
- **Level of Detail**: Simplify distant nodes
- **Spatial Indexing**: Quadtree for fast hit detection
- **Incremental Layout**: Update only moved nodes
- **GPU Rendering**: Use shaders for node drawing

## Build System

### CMake Structure

```
CMakeLists.txt (root)
    ├── lib/CMakeLists.txt          # libista
    ├── src/CMakeLists.txt          # C++ examples
    ├── lib/python/CMakeLists.txt   # Python bindings
    └── gui/CMakeLists.txt          # GUI application
```

### Dependencies Resolution

1. Check for system-installed GLFW
2. Fall back to bundled GLFW in `external/glfw/`
3. Check for Dear ImGui in `external/imgui/`
4. If missing, warn and skip GUI build

### Build Targets

- `libista`: Core OWL2 library
- `ista`: C++ example program
- `_libista_owl2`: Python module
- `ista_gui`: GUI application (if BUILD_GUI=ON)

## Cross-Platform Considerations

### Platform Differences

| Feature | Windows | macOS | Linux |
|---------|---------|-------|-------|
| OpenGL | Yes | Deprecated but works | Yes |
| GLFW | Works | Works | Requires X11 libs |
| File Paths | Backslash | Slash | Slash |
| Line Endings | CRLF | LF | LF |

### Platform-Specific Code

```cpp
#ifdef __APPLE__
    glfwWindowHint(GLFW_OPENGL_FORWARD_COMPAT, GL_TRUE);
#endif

#ifdef _WIN32
    // Windows-specific code
#elif __APPLE__
    // macOS-specific code
#elif __linux__
    // Linux-specific code
#endif
```

## Testing Strategy

### Manual Testing

- Load various ontology sizes
- Test all UI interactions
- Verify cross-platform builds
- Check memory usage

### Automated Testing (Future)

- Unit tests for graph algorithms
- Integration tests for load/save
- UI automation with ImGui Test Engine
- Performance benchmarks

## Security Considerations

- **File Parsing**: RDFXMLParser validates input
- **User Input**: File paths sanitized
- **Memory Safety**: Modern C++ (smart pointers, no raw new/delete)
- **No Network**: Offline application, no external connections

## License

The GUI application follows the same license as the ISTA project, using:
- **Dear ImGui**: MIT License
- **GLFW**: zlib License
- Both are permissive and commercial-friendly

## Conclusion

The ISTA GUI provides a solid foundation for visual knowledge graph manipulation. The architecture is simple, maintainable, and extensible. Future enhancements will focus on data population features while maintaining the lightweight, cross-platform design.
