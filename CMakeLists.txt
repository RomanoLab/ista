cmake_minimum_required (VERSION 3.15...3.19)
set (CMAKE_CXX_STANDARD 20)

# Enable C and Objective-C for GUI (needed for Native File Dialog on macOS)
if(APPLE)
    project(ISTA CXX C OBJC)
else()
    project(ISTA CXX C)
endif()

# Option to build Python bindings
option(BUILD_PYTHON_BINDINGS "Build Python bindings using pybind11" ON)

# Option to build GUI application
option(BUILD_GUI "Build GUI application for knowledge graph editing" ON)

add_subdirectory(lib)
add_subdirectory(src)

# Add Python bindings if requested
if(BUILD_PYTHON_BINDINGS)
    add_subdirectory(lib/python)
endif()

# Add GUI application if requested
if(BUILD_GUI)
    add_subdirectory(gui)
endif()
