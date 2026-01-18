#ifndef ISTA_OWL2_LOADER_POSTGRES_READER_HPP
#define ISTA_OWL2_LOADER_POSTGRES_READER_HPP

#include "database_reader.hpp"

// Forward declare PostgreSQL types to avoid including libpq-fe.h in header
struct pg_conn;
struct pg_result;
typedef struct pg_conn PGconn;
typedef struct pg_result PGresult;

namespace ista {
namespace owl2 {
namespace loader {

/**
 * @brief PostgreSQL database reader implementation.
 * 
 * Reads data from PostgreSQL databases using the libpq C API.
 * Supports both simple table access and custom SQL queries.
 * 
 * YAML configuration example:
 * @code{.yaml}
 * sources:
 *   my_postgres_db:
 *     type: postgres  # or "postgresql"
 *     connection:
 *       host: "localhost"
 *       port: 5432
 *       database: "mydb"
 *       username: "${DB_USER}"
 *       password: "${DB_PASS}"
 *       # Alternative: use a connection string
 *       # connection_string: "postgresql://user:pass@host:5432/dbname"
 *     table: my_table
 *     # or use a custom query:
 *     # query: "SELECT id, name FROM my_table WHERE active = true"
 * @endcode
 */
class PostgresReader : public DatabaseReader {
public:
    /**
     * @brief Construct a PostgreSQL reader from a data source definition.
     * 
     * @param source The data source definition (must have type "postgres" or "postgresql")
     */
    explicit PostgresReader(const DataSourceDef& source);
    
    ~PostgresReader() override;
    
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
    PGconn* conn_ = nullptr;
    PGresult* result_ = nullptr;
    int num_fields_ = 0;
    int num_rows_ = 0;
    int current_row_ = 0;
    
    /**
     * @brief Build a libpq connection string from connection parameters.
     */
    std::string build_connection_string() const;
    
    /**
     * @brief Clear the result set.
     */
    void clear_result();
};

} // namespace loader
} // namespace owl2
} // namespace ista

#endif // ISTA_OWL2_LOADER_POSTGRES_READER_HPP
