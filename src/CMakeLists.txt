file(GLOB SRC_FILES *.cpp)
message(STATUS "Executable sources: '${SRC_FILES}")
add_executable(ista ${SRC_FILES})
target_link_libraries(ista LINK_PUBLIC libista)