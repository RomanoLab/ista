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
    // Find the line start and determine the column position before we skip whitespace.
    // This is needed so parse_map/parse_list's get_indent() works correctly.
    size_t line_start = state.pos;
    if (line_start > 0) {
        size_t p = line_start;
        while (p > 0 && state.content[p - 1] != '\n') {
            p--;
        }
        line_start = p;
    }

    // Check if the content between line_start and current pos is all whitespace.
    // If so, we can safely rewind to line_start for parse_map/parse_list.
    // If not (e.g., we're after "- " in a list item), we should not rewind.
    bool at_clean_line_start = true;
    for (size_t i = line_start; i < state.pos; ++i) {
        if (state.content[i] != ' ' && state.content[i] != '\t') {
            at_clean_line_start = false;
            break;
        }
    }

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
        if (at_clean_line_start) {
            state.pos = line_start;  // Rewind to line start so parse_list sees correct indent
        }
        return parse_list(state, base_indent);
    }

    // Check if this looks like a map (has a colon followed by space/newline)
    // Skip quoted strings when looking for colons (URLs like http:// are not maps)
    if (c != '"' && c != '\'') {
        size_t search_pos = state.pos;
        size_t newline_pos = state.content.find('\n', search_pos);
        size_t end_pos = (newline_pos != std::string::npos) ? newline_pos : state.content.size();

        bool found_map_colon = false;
        for (size_t i = search_pos; i < end_pos; ++i) {
            if (state.content[i] == ':') {
                // A map key requires colon followed by space, newline, or end
                size_t next = i + 1;
                if (next >= end_pos || state.content[next] == ' ' ||
                    state.content[next] == '\t' || state.content[next] == '\n') {
                    found_map_colon = true;
                    break;
                }
                // Otherwise it's part of a scalar (e.g., http://)
            }
        }

        if (found_map_colon) {
            if (at_clean_line_start) {
                // Rewind to line start so parse_map's get_indent() works correctly
                state.pos = line_start;
            }
            return parse_map(state, base_indent);
        }
    }

    // Otherwise it's a scalar
    return YamlNode::make_scalar(parse_scalar(state));
}

YamlNodePtr YamlParser::parse_map(ParseState& state, int base_indent) {
    auto map_node = YamlNode::make_map();
    bool first_entry = true;
    int effective_indent = base_indent;

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

        if (first_entry) {
            first_entry = false;
            // On the first entry, determine the effective indent level.
            // If indent < base_indent, we're likely in the middle of a line
            // (e.g., after "- " in a list item). In that case, skip the indent
            // check for this first entry and use base_indent going forward.
            if (indent < base_indent) {
                effective_indent = base_indent;
                // Don't break — process this first entry
            } else {
                effective_indent = indent;
            }
        } else if (indent < effective_indent) {
            // If indent is less than effective indent, we're done with this map
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
            size_t pos_before_val = state.pos;
            value = parse_value(state, indent + 1);

            // Only skip to end of line for single-line values.
            // Multi-line values (maps, lists) already leave pos at the right place.
            if (value->is_scalar() || state.pos == pos_before_val) {
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
            // Item value is on same line - could be a map or scalar
            size_t pos_before = state.pos;
            item = parse_value(state, indent + 2);

            // Only skip to end of line for single-line values (scalars, inline maps/lists).
            // Multi-line values (maps, lists parsed over multiple lines) already leave
            // state.pos at the correct position (start of the next relevant line).
            if (item->is_scalar() || state.pos == pos_before) {
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
