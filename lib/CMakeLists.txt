# Collect all C++ source files recursively, but exclude python bindings
file(GLOB_RECURSE lib_sources ${CMAKE_CURRENT_SOURCE_DIR}/*.cpp)

# Exclude Python bindings from the main library
list(FILTER lib_sources EXCLUDE REGEX ".*python/.*")

message(STATUS "Library sources: ${lib_sources}")

# Add pugixml sources
set(PUGIXML_DIR ${CMAKE_CURRENT_SOURCE_DIR}/../external/pugixml)
if(EXISTS ${PUGIXML_DIR}/src/pugixml.cpp)
    list(APPEND lib_sources ${PUGIXML_DIR}/src/pugixml.cpp)
    message(STATUS "Added pugixml from: ${PUGIXML_DIR}")
else()
    message(WARNING "pugixml not found at ${PUGIXML_DIR} - RDF/XML parser will not work")
endif()

# Create the libista library
add_library(libista ${lib_sources})

# Make headers accessible to library consumers
target_include_directories(libista PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}
    ${PUGIXML_DIR}/src
)

# Set C++20 standard for the library
set_target_properties(libista PROPERTIES
    CXX_STANDARD 20
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)

# Set output name (removes duplicate 'lib' prefix on Unix)
set_target_properties(libista PROPERTIES OUTPUT_NAME ista)
