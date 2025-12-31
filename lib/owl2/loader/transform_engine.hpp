#ifndef ISTA_OWL2_LOADER_TRANSFORM_ENGINE_HPP
#define ISTA_OWL2_LOADER_TRANSFORM_ENGINE_HPP

#include <string>
#include <map>
#include <vector>
#include <functional>
#include <optional>
#include <stdexcept>

namespace ista {
namespace owl2 {
namespace loader {

/**
 * @brief Exception thrown when a transform fails
 */
class TransformException : public std::runtime_error {
public:
    explicit TransformException(const std::string& message)
        : std::runtime_error("Transform error: " + message) {}
};

/**
 * @brief Definition of a transform that can be applied to values
 * 
 * Transforms can be:
 * - Simple built-in transforms (split, prefix, lowercase, etc.)
 * - Parameterized transforms (split with delimiter and index)
 * - Chained transforms (apply multiple transforms in sequence)
 */
struct TransformDef {
    std::string type;  // "split", "chain", "prefix", "suffix", "strip_prefix", 
                       // "lowercase", "uppercase", "to_int", "to_float", "regex_extract"
    std::map<std::string, std::string> params;
    std::vector<TransformDef> steps;  // For chain transforms
    
    TransformDef() = default;
    TransformDef(const std::string& t) : type(t) {}
    TransformDef(const std::string& t, const std::map<std::string, std::string>& p) 
        : type(t), params(p) {}
};

/**
 * @brief Engine for applying named transforms to string values
 * 
 * The TransformEngine provides a library of built-in transforms that can be
 * applied to data values during ontology population. This replaces the use
 * of lambda functions in Python code with named, parameterized, serializable
 * transforms.
 * 
 * Built-in transforms:
 * - split: Split string by delimiter and take element at index
 *   params: delimiter (string), index (int, negative for from end)
 * - prefix: Add a prefix to the value
 *   params: value (string to prepend)
 * - suffix: Add a suffix to the value
 *   params: value (string to append)
 * - strip_prefix: Remove a prefix if present
 *   params: value (string to remove)
 * - strip_suffix: Remove a suffix if present
 *   params: value (string to remove)
 * - lowercase: Convert to lowercase
 * - uppercase: Convert to uppercase
 * - trim: Remove leading/trailing whitespace
 * - to_int: Parse as integer (for type checking)
 * - to_float: Parse as float (for type checking)
 * - replace: Replace substring
 *   params: old (string to find), new (string to replace with)
 * - regex_extract: Extract using regex capture group
 *   params: pattern (regex), group (int, default 0)
 * - chain: Apply multiple transforms in sequence
 *   steps: list of TransformDefs
 * 
 * @par Example Usage
 * @code
 * TransformEngine engine;
 * 
 * // Simple transform
 * std::string result = engine.apply_builtin("lowercase", "HELLO", {});
 * // result = "hello"
 * 
 * // Parameterized transform
 * std::map<std::string, std::string> params = {{"delimiter", "::"}, {"index", "-1"}};
 * result = engine.apply_builtin("split", "Compound::DB12345", params);
 * // result = "DB12345"
 * 
 * // Named transform from registry
 * TransformDef def("split", {{"delimiter", "::"}, {"index", "-1"}});
 * engine.register_transform("extract_id", def);
 * result = engine.apply("extract_id", "Compound::DB12345", engine.get_registry());
 * // result = "DB12345"
 * @endcode
 */
class TransformEngine {
public:
    using TransformFunc = std::function<std::string(const std::string&, 
                                                     const std::map<std::string, std::string>&)>;
    
    /**
     * @brief Construct a TransformEngine with built-in transforms registered
     */
    TransformEngine();
    
    /**
     * @brief Apply a named transform from the registry
     * 
     * @param transform_name Name of the transform to apply
     * @param value The input value to transform
     * @param registry Map of transform names to definitions
     * @return Transformed value
     * @throws TransformException if transform not found or fails
     */
    std::string apply(const std::string& transform_name,
                      const std::string& value,
                      const std::map<std::string, TransformDef>& registry) const;
    
    /**
     * @brief Apply a transform definition directly
     * 
     * @param def The transform definition
     * @param value The input value to transform
     * @param registry Map of transform names (for resolving references in chains)
     * @return Transformed value
     */
    std::string apply_def(const TransformDef& def,
                          const std::string& value,
                          const std::map<std::string, TransformDef>& registry) const;
    
    /**
     * @brief Apply a built-in transform by type name
     * 
     * @param type The transform type (e.g., "split", "lowercase")
     * @param value The input value
     * @param params Transform parameters
     * @return Transformed value
     * @throws TransformException if transform type unknown or fails
     */
    std::string apply_builtin(const std::string& type,
                              const std::string& value,
                              const std::map<std::string, std::string>& params) const;
    
    /**
     * @brief Register a custom transform function
     * 
     * @param name Transform type name
     * @param func The transform function
     */
    void register_builtin(const std::string& name, TransformFunc func);
    
    /**
     * @brief Check if a builtin transform type exists
     */
    bool has_builtin(const std::string& name) const;
    
    /**
     * @brief Get list of available builtin transform types
     */
    std::vector<std::string> get_builtin_names() const;
    
private:
    std::map<std::string, TransformFunc> builtins_;
    
    // Initialize built-in transforms
    void init_builtins();
    
    // Helper to get required param
    std::string get_param(const std::map<std::string, std::string>& params,
                          const std::string& name,
                          const std::string& default_value = "") const;
    
    // Helper to get int param
    int get_int_param(const std::map<std::string, std::string>& params,
                      const std::string& name,
                      int default_value = 0) const;
};

} // namespace loader
} // namespace owl2
} // namespace ista

#endif // ISTA_OWL2_LOADER_TRANSFORM_ENGINE_HPP
