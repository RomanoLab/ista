#include "yaml_parser.hpp"
#include <fstream>
#include <sstream>
#include <algorithm>
#include <cctype>

namespace ista {
namespace owl2 {
namespace loader {

// YamlNode implementation

const std::string& YamlNode::as_string() const {
    if (type_ != Type::Scalar) {
        throw YamlParseException("Node is not a scalar");
    }
    return scalar_;
}

int YamlNode::as_int() const {
    return std::stoi(as_string());
}

double YamlNode::as_double() const {
    return std::stod(as_string());
}

bool YamlNode::as_bool() const {
    const std::string& s = as_string();
    if (s == "true" || s == "True" || s == "TRUE" || s == "yes" || s == "Yes" || s == "YES") {
        return true;
    }
    if (s == "false" || s == "False" || s == "FALSE" || s == "no" || s == "No" || s == "NO") {
        return false;
    }
    throw YamlParseException("Cannot convert '" + s + "' to boolean");
}

const YamlNode::MapValue& YamlNode::as_map() const {
    if (type_ != Type::Map) {
        throw YamlParseException("Node is not a map");
    }
    return map_;
}

bool YamlNode::has_key(const std::string& key) const {
    if (type_ != Type::Map) return false;
    return map_.find(key) != map_.end();
}

YamlNodePtr YamlNode::get(const std::string& key) const {
    if (type_ != Type::Map) {
        throw YamlParseException("Node is not a map");
    }
    auto it = map_.find(key);
    if (it == map_.end()) {
        return make_null();
    }
    return it->second;
}

const YamlNode::ListValue& YamlNode::as_list() const {
    if (type_ != Type::List) {
        throw YamlParseException("Node is not a list");
    }
    return list_;
}

size_t YamlNode::size() const {
    if (type_ == Type::List) return list_.size();
    if (type_ == Type::Map) return map_.size();
    return 0;
}

YamlNodePtr YamlNode::get(size_t index) const {
    if (type_ != Type::List) {
        throw YamlParseException("Node is not a list");
    }
    if (index >= list_.size()) {
        return make_null();
    }
    return list_[index];
}

std::string YamlNode::get_string(const std::string& key, const std::string& default_value) const {
    if (!has_key(key)) return default_value;
    auto node = get(key);
    if (node->is_null() || !node->is_scalar()) return default_value;
    return node->as_string();
}

int YamlNode::get_int(const std::string& key, int default_value) const {
    if (!has_key(key)) return default_value;
    auto node = get(key);
    if (node->is_null() || !node->is_scalar()) return default_value;
    try {
        return node->as_int();
    } catch (...) {
        return default_value;
    }
}

bool YamlNode::get_bool(const std::string& key, bool default_value) const {
    if (!has_key(key)) return default_value;
    auto node = get(key);
    if (node->is_null() || !node->is_scalar()) return default_value;
    try {
        return node->as_bool();
    } catch (...) {
        return default_value;
    }
}

void YamlNode::set(const std::string& key, YamlNodePtr value) {
    if (type_ != Type::Map) {
        type_ = Type::Map;
        map_.clear();
    }
    map_[key] = value;
}

void YamlNode::append(YamlNodePtr value) {
    if (type_ != Type::List) {
        type_ = Type::List;
        list_.clear();
    }
    list_.push_back(value);
}

// ParseState helpers

void YamlParser::ParseState::skip_whitespace() {
    while (!at_end() && (peek() == ' ' || peek() == '\t')) {
        advance();
    }
}

void YamlParser::ParseState::skip_line() {
    while (!at_end() && peek() != '\n') {
        advance();
    }
    if (!at_end()) advance();  // Skip the newline
}

int YamlParser::ParseState::get_indent() {
    size_t start = pos;
    int indent = 0;
    while (pos < content.size() && content[pos] == ' ') {
        indent++;
        pos++;
    }
    // Don't count tabs as indentation for simplicity
    return indent;
}

std::string YamlParser::ParseState::read_until(const std::string& delimiters) {
    std::string result;
    while (!at_end() && delimiters.find(peek()) == std::string::npos) {
        result += advance();
    }
    return result;
}

std::string YamlParser::ParseState::read_quoted_string() {
    char quote = advance();  // Skip opening quote
    std::string result;
    while (!at_end() && peek() != quote) {
        if (peek() == '\\') {
            advance();  // Skip backslash
            if (!at_end()) {
                char c = advance();
                switch (c) {
                    case 'n': result += '\n'; break;
                    case 't': result += '\t'; break;
                    case 'r': result += '\r'; break;
                    case '\\': result += '\\'; break;
                    case '"': result += '"'; break;
                    case '\'': result += '\''; break;
                    default: result += c; break;
                }
            }
        } else {
            result += advance();
        }
    }
    if (!at_end()) advance();  // Skip closing quote
    return result;
}

// YamlParser implementation

YamlNodePtr YamlParser::parse(const std::string& content) {
    ParseState state(content);
    
    // Skip any leading whitespace and comments
    while (!state.at_end()) {
        state.skip_whitespace();
        if (state.peek() == '#') {
            state.skip_line();
        } else if (state.peek() == '\n') {
            state.advance();
        } else {
            break;
        }
    }
    
    if (state.at_end()) {
        return YamlNode::make_null();
    }
    
    return parse_value(state, 0);
}

YamlNodePtr YamlParser::parse_file(const std::string& filepath) {
    std::ifstream file(filepath);
    if (!file.is_open()) {
        throw YamlParseException("Could not open file: " + filepath);
    }
    
    std::stringstream buffer;
    buffer << file.rdbuf();
    return parse(buffer.str());
}

YamlNodePtr YamlParser::parse_value(ParseState& state, int base_indent) {
    state.skip_whitespace();
    
    if (state.at_end()) {
        return YamlNode::make_null();
    }
    
    char c = state.peek();
    
    // Inline structures
    if (c == '{') {
        return parse_inline_map(state);
    }
    if (c == '[') {
        return parse_inline_list(state);
    }
    
    // Check if this is a list item
    if (c == '-') {
        return parse_list(state, base_indent);
    }
    
    // Check if this looks like a map (has a colon)
    size_t save_pos = state.pos;
    std::string first_word = state.read_until(":[\n#");
    state.pos = save_pos;
    
    if (!first_word.empty() && state.pos < state.content.size()) {
        size_t colon_pos = state.content.find(':', state.pos);
        size_t newline_pos = state.content.find('\n', state.pos);
        if (colon_pos != std::string::npos && 
            (newline_pos == std::string::npos || colon_pos < newline_pos)) {
            return parse_map(state, base_indent);
        }
    }
    
    // Otherwise it's a scalar
    return YamlNode::make_scalar(parse_scalar(state));
}

YamlNodePtr YamlParser::parse_map(ParseState& state, int base_indent) {
    auto map_node = YamlNode::make_map();
    
    while (!state.at_end()) {
        // Save position for indent check
        size_t line_start = state.pos;
        
        // Get indentation of this line
        int indent = state.get_indent();
        
        // Skip blank lines and comments
        if (state.peek() == '\n') {
            state.advance();
            continue;
        }
        if (state.peek() == '#') {
            state.skip_line();
            continue;
        }
        
        // If indent is less than base, we're done with this map
        if (indent < base_indent) {
            state.pos = line_start;  // Rewind
            break;
        }
        
        // If this is a list item, we're done with this map
        if (state.peek() == '-') {
            state.pos = line_start;
            break;
        }
        
        // Parse key
        std::string key = parse_key(state);
        if (key.empty()) {
            state.skip_line();
            continue;
        }
        
        state.skip_whitespace();
        
        // Expect colon
        if (state.peek() != ':') {
            throw YamlParseException("Expected ':' after key '" + key + "'", state.line);
        }
        state.advance();  // Skip colon
        
        state.skip_whitespace();
        
        // Parse value
        YamlNodePtr value;
        if (state.peek() == '\n' || state.peek() == '#') {
            // Value is on next line(s), need to determine its indent
            if (state.peek() == '#') {
                state.skip_line();
            } else {
                state.advance();  // Skip newline
            }
            
            // Skip empty lines
            while (!state.at_end()) {
                size_t pos_before = state.pos;
                int next_indent = state.get_indent();
                if (state.peek() == '\n') {
                    state.advance();
                    continue;
                }
                if (state.peek() == '#') {
                    state.skip_line();
                    continue;
                }
                state.pos = pos_before;
                break;
            }
            
            // Get the actual value indent
            size_t value_line_start = state.pos;
            int value_indent = state.get_indent();
            state.pos = value_line_start;
            
            if (value_indent > indent) {
                value = parse_value(state, value_indent);
            } else {
                value = YamlNode::make_null();
                state.pos = value_line_start;
            }
        } else {
            // Value is on same line
            value = parse_value(state, indent + 1);
            
            // Skip to end of line
            while (!state.at_end() && state.peek() != '\n') {
                if (state.peek() == '#') {
                    state.skip_line();
                    break;
                }
                state.advance();
            }
            if (!state.at_end() && state.peek() == '\n') {
                state.advance();
            }
        }
        
        map_node->set(key, value);
    }
    
    return map_node;
}

YamlNodePtr YamlParser::parse_list(ParseState& state, int base_indent) {
    auto list_node = YamlNode::make_list();
    
    while (!state.at_end()) {
        size_t line_start = state.pos;
        int indent = state.get_indent();
        
        // Skip blank lines and comments
        if (state.peek() == '\n') {
            state.advance();
            continue;
        }
        if (state.peek() == '#') {
            state.skip_line();
            continue;
        }
        
        // If indent is less than base, we're done
        if (indent < base_indent) {
            state.pos = line_start;
            break;
        }
        
        // Expect list item marker
        if (state.peek() != '-') {
            state.pos = line_start;
            break;
        }
        
        state.advance();  // Skip '-'
        state.skip_whitespace();
        
        // Parse the item value
        YamlNodePtr item;
        if (state.peek() == '\n') {
            state.advance();
            // Item value is on next line(s)
            size_t item_line_start = state.pos;
            int item_indent = state.get_indent();
            state.pos = item_line_start;
            item = parse_value(state, item_indent);
        } else {
            // Item value is on same line - could be a map
            item = parse_value(state, indent + 2);
            
            // Skip to end of line if we haven't moved there
            while (!state.at_end() && state.peek() != '\n') {
                if (state.peek() == '#') {
                    state.skip_line();
                    break;
                }
                state.advance();
            }
            if (!state.at_end() && state.peek() == '\n') {
                state.advance();
            }
        }
        
        list_node->append(item);
    }
    
    return list_node;
}

YamlNodePtr YamlParser::parse_inline_map(ParseState& state) {
    state.advance();  // Skip '{'
    auto map_node = YamlNode::make_map();
    
    while (!state.at_end()) {
        state.skip_whitespace();
        
        if (state.peek() == '}') {
            state.advance();
            break;
        }
        
        // Parse key
        std::string key = parse_key(state);
        state.skip_whitespace();
        
        if (state.peek() != ':') {
            throw YamlParseException("Expected ':' in inline map", state.line);
        }
        state.advance();
        state.skip_whitespace();
        
        // Parse value
        YamlNodePtr value;
        if (state.peek() == '{') {
            value = parse_inline_map(state);
        } else if (state.peek() == '[') {
            value = parse_inline_list(state);
        } else if (state.peek() == '"' || state.peek() == '\'') {
            value = YamlNode::make_scalar(state.read_quoted_string());
        } else {
            std::string scalar = state.read_until(",}");
            // Trim trailing whitespace
            while (!scalar.empty() && std::isspace(scalar.back())) {
                scalar.pop_back();
            }
            value = YamlNode::make_scalar(scalar);
        }
        
        map_node->set(key, value);
        
        state.skip_whitespace();
        if (state.peek() == ',') {
            state.advance();
        }
    }
    
    return map_node;
}

YamlNodePtr YamlParser::parse_inline_list(ParseState& state) {
    state.advance();  // Skip '['
    auto list_node = YamlNode::make_list();
    
    while (!state.at_end()) {
        state.skip_whitespace();
        
        if (state.peek() == ']') {
            state.advance();
            break;
        }
        
        // Parse value
        YamlNodePtr value;
        if (state.peek() == '{') {
            value = parse_inline_map(state);
        } else if (state.peek() == '[') {
            value = parse_inline_list(state);
        } else if (state.peek() == '"' || state.peek() == '\'') {
            value = YamlNode::make_scalar(state.read_quoted_string());
        } else {
            std::string scalar = state.read_until(",]");
            // Trim
            while (!scalar.empty() && std::isspace(scalar.back())) {
                scalar.pop_back();
            }
            value = YamlNode::make_scalar(scalar);
        }
        
        list_node->append(value);
        
        state.skip_whitespace();
        if (state.peek() == ',') {
            state.advance();
        }
    }
    
    return list_node;
}

std::string YamlParser::parse_scalar(ParseState& state) {
    state.skip_whitespace();
    
    if (state.peek() == '"' || state.peek() == '\'') {
        return state.read_quoted_string();
    }
    
    std::string result = state.read_until("\n#,]}");
    
    // Trim trailing whitespace
    while (!result.empty() && std::isspace(result.back())) {
        result.pop_back();
    }
    
    return result;
}

std::string YamlParser::parse_key(ParseState& state) {
    state.skip_whitespace();
    
    if (state.peek() == '"' || state.peek() == '\'') {
        return state.read_quoted_string();
    }
    
    std::string key = state.read_until(":");
    
    // Trim trailing whitespace
    while (!key.empty() && std::isspace(key.back())) {
        key.pop_back();
    }
    
    return key;
}

} // namespace loader
} // namespace owl2
} // namespace ista
