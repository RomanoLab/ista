#pragma once

#include <string>
#include <vector>
#include <memory>
#include <optional>
#include "../../lib/owl2/owl2.hpp"

// Forward declaration for GLFW
struct GLFWwindow;

namespace ista {
namespace gui {

/**
 * @brief Represents a node in the visual graph representation
 */
struct GraphNode {
    std::string id;           // IRI or unique identifier
    std::string label;        // Display label
    float x, y;              // Position in graph
    float vx, vy;            // Velocity for force-directed layout
    bool is_class;           // True if class, false if individual
    bool selected;           // Selection state
    
    GraphNode(const std::string& id, const std::string& label, bool is_class = false)
        : id(id), label(label), x(0), y(0), vx(0), vy(0), 
          is_class(is_class), selected(false) {}
};

/**
 * @brief Represents an edge in the visual graph representation
 */
struct GraphEdge {
    std::string from;        // Source node ID
    std::string to;          // Target node ID
    std::string label;       // Property label
    bool is_subclass;        // True if subClassOf relationship
    
    GraphEdge(const std::string& from, const std::string& to, const std::string& label, bool is_subclass = false)
        : from(from), to(to), label(label), is_subclass(is_subclass) {}
};

/**
 * @brief Main Knowledge Graph Editor Application
 * 
 * This class manages the GUI state, ontology, and graph visualization
 * for the knowledge graph population tool.
 */
class KnowledgeGraphEditor {
public:
    KnowledgeGraphEditor();
    ~KnowledgeGraphEditor();
    
    /**
     * @brief Initialize the GUI window and rendering context
     * @return true if initialization successful
     */
    bool initialize();
    
    /**
     * @brief Main application loop
     * @return Exit code (0 for success)
     */
    int run();
    
    /**
     * @brief Clean up resources
     */
    void shutdown();
    
    /**
     * @brief Load an OWL 2 ontology from file
     * @param filepath Path to the ontology file (RDF/XML)
     * @return true if loaded successfully
     */
    bool load_ontology(const std::string& filepath);
    
    /**
     * @brief Save the current ontology to file
     * @param filepath Path to save the ontology
     * @return true if saved successfully
     */
    bool save_ontology(const std::string& filepath);
    
private:
    // GUI rendering methods
    void render_menu_bar();
    void render_graph_view();
    void render_properties_panel();
    void render_data_source_panel();
    void render_class_selector();
    void render_preferences_window();
    
    // Graph construction from ontology
    void build_graph_from_ontology();
    void extract_class_hierarchy();
    void extract_individuals();
    void extract_object_properties();
    
    // Graph layout algorithms
    void apply_force_directed_layout();
    void apply_hierarchical_layout();
    
    // Interaction handling
    void handle_node_selection(const GraphNode* node);
    void handle_node_drag(GraphNode* node, float dx, float dy);
    
    // Label formatting
    std::string format_label(const std::string& abbreviated_iri) const;
    
    // Data source management
    void add_data_source(const std::string& filepath);
    void map_data_source_to_class(const std::string& source_id, const std::string& class_iri);
    
    // Window and rendering state
    GLFWwindow* window_;
    int window_width_;
    int window_height_;
    
    // Ontology data
    std::unique_ptr<ista::owl2::Ontology> ontology_;
    std::string current_filepath_;
    bool ontology_modified_;
    
    // Graph visualization data
    std::vector<GraphNode> nodes_;
    std::vector<GraphEdge> edges_;
    GraphNode* selected_node_;
    GraphNode* dragged_node_;
    const GraphEdge* selected_edge_;
    
    // View state
    float view_offset_x_;
    float view_offset_y_;
    float zoom_level_;
    bool show_class_hierarchy_;
    bool show_individuals_;
    
    // Data source panel state
    struct DataSource {
        std::string filepath;
        std::string format;  // "csv", "tsv", "excel", "sqlite", "postgres", "mysql"
        std::optional<std::string> mapped_class_iri;
        
        // Metadata (populated without loading full file)
        bool metadata_loaded = false;
        std::string error_message;
        
        // For CSV/TSV/Excel
        std::vector<std::string> column_names;
        size_t estimated_row_count = 0;
        std::vector<std::vector<std::string>> preview_rows;  // First few rows
        
        // For Excel specifically
        std::vector<std::string> sheet_names;
        std::string active_sheet;
        
        // For SQL databases
        std::string connection_string;
        std::vector<std::string> table_names;
        std::string active_table;
    };
    std::vector<DataSource> data_sources_;
    int selected_data_source_;
    
    // Data source metadata extraction
    void load_data_source_metadata(DataSource& ds);
    void load_csv_metadata(DataSource& ds);
    void load_excel_metadata(DataSource& ds);
    void load_sql_metadata(DataSource& ds);
    
    // UI state
    bool show_ontology_loader_;
    bool show_about_dialog_;
    bool show_preferences_;
    
    // Preferences
    bool pref_show_namespace_prefix_;
};

} // namespace gui
} // namespace ista
