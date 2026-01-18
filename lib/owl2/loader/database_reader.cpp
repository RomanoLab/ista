#include "database_reader.hpp"
#include <sstream>

namespace ista {
namespace owl2 {
namespace loader {

DatabaseReader::DatabaseReader(const DataSourceDef& source)
    : source_(source) {
}

bool DatabaseReader::open() {
    // Connect to database
    if (!connect()) {
        return false;
    }
    is_connected_ = true;
    
    // Execute the query
    if (!execute_query()) {
        disconnect();
        is_connected_ = false;
        return false;
    }
    query_executed_ = true;
    
    // Fetch metadata
    headers_ = fetch_column_names();
    total_rows_ = fetch_row_count();
    
    return true;
}

void DatabaseReader::close() {
    if (is_connected_) {
        disconnect();
        is_connected_ = false;
    }
    query_executed_ = false;
    headers_.clear();
    total_rows_ = 0;
}

std::string DatabaseReader::build_query() const {
    // If a custom query is provided, use it directly
    if (source_.query.has_value() && !source_.query->empty()) {
        return source_.query.value();
    }
    
    // Otherwise, build a simple SELECT * FROM table query
    if (source_.table.has_value() && !source_.table->empty()) {
        return "SELECT * FROM " + source_.table.value();
    }
    
    throw DataLoaderException("Database source '" + source_.name + 
                              "' must specify either 'table' or 'query'");
}

std::string DatabaseReader::connection_description() const {
    std::ostringstream ss;
    ss << source_.type << "://";
    
    if (source_.connection.has_value()) {
        const auto& conn = source_.connection.value();
        if (!conn.username.empty()) {
            ss << conn.username << "@";
        }
        ss << conn.host;
        if (conn.port > 0) {
            ss << ":" << conn.port;
        }
        ss << "/" << conn.database;
    } else if (!source_.path.empty()) {
        // For file-based databases like SQLite
        ss << source_.path;
    }
    
    return ss.str();
}

} // namespace loader
} // namespace owl2
} // namespace ista
