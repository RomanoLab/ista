#ifndef ISTA_OWL2_KONCLUDE_WRAPPER_HPP
#define ISTA_OWL2_KONCLUDE_WRAPPER_HPP

#include "../core/ontology.hpp"
#include <string>
#include <vector>
#include <optional>
#include <stdexcept>
#include <filesystem>
#include <cstdlib>

namespace ista {
namespace owl2 {
namespace reasoner {

/**
 * @brief Exception thrown when Konclude reasoning fails
 */
class KoncludeException : public std::runtime_error {
public:
    explicit KoncludeException(const std::string& message)
        : std::runtime_error("Konclude Reasoner Error: " + message) {}
};

/**
 * @brief Configuration for Konclude reasoner
 */
struct KoncludeConfig {
    // Path to Konclude executable
    std::string konclude_path = "Konclude";
    
    // Number of worker threads (-1 = auto)
    int worker_threads = -1;
    
    // Enable verbose output
    bool verbose = false;
    
    // Timeout in seconds (0 = no timeout)
    int timeout_seconds = 0;
    
    // Temporary directory for intermediate files
    std::string temp_dir = ".";
};

/**
 * @brief Results from reasoning operations
 */
struct ReasoningResult {
    bool success = false;
    bool is_consistent = true;
    std::string error_message;
    std::vector<std::string> inferred_axioms;
    double reasoning_time_seconds = 0.0;
};

/**
 * @brief Wrapper for Konclude OWL2 reasoner
 * 
 * This class provides a C++ interface to the Konclude reasoner via command-line.
 * Konclude is a high-performance, parallel OWL 2 DL reasoner.
 * 
 * Supported reasoning tasks:
 * - Consistency checking
 * - Classification (compute class hierarchy)
 * - Realization (compute instance types)
 * - Satisfiability checking
 * 
 * Example usage:
 * @code
 * KoncludeWrapper reasoner;
 * reasoner.set_konclude_path("/path/to/Konclude");
 * 
 * Ontology onto = ...;
 * auto result = reasoner.classify(onto);
 * if (result.success) {
 *     // Load inferred axioms
 *     Ontology inferred = reasoner.load_inferred_ontology();
 * }
 * @endcode
 */
class KoncludeWrapper {
public:
    /**
     * @brief Construct a Konclude wrapper with default configuration
     */
    KoncludeWrapper() = default;
    
    /**
     * @brief Construct a Konclude wrapper with custom configuration
     */
    explicit KoncludeWrapper(const KoncludeConfig& config);
    
    /**
     * @brief Set the path to Konclude executable
     */
    void set_konclude_path(const std::string& path);
    
    /**
     * @brief Set the number of worker threads
     * @param threads Number of threads (-1 for auto-detection)
     */
    void set_worker_threads(int threads);
    
    /**
     * @brief Enable or disable verbose output
     */
    void set_verbose(bool verbose);
    
    /**
     * @brief Check if the ontology is consistent
     * 
     * @param ontology The ontology to check
     * @return ReasoningResult with is_consistent set appropriately
     */
    ReasoningResult check_consistency(const Ontology& ontology);
    
    /**
     * @brief Classify the ontology (compute class hierarchy)
     * 
     * @param ontology The ontology to classify
     * @return ReasoningResult with inferred subclass axioms
     */
    ReasoningResult classify(const Ontology& ontology);
    
    /**
     * @brief Realize the ontology (compute instance types)
     * 
     * @param ontology The ontology to realize
     * @return ReasoningResult with inferred class assertions
     */
    ReasoningResult realize(const Ontology& ontology);
    
    /**
     * @brief Check if a specific class is satisfiable
     * 
     * @param ontology The ontology context
     * @param class_iri IRI of the class to check
     * @return ReasoningResult with is_consistent indicating satisfiability
     */
    ReasoningResult check_satisfiability(const Ontology& ontology, const IRI& class_iri);
    
    /**
     * @brief Load the inferred ontology from the last reasoning operation
     * 
     * @return The ontology with inferred axioms, or empty ontology if none
     */
    std::optional<Ontology> load_inferred_ontology();
    
    /**
     * @brief Get the configuration
     */
    const KoncludeConfig& get_config() const { return config_; }
    
    /**
     * @brief Check if Konclude is available at the configured path
     */
    bool is_available() const;
    
private:
    KoncludeConfig config_;
    std::string last_output_file_;
    
    /**
     * @brief Execute a Konclude command
     */
    ReasoningResult execute_command(
        const std::string& command,
        const std::string& input_file,
        const std::string& output_file,
        const std::vector<std::string>& extra_args = {}
    );
    
    /**
     * @brief Save ontology to a temporary file
     */
    std::string save_to_temp_file(const Ontology& ontology);
    
    /**
     * @brief Parse Konclude output for timing information
     */
    double parse_timing_info(const std::string& output);
    
    /**
     * @brief Build command line arguments
     */
    std::string build_command(
        const std::string& command,
        const std::string& input_file,
        const std::string& output_file,
        const std::vector<std::string>& extra_args
    );
};

} // namespace reasoner
} // namespace owl2
} // namespace ista

#endif // ISTA_OWL2_KONCLUDE_WRAPPER_HPP
