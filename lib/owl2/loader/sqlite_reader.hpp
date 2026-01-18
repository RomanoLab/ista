#ifndef ISTA_OWL2_LOADER_SQLITE_READER_HPP
#define ISTA_OWL2_LOADER_SQLITE_READER_HPP

#include "database_reader.hpp"

// Forward declare sqlite3 types to avoid including sqlite3.h in header
struct sqlite3;
struct sqlite3_stmt;

namespace ista {
namespace owl2 {
namespace loader {

/**
 * @brief SQLite database reader implementation.
 * 
 * Reads data from SQLite database files using the sqlite3 C API.
 * SQLite databases are file-based and don't require a server.
 * 
 * YAML configuration example:
 * @code{.yaml}
 * sources:
 *   my_sqlite_db:
 *     type: sqlite
 *     path: "./data/mydb.sqlite"
 *     table: my_table
 *     # or use a custom query:
 *     # query: "SELECT id, name FROM my_table WHERE active = 1"
 * @endcode
 */
class SqliteReader : public DatabaseReader {
public:
    /**
     * @brief Construct a SQLite reader from a data source definition.
     * 
     * @param source The data source definition (must have type "sqlite")
     */
    explicit SqliteReader(const DataSourceDef& source);
    
    ~SqliteReader() override;
    
    // DataSourceReader interface
    bool has_next() const override;
    DataRow next() override;
    void reset() override;
    
protected:
    // DatabaseReader interface
    bool connect() override;
    void disconnect() override;
    bool execute_query() override;
    std::vector<std::string> fetch_column_names() override;
    size_t fetch_row_count() override;
    
private:
    sqlite3* db_ = nullptr;
    sqlite3_stmt* stmt_ = nullptr;
    bool has_row_ = false;
    int column_count_ = 0;
    
    /**
     * @brief Finalize the prepared statement.
     */
    void finalize_statement();
};

} // namespace loader
} // namespace owl2
} // namespace ista

#endif // ISTA_OWL2_LOADER_SQLITE_READER_HPP
