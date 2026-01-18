# Collect all C++ source files recursively, but exclude python bindings
file(GLOB_RECURSE lib_sources ${CMAKE_CURRENT_SOURCE_DIR}/*.cpp)

# Exclude Python bindings from the main library
list(FILTER lib_sources EXCLUDE REGEX ".*python/.*")

# Exclude database readers by default (conditionally added below)
list(FILTER lib_sources EXCLUDE REGEX ".*sqlite_reader\\.cpp$")
list(FILTER lib_sources EXCLUDE REGEX ".*mysql_reader\\.cpp$")
list(FILTER lib_sources EXCLUDE REGEX ".*postgres_reader\\.cpp$")

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

# =============================================================================
# Optional Database Support
# =============================================================================

# Track extra libraries to link
set(EXTRA_LIBS "")
set(EXTRA_INCLUDE_DIRS "")

# SQLite support
find_package(SQLite3 QUIET)
if(SQLite3_FOUND)
    message(STATUS "SQLite3 found - enabling SQLite data source support")
    target_compile_definitions(libista PUBLIC ISTA_HAS_SQLITE)
    target_sources(libista PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/owl2/loader/sqlite_reader.cpp)
    list(APPEND EXTRA_LIBS SQLite::SQLite3)
else()
    message(STATUS "SQLite3 not found - SQLite data source support disabled")
endif()

# MySQL support
# Try to find MySQL using different methods
find_package(MySQL QUIET)
if(NOT MySQL_FOUND)
    # Try PkgConfig as fallback
    find_package(PkgConfig QUIET)
    if(PkgConfig_FOUND)
        pkg_check_modules(MYSQL QUIET mysqlclient)
    endif()
endif()

if(MySQL_FOUND OR MYSQL_FOUND)
    message(STATUS "MySQL found - enabling MySQL data source support")
    target_compile_definitions(libista PUBLIC ISTA_HAS_MYSQL)
    target_sources(libista PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/owl2/loader/mysql_reader.cpp)
    if(MySQL_FOUND)
        list(APPEND EXTRA_LIBS ${MYSQL_LIBRARIES})
        list(APPEND EXTRA_INCLUDE_DIRS ${MYSQL_INCLUDE_DIRS})
    else()
        list(APPEND EXTRA_LIBS ${MYSQL_LIBRARIES})
        list(APPEND EXTRA_INCLUDE_DIRS ${MYSQL_INCLUDE_DIRS})
    endif()
else()
    message(STATUS "MySQL not found - MySQL data source support disabled")
endif()

# PostgreSQL support
find_package(PostgreSQL QUIET)
if(PostgreSQL_FOUND)
    message(STATUS "PostgreSQL found - enabling PostgreSQL data source support")
    target_compile_definitions(libista PUBLIC ISTA_HAS_POSTGRES)
    target_sources(libista PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/owl2/loader/postgres_reader.cpp)
    list(APPEND EXTRA_LIBS PostgreSQL::PostgreSQL)
else()
    message(STATUS "PostgreSQL not found - PostgreSQL data source support disabled")
endif()

# Add extra include directories
if(EXTRA_INCLUDE_DIRS)
    target_include_directories(libista PRIVATE ${EXTRA_INCLUDE_DIRS})
endif()

# Link extra libraries
if(EXTRA_LIBS)
    target_link_libraries(libista PUBLIC ${EXTRA_LIBS})
endif()

# Print summary
message(STATUS "Database support summary:")
message(STATUS "  SQLite:     ${SQLite3_FOUND}")
message(STATUS "  MySQL:      ${MySQL_FOUND} OR ${MYSQL_FOUND}")
message(STATUS "  PostgreSQL: ${PostgreSQL_FOUND}")
