# FindMySQL.cmake - Locate MySQL client library
#
# This module defines:
#   MySQL_FOUND        - TRUE if MySQL client library and headers are found
#   MYSQL_INCLUDE_DIRS - Include directories for MySQL headers
#   MYSQL_LIBRARIES    - Libraries to link against
#
# Searches the following locations:
#   - MYSQL_ROOT (CMake variable or environment variable)
#   - Standard Windows install paths (Program Files)
#   - Standard Unix paths (/usr, /usr/local)

# Candidate root directories
set(_mysql_search_dirs "")

if(MYSQL_ROOT)
    list(APPEND _mysql_search_dirs "${MYSQL_ROOT}")
endif()
if(DEFINED ENV{MYSQL_ROOT})
    list(APPEND _mysql_search_dirs "$ENV{MYSQL_ROOT}")
endif()
if(DEFINED ENV{MYSQL_DIR})
    list(APPEND _mysql_search_dirs "$ENV{MYSQL_DIR}")
endif()

if(WIN32)
    # Standard Windows install locations
    file(GLOB _mysql_win_dirs
        "C:/Program Files/MySQL/MySQL Server*"
        "C:/Program Files (x86)/MySQL/MySQL Server*"
    )
    list(APPEND _mysql_search_dirs ${_mysql_win_dirs})
endif()

# Find the header
find_path(MYSQL_INCLUDE_DIR
    NAMES mysql.h
    HINTS ${_mysql_search_dirs}
    PATH_SUFFIXES include
)

# Find the library
find_library(MYSQL_LIBRARY
    NAMES mysqlclient libmysql mysql
    HINTS ${_mysql_search_dirs}
    PATH_SUFFIXES lib lib64
)

include(FindPackageHandleStandardArgs)
find_package_handle_standard_args(MySQL
    REQUIRED_VARS MYSQL_LIBRARY MYSQL_INCLUDE_DIR
)

if(MySQL_FOUND)
    # Set the parent of include dir so #include <mysql/mysql.h> works,
    # but also provide the direct dir for #include <mysql.h>
    set(MYSQL_INCLUDE_DIRS "${MYSQL_INCLUDE_DIR}")
    set(MYSQL_LIBRARIES "${MYSQL_LIBRARY}")
    mark_as_advanced(MYSQL_INCLUDE_DIR MYSQL_LIBRARY)

    # On Windows, ensure the DLL can be found at runtime
    if(WIN32)
        get_filename_component(_mysql_lib_dir "${MYSQL_LIBRARY}" DIRECTORY)
        get_filename_component(_mysql_root "${_mysql_lib_dir}" DIRECTORY)
        if(EXISTS "${_mysql_root}/lib/libmysql.dll")
            set(MYSQL_DLL_DIR "${_mysql_root}/lib" CACHE PATH "Directory containing libmysql.dll")
        endif()
    endif()
endif()
