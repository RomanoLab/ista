cmake_minimum_required(VERSION 3.15)

# Find OpenGL - handle macOS framework location
if(APPLE)
    find_library(OPENGL_LIBRARY OpenGL)
    if(NOT OPENGL_LIBRARY)
        message(FATAL_ERROR "OpenGL framework not found on macOS")
    endif()
    set(OPENGL_LIBRARIES ${OPENGL_LIBRARY})
    add_library(OpenGL::GL INTERFACE IMPORTED)
    set_target_properties(OpenGL::GL PROPERTIES
        INTERFACE_LINK_LIBRARIES "${OPENGL_LIBRARY}"
    )
else()
    find_package(OpenGL REQUIRED)
endif()

# Find or fetch GLFW
find_package(glfw3 QUIET)
if(NOT glfw3_FOUND)
    message(STATUS "GLFW not found, will use bundled version from external/glfw")
    set(GLFW_DIR ${CMAKE_CURRENT_SOURCE_DIR}/../external/glfw)
    if(EXISTS ${GLFW_DIR}/CMakeLists.txt)
        set(GLFW_BUILD_DOCS OFF CACHE BOOL "" FORCE)
        set(GLFW_BUILD_TESTS OFF CACHE BOOL "" FORCE)
        set(GLFW_BUILD_EXAMPLES OFF CACHE BOOL "" FORCE)
        add_subdirectory(${GLFW_DIR} ${CMAKE_BINARY_DIR}/glfw)
    else()
        message(WARNING "GLFW not found. Please install GLFW or add it to external/glfw")
    endif()
endif()

# Native File Dialog sources
set(NFD_DIR ${CMAKE_CURRENT_SOURCE_DIR}/../external/nfd)
if(EXISTS ${NFD_DIR}/src/include/nfd.h)
    if(APPLE)
        set(NFD_SOURCES ${NFD_DIR}/src/nfd_cocoa.m)
    elseif(WIN32)
        set(NFD_SOURCES ${NFD_DIR}/src/nfd_win.cpp)
    elseif(UNIX)
        # Linux - try GTK3 first, then portal
        set(NFD_SOURCES ${NFD_DIR}/src/nfd_gtk.cpp)
    endif()
else()
    message(WARNING "Native File Dialog not found in external/nfd")
    set(NFD_SOURCES "")
endif()

# Dear ImGui sources
set(IMGUI_DIR ${CMAKE_CURRENT_SOURCE_DIR}/../external/imgui)
if(EXISTS ${IMGUI_DIR}/imgui.cpp)
    set(IMGUI_SOURCES
        ${IMGUI_DIR}/imgui.cpp
        ${IMGUI_DIR}/imgui_demo.cpp
        ${IMGUI_DIR}/imgui_draw.cpp
        ${IMGUI_DIR}/imgui_tables.cpp
        ${IMGUI_DIR}/imgui_widgets.cpp
        ${IMGUI_DIR}/backends/imgui_impl_glfw.cpp
        ${IMGUI_DIR}/backends/imgui_impl_opengl3.cpp
    )
else()
    message(WARNING "Dear ImGui not found in external/imgui. Please download it from https://github.com/ocornut/imgui")
    set(IMGUI_SOURCES "")
endif()

# Collect GUI source files
set(GUI_SOURCES
    src/main.cpp
    src/kg_editor.cpp
)

# Create executable
if(IMGUI_SOURCES)
    add_executable(ista_gui ${GUI_SOURCES} ${IMGUI_SOURCES} ${NFD_SOURCES})

    # Set language for NFD Cocoa file to Objective-C
    if(APPLE AND NFD_SOURCES)
        set_source_files_properties(${NFD_SOURCES} PROPERTIES
            LANGUAGE OBJC
        )
    endif()

    # Include directories
    target_include_directories(ista_gui PRIVATE
        ${CMAKE_CURRENT_SOURCE_DIR}/include
        ${IMGUI_DIR}
        ${IMGUI_DIR}/backends
        ${CMAKE_CURRENT_SOURCE_DIR}/../lib
        ${NFD_DIR}/src/include
    )

    # Link libraries
    target_link_libraries(ista_gui PRIVATE
        libista
        glfw
        OpenGL::GL
    )

    # Platform-specific settings
    if(APPLE)
        target_link_libraries(ista_gui PRIVATE
            "-framework Cocoa"
            "-framework IOKit"
            "-framework CoreVideo"
            "-framework UniformTypeIdentifiers"
            "-framework AppKit"
        )
    elseif(UNIX)
        target_link_libraries(ista_gui PRIVATE
            ${CMAKE_DL_LIBS}
            pthread
        )
    endif()

    # Set C++ standard
    set_target_properties(ista_gui PROPERTIES
        CXX_STANDARD 20
        CXX_STANDARD_REQUIRED ON
    )

    # Install target
    install(TARGETS ista_gui DESTINATION bin)

    message(STATUS "ISTA GUI will be built")
else()
    message(STATUS "Skipping ISTA GUI build - Dear ImGui not found")
endif()
