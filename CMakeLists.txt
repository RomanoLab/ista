cmake_minimum_required (VERSION 3.15...3.19)
set (CMAKE_CXX_STANDARD 20)

project(ista)

file(GLOB_RECURSE lib_sources ${CMAKE_CURRENT_SOURCE_DIR}/lib/*.cpp)
message(STATUS "Library sources: '${lib_sources}")

add_library(libista SHARED ${lib_sources})