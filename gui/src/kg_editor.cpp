#include "../include/kg_editor.hpp"
#include "../../lib/owl2/parser/rdfxml_parser.hpp"
#include "../../lib/owl2/serializer/rdfxml_serializer.hpp"

// Silence OpenGL deprecation warnings on macOS
#define GL_SILENCE_DEPRECATION

// GLFW must be included before ImGui GLFW backend
#include <GLFW/glfw3.h>

#include "imgui.h"
#include "imgui_impl_glfw.h"
#include "imgui_impl_opengl3.h"
#include "nfd.h"

#include <iostream>
#include <fstream>
#include <algorithm>
#include <cmath>
#include <ctime>
#include <unordered_map>
#include <variant>

namespace ista {
namespace gui {

KnowledgeGraphEditor::KnowledgeGraphEditor()
    : window_(nullptr)
    , window_width_(1920)
    , window_height_(1080)
    , ontology_(nullptr)
    , ontology_modified_(false)
    , selected_node_(nullptr)
    , dragged_node_(nullptr)
    , selected_edge_(nullptr)
    , view_offset_x_(0.0f)
    , view_offset_y_(0.0f)
    , zoom_level_(1.0f)
    , show_class_hierarchy_(true)
    , show_individuals_(true)
    , selected_data_source_(-1)
    , show_ontology_loader_(false)
    , show_about_dialog_(false)
    , show_preferences_(false)
    , show_add_data_source_menu_(false)
    , show_database_config_dialog_(false)
    , db_type_selection_("mysql")
    , pref_show_namespace_prefix_(false)
{
}

KnowledgeGraphEditor::~KnowledgeGraphEditor() {
    shutdown();
}

bool KnowledgeGraphEditor::initialize() {
    // Initialize NFD (Native File Dialog)
    NFD_Init();

    // Initialize GLFW
    if (!glfwInit()) {
        std::cerr << "Failed to initialize GLFW" << std::endl;
        NFD_Quit();
        return false;
    }

    // Set OpenGL version (3.3 Core)
    glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 3);
    glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 3);
    glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE);

#ifdef __APPLE__
    glfwWindowHint(GLFW_OPENGL_FORWARD_COMPAT, GL_TRUE);
#endif

    // Create window
    window_ = glfwCreateWindow(window_width_, window_height_,
                               "ISTA Knowledge Graph Editor", nullptr, nullptr);
    if (!window_) {
        std::cerr << "Failed to create GLFW window" << std::endl;
        glfwTerminate();
        return false;
    }

    glfwMakeContextCurrent(window_);
    glfwSwapInterval(1); // Enable vsync

    // Setup Dear ImGui context
    IMGUI_CHECKVERSION();
    ImGui::CreateContext();
    ImGuiIO& io = ImGui::GetIO();
    io.ConfigFlags |= ImGuiConfigFlags_NavEnableKeyboard;
    // Note: Docking requires IMGUI_HAS_DOCK to be defined when compiling ImGui
    // io.ConfigFlags |= ImGuiConfigFlags_DockingEnable;

    // Setup ImGui style
    ImGui::StyleColorsDark();
    
    // Enable antialiasing for smoother text and shapes
    ImGuiStyle& style = ImGui::GetStyle();
    style.AntiAliasedLines = true;
    style.AntiAliasedLinesUseTex = true;
    style.AntiAliasedFill = true;

    // Setup Platform/Renderer backends
    ImGui_ImplGlfw_InitForOpenGL(window_, true);
    ImGui_ImplOpenGL3_Init("#version 330");

    std::cout << "ISTA Knowledge Graph Editor initialized successfully" << std::endl;
    return true;
}

int KnowledgeGraphEditor::run() {
    while (!glfwWindowShouldClose(window_)) {
        glfwPollEvents();

        // Start ImGui frame
        ImGui_ImplOpenGL3_NewFrame();
        ImGui_ImplGlfw_NewFrame();
        ImGui::NewFrame();

        // Render UI with fixed layout
        render_menu_bar();
        render_toolbar();

        // Create a fullscreen window for the main layout
        ImGuiViewport* viewport = ImGui::GetMainViewport();
        ImGui::SetNextWindowPos(ImVec2(viewport->Pos.x, viewport->Pos.y + 60)); // Offset for menu bar + toolbar
        ImGui::SetNextWindowSize(ImVec2(viewport->Size.x, viewport->Size.y - 60));

        ImGuiWindowFlags window_flags = ImGuiWindowFlags_NoTitleBar | ImGuiWindowFlags_NoCollapse |
                                       ImGuiWindowFlags_NoResize | ImGuiWindowFlags_NoMove |
                                       ImGuiWindowFlags_NoBringToFrontOnFocus | ImGuiWindowFlags_NoNavFocus;

        ImGui::Begin("MainLayout", nullptr, window_flags);

        // Create three-column layout
        // Left panel: Data Sources (20% width)
        float left_panel_width = ImGui::GetContentRegionAvail().x * 0.2f;
        float right_panel_width = ImGui::GetContentRegionAvail().x * 0.25f;

        ImGui::BeginChild("LeftPanel", ImVec2(left_panel_width, 0), true);
        render_data_source_panel();
        ImGui::EndChild();

        ImGui::SameLine();

        // Center panel: Graph View (55% width)
        float center_panel_width = ImGui::GetContentRegionAvail().x - right_panel_width;
        ImGui::BeginChild("CenterPanel", ImVec2(center_panel_width, 0), true);
        render_graph_view();
        ImGui::EndChild();

        ImGui::SameLine();

        // Right panel: Properties (25% width)
        ImGui::BeginChild("RightPanel", ImVec2(0, 0), true);
        render_properties_panel();
        ImGui::EndChild();

        ImGui::End();

        // Handle file dialog request
        if (show_ontology_loader_) {
            show_ontology_loader_ = false;

            nfdchar_t *outPath;
            nfdfilteritem_t filterItem[2] = { { "OWL/RDF Files", "owl,rdf" }, { "All Files", "*" } };
            nfdresult_t result = NFD_OpenDialog(&outPath, filterItem, 2, nullptr);

            if (result == NFD_OKAY) {
                std::string filepath(outPath);
                load_ontology(filepath);
                NFD_FreePath(outPath);
            } else if (result == NFD_ERROR) {
                std::cerr << "File dialog error: " << NFD_GetError() << std::endl;
            }
            // NFD_CANCEL - user cancelled, do nothing
        }

        if (show_about_dialog_) {
            ImGui::OpenPopup("About");
            show_about_dialog_ = false;
        }

        if (ImGui::BeginPopupModal("About", nullptr, ImGuiWindowFlags_AlwaysAutoResize)) {
            ImGui::Text("ISTA Knowledge Graph Editor");
            ImGui::Text("Version 0.1.0");
            ImGui::Separator();
            ImGui::Text("A lightweight, cross-platform GUI for");
            ImGui::Text("populating OWL 2 knowledge graphs.");
            ImGui::Separator();
            ImGui::Text("Built with Dear ImGui and GLFW");

            if (ImGui::Button("Close")) {
                ImGui::CloseCurrentPopup();
            }
            ImGui::EndPopup();
        }

        // Handle preferences window
        if (show_preferences_) {
            ImGui::OpenPopup("Preferences");
            show_preferences_ = false;
        }

        if (ImGui::BeginPopupModal("Preferences", nullptr, ImGuiWindowFlags_AlwaysAutoResize)) {
            ImGui::Text("Display Options");
            ImGui::Separator();

            ImGui::Checkbox("Show namespace prefix in labels", &pref_show_namespace_prefix_);
            ImGui::SameLine();
            ImGui::TextDisabled("(?)");
            if (ImGui::IsItemHovered()) {
                ImGui::SetTooltip("When enabled, shows full IRIs like 'ex:Class'.\nWhen disabled, shows only 'Class'.");
            }

            ImGui::Separator();

            if (ImGui::Button("Close", ImVec2(120, 0))) {
                ImGui::CloseCurrentPopup();
            }
            ImGui::EndPopup();
        }

        // Handle database configuration dialog
        render_database_config_dialog();

        // Rendering
        ImGui::Render();
        int display_w, display_h;
        glfwGetFramebufferSize(window_, &display_w, &display_h);
        glViewport(0, 0, display_w, display_h);
        glClearColor(0.1f, 0.1f, 0.1f, 1.0f);
        glClear(GL_COLOR_BUFFER_BIT);
        ImGui_ImplOpenGL3_RenderDrawData(ImGui::GetDrawData());

        glfwSwapBuffers(window_);
    }

    return 0;
}

void KnowledgeGraphEditor::shutdown() {
    if (window_) {
        ImGui_ImplOpenGL3_Shutdown();
        ImGui_ImplGlfw_Shutdown();
        ImGui::DestroyContext();

        glfwDestroyWindow(window_);
        glfwTerminate();
        window_ = nullptr;
    }

    // Clean up NFD
    NFD_Quit();
}

bool KnowledgeGraphEditor::load_ontology(const std::string& filepath) {
    try {
        auto onto = ista::owl2::RDFXMLParser::parseFromFile(filepath);
        ontology_ = std::make_unique<ista::owl2::Ontology>(std::move(onto));
        current_filepath_ = filepath;
        ontology_modified_ = false;

        // Build graph visualization
        build_graph_from_ontology();

        std::cout << "Loaded ontology: " << filepath << std::endl;
        std::cout << "Classes: " << ontology_->getClasses().size() << std::endl;
        std::cout << "Individuals: " << ontology_->getIndividuals().size() << std::endl;
        std::cout << "Object Properties: " << ontology_->getObjectPropertyCount() << std::endl;
        std::cout << "Data Properties: " << ontology_->getDataPropertyCount() << std::endl;
        std::cout << "Annotation Properties: " << ontology_->getAnnotationProperties().size() << std::endl;

        return true;
    } catch (const std::exception& e) {
        std::cerr << "Error loading ontology: " << e.what() << std::endl;
        return false;
    }
}

bool KnowledgeGraphEditor::save_ontology(const std::string& filepath) {
    if (!ontology_) {
        std::cerr << "No ontology loaded" << std::endl;
        return false;
    }

    try {
        ista::owl2::RDFXMLSerializer serializer;
        serializer.serializeToFile(*ontology_, filepath);
        current_filepath_ = filepath;
        ontology_modified_ = false;
        std::cout << "Saved ontology: " << filepath << std::endl;
        return true;
    } catch (const std::exception& e) {
        std::cerr << "Error saving ontology: " << e.what() << std::endl;
        return false;
    }
}

void KnowledgeGraphEditor::render_menu_bar() {
    if (ImGui::BeginMainMenuBar()) {
        if (ImGui::BeginMenu("File")) {
            if (ImGui::MenuItem("Load Ontology", "Ctrl+O")) {
                show_ontology_loader_ = true;
            }
            if (ImGui::MenuItem("Save Ontology", "Ctrl+S", false, ontology_ != nullptr)) {
                if (!current_filepath_.empty()) {
                    save_ontology(current_filepath_);
                }
            }
            if (ImGui::MenuItem("Save As...", nullptr, false, ontology_ != nullptr)) {
                nfdchar_t *savePath;
                nfdfilteritem_t filterItem[1] = { { "OWL/RDF Files", "owl,rdf" } };
                nfdresult_t result = NFD_SaveDialog(&savePath, filterItem, 1, nullptr, "ontology.owl");

                if (result == NFD_OKAY) {
                    std::string filepath(savePath);
                    save_ontology(filepath);
                    NFD_FreePath(savePath);
                } else if (result == NFD_ERROR) {
                    std::cerr << "Save dialog error: " << NFD_GetError() << std::endl;
                }
            }
            ImGui::Separator();
            if (ImGui::MenuItem("Preferences...", nullptr)) {
                show_preferences_ = true;
            }
            ImGui::Separator();
            if (ImGui::MenuItem("Exit", "Alt+F4")) {
                glfwSetWindowShouldClose(window_, true);
            }
            ImGui::EndMenu();
        }

        if (ImGui::BeginMenu("View")) {
            ImGui::MenuItem("Show Class Hierarchy", nullptr, &show_class_hierarchy_);
            ImGui::MenuItem("Show Individuals", nullptr, &show_individuals_);
            ImGui::Separator();
            if (ImGui::MenuItem("Reset View")) {
                view_offset_x_ = 0.0f;
                view_offset_y_ = 0.0f;
                zoom_level_ = 1.0f;
            }
            ImGui::EndMenu();
        }

        if (ImGui::BeginMenu("Data")) {
            if (ImGui::MenuItem("Add Data Source", nullptr, false, ontology_ != nullptr)) {
                nfdchar_t *dataPath;
                nfdfilteritem_t filterItem[2] = { { "Data Files", "csv,xlsx" }, { "All Files", "*" } };
                nfdresult_t result = NFD_OpenDialog(&dataPath, filterItem, 2, nullptr);

                if (result == NFD_OKAY) {
                    std::string filepath(dataPath);
                    add_data_source(filepath);
                    NFD_FreePath(dataPath);
                } else if (result == NFD_ERROR) {
                    std::cerr << "File dialog error: " << NFD_GetError() << std::endl;
                }
            }
            if (ImGui::MenuItem("Populate from CSV", nullptr, false, ontology_ != nullptr)) {
                // TODO: Open CSV population dialog
            }
            ImGui::EndMenu();
        }

        if (ImGui::BeginMenu("Help")) {
            if (ImGui::MenuItem("About")) {
                show_about_dialog_ = true;
            }
            ImGui::EndMenu();
        }

        // Status bar on the right
        if (ontology_) {
            ImGui::SameLine(ImGui::GetWindowWidth() - 750);
            ImGui::Text("Classes: %zu | Individuals: %zu | ObjProps: %zu | DataProps: %zu | AnnotProps: %zu | Modified: %s",
                       ontology_->getClasses().size(),
                       ontology_->getIndividuals().size(),
                       ontology_->getObjectPropertyCount(),
                       ontology_->getDataPropertyCount(),
                       ontology_->getAnnotationProperties().size(),
                       ontology_modified_ ? "Yes" : "No");
        }

        ImGui::EndMainMenuBar();
    }
}

void KnowledgeGraphEditor::render_toolbar() {
    ImGuiViewport* viewport = ImGui::GetMainViewport();
    ImGui::SetNextWindowPos(ImVec2(viewport->Pos.x, viewport->Pos.y + 20)); // Below menu bar
    ImGui::SetNextWindowSize(ImVec2(viewport->Size.x, 40));
    
    ImGuiWindowFlags window_flags = ImGuiWindowFlags_NoTitleBar | ImGuiWindowFlags_NoResize | 
                                   ImGuiWindowFlags_NoMove | ImGuiWindowFlags_NoScrollbar | 
                                   ImGuiWindowFlags_NoSavedSettings;
    
    ImGui::PushStyleVar(ImGuiStyleVar_WindowPadding, ImVec2(8, 8));
    ImGui::PushStyleVar(ImGuiStyleVar_ItemSpacing, ImVec2(8, 8));
    ImGui::PushStyleColor(ImGuiCol_Button, ImVec4(0.2f, 0.25f, 0.3f, 1.0f));
    ImGui::PushStyleColor(ImGuiCol_ButtonHovered, ImVec4(0.3f, 0.35f, 0.4f, 1.0f));
    ImGui::PushStyleColor(ImGuiCol_ButtonActive, ImVec4(0.15f, 0.2f, 0.25f, 1.0f));
    
    if (ImGui::Begin("##Toolbar", nullptr, window_flags)) {
        // New/Clear ontology
        if (ImGui::Button("Clear Ontology", ImVec2(120, 24))) {
            if (ontology_) {
                ImGui::OpenPopup("ConfirmClear");
            }
        }
        if (ImGui::IsItemHovered()) {
            ImGui::SetTooltip("Clear the currently loaded ontology");
        }
        
        // Confirmation dialog for clearing ontology
        if (ImGui::BeginPopupModal("ConfirmClear", nullptr, ImGuiWindowFlags_AlwaysAutoResize)) {
            ImGui::Text("Are you sure you want to clear the current ontology?");
            if (ontology_modified_) {
                ImGui::TextColored(ImVec4(1.0f, 0.6f, 0.0f, 1.0f), "Warning: You have unsaved changes!");
            }
            ImGui::Separator();
            
            if (ImGui::Button("Yes, Clear", ImVec2(120, 0))) {
                ontology_.reset();
                nodes_.clear();
                edges_.clear();
                data_sources_.clear();
                selected_node_ = nullptr;
                dragged_node_ = nullptr;
                selected_edge_ = nullptr;
                selected_data_source_ = -1;
                current_filepath_.clear();
                ontology_modified_ = false;
                ImGui::CloseCurrentPopup();
            }
            ImGui::SameLine();
            if (ImGui::Button("Cancel", ImVec2(120, 0))) {
                ImGui::CloseCurrentPopup();
            }
            ImGui::EndPopup();
        }
        
        ImGui::SameLine();
        
        // Save ontology (with dropdown menu)
        bool can_save = (ontology_ != nullptr);
        if (!can_save) {
            ImGui::PushStyleVar(ImGuiStyleVar_Alpha, 0.5f);
        }
        if (ImGui::Button("Save", ImVec2(80, 24)) && can_save) {
            ImGui::OpenPopup("SaveMenu");
        }
        if (!can_save) {
            ImGui::PopStyleVar();
        }
        if (ImGui::IsItemHovered() && can_save) {
            ImGui::SetTooltip("Save ontology");
        }
        
        // Save menu popup
        if (ImGui::BeginPopup("SaveMenu")) {
            ImGui::TextColored(ImVec4(0.8f, 0.8f, 1.0f, 1.0f), "Save Options");
            ImGui::Separator();
            
            if (ImGui::MenuItem("Save As New File...", nullptr, false, true)) {
                // Trigger save-as dialog
                nfdchar_t *savePath;
                nfdfilteritem_t filterItem[1] = { { "OWL/RDF Files", "owl,rdf" } };
                
                // Suggest a filename based on current file
                std::string default_name = "ontology-populated.owl";
                if (!current_filepath_.empty()) {
                    size_t last_slash = current_filepath_.find_last_of("/\\");
                    size_t last_dot = current_filepath_.find_last_of(".");
                    if (last_slash != std::string::npos && last_dot != std::string::npos && last_dot > last_slash) {
                        std::string base_name = current_filepath_.substr(last_slash + 1, last_dot - last_slash - 1);
                        default_name = base_name + "-populated.owl";
                    }
                }
                
                nfdresult_t result = NFD_SaveDialog(&savePath, filterItem, 1, nullptr, default_name.c_str());
                
                if (result == NFD_OKAY) {
                    std::string filepath(savePath);
                    save_ontology(filepath);
                    NFD_FreePath(savePath);
                } else if (result == NFD_ERROR) {
                    std::cerr << "Save dialog error: " << NFD_GetError() << std::endl;
                }
                ImGui::CloseCurrentPopup();
            }
            if (ImGui::IsItemHovered()) {
                ImGui::SetTooltip("Recommended: Save to a new file to preserve original ontology");
            }
            
            ImGui::Separator();
            
            // Option to overwrite current file (with warning)
            bool has_current_file = !current_filepath_.empty();
            if (ImGui::MenuItem("Overwrite Current File", nullptr, false, has_current_file)) {
                ImGui::OpenPopup("ConfirmOverwrite");
                ImGui::CloseCurrentPopup();
            }
            if (ImGui::IsItemHovered()) {
                if (has_current_file) {
                    ImGui::SetTooltip("Warning: This will overwrite the original ontology file");
                } else {
                    ImGui::SetTooltip("No file currently loaded");
                }
            }
            
            ImGui::EndPopup();
        }
        
        // Confirmation dialog for overwriting
        if (ImGui::BeginPopupModal("ConfirmOverwrite", nullptr, ImGuiWindowFlags_AlwaysAutoResize)) {
            ImGui::TextColored(ImVec4(1.0f, 0.6f, 0.0f, 1.0f), "Warning!");
            ImGui::Separator();
            ImGui::Text("You are about to overwrite the original ontology file:");
            ImGui::TextWrapped("%s", current_filepath_.c_str());
            ImGui::Spacing();
            ImGui::TextWrapped("This will replace the unpopulated ontology with the current state.");
            ImGui::TextColored(ImVec4(0.8f, 0.8f, 0.8f, 1.0f), "Consider using 'Save As New File' instead.");
            ImGui::Separator();
            
            if (ImGui::Button("Yes, Overwrite", ImVec2(140, 0))) {
                save_ontology(current_filepath_);
                ImGui::CloseCurrentPopup();
            }
            ImGui::SameLine();
            if (ImGui::Button("Cancel", ImVec2(140, 0))) {
                ImGui::CloseCurrentPopup();
            }
            ImGui::EndPopup();
        }
        
        ImGui::SameLine();
        ImGui::Spacing();
        ImGui::SameLine();
        
        // Save project (placeholder for future)
        ImGui::PushStyleVar(ImGuiStyleVar_Alpha, 0.5f);
        if (ImGui::Button("Save Project", ImVec2(100, 24))) {
            // TODO: Implement project saving
        }
        ImGui::PopStyleVar();
        if (ImGui::IsItemHovered()) {
            ImGui::SetTooltip("Save project (coming soon)");
        }
        
        ImGui::SameLine();
        ImGui::Spacing();
        ImGui::SameLine();
        
        // Add mapped data to ontology
        bool can_add_data = (ontology_ != nullptr && selected_data_source_ >= 0 && 
                            selected_data_source_ < static_cast<int>(data_sources_.size()));
        if (!can_add_data) {
            ImGui::PushStyleVar(ImGuiStyleVar_Alpha, 0.5f);
        }
        if (ImGui::Button("Add Data to Ontology", ImVec2(150, 24)) && can_add_data) {
            // TODO: Implement data population from selected source
            ImGui::OpenPopup("AddDataPopup");
        }
        if (!can_add_data) {
            ImGui::PopStyleVar();
        }
        if (ImGui::IsItemHovered()) {
            if (can_add_data) {
                ImGui::SetTooltip("Populate ontology with data from selected source");
            } else {
                ImGui::SetTooltip("Load an ontology and select a data source first");
            }
        }
        
        // Placeholder popup for data addition
        if (ImGui::BeginPopupModal("AddDataPopup", nullptr, ImGuiWindowFlags_AlwaysAutoResize)) {
            ImGui::Text("Data population feature coming soon!");
            ImGui::Separator();
            ImGui::Text("This will allow you to:");
            ImGui::BulletText("Map data columns to ontology properties");
            ImGui::BulletText("Create individuals from data rows");
            ImGui::BulletText("Validate data against ontology constraints");
            ImGui::Separator();
            if (ImGui::Button("OK", ImVec2(120, 0))) {
                ImGui::CloseCurrentPopup();
            }
            ImGui::EndPopup();
        }
        
        ImGui::SameLine();
        ImGui::Spacing();
        ImGui::SameLine();
        
        // Refresh graph layout
        bool can_refresh = (ontology_ != nullptr);
        if (!can_refresh) {
            ImGui::PushStyleVar(ImGuiStyleVar_Alpha, 0.5f);
        }
        if (ImGui::Button("Refresh Layout", ImVec2(120, 24)) && can_refresh) {
            apply_force_directed_layout();
        }
        if (!can_refresh) {
            ImGui::PopStyleVar();
        }
        if (ImGui::IsItemHovered() && can_refresh) {
            ImGui::SetTooltip("Recalculate graph layout");
        }
        
        ImGui::SameLine();
        
        // Zoom controls
        if (!can_refresh) {
            ImGui::PushStyleVar(ImGuiStyleVar_Alpha, 0.5f);
        }
        if (ImGui::Button("Zoom In", ImVec2(80, 24)) && can_refresh) {
            zoom_level_ *= 1.2f;
            zoom_level_ = std::min(zoom_level_, 5.0f);
        }
        if (!can_refresh) {
            ImGui::PopStyleVar();
        }
        
        ImGui::SameLine();
        
        if (!can_refresh) {
            ImGui::PushStyleVar(ImGuiStyleVar_Alpha, 0.5f);
        }
        if (ImGui::Button("Zoom Out", ImVec2(80, 24)) && can_refresh) {
            zoom_level_ *= 0.8f;
            zoom_level_ = std::max(zoom_level_, 0.1f);
        }
        if (!can_refresh) {
            ImGui::PopStyleVar();
        }
        
        ImGui::SameLine();
        
        if (!can_refresh) {
            ImGui::PushStyleVar(ImGuiStyleVar_Alpha, 0.5f);
        }
        if (ImGui::Button("Reset View", ImVec2(90, 24)) && can_refresh) {
            view_offset_x_ = 0.0f;
            view_offset_y_ = 0.0f;
            zoom_level_ = 1.0f;
        }
        if (!can_refresh) {
            ImGui::PopStyleVar();
        }
        if (ImGui::IsItemHovered() && can_refresh) {
            ImGui::SetTooltip("Reset pan and zoom");
        }
        
        ImGui::End();
    }
    
    ImGui::PopStyleColor(3);
    ImGui::PopStyleVar(2);
}

void KnowledgeGraphEditor::render_graph_view() {
    // Header
    ImGui::Text("Knowledge Graph Visualization");
    ImGui::Separator();

    if (!ontology_) {
        ImGui::TextColored(ImVec4(0.6f, 0.6f, 0.6f, 1.0f),
                          "No ontology loaded. Use File > Load Ontology to begin.");
        return;
    }

    // Get drawing area
    ImVec2 canvas_pos = ImGui::GetCursorScreenPos();
    ImVec2 canvas_size = ImGui::GetContentRegionAvail();
    ImDrawList* draw_list = ImGui::GetWindowDrawList();

    // Create invisible button to capture mouse input in canvas
    ImGui::InvisibleButton("canvas", canvas_size, ImGuiButtonFlags_MouseButtonLeft | ImGuiButtonFlags_MouseButtonRight);
    bool is_canvas_hovered = ImGui::IsItemHovered();
    bool is_canvas_active = ImGui::IsItemActive();

    // Draw background
    draw_list->AddRectFilled(canvas_pos,
                            ImVec2(canvas_pos.x + canvas_size.x, canvas_pos.y + canvas_size.y),
                            IM_COL32(20, 20, 20, 255));

    // Draw grid
    const float grid_step = 50.0f * zoom_level_;
    for (float x = fmodf(view_offset_x_, grid_step); x < canvas_size.x; x += grid_step) {
        draw_list->AddLine(ImVec2(canvas_pos.x + x, canvas_pos.y),
                          ImVec2(canvas_pos.x + x, canvas_pos.y + canvas_size.y),
                          IM_COL32(40, 40, 40, 255));
    }
    for (float y = fmodf(view_offset_y_, grid_step); y < canvas_size.y; y += grid_step) {
        draw_list->AddLine(ImVec2(canvas_pos.x, canvas_pos.y + y),
                          ImVec2(canvas_pos.x + canvas_size.x, canvas_pos.y + y),
                          IM_COL32(40, 40, 40, 255));
    }

    // Track if anything was clicked
    bool clicked_on_something = false;

    // Draw edges
    for (const auto& edge : edges_) {
        auto from_it = std::find_if(nodes_.begin(), nodes_.end(),
                                    [&edge](const GraphNode& n) { return n.id == edge.from; });
        auto to_it = std::find_if(nodes_.begin(), nodes_.end(),
                                  [&edge](const GraphNode& n) { return n.id == edge.to; });

        if (from_it != nodes_.end() && to_it != nodes_.end()) {
            // Skip if nodes are hidden by view settings
            if ((!show_class_hierarchy_ && from_it->is_class) || (!show_class_hierarchy_ && to_it->is_class)) {
                continue;
            }
            if ((!show_individuals_ && !from_it->is_class) || (!show_individuals_ && !to_it->is_class)) {
                continue;
            }

            ImVec2 p1(canvas_pos.x + from_it->x * zoom_level_ + view_offset_x_,
                     canvas_pos.y + from_it->y * zoom_level_ + view_offset_y_);
            ImVec2 p2(canvas_pos.x + to_it->x * zoom_level_ + view_offset_x_,
                     canvas_pos.y + to_it->y * zoom_level_ + view_offset_y_);

            ImU32 edge_color = edge.is_subclass ?
                IM_COL32(100, 150, 255, 200) :  // Blue for subClassOf
                IM_COL32(150, 200, 150, 200);   // Green for object properties

            // Check if there's a reverse edge (bidirectional)
            bool has_reverse = false;
            for (const auto& other_edge : edges_) {
                if (other_edge.from == edge.to && other_edge.to == edge.from) {
                    has_reverse = true;
                    break;
                }
            }

            // Draw curved line if bidirectional, straight line otherwise
            if (has_reverse) {
                // Calculate control point for bezier curve (offset to the right of the line)
                float dx = p2.x - p1.x;
                float dy = p2.y - p1.y;
                float len = sqrtf(dx * dx + dy * dy);

                if (len > 0) {
                    // Perpendicular vector (rotate 90 degrees)
                    float perp_x = -dy / len;
                    float perp_y = dx / len;

                    // Offset amount (20% of distance between nodes)
                    float offset = len * 0.2f;

                    // Control point for quadratic bezier
                    ImVec2 ctrl((p1.x + p2.x) * 0.5f + perp_x * offset,
                               (p1.y + p2.y) * 0.5f + perp_y * offset);

                    // Draw bezier curve
                    draw_list->AddBezierQuadratic(p1, ctrl, p2, edge_color, 2.0f);
                }
            } else {
                // Straight line for unidirectional edges
                draw_list->AddLine(p1, p2, edge_color, 2.0f);
            }

            // Draw arrow at the edge of the destination node
            float dx, dy, len;
            
            // Get the radius of the destination node
            float to_node_radius = to_it->is_class ? 30.0f : 20.0f;

            if (has_reverse) {
                // For curved edges, calculate tangent at the end of the bezier curve
                // Tangent at t=1 for quadratic bezier: 2*(ctrl - p2)
                float perp_x_calc = -((p2.y - p1.y) / sqrtf((p2.x - p1.x) * (p2.x - p1.x) + (p2.y - p1.y) * (p2.y - p1.y)));
                float perp_y_calc = ((p2.x - p1.x) / sqrtf((p2.x - p1.x) * (p2.x - p1.x) + (p2.y - p1.y) * (p2.y - p1.y)));
                float offset_calc = sqrtf((p2.x - p1.x) * (p2.x - p1.x) + (p2.y - p1.y) * (p2.y - p1.y)) * 0.2f;
                ImVec2 ctrl((p1.x + p2.x) * 0.5f + perp_x_calc * offset_calc,
                           (p1.y + p2.y) * 0.5f + perp_y_calc * offset_calc);

                dx = p2.x - ctrl.x;
                dy = p2.y - ctrl.y;
            } else {
                // For straight edges
                dx = p2.x - p1.x;
                dy = p2.y - p1.y;
            }

            len = sqrtf(dx * dx + dy * dy);
            if (len > 0) {
                dx /= len;
                dy /= len;
                
                // Position arrow tip at the edge of the destination node
                ImVec2 arrow_base(p2.x - dx * to_node_radius, p2.y - dy * to_node_radius);
                
                float arrow_size = 12.0f;  // Fixed size for visibility
                ImVec2 arrow_p1(arrow_base.x - dx * arrow_size - dy * arrow_size * 0.5f,
                               arrow_base.y - dy * arrow_size + dx * arrow_size * 0.5f);
                ImVec2 arrow_p2(arrow_base.x - dx * arrow_size + dy * arrow_size * 0.5f,
                               arrow_base.y - dy * arrow_size - dx * arrow_size * 0.5f);
                draw_list->AddTriangleFilled(arrow_base, arrow_p1, arrow_p2, edge_color);

                // Draw edge label at midpoint
                if (!edge.label.empty()) {
                    std::string display_label = format_label(edge.label);
                    ImVec2 mid_point;

                    if (has_reverse) {
                        // For curved edges, calculate point on bezier curve at t=0.5
                        float perp_x_calc = -((p2.y - p1.y) / sqrtf((p2.x - p1.x) * (p2.x - p1.x) + (p2.y - p1.y) * (p2.y - p1.y)));
                        float perp_y_calc = ((p2.x - p1.x) / sqrtf((p2.x - p1.x) * (p2.x - p1.x) + (p2.y - p1.y) * (p2.y - p1.y)));
                        float offset_calc = sqrtf((p2.x - p1.x) * (p2.x - p1.x) + (p2.y - p1.y) * (p2.y - p1.y)) * 0.2f;
                        ImVec2 ctrl((p1.x + p2.x) * 0.5f + perp_x_calc * offset_calc,
                                   (p1.y + p2.y) * 0.5f + perp_y_calc * offset_calc);

                        // Quadratic bezier at t=0.5: B(0.5) = 0.25*P0 + 0.5*P1 + 0.25*P2
                        mid_point.x = 0.25f * p1.x + 0.5f * ctrl.x + 0.25f * p2.x;
                        mid_point.y = 0.25f * p1.y + 0.5f * ctrl.y + 0.25f * p2.y;
                    } else {
                        // Straight line midpoint
                        mid_point.x = (p1.x + p2.x) * 0.5f;
                        mid_point.y = (p1.y + p2.y) * 0.5f;
                    }

                    ImVec2 text_size = ImGui::CalcTextSize(display_label.c_str());

                    // Draw background rectangle for label
                    ImVec2 label_min(mid_point.x - text_size.x * 0.5f - 3, mid_point.y - text_size.y * 0.5f - 2);
                    ImVec2 label_max(mid_point.x + text_size.x * 0.5f + 3, mid_point.y + text_size.y * 0.5f + 2);
                    draw_list->AddRectFilled(label_min, label_max, IM_COL32(20, 20, 20, 200));
                    draw_list->AddRect(label_min, label_max, edge_color);

                    // Draw text
                    draw_list->AddText(ImVec2(mid_point.x - text_size.x * 0.5f, mid_point.y - text_size.y * 0.5f),
                                      IM_COL32(220, 220, 220, 255), display_label.c_str());
                }
            }

            // Handle edge click detection
            if (is_canvas_hovered && ImGui::IsMouseClicked(0)) {
                ImVec2 mouse_pos = ImGui::GetMousePos();
                float click_distance = 10.0f; // Pixels away from edge to still count as click

                // Calculate distance from mouse to edge (line or curve)
                float dist_to_edge;
                if (has_reverse) {
                    // For curved edges, approximate distance to bezier curve
                    // Sample points along the curve and find minimum distance
                    float min_dist = FLT_MAX;
                    for (float t = 0.0f; t <= 1.0f; t += 0.1f) {
                        float perp_x_calc = -((p2.y - p1.y) / sqrtf((p2.x - p1.x) * (p2.x - p1.x) + (p2.y - p1.y) * (p2.y - p1.y)));
                        float perp_y_calc = ((p2.x - p1.x) / sqrtf((p2.x - p1.x) * (p2.x - p1.x) + (p2.y - p1.y) * (p2.y - p1.y)));
                        float offset_calc = sqrtf((p2.x - p1.x) * (p2.x - p1.x) + (p2.y - p1.y) * (p2.y - p1.y)) * 0.2f;
                        ImVec2 ctrl((p1.x + p2.x) * 0.5f + perp_x_calc * offset_calc,
                                   (p1.y + p2.y) * 0.5f + perp_y_calc * offset_calc);

                        // Quadratic bezier formula: B(t) = (1-t)^2*P0 + 2*(1-t)*t*P1 + t^2*P2
                        float one_minus_t = 1.0f - t;
                        ImVec2 curve_point(
                            one_minus_t * one_minus_t * p1.x + 2 * one_minus_t * t * ctrl.x + t * t * p2.x,
                            one_minus_t * one_minus_t * p1.y + 2 * one_minus_t * t * ctrl.y + t * t * p2.y
                        );

                        float dx_mouse = mouse_pos.x - curve_point.x;
                        float dy_mouse = mouse_pos.y - curve_point.y;
                        float dist = sqrtf(dx_mouse * dx_mouse + dy_mouse * dy_mouse);
                        if (dist < min_dist) min_dist = dist;
                    }
                    dist_to_edge = min_dist;
                } else {
                    // For straight edges, calculate perpendicular distance to line
                    float edge_dx = p2.x - p1.x;
                    float edge_dy = p2.y - p1.y;
                    float edge_len_sq = edge_dx * edge_dx + edge_dy * edge_dy;

                    if (edge_len_sq > 0) {
                        float t = ((mouse_pos.x - p1.x) * edge_dx + (mouse_pos.y - p1.y) * edge_dy) / edge_len_sq;
                        t = std::max(0.0f, std::min(1.0f, t)); // Clamp to line segment

                        ImVec2 closest_point(p1.x + t * edge_dx, p1.y + t * edge_dy);
                        float dx_mouse = mouse_pos.x - closest_point.x;
                        float dy_mouse = mouse_pos.y - closest_point.y;
                        dist_to_edge = sqrtf(dx_mouse * dx_mouse + dy_mouse * dy_mouse);
                    } else {
                        dist_to_edge = FLT_MAX;
                    }
                }

                if (dist_to_edge < click_distance) {
                    // Edge was clicked - deselect node and select edge
                    if (selected_node_) {
                        selected_node_->selected = false;
                        selected_node_ = nullptr;
                    }
                    selected_edge_ = &edge;
                    clicked_on_something = true;
                }
            }
        }
    }

    // Draw nodes
    for (auto& node : nodes_) {
        if (!show_class_hierarchy_ && node.is_class) continue;
        if (!show_individuals_ && !node.is_class) continue;

        ImVec2 node_pos(canvas_pos.x + node.x * zoom_level_ + view_offset_x_,
                       canvas_pos.y + node.y * zoom_level_ + view_offset_y_);

        float node_radius = node.is_class ? 30.0f : 20.0f;
        ImU32 node_color = node.is_class ?
            IM_COL32(70, 130, 180, 255) :   // Steel blue for classes
            IM_COL32(60, 179, 113, 255);    // Medium sea green for individuals

        if (node.selected) {
            node_color = IM_COL32(255, 215, 0, 255); // Gold for selected
        }

        // Draw node circle
        draw_list->AddCircleFilled(node_pos, node_radius, node_color);
        draw_list->AddCircle(node_pos, node_radius, IM_COL32(255, 255, 255, 255), 0, 2.0f);

        // Draw label
        std::string display_label = format_label(node.label);
        ImVec2 text_size = ImGui::CalcTextSize(display_label.c_str());
        draw_list->AddText(ImVec2(node_pos.x - text_size.x * 0.5f,
                                 node_pos.y + node_radius + 5),
                          IM_COL32(255, 255, 255, 255),
                          display_label.c_str());

        // Handle node interaction (only when canvas is hovered)
        if (is_canvas_hovered) {
            ImVec2 mouse_pos = ImGui::GetMousePos();
            float dist_sq = (mouse_pos.x - node_pos.x) * (mouse_pos.x - node_pos.x) +
                           (mouse_pos.y - node_pos.y) * (mouse_pos.y - node_pos.y);

            if (dist_sq < node_radius * node_radius) {
                if (ImGui::IsMouseClicked(0)) {
                    handle_node_selection(&node);
                    clicked_on_something = true;
                }
                if (ImGui::IsMouseDragging(0)) {
                    ImVec2 delta = ImGui::GetMouseDragDelta(0);
                    handle_node_drag(&node, delta.x, delta.y);
                    ImGui::ResetMouseDragDelta(0);
                }
            }
        }
    }

    // Handle panning with left-click drag on empty space
    if (is_canvas_hovered && ImGui::IsMouseDragging(ImGuiMouseButton_Left) && !clicked_on_something) {
        ImVec2 delta = ImGui::GetMouseDragDelta(ImGuiMouseButton_Left);
        view_offset_x_ += delta.x;
        view_offset_y_ += delta.y;
        ImGui::ResetMouseDragDelta(ImGuiMouseButton_Left);
    }
    
    // Handle click on empty canvas (deselect all)
    if (is_canvas_hovered && ImGui::IsMouseClicked(0) && !clicked_on_something && !selected_edge_) {
        // Only deselect if not dragging (to allow panning)
        if (!ImGui::IsMouseDragging(ImGuiMouseButton_Left)) {
            // Deselect all nodes
            for (auto& n : nodes_) {
                n.selected = false;
            }
            selected_node_ = nullptr;
            selected_edge_ = nullptr;
        }
    }

    // Handle panning with middle mouse button or right mouse button (alternative)
    if (is_canvas_hovered && (ImGui::IsMouseDragging(ImGuiMouseButton_Middle) ||
                              ImGui::IsMouseDragging(ImGuiMouseButton_Right))) {
        ImVec2 delta = ImGui::GetMouseDragDelta(ImGuiMouseButton_Middle);
        if (delta.x == 0.0f && delta.y == 0.0f) {
            delta = ImGui::GetMouseDragDelta(ImGuiMouseButton_Right);
        }
        view_offset_x_ += delta.x;
        view_offset_y_ += delta.y;
        ImGui::ResetMouseDragDelta(ImGuiMouseButton_Middle);
        ImGui::ResetMouseDragDelta(ImGuiMouseButton_Right);
    }

    // Handle zooming with mouse wheel (only when canvas is hovered)
    float wheel = ImGui::GetIO().MouseWheel;
    if (wheel != 0 && is_canvas_hovered) {
        zoom_level_ *= (1.0f + wheel * 0.1f);
        zoom_level_ = std::max(0.1f, std::min(zoom_level_, 5.0f));
    }
}

void KnowledgeGraphEditor::render_properties_panel() {
    // Header
    ImGui::Text("Ontology Properties");
    ImGui::Separator();

    if (selected_edge_) {
        // Display edge properties
        ImGui::Text("Object Property");
        ImGui::Separator();

        std::string display_label = format_label(selected_edge_->label);
        ImGui::Text("Property: %s", display_label.c_str());
        ImGui::Text("Full Label: %s", selected_edge_->label.c_str());
        ImGui::Separator();

        // Find the source and target nodes
        auto from_it = std::find_if(nodes_.begin(), nodes_.end(),
                                    [this](const GraphNode& n) { return n.id == selected_edge_->from; });
        auto to_it = std::find_if(nodes_.begin(), nodes_.end(),
                                  [this](const GraphNode& n) { return n.id == selected_edge_->to; });

        if (from_it != nodes_.end() && to_it != nodes_.end()) {
            std::string from_label = format_label(from_it->label);
            std::string to_label = format_label(to_it->label);

            ImGui::Text("Domain: %s", from_label.c_str());
            ImGui::Text("Domain IRI: %s", selected_edge_->from.c_str());
            ImGui::Separator();
            ImGui::Text("Range: %s", to_label.c_str());
            ImGui::Text("Range IRI: %s", selected_edge_->to.c_str());
        } else {
            ImGui::Text("Domain IRI: %s", selected_edge_->from.c_str());
            ImGui::Text("Range IRI: %s", selected_edge_->to.c_str());
        }

        ImGui::Separator();
        ImGui::Text("Type: %s", selected_edge_->is_subclass ? "SubClassOf" : "Object Property");

    } else if (!selected_node_) {
        ImGui::TextColored(ImVec4(0.6f, 0.6f, 0.6f, 1.0f),
                          "Select a node or edge to view properties");
    } else {
        ImGui::Text("Node: %s", selected_node_->label.c_str());
        ImGui::Text("IRI: %s", selected_node_->id.c_str());
        ImGui::Text("Type: %s", selected_node_->is_class ? "Class" : "Individual");
        ImGui::Separator();

        if (ontology_) {
            // Show axioms related to this entity
            ImGui::Text("Related Axioms:");
            // TODO: Query and display axioms
        }
    }
}

void KnowledgeGraphEditor::render_data_source_panel() {
    // Header
    ImGui::Text("Data Sources");
    ImGui::Separator();

    if (!ontology_) {
        ImGui::TextColored(ImVec4(0.6f, 0.6f, 0.6f, 1.0f),
                          "Load an ontology first");
        return;
    }

    if (ImGui::Button("Add Data Source")) {
        ImGui::OpenPopup("AddDataSourceMenu");
    }

    // Render the popup menu right after the button
    if (ImGui::BeginPopup("AddDataSourceMenu")) {
        ImGui::Text("Add Data Source");
        ImGui::Separator();

        if (ImGui::MenuItem("From File...")) {
            // Open file dialog
            nfdchar_t *dataPath;
            nfdfilteritem_t filterItem[4] = {
                { "CSV Files", "csv,tsv,tab" },
                { "Excel Files", "xlsx,xls" },
                { "SQLite Database", "db,sqlite,sqlite3" },
                { "All Files", "*" }
            };
            nfdresult_t result = NFD_OpenDialog(&dataPath, filterItem, 4, nullptr);

            if (result == NFD_OKAY) {
                std::string filepath(dataPath);
                add_data_source(filepath);
                NFD_FreePath(dataPath);
            } else if (result == NFD_ERROR) {
                std::cerr << "File dialog error: " << NFD_GetError() << std::endl;
            }
            ImGui::CloseCurrentPopup();
        }

        if (ImGui::MenuItem("From Database...")) {
            // Open database configuration dialog
            show_database_config_dialog_ = true;
            temp_database_config_ = DataSource();
            temp_database_config_.is_database = true;
            temp_database_config_.format = "mysql";  // Default to MySQL
            temp_database_config_.db_config.port = get_default_port("mysql");
            db_type_selection_ = "mysql";
            ImGui::CloseCurrentPopup();
        }

        ImGui::EndPopup();
    }

    ImGui::Separator();

    // List data sources
    for (size_t i = 0; i < data_sources_.size(); ++i) {
        ImGui::PushID(static_cast<int>(i));

        // Extract filename from path or use database identifier
        std::string display_name;
        if (data_sources_[i].is_database) {
            // For databases, show an icon and the connection identifier
            display_name = "[DB] " + data_sources_[i].filepath;
        } else {
            // For files, extract just the filename
            display_name = data_sources_[i].filepath;
            size_t last_slash = display_name.find_last_of("/\\");
            if (last_slash != std::string::npos) {
                display_name = display_name.substr(last_slash + 1);
            }
        }

        bool is_selected = (selected_data_source_ == static_cast<int>(i));
        if (ImGui::Selectable(display_name.c_str(), is_selected)) {
            selected_data_source_ = static_cast<int>(i);
        }

        if (data_sources_[i].mapped_class_iri.has_value()) {
            ImGui::SameLine();
            ImGui::TextColored(ImVec4(0.5f, 1.0f, 0.5f, 1.0f),
                             " -> %s", data_sources_[i].mapped_class_iri.value().c_str());
        }

        ImGui::PopID();
    }

    // Display metadata for selected data source
    if (selected_data_source_ >= 0 && selected_data_source_ < static_cast<int>(data_sources_.size())) {
        ImGui::Separator();
        ImGui::Text("Data Source Details");
        ImGui::Separator();

        const auto& ds = data_sources_[selected_data_source_];

        // Show format and type
        ImGui::Text("Type: %s", ds.is_database ? "Database" : "File");
        ImGui::Text("Format: %s", ds.format.c_str());

        // Show database connection details if it's a database
        if (ds.is_database) {
            ImGui::Separator();
            ImGui::Text("Connection Details:");

            if (ds.db_config.use_connection_string) {
                ImGui::Text("Connection String:");
                ImGui::TextWrapped("%s", ds.db_config.connection_string.c_str());
            } else {
                ImGui::Text("Host: %s", ds.db_config.host.c_str());
                ImGui::Text("Port: %d", ds.db_config.port);
                ImGui::Text("Database: %s", ds.db_config.database.c_str());
                ImGui::Text("Username: %s", ds.db_config.username.c_str());
            }
        }

        // Show error message if metadata loading failed
        if (!ds.error_message.empty()) {
            ImGui::TextColored(ImVec4(1.0f, 0.4f, 0.4f, 1.0f), "Error:");
            ImGui::TextWrapped("%s", ds.error_message.c_str());
        }

        // Show metadata if loaded
        if (ds.metadata_loaded) {
            // For CSV/TSV/Excel
            if (!ds.column_names.empty()) {
                ImGui::Text("Columns: %zu", ds.column_names.size());
                ImGui::Text("Estimated Rows: %zu", ds.estimated_row_count);

                ImGui::Separator();
                ImGui::Text("Column Names:");

                // Show column names in a scrollable region
                ImGui::BeginChild("ColumnNames", ImVec2(0, 100), true);
                for (size_t i = 0; i < ds.column_names.size(); ++i) {
                    ImGui::BulletText("%s", ds.column_names[i].c_str());
                }
                ImGui::EndChild();

                // Show preview data
                if (!ds.preview_rows.empty()) {
                    ImGui::Separator();
                    ImGui::Text("Data Preview (first %zu rows):", ds.preview_rows.size());

                    ImGui::BeginChild("DataPreview", ImVec2(0, 0), true, ImGuiWindowFlags_HorizontalScrollbar);

                    // Display as table
                    if (ImGui::BeginTable("PreviewTable", ds.column_names.size(),
                                         ImGuiTableFlags_Borders | ImGuiTableFlags_RowBg |
                                         ImGuiTableFlags_ScrollX | ImGuiTableFlags_ScrollY)) {

                        // Header row
                        for (const auto& col_name : ds.column_names) {
                            ImGui::TableSetupColumn(col_name.c_str());
                        }
                        ImGui::TableHeadersRow();

                        // Data rows
                        for (const auto& row : ds.preview_rows) {
                            ImGui::TableNextRow();
                            for (size_t col = 0; col < row.size() && col < ds.column_names.size(); ++col) {
                                ImGui::TableSetColumnIndex(col);
                                ImGui::TextUnformatted(row[col].c_str());
                            }
                        }

                        ImGui::EndTable();
                    }

                    ImGui::EndChild();
                }
            }

            // For Excel (when implemented)
            if (!ds.sheet_names.empty()) {
                ImGui::Text("Sheets: %zu", ds.sheet_names.size());
                ImGui::BeginChild("SheetNames", ImVec2(0, 100), true);
                for (const auto& sheet : ds.sheet_names) {
                    ImGui::BulletText("%s", sheet.c_str());
                }
                ImGui::EndChild();
            }

            // For SQL databases (when implemented)
            if (!ds.table_names.empty()) {
                ImGui::Text("Tables: %zu", ds.table_names.size());
                ImGui::BeginChild("TableNames", ImVec2(0, 100), true);
                for (const auto& table : ds.table_names) {
                    ImGui::BulletText("%s", table.c_str());
                }
                ImGui::EndChild();
            }
        }
    }
}

void KnowledgeGraphEditor::build_graph_from_ontology() {
    if (!ontology_) return;

    nodes_.clear();
    edges_.clear();

    // Extract classes
    if (show_class_hierarchy_) {
        extract_class_hierarchy();
    }

    // Extract individuals
    if (show_individuals_) {
        extract_individuals();
    }

    // Extract object properties (creates edges from Domain to Range)
    extract_object_properties();

    // Apply initial layout
    apply_hierarchical_layout();
}

void KnowledgeGraphEditor::extract_class_hierarchy() {
    if (!ontology_) return;

    auto classes = ontology_->getClasses();

    // Add class nodes
    for (const auto& cls : classes) {
        std::string iri = cls.getIRI().toString();
        std::string label = cls.getIRI().getAbbreviated();
        nodes_.emplace_back(iri, label, true);
    }

    // Add subClassOf edges - iterate through all class axioms
    auto class_axioms = ontology_->getClassAxioms();
    for (const auto& axiom : class_axioms) {
        if (axiom->getAxiomType() == "SubClassOf") {
            auto subclass_axiom = std::dynamic_pointer_cast<ista::owl2::SubClassOf>(axiom);
            if (subclass_axiom) {
                // TODO: Handle class expressions properly
                // For now, skip complex class expressions
            }
        }
    }
}

void KnowledgeGraphEditor::extract_individuals() {
    if (!ontology_) return;

    auto individuals = ontology_->getIndividuals();

    // Add individual nodes
    for (const auto& ind : individuals) {
        std::string iri = ind.getIRI().toString();
        std::string label = ind.getIRI().getAbbreviated();
        nodes_.emplace_back(iri, label, false);
    }

    // Add object property assertion edges - iterate through assertion axioms
    auto assertion_axioms = ontology_->getAssertionAxioms();

    for (const auto& axiom : assertion_axioms) {
        if (axiom->getAxiomType() == "ObjectPropertyAssertion") {
            auto obj_prop_axiom = std::dynamic_pointer_cast<ista::owl2::ObjectPropertyAssertion>(axiom);
            if (obj_prop_axiom) {
                // Get source and target individuals (handle variant)
                auto source = obj_prop_axiom->getSource();
                auto target = obj_prop_axiom->getTarget();

                // Only handle NamedIndividuals for now
                if (std::holds_alternative<ista::owl2::NamedIndividual>(source) &&
                    std::holds_alternative<ista::owl2::NamedIndividual>(target)) {

                    auto source_ind = std::get<ista::owl2::NamedIndividual>(source);
                    auto target_ind = std::get<ista::owl2::NamedIndividual>(target);

                    // Get property (ObjectPropertyExpression is a variant)
                    auto prop_expr = obj_prop_axiom->getProperty();
                    std::string prop;
                    if (std::holds_alternative<ista::owl2::ObjectProperty>(prop_expr)) {
                        // Regular property
                        auto obj_prop = std::get<ista::owl2::ObjectProperty>(prop_expr);
                        prop = obj_prop.getIRI().getAbbreviated();
                    } else {
                        // Inverse property: pair<ObjectProperty, bool>
                        auto prop_pair = std::get<std::pair<ista::owl2::ObjectProperty, bool>>(prop_expr);
                        prop = "inv(" + prop_pair.first.getIRI().getAbbreviated() + ")";
                    }

                    std::string from = source_ind.getIRI().toString();
                    std::string to = target_ind.getIRI().toString();
                    edges_.emplace_back(from, to, prop, false);
                }
            }
        }
    }
}

void KnowledgeGraphEditor::extract_object_properties() {
    if (!ontology_) return;

    // Get all object property axioms
    auto obj_prop_axioms = ontology_->getObjectPropertyAxioms();

    // Map to store domain and range for each property
    std::unordered_map<std::string, std::string> property_domains;
    std::unordered_map<std::string, std::string> property_ranges;

    // Extract domain and range axioms
    for (const auto& axiom : obj_prop_axioms) {
        if (axiom->getAxiomType() == "ObjectPropertyDomain") {
            auto domain_axiom = std::dynamic_pointer_cast<ista::owl2::ObjectPropertyDomain>(axiom);
            if (domain_axiom) {
                auto prop_expr = domain_axiom->getProperty();
                auto domain_expr = domain_axiom->getDomain();

                // Only handle simple properties (not inverse) and named classes for now
                if (std::holds_alternative<ista::owl2::ObjectProperty>(prop_expr)) {
                    auto obj_prop = std::get<ista::owl2::ObjectProperty>(prop_expr);
                    std::string prop_iri = obj_prop.getIRI().toString();

                    // Check if domain is a simple named class
                    if (domain_expr->getExpressionType() == "Class" || domain_expr->getExpressionType() == "NamedClass") {
                        // Try to cast to NamedClass first
                        auto named_class = std::dynamic_pointer_cast<ista::owl2::NamedClass>(domain_expr);
                        if (named_class) {
                            property_domains[prop_iri] = named_class->getClass().getIRI().toString();
                        } else {
                            // Fallback to Class
                            auto domain_class = std::dynamic_pointer_cast<ista::owl2::Class>(domain_expr);
                            if (domain_class) {
                                property_domains[prop_iri] = domain_class->getIRI().toString();
                            }
                        }
                    }
                }
            }
        } else if (axiom->getAxiomType() == "ObjectPropertyRange") {
            auto range_axiom = std::dynamic_pointer_cast<ista::owl2::ObjectPropertyRange>(axiom);
            if (range_axiom) {
                auto prop_expr = range_axiom->getProperty();
                auto range_expr = range_axiom->getRange();

                // Only handle simple properties (not inverse) and named classes for now
                if (std::holds_alternative<ista::owl2::ObjectProperty>(prop_expr)) {
                    auto obj_prop = std::get<ista::owl2::ObjectProperty>(prop_expr);
                    std::string prop_iri = obj_prop.getIRI().toString();

                    // Check if range is a simple named class
                    if (range_expr->getExpressionType() == "Class" || range_expr->getExpressionType() == "NamedClass") {
                        // Try to cast to NamedClass first
                        auto named_class = std::dynamic_pointer_cast<ista::owl2::NamedClass>(range_expr);
                        if (named_class) {
                            property_ranges[prop_iri] = named_class->getClass().getIRI().toString();
                        } else {
                            // Fallback to Class
                            auto range_class = std::dynamic_pointer_cast<ista::owl2::Class>(range_expr);
                            if (range_class) {
                                property_ranges[prop_iri] = range_class->getIRI().toString();
                            }
                        }
                    }
                }
            }
        }
    }

    // Create edges from Domain to Range for each property
    auto object_properties = ontology_->getObjectProperties();

    for (const auto& obj_prop : object_properties) {
        std::string prop_iri = obj_prop.getIRI().toString();
        std::string prop_label = obj_prop.getIRI().getAbbreviated();

        // Check if we have both domain and range
        auto domain_it = property_domains.find(prop_iri);
        auto range_it = property_ranges.find(prop_iri);

        if (domain_it != property_domains.end() && range_it != property_ranges.end()) {
            std::string domain_iri = domain_it->second;
            std::string range_iri = range_it->second;

            // Create edge from domain to range
            edges_.emplace_back(domain_iri, range_iri, prop_label, false);
        }
    }
}

void KnowledgeGraphEditor::apply_hierarchical_layout() {
    if (nodes_.empty()) return;
    
    // Initialize random number generator
    std::srand(static_cast<unsigned>(std::time(nullptr)));
    
    // Build adjacency information to identify connected components
    std::unordered_map<std::string, std::vector<std::string>> adjacency;
    std::unordered_map<std::string, int> degree;
    
    for (const auto& node : nodes_) {
        degree[node.id] = 0;
        adjacency[node.id] = {};
    }
    
    for (const auto& edge : edges_) {
        adjacency[edge.from].push_back(edge.to);
        adjacency[edge.to].push_back(edge.from);
        degree[edge.from]++;
        degree[edge.to]++;
    }
    
    // Separate connected nodes from isolated nodes
    std::vector<GraphNode*> connected_nodes;
    std::vector<GraphNode*> isolated_nodes;
    
    for (auto& node : nodes_) {
        if (degree[node.id] > 0) {
            connected_nodes.push_back(&node);
        } else {
            isolated_nodes.push_back(&node);
        }
    }
    
    // Initialize connected nodes with better distribution
    const float connected_spread = 600.0f;
    const float connected_center_x = 700.0f;
    const float connected_center_y = 500.0f;
    
    for (auto* node : connected_nodes) {
        // Use polar coordinates for more even distribution
        float angle = (std::rand() / static_cast<float>(RAND_MAX)) * 2.0f * 3.14159f;
        float radius = (std::rand() / static_cast<float>(RAND_MAX)) * connected_spread * 0.5f;
        node->x = connected_center_x + radius * std::cos(angle);
        node->y = connected_center_y + radius * std::sin(angle);
        node->vx = 0.0f;
        node->vy = 0.0f;
    }
    
    // Place isolated nodes in a natural circular arrangement around the connected component
    if (!isolated_nodes.empty()) {
        const float isolation_radius = connected_spread * 0.7f + 150.0f;
        const float angle_step = (2.0f * 3.14159f) / static_cast<float>(isolated_nodes.size());
        
        // Add some randomness to avoid perfect circle
        for (size_t i = 0; i < isolated_nodes.size(); ++i) {
            float base_angle = i * angle_step;
            float angle_noise = ((std::rand() / static_cast<float>(RAND_MAX)) - 0.5f) * 0.3f;
            float radius_noise = ((std::rand() / static_cast<float>(RAND_MAX)) - 0.5f) * 80.0f;
            
            float angle = base_angle + angle_noise;
            float radius = isolation_radius + radius_noise;
            
            isolated_nodes[i]->x = connected_center_x + radius * std::cos(angle);
            isolated_nodes[i]->y = connected_center_y + radius * std::sin(angle);
            isolated_nodes[i]->vx = 0.0f;
            isolated_nodes[i]->vy = 0.0f;
        }
    }
    
    // Run force-directed layout only on connected nodes
    apply_force_directed_layout();
}

void KnowledgeGraphEditor::apply_force_directed_layout() {
    // Improved force-directed layout with better overlap prevention

    if (nodes_.empty()) return;

    // Count only connected nodes for better spacing
    int connected_count = 0;
    for (const auto& node : nodes_) {
        bool has_edges = false;
        for (const auto& edge : edges_) {
            if (edge.from == node.id || edge.to == node.id) {
                has_edges = true;
                break;
            }
        }
        if (has_edges) connected_count++;
    }

    if (connected_count == 0) return;

    // Layout parameters - tuned for better spread and less overlap
    const int iterations = 800;  // More iterations for better convergence
    const float area = 1200.0f * 800.0f;  // Larger area for more space
    const float k = std::sqrt(area / static_cast<float>(std::max(1, connected_count)));  // Optimal distance
    const float c_repulsion = k * k * 2.5f;  // Stronger repulsion to prevent overlap
    const float c_attraction = k * 0.8f;     // Slightly weaker attraction for more spread
    float temperature = 150.0f;       // Higher initial temperature
    const float cooling = 0.97f;      // Slower cooling for better settling
    const float min_temp = 0.5f;      // Higher minimum for continued movement

    // Build node index map for fast lookup
    std::unordered_map<std::string, size_t> node_index;
    for (size_t i = 0; i < nodes_.size(); ++i) {
        node_index[nodes_[i].id] = i;
    }

    // Build set of connected node IDs for faster lookup
    std::unordered_set<std::string> connected_node_ids;
    for (const auto& edge : edges_) {
        connected_node_ids.insert(edge.from);
        connected_node_ids.insert(edge.to);
    }
    
    // Run simulation iterations
    for (int iter = 0; iter < iterations; ++iter) {
        // Reset forces
        for (auto& node : nodes_) {
            node.vx = 0.0f;
            node.vy = 0.0f;
        }

        // Calculate repulsive forces only between connected nodes
        for (size_t i = 0; i < nodes_.size(); ++i) {
            // Skip isolated nodes in force calculations
            if (connected_node_ids.find(nodes_[i].id) == connected_node_ids.end()) continue;
            
            for (size_t j = i + 1; j < nodes_.size(); ++j) {
                // Skip isolated nodes in force calculations
                if (connected_node_ids.find(nodes_[j].id) == connected_node_ids.end()) continue;
                
                float dx = nodes_[i].x - nodes_[j].x;
                float dy = nodes_[i].y - nodes_[j].y;
                float dist_sq = dx * dx + dy * dy;

                // Avoid division by zero
                if (dist_sq < 0.01f) {
                    dist_sq = 0.01f;
                    dx = (std::rand() / static_cast<float>(RAND_MAX)) * 0.1f - 0.05f;
                    dy = (std::rand() / static_cast<float>(RAND_MAX)) * 0.1f - 0.05f;
                }

                float dist = std::sqrt(dist_sq);
                float repulsion = c_repulsion / dist;

                // Apply repulsive force
                nodes_[i].vx += (dx / dist) * repulsion;
                nodes_[i].vy += (dy / dist) * repulsion;
                nodes_[j].vx -= (dx / dist) * repulsion;
                nodes_[j].vy -= (dy / dist) * repulsion;
            }
        }

        // Calculate attractive forces along edges
        for (const auto& edge : edges_) {
            auto it_from = node_index.find(edge.from);
            auto it_to = node_index.find(edge.to);

            if (it_from != node_index.end() && it_to != node_index.end()) {
                size_t idx_from = it_from->second;
                size_t idx_to = it_to->second;

                float dx = nodes_[idx_from].x - nodes_[idx_to].x;
                float dy = nodes_[idx_from].y - nodes_[idx_to].y;
                float dist = std::sqrt(dx * dx + dy * dy);

                if (dist > 0.01f) {
                    float attraction = (dist * dist) / c_attraction;

                    // Apply attractive force
                    nodes_[idx_from].vx -= (dx / dist) * attraction;
                    nodes_[idx_from].vy -= (dy / dist) * attraction;
                    nodes_[idx_to].vx += (dx / dist) * attraction;
                    nodes_[idx_to].vy += (dy / dist) * attraction;
                }
            }
        }

        // Update positions with temperature-based displacement limiting (only for connected nodes)
        for (auto& node : nodes_) {
            // Skip isolated nodes - they stay in their initial positions
            if (connected_node_ids.find(node.id) == connected_node_ids.end()) continue;
            
            float force_mag = std::sqrt(node.vx * node.vx + node.vy * node.vy);

            if (force_mag > 0.01f) {
                float displacement = std::min(force_mag, temperature);
                node.x += (node.vx / force_mag) * displacement;
                node.y += (node.vy / force_mag) * displacement;

                // Keep nodes within reasonable bounds
                node.x = std::max(50.0f, std::min(node.x, 1500.0f));
                node.y = std::max(50.0f, std::min(node.y, 1000.0f));
            }
        }

        // Cool down temperature
        temperature *= cooling;
        if (temperature < min_temp) {
            temperature = min_temp;
        }
    }
}

void KnowledgeGraphEditor::handle_node_selection(const GraphNode* node) {
    // Deselect all nodes
    for (auto& n : nodes_) {
        n.selected = false;
    }

    // Deselect edge
    selected_edge_ = nullptr;

    // Select clicked node
    auto it = std::find_if(nodes_.begin(), nodes_.end(),
                          [node](const GraphNode& n) { return n.id == node->id; });
    if (it != nodes_.end()) {
        it->selected = true;
        selected_node_ = &(*it);
    }
}

void KnowledgeGraphEditor::handle_node_drag(GraphNode* node, float dx, float dy) {
    node->x += dx / zoom_level_;
    node->y += dy / zoom_level_;
}

std::string KnowledgeGraphEditor::format_label(const std::string& abbreviated_iri) const {
    if (pref_show_namespace_prefix_) {
        // Show the full abbreviated IRI (e.g., "ex:Class")
        return abbreviated_iri;
    } else {
        // Remove namespace prefix, show only local name after '#' (e.g., "Class" from "http://example.org#Class")
        size_t hash_pos = abbreviated_iri.find('#');
        if (hash_pos != std::string::npos && hash_pos < abbreviated_iri.length() - 1) {
            return abbreviated_iri.substr(hash_pos + 1);
        }
        // Fallback to colon-based splitting if no hash found
        size_t colon_pos = abbreviated_iri.find_last_of(':');
        if (colon_pos != std::string::npos && colon_pos < abbreviated_iri.length() - 1) {
            return abbreviated_iri.substr(colon_pos + 1);
        }
        return abbreviated_iri;
    }
}

void KnowledgeGraphEditor::add_data_source(const std::string& filepath) {
    DataSource ds;
    ds.filepath = filepath;

    // Determine format from extension
    if (filepath.ends_with(".csv")) {
        ds.format = "csv";
    } else if (filepath.ends_with(".tsv") || filepath.ends_with(".tab")) {
        ds.format = "tsv";
    } else if (filepath.ends_with(".xlsx") || filepath.ends_with(".xls")) {
        ds.format = "excel";
    } else if (filepath.ends_with(".db") || filepath.ends_with(".sqlite") || filepath.ends_with(".sqlite3")) {
        ds.format = "sqlite";
    } else {
        ds.format = "unknown";
    }

    // Load metadata without reading entire file
    load_data_source_metadata(ds);

    data_sources_.push_back(ds);
}

void KnowledgeGraphEditor::load_data_source_metadata(DataSource& ds) {
    ds.metadata_loaded = false;
    ds.error_message.clear();

    try {
        if (ds.format == "csv" || ds.format == "tsv") {
            load_csv_metadata(ds);
        } else if (ds.format == "excel") {
            load_excel_metadata(ds);
        } else if (ds.format == "sqlite") {
            load_sql_metadata(ds);
        } else {
            ds.error_message = "Unsupported file format";
        }
    } catch (const std::exception& e) {
        ds.error_message = std::string("Error loading metadata: ") + e.what();
        std::cerr << "Failed to load metadata for " << ds.filepath << ": " << e.what() << std::endl;
    }
}

void KnowledgeGraphEditor::load_csv_metadata(DataSource& ds) {
    std::ifstream file(ds.filepath);
    if (!file.is_open()) {
        throw std::runtime_error("Could not open file");
    }

    char delimiter = (ds.format == "tsv") ? '\t' : ',';
    std::string line;
    size_t line_count = 0;
    const size_t preview_count = 5; // Number of preview rows to read

    // Helper function to parse CSV line (same logic as CSVParser)
    auto parse_line = [delimiter](const std::string& line) -> std::vector<std::string> {
        std::vector<std::string> result;
        std::string current_field;
        bool in_quotes = false;

        for (size_t i = 0; i < line.length(); ++i) {
            char c = line[i];

            if (c == '"') {
                if (in_quotes && i + 1 < line.length() && line[i + 1] == '"') {
                    current_field += '"';
                    ++i;
                } else {
                    in_quotes = !in_quotes;
                }
            } else if (c == delimiter && !in_quotes) {
                result.push_back(current_field);
                current_field.clear();
            } else {
                current_field += c;
            }
        }
        result.push_back(current_field);
        return result;
    };

    // Read header
    if (std::getline(file, line)) {
        ds.column_names = parse_line(line);
        line_count++;
    }

    // Read preview rows
    while (std::getline(file, line) && ds.preview_rows.size() < preview_count) {
        auto row = parse_line(line);
        if (!row.empty()) {
            ds.preview_rows.push_back(row);
        }
        line_count++;
    }

    // Estimate total row count by reading rest of file in chunks
    // This is faster than reading line by line
    const size_t chunk_size = 64 * 1024; // 64KB chunks
    std::vector<char> buffer(chunk_size);

    while (file.read(buffer.data(), chunk_size) || file.gcount() > 0) {
        size_t bytes_read = file.gcount();
        line_count += std::count(buffer.data(), buffer.data() + bytes_read, '\n');
    }

    ds.estimated_row_count = line_count - 1; // Subtract header
    ds.metadata_loaded = true;

    file.close();
}

void KnowledgeGraphEditor::load_excel_metadata(DataSource& ds) {
    // For Excel support, we would need a library like libxlsxwriter or xlsxio
    // For now, set an error message indicating this needs implementation
    ds.error_message = "Excel support requires additional libraries (not yet implemented)";
    ds.metadata_loaded = false;

    // TODO: Implement Excel metadata reading using a library
    // Would extract: sheet names, column names per sheet, row counts
}

void KnowledgeGraphEditor::load_sql_metadata(DataSource& ds) {
    // For SQL support, we would need database libraries (SQLite, libpq, MySQL connector)
    // For now, set an error message indicating this needs implementation
    ds.error_message = "SQL database support requires additional libraries (not yet implemented)";
    ds.metadata_loaded = false;

    // TODO: Implement SQL metadata reading
    // For SQLite: use sqlite3 library to query schema
    // For PostgreSQL: use libpq
    // For MySQL: use MySQL Connector/C++
}

void KnowledgeGraphEditor::map_data_source_to_class(const std::string& source_id,
                                                    const std::string& class_iri) {
    // TODO: Implement data source to class mapping
}

void KnowledgeGraphEditor::render_database_config_dialog() {
    if (show_database_config_dialog_) {
        ImGui::OpenPopup("Database Configuration");
        show_database_config_dialog_ = false;
    }

    ImGui::SetNextWindowSize(ImVec2(600, 500), ImGuiCond_FirstUseEver);
    if (ImGui::BeginPopupModal("Database Configuration", nullptr, ImGuiWindowFlags_AlwaysAutoResize)) {
        ImGui::Text("Configure Database Connection");
        ImGui::Separator();

        // Database type selection
        ImGui::Text("Database Type:");
        ImGui::SameLine();

        const char* db_types[] = { "MySQL", "PostgreSQL", "SQL Server" };
        const char* db_type_values[] = { "mysql", "postgres", "sqlserver" };
        int current_type = 0;
        if (db_type_selection_ == "postgres") current_type = 1;
        else if (db_type_selection_ == "sqlserver") current_type = 2;

        if (ImGui::Combo("##DBType", &current_type, db_types, IM_ARRAYSIZE(db_types))) {
            db_type_selection_ = db_type_values[current_type];
            temp_database_config_.format = db_type_selection_;

            // Update default port when type changes
            if (temp_database_config_.db_config.port == get_default_port("mysql") ||
                temp_database_config_.db_config.port == get_default_port("postgres") ||
                temp_database_config_.db_config.port == get_default_port("sqlserver")) {
                temp_database_config_.db_config.port = get_default_port(db_type_selection_);
            }
        }

        ImGui::Separator();

        // Connection method tabs
        if (ImGui::BeginTabBar("ConnectionTabs")) {
            if (ImGui::BeginTabItem("Standard Connection")) {
                ImGui::Spacing();

                // Host
                ImGui::Text("Host:");
                ImGui::SameLine(150);
                char host_buf[256];
                strncpy(host_buf, temp_database_config_.db_config.host.c_str(), sizeof(host_buf) - 1);
                host_buf[sizeof(host_buf) - 1] = '\0';
                if (ImGui::InputText("##Host", host_buf, sizeof(host_buf))) {
                    temp_database_config_.db_config.host = host_buf;
                }

                // Port
                ImGui::Text("Port:");
                ImGui::SameLine(150);
                int port = temp_database_config_.db_config.port;
                if (ImGui::InputInt("##Port", &port)) {
                    temp_database_config_.db_config.port = port;
                }
                ImGui::SameLine();
                ImGui::TextDisabled("(?)");
                if (ImGui::IsItemHovered()) {
                    ImGui::SetTooltip("Default ports:\nMySQL: 3306\nPostgreSQL: 5432\nSQL Server: 1433");
                }

                // Database name
                ImGui::Text("Database:");
                ImGui::SameLine(150);
                char db_buf[256];
                strncpy(db_buf, temp_database_config_.db_config.database.c_str(), sizeof(db_buf) - 1);
                db_buf[sizeof(db_buf) - 1] = '\0';
                if (ImGui::InputText("##Database", db_buf, sizeof(db_buf))) {
                    temp_database_config_.db_config.database = db_buf;
                }

                // Username
                ImGui::Text("Username:");
                ImGui::SameLine(150);
                char user_buf[256];
                strncpy(user_buf, temp_database_config_.db_config.username.c_str(), sizeof(user_buf) - 1);
                user_buf[sizeof(user_buf) - 1] = '\0';
                if (ImGui::InputText("##Username", user_buf, sizeof(user_buf))) {
                    temp_database_config_.db_config.username = user_buf;
                }

                // Password
                ImGui::Text("Password:");
                ImGui::SameLine(150);
                char pass_buf[256];
                strncpy(pass_buf, temp_database_config_.db_config.password.c_str(), sizeof(pass_buf) - 1);
                pass_buf[sizeof(pass_buf) - 1] = '\0';
                if (ImGui::InputText("##Password", pass_buf, sizeof(pass_buf), ImGuiInputTextFlags_Password)) {
                    temp_database_config_.db_config.password = pass_buf;
                }

                temp_database_config_.db_config.use_connection_string = false;

                ImGui::EndTabItem();
            }

            if (ImGui::BeginTabItem("Connection String")) {
                ImGui::Spacing();
                ImGui::Text("Enter a custom connection string:");
                ImGui::Spacing();

                char conn_str_buf[1024];
                strncpy(conn_str_buf, temp_database_config_.db_config.connection_string.c_str(), sizeof(conn_str_buf) - 1);
                conn_str_buf[sizeof(conn_str_buf) - 1] = '\0';
                if (ImGui::InputTextMultiline("##ConnectionString", conn_str_buf, sizeof(conn_str_buf), ImVec2(550, 100))) {
                    temp_database_config_.db_config.connection_string = conn_str_buf;
                }

                ImGui::Spacing();
                ImGui::TextWrapped("Example formats:");
                ImGui::Spacing();

                if (db_type_selection_ == "mysql") {
                    ImGui::TextWrapped("MySQL: Server=localhost;Database=mydb;Uid=user;Pwd=password;");
                } else if (db_type_selection_ == "postgres") {
                    ImGui::TextWrapped("PostgreSQL: Host=localhost;Database=mydb;Username=user;Password=password;Port=5432;");
                } else if (db_type_selection_ == "sqlserver") {
                    ImGui::TextWrapped("SQL Server: Server=localhost,1433;Database=mydb;User Id=user;Password=password;");
                }

                temp_database_config_.db_config.use_connection_string = true;

                ImGui::EndTabItem();
            }

            ImGui::EndTabBar();
        }

        ImGui::Separator();
        ImGui::Spacing();

        // Information box
        ImGui::PushStyleColor(ImGuiCol_ChildBg, ImVec4(0.15f, 0.15f, 0.2f, 1.0f));
        ImGui::BeginChild("InfoBox", ImVec2(550, 60), true);
        ImGui::TextColored(ImVec4(0.8f, 0.8f, 1.0f, 1.0f), "Note:");
        ImGui::TextWrapped("Connection will be tested when you click 'Connect'. Make sure the database server is accessible and credentials are correct.");
        ImGui::EndChild();
        ImGui::PopStyleColor();

        ImGui::Spacing();
        ImGui::Separator();

        // Buttons
        if (ImGui::Button("Test Connection", ImVec2(150, 0))) {
            // TODO: Implement connection testing
            std::cout << "Testing connection to " << db_type_selection_ << " database..." << std::endl;
            // For now, just show that the feature is planned
            ImGui::OpenPopup("ConnectionTest");
        }

        // Connection test popup
        if (ImGui::BeginPopupModal("ConnectionTest", nullptr, ImGuiWindowFlags_AlwaysAutoResize)) {
            ImGui::Text("Connection testing is not yet implemented.");
            ImGui::Separator();
            ImGui::Text("This will be available when database libraries are integrated:");
            ImGui::BulletText("MySQL: libmysqlclient or MySQL Connector/C++");
            ImGui::BulletText("PostgreSQL: libpq");
            ImGui::BulletText("SQL Server: ODBC or FreeTDS");
            ImGui::Separator();
            if (ImGui::Button("OK", ImVec2(120, 0))) {
                ImGui::CloseCurrentPopup();
            }
            ImGui::EndPopup();
        }

        ImGui::SameLine();
        if (ImGui::Button("Connect", ImVec2(150, 0))) {
            // Validate input
            bool valid = false;
            if (temp_database_config_.db_config.use_connection_string) {
                valid = !temp_database_config_.db_config.connection_string.empty();
            } else {
                valid = !temp_database_config_.db_config.host.empty() &&
                       !temp_database_config_.db_config.database.empty() &&
                       !temp_database_config_.db_config.username.empty() &&
                       temp_database_config_.db_config.port > 0;
            }

            if (valid) {
                // Add the database configuration to data sources
                temp_database_config_.metadata_loaded = false;
                temp_database_config_.error_message = "Database support requires additional libraries (not yet implemented)";

                // Generate a display name for the database
                if (temp_database_config_.db_config.use_connection_string) {
                    temp_database_config_.filepath = db_type_selection_ + " (custom connection)";
                } else {
                    temp_database_config_.filepath = db_type_selection_ + "://" +
                        temp_database_config_.db_config.host + ":" +
                        std::to_string(temp_database_config_.db_config.port) + "/" +
                        temp_database_config_.db_config.database;
                }

                data_sources_.push_back(temp_database_config_);

                std::cout << "Added database configuration: " << temp_database_config_.filepath << std::endl;
                ImGui::CloseCurrentPopup();
            } else {
                ImGui::OpenPopup("ValidationError");
            }
        }

        // Validation error popup
        if (ImGui::BeginPopupModal("ValidationError", nullptr, ImGuiWindowFlags_AlwaysAutoResize)) {
            ImGui::Text("Please fill in all required fields:");
            if (temp_database_config_.db_config.use_connection_string) {
                ImGui::BulletText("Connection String");
            } else {
                ImGui::BulletText("Host");
                ImGui::BulletText("Port (must be > 0)");
                ImGui::BulletText("Database");
                ImGui::BulletText("Username");
            }
            ImGui::Separator();
            if (ImGui::Button("OK", ImVec2(120, 0))) {
                ImGui::CloseCurrentPopup();
            }
            ImGui::EndPopup();
        }

        ImGui::SameLine();
        if (ImGui::Button("Cancel", ImVec2(150, 0))) {
            ImGui::CloseCurrentPopup();
        }

        ImGui::EndPopup();
    }
}

int KnowledgeGraphEditor::get_default_port(const std::string& db_type) const {
    if (db_type == "mysql") {
        return 3306;
    } else if (db_type == "postgres") {
        return 5432;
    } else if (db_type == "sqlserver") {
        return 1433;
    }
    return 0;
}

} // namespace gui
} // namespace ista
