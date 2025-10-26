cmake_minimum_required (VERSION 3.15...3.19)
set (CMAKE_CXX_STANDARD 20)

project(ISTA CXX)

# Option to build Python bindings
option(BUILD_PYTHON_BINDINGS "Build Python bindings using pybind11" ON)

add_subdirectory(lib)
add_subdirectory(src)

# Add Python bindings if requested
if(BUILD_PYTHON_BINDINGS)
    add_subdirectory(lib/python)
endif()
