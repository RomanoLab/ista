cmake_minimum_required(VERSION 3.15...3.27)

project(libista_python_bindings LANGUAGES CXX)

# Set C++20 standard
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# ============================================================================
# Find Python and pybind11
# ============================================================================

# Find Python interpreter and development components
find_package(Python COMPONENTS Interpreter Development REQUIRED)

# Try to find pybind11 via find_package first
# If not found, try to use pybind11 as a subdirectory
find_package(pybind11 CONFIG QUIET)

if(NOT pybind11_FOUND)
    # Check if pybind11 is available as a git submodule or subdirectory
    if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/../../external/pybind11/CMakeLists.txt")
        message(STATUS "Using pybind11 from external/pybind11")
        add_subdirectory(${CMAKE_CURRENT_SOURCE_DIR}/../../external/pybind11 ${CMAKE_CURRENT_BINARY_DIR}/pybind11)
    elseif(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/pybind11/CMakeLists.txt")
        message(STATUS "Using pybind11 from lib/python/pybind11")
        add_subdirectory(pybind11)
    else()
        message(FATAL_ERROR
            "pybind11 not found!\n"
            "Please install pybind11 via one of these methods:\n"
            "  1. Install system-wide: pip install pybind11\n"
            "  2. Clone as submodule: git submodule add https://github.com/pybind/pybind11.git external/pybind11\n"
            "  3. Clone locally: git clone https://github.com/pybind/pybind11.git lib/python/pybind11"
        )
    endif()
endif()

# ============================================================================
# Create Python extension module
# ============================================================================

# Create the Python module using pybind11
pybind11_add_module(_libista_owl2 MODULE
    bindings_simple.cpp
)

# Link against the libista library
target_link_libraries(_libista_owl2 PRIVATE libista)

# Include directories
target_include_directories(_libista_owl2 PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/..
    ${CMAKE_CURRENT_SOURCE_DIR}/../owl2
)

# Set proper module properties
set_target_properties(_libista_owl2 PROPERTIES
    CXX_STANDARD 20
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
    CXX_VISIBILITY_PRESET hidden
    VISIBILITY_INLINES_HIDDEN ON
)

# Enable position independent code (required for shared libraries)
set_target_properties(_libista_owl2 PROPERTIES
    POSITION_INDEPENDENT_CODE ON
)

# ============================================================================
# Installation
# ============================================================================

# Install the Python module to the appropriate location
# This will install to site-packages or dist-packages
install(TARGETS _libista_owl2
    LIBRARY DESTINATION ${Python_SITEARCH}
    RUNTIME DESTINATION ${Python_SITEARCH}
)

# Optionally, you can also install a pure Python wrapper package
# that imports the C++ extension module
if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/__init__.py")
    install(FILES __init__.py
        DESTINATION ${Python_SITEARCH}/libista_owl2
    )
endif()

# ============================================================================
# Testing (optional)
# ============================================================================

# Enable testing if requested
option(BUILD_PYTHON_TESTS "Build Python binding tests" OFF)

if(BUILD_PYTHON_TESTS)
    enable_testing()

    # Add a test that imports the module
    add_test(
        NAME python_import_test
        COMMAND ${Python_EXECUTABLE} -c "import _libista_owl2; print('Successfully imported _libista_owl2')"
    )

    # Set the Python path to find the built module
    set_tests_properties(python_import_test PROPERTIES
        ENVIRONMENT "PYTHONPATH=$<TARGET_FILE_DIR:_libista_owl2>"
    )
endif()

# ============================================================================
# Print configuration summary
# ============================================================================

message(STATUS "========================================")
message(STATUS "libista Python Bindings Configuration")
message(STATUS "========================================")
message(STATUS "Python version: ${Python_VERSION}")
message(STATUS "Python executable: ${Python_EXECUTABLE}")
message(STATUS "Python include dirs: ${Python_INCLUDE_DIRS}")
message(STATUS "Python libraries: ${Python_LIBRARIES}")
message(STATUS "pybind11 version: ${pybind11_VERSION}")
message(STATUS "Install directory: ${Python_SITEARCH}")
message(STATUS "Build tests: ${BUILD_PYTHON_TESTS}")
message(STATUS "========================================")
