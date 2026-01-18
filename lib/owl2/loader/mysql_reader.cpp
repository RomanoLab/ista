#include "mysql_reader.hpp"
#include <mysql/mysql.h>

namespace ista {
namespace owl2 {
namespace loader {

MySqlReader::MySqlReader(const DataSourceDef& source)
    : DatabaseReader(source) {
    if (source.type != "mysql") {
        throw DataLoaderException("MySqlReader requires source type 'mysql', got '" + 
                                  source.type + "'");
    }
    if (!source.connection.has_value()) {
        throw DataLoaderException("MySQL source '" + source.name + 
                                  "' requires 'connection' configuration");
    }
}

MySqlReader::~MySqlReader() {
    close();
}

bool MySqlReader::connect() {
    // Initialize MySQL connection handle
    conn_ = mysql_init(nullptr);
    if (!conn_) {
        throw DataLoaderException("Failed to initialize MySQL connection");
    }
    
    const auto& c = source_.connection.value();
    
    // Use connection string if provided, otherwise use individual parameters
    if (c.use_connection_string && !c.connection_string.empty()) {
        // MySQL doesn't support connection strings directly in the C API,
        // but we can parse common formats or use mysql_options
        throw DataLoaderException("MySQL connection strings are not yet supported. "
                                  "Please use individual connection parameters.");
    }
    
    // Determine port (0 means use default)
    unsigned int port = c.port > 0 ? static_cast<unsigned int>(c.port) : 0;
    
    // Connect to the database
    MYSQL* result = mysql_real_connect(
        conn_,
        c.host.c_str(),
        c.username.c_str(),
        c.password.c_str(),
        c.database.c_str(),
        port,
        nullptr,  // unix_socket
        0         // client_flag
    );
    
    if (!result) {
        std::string error = mysql_error(conn_);
        mysql_close(conn_);
        conn_ = nullptr;
        throw DataLoaderException("Failed to connect to MySQL database at " + 
                                  connection_description() + ": " + error);
    }
    
    // Set UTF-8 encoding
    mysql_set_character_set(conn_, "utf8mb4");
    
    return true;
}

void MySqlReader::disconnect() {
    free_result();
    if (conn_) {
        mysql_close(conn_);
        conn_ = nullptr;
    }
}

bool MySqlReader::execute_query() {
    std::string query = build_query();
    
    if (mysql_query(conn_, query.c_str()) != 0) {
        std::string error = mysql_error(conn_);
        throw DataLoaderException("Failed to execute MySQL query: " + error + 
                                  "\nQuery: " + query);
    }
    
    // Store result (loads all rows into memory)
    // For very large result sets, mysql_use_result() could be used instead,
    // but that has limitations (must fetch all rows before another query)
    result_ = mysql_store_result(conn_);
    if (!result_) {
        // Check if query was supposed to return data
        if (mysql_field_count(conn_) > 0) {
            std::string error = mysql_error(conn_);
            throw DataLoaderException("Failed to store MySQL result: " + error);
        }
        // Query was INSERT/UPDATE/DELETE with no result set
        throw DataLoaderException("MySQL query did not return a result set. "
                                  "Data loading requires SELECT queries.");
    }
    
    num_fields_ = mysql_num_fields(result_);
    
    // Fetch first row
    fetch_next_row();
    
    return true;
}

std::vector<std::string> MySqlReader::fetch_column_names() {
    std::vector<std::string> names;
    names.reserve(num_fields_);
    
    MYSQL_FIELD* fields = mysql_fetch_fields(result_);
    for (unsigned int i = 0; i < num_fields_; ++i) {
        names.push_back(fields[i].name ? fields[i].name : "");
    }
    
    return names;
}

size_t MySqlReader::fetch_row_count() {
    // mysql_store_result loads all rows, so we have an accurate count
    return static_cast<size_t>(mysql_num_rows(result_));
}

bool MySqlReader::has_next() const {
    return has_row_;
}

DataRow MySqlReader::next() {
    if (!has_row_) {
        throw DataLoaderException("No more rows available in MySQL result set");
    }
    
    DataRow row;
    
    // Read current row values
    for (unsigned int i = 0; i < num_fields_; ++i) {
        if (current_row_[i]) {
            // Use length to properly handle binary data and embedded nulls
            row[headers_[i]] = std::string(current_row_[i], current_lengths_[i]);
        } else {
            row[headers_[i]] = "";
        }
    }
    
    // Advance to next row
    fetch_next_row();
    
    return row;
}

void MySqlReader::reset() {
    if (result_) {
        // Seek back to beginning of result set
        mysql_data_seek(result_, 0);
        fetch_next_row();
    }
}

void MySqlReader::free_result() {
    if (result_) {
        mysql_free_result(result_);
        result_ = nullptr;
    }
    current_row_ = nullptr;
    current_lengths_ = nullptr;
    has_row_ = false;
    num_fields_ = 0;
}

void MySqlReader::fetch_next_row() {
    current_row_ = mysql_fetch_row(result_);
    if (current_row_) {
        current_lengths_ = mysql_fetch_lengths(result_);
        has_row_ = true;
    } else {
        current_lengths_ = nullptr;
        has_row_ = false;
    }
}

} // namespace loader
} // namespace owl2
} // namespace ista
