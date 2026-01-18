#ifndef ISTA_OWL2_LOADER_DATABASE_READER_HPP
#define ISTA_OWL2_LOADER_DATABASE_READER_HPP

#include "data_loader.hpp"
#include "mapping_spec.hpp"
#include <string>
#include <vector>
#include <optional>

namespace ista {
namespace owl2 {
namespace loader {

/**
 * @brief Abstract base class for database-backed data source readers.
 * 
 * This class provides common functionality for SQL database readers,
 * including connection management, query building, and result iteration.
 * Concrete implementations (SQLite, MySQL, PostgreSQL) inherit from this
 * class and implement the database-specific operations.
 */
class DatabaseReader : public DataSourceReader {
public:
    /**
     * @brief Construct a database reader from a data source definition.
     * 
     * @param source The data source definition containing connection info
     */
    explicit DatabaseReader(const DataSourceDef& source);
    
    virtual ~DatabaseReader() = default;
    
    // DataSourceReader interface
    bool open() override;
    void close() override;
    std::vector<std::string> headers() const override { return headers_; }
    size_t row_count() const override { return total_rows_; }
    
protected:
    /**
     * @brief Establish a connection to the database.
     * 
     * @return true if connection was successful
     */
    virtual bool connect() = 0;
    
    /**
     * @brief Close the database connection.
     */
    virtual void disconnect() = 0;
    
    /**
     * @brief Execute the query and prepare for iteration.
     * 
     * This should execute the SQL query (either from table or custom query)
     * and prepare the result set for iteration via has_next()/next().
     * 
     * @return true if query execution was successful
     */
    virtual bool execute_query() = 0;
    
    /**
     * @brief Get the column names from the result set.
     * 
     * Called after execute_query() to populate headers_.
     * 
     * @return Vector of column names
     */
    virtual std::vector<std::string> fetch_column_names() = 0;
    
    /**
     * @brief Get the row count from the result set.
     * 
     * Called after execute_query() to populate total_rows_.
     * Return 0 if count is unknown or expensive to compute.
     * 
     * @return Number of rows, or 0 if unknown
     */
    virtual size_t fetch_row_count() = 0;
    
    /**
     * @brief Build the SQL query string.
     * 
     * If a custom query is provided, returns it directly.
     * Otherwise, builds a SELECT * FROM table query.
     * 
     * @return The SQL query to execute
     */
    std::string build_query() const;
    
    /**
     * @brief Get a safe description of the connection for error messages.
     * 
     * Returns connection details without exposing the password.
     * 
     * @return Connection description string
     */
    std::string connection_description() const;
    
    // Source definition
    DataSourceDef source_;
    
    // Cached headers and row count
    std::vector<std::string> headers_;
    size_t total_rows_ = 0;
    
    // Connection state
    bool is_connected_ = false;
    bool query_executed_ = false;
};

} // namespace loader
} // namespace owl2
} // namespace ista

#endif // ISTA_OWL2_LOADER_DATABASE_READER_HPP
