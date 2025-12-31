#ifndef ISTA_OWL2_LOADER_YAML_PARSER_HPP
#define ISTA_OWL2_LOADER_YAML_PARSER_HPP

#include <string>
#include <vector>
#include <map>
#include <variant>
#include <memory>
#include <stdexcept>

namespace ista {
namespace owl2 {
namespace loader {

/**
 * @brief Exception thrown when YAML parsing fails
 */
class YamlParseException : public std::runtime_error {
public:
    YamlParseException(const std::string& message, size_t line = 0)
        : std::runtime_error(line > 0 ? "YAML parse error at line " + std::to_string(line) + ": " + message
                                      : "YAML parse error: " + message),
          line_(line) {}
    
    size_t line() const { return line_; }
    
private:
    size_t line_;
};

// Forward declaration
class YamlNode;
using YamlNodePtr = std::shared_ptr<YamlNode>;

/**
 * @brief A minimal YAML parser supporting the subset needed for mapping specs
 * 
 * Supports:
 * - Scalars (strings, numbers, booleans)
 * - Maps (key: value)
 * - Lists (- item)
 * - Inline maps ({ key: value })
 * - Inline lists ([ item, item ])
 * - Comments (# comment)
 * - Multi-line strings (basic support)
 * 
 * Does NOT support:
 * - Anchors and aliases
 * - Tags
 * - Complex multi-line strings (|, >)
 * - Multiple documents
 */
class YamlNode {
public:
    enum class Type {
        Null,
        Scalar,
        Map,
        List
    };
    
    using ScalarValue = std::string;
    using MapValue = std::map<std::string, YamlNodePtr>;
    using ListValue = std::vector<YamlNodePtr>;
    
    YamlNode() : type_(Type::Null) {}
    explicit YamlNode(const std::string& scalar) : type_(Type::Scalar), scalar_(scalar) {}
    explicit YamlNode(const MapValue& map) : type_(Type::Map), map_(map) {}
    explicit YamlNode(const ListValue& list) : type_(Type::List), list_(list) {}
    
    Type type() const { return type_; }
    bool is_null() const { return type_ == Type::Null; }
    bool is_scalar() const { return type_ == Type::Scalar; }
    bool is_map() const { return type_ == Type::Map; }
    bool is_list() const { return type_ == Type::List; }
    
    // Scalar access
    const std::string& as_string() const;
    int as_int() const;
    double as_double() const;
    bool as_bool() const;
    
    // Map access
    const MapValue& as_map() const;
    bool has_key(const std::string& key) const;
    YamlNodePtr get(const std::string& key) const;
    YamlNodePtr operator[](const std::string& key) const { return get(key); }
    
    // List access
    const ListValue& as_list() const;
    size_t size() const;
    YamlNodePtr get(size_t index) const;
    YamlNodePtr operator[](size_t index) const { return get(index); }
    
    // Convenience methods with defaults
    std::string get_string(const std::string& key, const std::string& default_value = "") const;
    int get_int(const std::string& key, int default_value = 0) const;
    bool get_bool(const std::string& key, bool default_value = false) const;
    
    // Static factory
    static YamlNodePtr make_null() { return std::make_shared<YamlNode>(); }
    static YamlNodePtr make_scalar(const std::string& s) { return std::make_shared<YamlNode>(s); }
    static YamlNodePtr make_map() { return std::make_shared<YamlNode>(MapValue{}); }
    static YamlNodePtr make_list() { return std::make_shared<YamlNode>(ListValue{}); }
    
    // Modification (for building)
    void set(const std::string& key, YamlNodePtr value);
    void append(YamlNodePtr value);
    
private:
    Type type_;
    ScalarValue scalar_;
    MapValue map_;
    ListValue list_;
};

/**
 * @brief Parse YAML content into a node tree
 */
class YamlParser {
public:
    /**
     * @brief Parse YAML string into a node tree
     */
    static YamlNodePtr parse(const std::string& content);
    
    /**
     * @brief Parse YAML file
     */
    static YamlNodePtr parse_file(const std::string& filepath);
    
private:
    struct ParseState {
        const std::string& content;
        size_t pos = 0;
        size_t line = 1;
        
        ParseState(const std::string& c) : content(c) {}
        
        char peek() const { return pos < content.size() ? content[pos] : '\0'; }
        char advance() { 
            char c = peek();
            if (c == '\n') line++;
            pos++;
            return c;
        }
        bool at_end() const { return pos >= content.size(); }
        void skip_whitespace();
        void skip_line();
        int get_indent();
        std::string read_until(const std::string& delimiters);
        std::string read_quoted_string();
    };
    
    static YamlNodePtr parse_value(ParseState& state, int base_indent);
    static YamlNodePtr parse_map(ParseState& state, int base_indent);
    static YamlNodePtr parse_list(ParseState& state, int base_indent);
    static YamlNodePtr parse_inline_map(ParseState& state);
    static YamlNodePtr parse_inline_list(ParseState& state);
    static std::string parse_scalar(ParseState& state);
    static std::string parse_key(ParseState& state);
};

} // namespace loader
} // namespace owl2
} // namespace ista

#endif // ISTA_OWL2_LOADER_YAML_PARSER_HPP
