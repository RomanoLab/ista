#include "sqlite_reader.hpp"
#include <sqlite3.h>

namespace ista {
namespace owl2 {
namespace loader {

SqliteReader::SqliteReader(const DataSourceDef& source)
    : DatabaseReader(source) {
    if (source.type != "sqlite") {
        throw DataLoaderException("SqliteReader requires source type 'sqlite', got '" + 
                                  source.type + "'");
    }
    if (source.path.empty()) {
        throw DataLoaderException("SQLite source '" + source.name + 
                                  "' requires 'path' to database file");
    }
}

SqliteReader::~SqliteReader() {
    close();
}

bool SqliteReader::connect() {
    int rc = sqlite3_open(source_.path.c_str(), &db_);
    if (rc != SQLITE_OK) {
        std::string error = db_ ? sqlite3_errmsg(db_) : "Unable to allocate memory";
        if (db_) {
            sqlite3_close(db_);
            db_ = nullptr;
        }
        throw DataLoaderException("Failed to open SQLite database '" + source_.path + 
                                  "': " + error);
    }
    return true;
}

void SqliteReader::disconnect() {
    finalize_statement();
    if (db_) {
        sqlite3_close(db_);
        db_ = nullptr;
    }
}

bool SqliteReader::execute_query() {
    std::string query = build_query();
    
    int rc = sqlite3_prepare_v2(db_, query.c_str(), -1, &stmt_, nullptr);
    if (rc != SQLITE_OK) {
        std::string error = sqlite3_errmsg(db_);
        throw DataLoaderException("Failed to prepare SQLite query: " + error + 
                                  "\nQuery: " + query);
    }
    
    column_count_ = sqlite3_column_count(stmt_);
    
    // Step to first row to check if we have results
    rc = sqlite3_step(stmt_);
    if (rc == SQLITE_ROW) {
        has_row_ = true;
    } else if (rc == SQLITE_DONE) {
        has_row_ = false;
    } else {
        std::string error = sqlite3_errmsg(db_);
        throw DataLoaderException("Failed to execute SQLite query: " + error);
    }
    
    return true;
}

std::vector<std::string> SqliteReader::fetch_column_names() {
    std::vector<std::string> names;
    names.reserve(column_count_);
    
    for (int i = 0; i < column_count_; ++i) {
        const char* name = sqlite3_column_name(stmt_, i);
        names.push_back(name ? name : "");
    }
    
    return names;
}

size_t SqliteReader::fetch_row_count() {
    // SQLite doesn't provide row count without a separate COUNT query.
    // For large result sets, this would be expensive, so we return 0 (unknown).
    // The DataLoader handles unknown counts gracefully.
    return 0;
}

bool SqliteReader::has_next() const {
    return has_row_;
}

DataRow SqliteReader::next() {
    if (!has_row_) {
        throw DataLoaderException("No more rows available in SQLite result set");
    }
    
    DataRow row;
    
    // Read current row values
    for (int i = 0; i < column_count_; ++i) {
        const char* value = reinterpret_cast<const char*>(sqlite3_column_text(stmt_, i));
        row[headers_[i]] = value ? value : "";
    }
    
    // Advance to next row
    int rc = sqlite3_step(stmt_);
    if (rc == SQLITE_ROW) {
        has_row_ = true;
    } else if (rc == SQLITE_DONE) {
        has_row_ = false;
    } else {
        std::string error = sqlite3_errmsg(db_);
        throw DataLoaderException("Error fetching next SQLite row: " + error);
    }
    
    return row;
}

void SqliteReader::reset() {
    if (stmt_) {
        sqlite3_reset(stmt_);
        
        // Step to first row
        int rc = sqlite3_step(stmt_);
        if (rc == SQLITE_ROW) {
            has_row_ = true;
        } else if (rc == SQLITE_DONE) {
            has_row_ = false;
        } else {
            std::string error = sqlite3_errmsg(db_);
            throw DataLoaderException("Error resetting SQLite query: " + error);
        }
    }
}

void SqliteReader::finalize_statement() {
    if (stmt_) {
        sqlite3_finalize(stmt_);
        stmt_ = nullptr;
    }
    has_row_ = false;
    column_count_ = 0;
}

} // namespace loader
} // namespace owl2
} // namespace ista
