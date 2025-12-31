#include "transform_engine.hpp"
#include <algorithm>
#include <cctype>
#include <sstream>
#include <regex>

namespace ista {
namespace owl2 {
namespace loader {

TransformEngine::TransformEngine() {
    init_builtins();
}

void TransformEngine::init_builtins() {
    // split: Split by delimiter and take element at index
    builtins_["split"] = [this](const std::string& value, 
                                 const std::map<std::string, std::string>& params) -> std::string {
        std::string delimiter = get_param(params, "delimiter", ",");
        int index = get_int_param(params, "index", 0);
        
        std::vector<std::string> parts;
        size_t start = 0;
        size_t end = value.find(delimiter);
        
        while (end != std::string::npos) {
            parts.push_back(value.substr(start, end - start));
            start = end + delimiter.length();
            end = value.find(delimiter, start);
        }
        parts.push_back(value.substr(start));
        
        if (parts.empty()) {
            return value;
        }
        
        // Handle negative index (from end)
        if (index < 0) {
            index = static_cast<int>(parts.size()) + index;
        }
        
        if (index < 0 || index >= static_cast<int>(parts.size())) {
            throw TransformException("split: index " + std::to_string(index) + 
                                    " out of range for " + std::to_string(parts.size()) + " parts");
        }
        
        return parts[index];
    };
    
    // prefix: Add a prefix
    builtins_["prefix"] = [this](const std::string& value,
                                  const std::map<std::string, std::string>& params) -> std::string {
        std::string prefix = get_param(params, "value", "");
        return prefix + value;
    };
    
    // suffix: Add a suffix
    builtins_["suffix"] = [this](const std::string& value,
                                  const std::map<std::string, std::string>& params) -> std::string {
        std::string suffix = get_param(params, "value", "");
        return value + suffix;
    };
    
    // strip_prefix: Remove prefix if present
    builtins_["strip_prefix"] = [this](const std::string& value,
                                        const std::map<std::string, std::string>& params) -> std::string {
        std::string prefix = get_param(params, "value", "");
        if (prefix.empty()) return value;
        
        if (value.length() >= prefix.length() && 
            value.substr(0, prefix.length()) == prefix) {
            return value.substr(prefix.length());
        }
        return value;
    };
    
    // strip_suffix: Remove suffix if present
    builtins_["strip_suffix"] = [this](const std::string& value,
                                        const std::map<std::string, std::string>& params) -> std::string {
        std::string suffix = get_param(params, "value", "");
        if (suffix.empty()) return value;
        
        if (value.length() >= suffix.length() &&
            value.substr(value.length() - suffix.length()) == suffix) {
            return value.substr(0, value.length() - suffix.length());
        }
        return value;
    };
    
    // lowercase: Convert to lowercase
    builtins_["lowercase"] = [](const std::string& value,
                                 const std::map<std::string, std::string>&) -> std::string {
        std::string result = value;
        std::transform(result.begin(), result.end(), result.begin(),
                      [](unsigned char c) { return std::tolower(c); });
        return result;
    };
    
    // uppercase: Convert to uppercase
    builtins_["uppercase"] = [](const std::string& value,
                                 const std::map<std::string, std::string>&) -> std::string {
        std::string result = value;
        std::transform(result.begin(), result.end(), result.begin(),
                      [](unsigned char c) { return std::toupper(c); });
        return result;
    };
    
    // trim: Remove leading/trailing whitespace
    builtins_["trim"] = [](const std::string& value,
                            const std::map<std::string, std::string>&) -> std::string {
        size_t start = value.find_first_not_of(" \t\n\r\f\v");
        if (start == std::string::npos) return "";
        size_t end = value.find_last_not_of(" \t\n\r\f\v");
        return value.substr(start, end - start + 1);
    };
    
    // to_int: Validate/convert to integer string
    builtins_["to_int"] = [](const std::string& value,
                              const std::map<std::string, std::string>&) -> std::string {
        try {
            // Trim first
            std::string trimmed = value;
            size_t start = trimmed.find_first_not_of(" \t\n\r");
            if (start != std::string::npos) {
                size_t end = trimmed.find_last_not_of(" \t\n\r");
                trimmed = trimmed.substr(start, end - start + 1);
            }
            
            long long parsed = std::stoll(trimmed);
            return std::to_string(parsed);
        } catch (const std::exception& e) {
            throw TransformException("to_int: cannot parse '" + value + "' as integer");
        }
    };
    
    // to_float: Validate/convert to float string
    builtins_["to_float"] = [](const std::string& value,
                                const std::map<std::string, std::string>&) -> std::string {
        try {
            std::string trimmed = value;
            size_t start = trimmed.find_first_not_of(" \t\n\r");
            if (start != std::string::npos) {
                size_t end = trimmed.find_last_not_of(" \t\n\r");
                trimmed = trimmed.substr(start, end - start + 1);
            }
            
            double parsed = std::stod(trimmed);
            std::ostringstream oss;
            oss << parsed;
            return oss.str();
        } catch (const std::exception& e) {
            throw TransformException("to_float: cannot parse '" + value + "' as float");
        }
    };
    
    // replace: Replace substring
    builtins_["replace"] = [this](const std::string& value,
                                   const std::map<std::string, std::string>& params) -> std::string {
        std::string old_str = get_param(params, "old", "");
        std::string new_str = get_param(params, "new", "");
        
        if (old_str.empty()) return value;
        
        std::string result = value;
        size_t pos = 0;
        while ((pos = result.find(old_str, pos)) != std::string::npos) {
            result.replace(pos, old_str.length(), new_str);
            pos += new_str.length();
        }
        return result;
    };
    
    // regex_extract: Extract using regex
    builtins_["regex_extract"] = [this](const std::string& value,
                                         const std::map<std::string, std::string>& params) -> std::string {
        std::string pattern = get_param(params, "pattern", "(.*)");
        int group = get_int_param(params, "group", 1);
        
        try {
            std::regex re(pattern);
            std::smatch match;
            
            if (std::regex_search(value, match, re)) {
                if (group < static_cast<int>(match.size())) {
                    return match[group].str();
                }
                throw TransformException("regex_extract: group " + std::to_string(group) + 
                                        " not found in match");
            }
            return value;  // No match, return original
        } catch (const std::regex_error& e) {
            throw TransformException("regex_extract: invalid pattern '" + pattern + "': " + e.what());
        }
    };
    
    // identity: Return value unchanged (useful in chains)
    builtins_["identity"] = [](const std::string& value,
                                const std::map<std::string, std::string>&) -> std::string {
        return value;
    };
    
    // default_if_empty: Return default value if input is empty
    builtins_["default_if_empty"] = [this](const std::string& value,
                                            const std::map<std::string, std::string>& params) -> std::string {
        if (value.empty()) {
            return get_param(params, "value", "");
        }
        return value;
    };
}

std::string TransformEngine::apply(const std::string& transform_name,
                                    const std::string& value,
                                    const std::map<std::string, TransformDef>& registry) const {
    auto it = registry.find(transform_name);
    if (it == registry.end()) {
        throw TransformException("transform '" + transform_name + "' not found in registry");
    }
    return apply_def(it->second, value, registry);
}

std::string TransformEngine::apply_def(const TransformDef& def,
                                        const std::string& value,
                                        const std::map<std::string, TransformDef>& registry) const {
    // Handle chain transforms
    if (def.type == "chain") {
        std::string result = value;
        for (const auto& step : def.steps) {
            result = apply_def(step, result, registry);
        }
        return result;
    }
    
    // Handle reference to another named transform
    if (def.type == "ref") {
        std::string ref_name = def.params.count("name") ? def.params.at("name") : "";
        if (ref_name.empty()) {
            throw TransformException("ref transform requires 'name' parameter");
        }
        return apply(ref_name, value, registry);
    }
    
    // Apply builtin transform
    return apply_builtin(def.type, value, def.params);
}

std::string TransformEngine::apply_builtin(const std::string& type,
                                            const std::string& value,
                                            const std::map<std::string, std::string>& params) const {
    auto it = builtins_.find(type);
    if (it == builtins_.end()) {
        throw TransformException("unknown transform type: " + type);
    }
    return it->second(value, params);
}

void TransformEngine::register_builtin(const std::string& name, TransformFunc func) {
    builtins_[name] = std::move(func);
}

bool TransformEngine::has_builtin(const std::string& name) const {
    return builtins_.find(name) != builtins_.end();
}

std::vector<std::string> TransformEngine::get_builtin_names() const {
    std::vector<std::string> names;
    names.reserve(builtins_.size());
    for (const auto& pair : builtins_) {
        names.push_back(pair.first);
    }
    return names;
}

std::string TransformEngine::get_param(const std::map<std::string, std::string>& params,
                                        const std::string& name,
                                        const std::string& default_value) const {
    auto it = params.find(name);
    return (it != params.end()) ? it->second : default_value;
}

int TransformEngine::get_int_param(const std::map<std::string, std::string>& params,
                                    const std::string& name,
                                    int default_value) const {
    auto it = params.find(name);
    if (it == params.end()) return default_value;
    
    try {
        return std::stoi(it->second);
    } catch (...) {
        throw TransformException("parameter '" + name + "' must be an integer, got: " + it->second);
    }
}

} // namespace loader
} // namespace owl2
} // namespace ista
