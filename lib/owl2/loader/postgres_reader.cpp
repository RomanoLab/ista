#include "postgres_reader.hpp"
#include <libpq-fe.h>
#include <sstream>

namespace ista {
namespace owl2 {
namespace loader {

PostgresReader::PostgresReader(const DataSourceDef& source)
    : DatabaseReader(source) {
    if (source.type != "postgres" && source.type != "postgresql") {
        throw DataLoaderException("PostgresReader requires source type 'postgres' or 'postgresql', got '" + 
                                  source.type + "'");
    }
    if (!source.connection.has_value()) {
        throw DataLoaderException("PostgreSQL source '" + source.name + 
                                  "' requires 'connection' configuration");
    }
}

PostgresReader::~PostgresReader() {
    close();
}

std::string PostgresReader::build_connection_string() const {
    const auto& c = source_.connection.value();
    
    // If a connection string is provided, use it directly
    if (c.use_connection_string && !c.connection_string.empty()) {
        return c.connection_string;
    }
    
    // Build connection string from individual parameters
    std::ostringstream ss;
    
    if (!c.host.empty()) {
        ss << "host=" << c.host << " ";
    }
    if (c.port > 0) {
        ss << "port=" << c.port << " ";
    }
    if (!c.database.empty()) {
        ss << "dbname=" << c.database << " ";
    }
    if (!c.username.empty()) {
        ss << "user=" << c.username << " ";
    }
    if (!c.password.empty()) {
        ss << "password=" << c.password << " ";
    }
    
    return ss.str();
}

bool PostgresReader::connect() {
    std::string conn_string = build_connection_string();
    
    conn_ = PQconnectdb(conn_string.c_str());
    
    if (PQstatus(conn_) != CONNECTION_OK) {
        std::string error = PQerrorMessage(conn_);
        PQfinish(conn_);
        conn_ = nullptr;
        throw DataLoaderException("Failed to connect to PostgreSQL database at " + 
                                  connection_description() + ": " + error);
    }
    
    // Set UTF-8 encoding
    PQsetClientEncoding(conn_, "UTF8");
    
    return true;
}

void PostgresReader::disconnect() {
    clear_result();
    if (conn_) {
        PQfinish(conn_);
        conn_ = nullptr;
    }
}

bool PostgresReader::execute_query() {
    std::string query = build_query();
    
    result_ = PQexec(conn_, query.c_str());
    
    ExecStatusType status = PQresultStatus(result_);
    if (status != PGRES_TUPLES_OK) {
        std::string error = PQerrorMessage(conn_);
        clear_result();
        
        if (status == PGRES_COMMAND_OK) {
            throw DataLoaderException("PostgreSQL query did not return a result set. "
                                      "Data loading requires SELECT queries.");
        }
        throw DataLoaderException("Failed to execute PostgreSQL query: " + error + 
                                  "\nQuery: " + query);
    }
    
    num_fields_ = PQnfields(result_);
    num_rows_ = PQntuples(result_);
    current_row_ = 0;
    
    return true;
}

std::vector<std::string> PostgresReader::fetch_column_names() {
    std::vector<std::string> names;
    names.reserve(num_fields_);
    
    for (int i = 0; i < num_fields_; ++i) {
        char* name = PQfname(result_, i);
        names.push_back(name ? name : "");
    }
    
    return names;
}

size_t PostgresReader::fetch_row_count() {
    return static_cast<size_t>(num_rows_);
}

bool PostgresReader::has_next() const {
    return current_row_ < num_rows_;
}

DataRow PostgresReader::next() {
    if (current_row_ >= num_rows_) {
        throw DataLoaderException("No more rows available in PostgreSQL result set");
    }
    
    DataRow row;
    
    // Read current row values
    for (int i = 0; i < num_fields_; ++i) {
        if (PQgetisnull(result_, current_row_, i)) {
            row[headers_[i]] = "";
        } else {
            char* value = PQgetvalue(result_, current_row_, i);
            row[headers_[i]] = value ? value : "";
        }
    }
    
    // Advance to next row
    ++current_row_;
    
    return row;
}

void PostgresReader::reset() {
    current_row_ = 0;
}

void PostgresReader::clear_result() {
    if (result_) {
        PQclear(result_);
        result_ = nullptr;
    }
    num_fields_ = 0;
    num_rows_ = 0;
    current_row_ = 0;
}

} // namespace loader
} // namespace owl2
} // namespace ista
