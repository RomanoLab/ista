#ifndef ISTA_OWL2_LOADER_MYSQL_READER_HPP
#define ISTA_OWL2_LOADER_MYSQL_READER_HPP

#include "database_reader.hpp"

// Forward declare MySQL types to avoid including mysql.h in header
struct MYSQL;
struct MYSQL_RES;

namespace ista {
namespace owl2 {
namespace loader {

/**
 * @brief MySQL database reader implementation.
 * 
 * Reads data from MySQL databases using the MySQL C API (mysql-connector-c).
 * Supports both simple table access and custom SQL queries.
 * 
 * YAML configuration example:
 * @code{.yaml}
 * sources:
 *   my_mysql_db:
 *     type: mysql
 *     connection:
 *       host: "localhost"
 *       port: 3306
 *       database: "mydb"
 *       username: "${DB_USER}"
 *       password: "${DB_PASS}"
 *     table: my_table
 *     # or use a custom query:
 *     # query: "SELECT id, name FROM my_table WHERE active = 1"
 * @endcode
 */
class MySqlReader : public DatabaseReader {
public:
    /**
     * @brief Construct a MySQL reader from a data source definition.
     * 
     * @param source The data source definition (must have type "mysql")
     */
    explicit MySqlReader(const DataSourceDef& source);
    
    ~MySqlReader() override;
    
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
    MYSQL* conn_ = nullptr;
    MYSQL_RES* result_ = nullptr;
    unsigned int num_fields_ = 0;
    bool has_row_ = false;
    
    // Current row data (stored because mysql_fetch_row returns pointer)
    char** current_row_ = nullptr;
    unsigned long* current_lengths_ = nullptr;
    
    /**
     * @brief Free the result set.
     */
    void free_result();
    
    /**
     * @brief Fetch the next row from the result set.
     */
    void fetch_next_row();
};

} // namespace loader
} // namespace owl2
} // namespace ista

#endif // ISTA_OWL2_LOADER_MYSQL_READER_HPP
