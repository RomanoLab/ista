# ISTA GUI Changelog

## Recent Updates

### December 26, 2024

#### Fixed: Node Dragging Issue
**Problem:** When dragging nodes in the graph visualization, the entire window would move instead of just the node.

**Solution:** Added an invisible button overlay (`ImGui::InvisibleButton`) to capture mouse input within the canvas area. This prevents ImGui from treating mouse drags as window movement.

**Changes:**
- Added canvas interaction detection with `is_canvas_hovered` and `is_canvas_active` flags
- Mouse interactions (clicking, dragging, zooming) now only work when hovering over the canvas
- Prevents accidental window movement when interacting with the graph

**Files Modified:**
- `gui/src/kg_editor.cpp` - Added invisible button and hover checks

#### Enhanced: Object Property Edge Rendering
**Problem:** Object properties between individuals weren't clearly visible or labeled.

**Solution:** Improved edge rendering with:
- **Different colors** - Blue for subClassOf relationships, Green for object properties
- **Edge labels** - Property names displayed at the midpoint of each edge
- **Label backgrounds** - Semi-transparent black rectangles behind labels for readability
- **Label borders** - Colored borders matching the edge color
- **Visibility filtering** - Edges are hidden when their connected nodes are hidden

**Visual Improvements:**
- Object properties now render as **green arrows** between individuals
- SubClassOf relationships render as **blue arrows** between classes
- Property names (e.g., "hasDiagnosis", "inv(partOf)") appear on edges
- Labels have dark backgrounds to stay readable against any graph background
- Inverse properties are marked with "inv(...)" prefix

**Files Modified:**
- `gui/src/kg_editor.cpp` - Enhanced edge rendering with labels and colors

#### Added: Native File Dialog Support
**Feature:** System-native file picker dialogs for browsing files instead of typing paths.

**Implementation:**
- Integrated nativefiledialog-extended (NFD) library
- Added file dialogs for:
  - Load Ontology (.owl, .rdf files)
  - Save As (.owl, .rdf files with default name)
  - Add Data Source (.csv, .xlsx files)
- Platform-specific native dialogs (macOS Cocoa, Windows IFileDialog, Linux GTK3)

**Files Added/Modified:**
- `CMakeLists.txt` - Added Objective-C support for macOS
- `gui/CMakeLists.txt` - Added NFD integration and frameworks
- `gui/src/kg_editor.cpp` - Replaced text input with native dialogs
- `gui/include/kg_editor.hpp` - Removed filepath buffer
- `build_gui.sh` - Added NFD download
- `gui/setup_dependencies.sh` - Added NFD download

## Feature Summary

### Current Features
- ✅ Load/Save OWL 2 ontologies (RDF/XML format)
- ✅ Native file picker dialogs (macOS/Windows/Linux)
- ✅ Interactive graph visualization with pan and zoom
- ✅ Node selection and dragging (without window movement)
- ✅ **Color-coded edges** (blue for class hierarchy, green for object properties)
- ✅ **Edge labels** showing property names
- ✅ View toggles for classes and individuals
- ✅ Properties panel for selected nodes
- ✅ Data source management panel

### Planned Features
- 🔲 Force-directed graph layout
- 🔲 CSV/Excel data source mapping to ontology classes
- 🔲 Batch population of individuals from data sources
- 🔲 Search and filter functionality
- 🔲 Undo/redo support
- 🔲 Export graph visualizations as images
- 🔲 SPARQL query interface
- 🔲 Reasoner integration

## Build Instructions

```bash
# Download all dependencies (including NFD)
./build_gui.sh

# Or manually
cd gui && ./setup_dependencies.sh && cd ..
mkdir build && cd build
cmake .. -DBUILD_PYTHON_BINDINGS=OFF -DBUILD_GUI=ON
cmake --build .
```

## Usage Tips

### Graph Navigation
- **Pan view**: Right-click and drag on the canvas
- **Zoom**: Mouse wheel while hovering over the canvas
- **Select node**: Left-click on a node
- **Drag node**: Left-click and drag a node
- **Reset view**: View > Reset View

### Working with Edges
- **Blue arrows** indicate class hierarchy (subClassOf)
- **Green arrows** indicate object properties between individuals
- **Labels** show the property name (hover to see clearly)
- **Inverse properties** are prefixed with "inv(...)"

### Loading Ontologies
1. Click File > Load Ontology (or Ctrl+O)
2. Browse for your .owl or .rdf file
3. Click Open in the native file dialog
4. Graph will update automatically

### Understanding the Colors
- **Steel Blue circles** (large) = OWL Classes
- **Medium Sea Green circles** (small) = Individuals
- **Gold circles** = Selected node
- **Blue arrows** = SubClassOf relationships
- **Green arrows** = Object Property assertions

## Known Limitations

1. **Class expressions**: Complex class expressions (intersections, unions, restrictions) are not yet fully visualized
2. **Large ontologies**: Performance may degrade with 1000+ nodes (consider filtering)
3. **Layout**: Currently uses simple hierarchical layout (force-directed coming soon)
4. **Editing**: Read-only visualization (no axiom editing yet)

## Troubleshooting

### Nodes don't drag properly
- Make sure you're clicking and dragging directly on the node (not near it)
- The cursor should be hovering over the canvas area

### Edges not visible
- Check View menu - ensure both "Show Class Hierarchy" and "Show Individuals" are enabled
- Zoom out to see the full graph
- Make sure your ontology has object property assertions

### Window moves when I try to drag nodes
- This should be fixed in the latest version
- If still happening, try clicking closer to the center of the node
- Rebuild with `./build_gui.sh` to get the latest fixes

### Edge labels are hard to read
- Zoom in closer to the edge
- Labels have dark backgrounds for contrast
- Consider renaming properties to shorter names if needed

## Contributing

To add new features or fix bugs:
1. Read the architecture documentation in `gui/ARCHITECTURE.md`
2. Follow the existing code style (C++20, ImGui patterns)
3. Test on your platform before committing
4. Update this changelog with your changes

## Version History

- **v0.1.0** (Dec 26, 2024)
  - Initial GUI release
  - Basic graph visualization
  - Native file dialogs
  - Fixed node dragging
  - Enhanced edge rendering with labels
  - Cross-platform support (macOS, Windows, Linux)
