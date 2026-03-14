cmake_minimum_required (VERSION 3.15...3.19)
set (CMAKE_CXX_STANDARD 20)

# Add project-local CMake modules (e.g. FindMySQL)
list(APPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_SOURCE_DIR}/cmake")

# Read version from the single source-of-truth VERSION file
file(READ "${CMAKE_CURRENT_SOURCE_DIR}/VERSION" ISTA_VERSION)
string(STRIP "${ISTA_VERSION}" ISTA_VERSION)

# Enable C and Objective-C for GUI (needed for Native File Dialog on macOS)
if(APPLE)
    project(ISTA VERSION ${ISTA_VERSION} LANGUAGES CXX C OBJC)
else()
    project(ISTA VERSION ${ISTA_VERSION} LANGUAGES CXX C)
endif()

# Propagate individual version components for configure_file
set(ISTA_VERSION_MAJOR ${PROJECT_VERSION_MAJOR})
set(ISTA_VERSION_MINOR ${PROJECT_VERSION_MINOR})
set(ISTA_VERSION_PATCH ${PROJECT_VERSION_PATCH})

# Generate the C++ version header from the template
configure_file(
    "${CMAKE_CURRENT_SOURCE_DIR}/lib/owl2/core/version.hpp.in"
    "${CMAKE_CURRENT_BINARY_DIR}/generated/ista/version.hpp"
    @ONLY
)

# Make the generated header available to all targets
include_directories("${CMAKE_CURRENT_BINARY_DIR}/generated")

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
