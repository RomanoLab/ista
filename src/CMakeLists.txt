file(GLOB SRC_FILES *.cpp)
add_executable(ista ${SRC_FILES})
target_link_libraries(ista libista)