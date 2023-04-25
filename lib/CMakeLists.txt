file(GLOB_RECURSE lib_sources ${CMAKE_CURRENT_SOURCE_DIR}/*.cpp)
message(STATUS "Library sources: '${lib_sources}")

add_library(libista ${lib_sources})