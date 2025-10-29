#include "konclude_wrapper.hpp"
#include "../serializer/rdfxml_serializer.hpp"
#include "../parser/rdfxml_parser.hpp"
#include <sstream>
#include <fstream>
#include <chrono>
#include <array>
#include <memory>
#include <cstdio>
#include <iostream>

#ifdef _WIN32
#include <windows.h>
#else
#include <unistd.h>
#endif

namespace ista {
namespace owl2 {
namespace reasoner {

KoncludeWrapper::KoncludeWrapper(const KoncludeConfig& config)
    : config_(config) {}

void KoncludeWrapper::set_konclude_path(const std::string& path) {
    config_.konclude_path = path;
}

void KoncludeWrapper::set_worker_threads(int threads) {
    config_.worker_threads = threads;
}

void KoncludeWrapper::set_verbose(bool verbose) {
    config_.verbose = verbose;
}

bool KoncludeWrapper::is_available() const {
    // Try to execute Konclude with --version or help
    std::string cmd = config_.konclude_path + " --help > /dev/null 2>&1";
#ifdef _WIN32
    cmd = config_.konclude_path + " --help > nul 2>&1";
#endif
    int result = std::system(cmd.c_str());
    return result == 0;
}

std::string KoncludeWrapper::save_to_temp_file(const Ontology& ontology) {
    // Generate unique temporary filename
    auto now = std::chrono::system_clock::now();
    auto timestamp = std::chrono::duration_cast<std::chrono::milliseconds>(
        now.time_since_epoch()).count();
    
    std::string temp_file = config_.temp_dir + "/ista_konclude_" + 
                           std::to_string(timestamp) + ".owl";
    
    // Serialize ontology to OWL 2 XML (Konclude's preferred format)
    RDFXMLSerializer serializer;
    serializer.serializeToFile(ontology, temp_file);
    
    return temp_file;
}

std::string KoncludeWrapper::build_command(
    const std::string& command,
    const std::string& input_file,
    const std::string& output_file,
    const std::vector<std::string>& extra_args) {
    
    std::ostringstream cmd;
    cmd << config_.konclude_path << " " << command;
    cmd << " -i " << input_file;
    
    if (!output_file.empty()) {
        cmd << " -o " << output_file;
    }
    
    // Add worker threads
    if (config_.worker_threads > 0) {
        cmd << " -w " << config_.worker_threads;
    } else if (config_.worker_threads == -1) {
        cmd << " -w AUTO";
    }
    
    // Add verbose flag
    if (config_.verbose) {
        cmd << " -v";
    }
    
    // Add extra arguments
    for (const auto& arg : extra_args) {
        cmd << " " << arg;
    }
    
    return cmd.str();
}

double KoncludeWrapper::parse_timing_info(const std::string& output) {
    // Parse timing information from Konclude output
    // Look for patterns like "Time: 1234ms" or similar
    size_t pos = output.find("Time:");
    if (pos != std::string::npos) {
        size_t end = output.find("ms", pos);
        if (end != std::string::npos) {
            std::string time_str = output.substr(pos + 5, end - pos - 5);
            try {
                double ms = std::stod(time_str);
                return ms / 1000.0; // Convert to seconds
            } catch (...) {
                // Parsing failed, return 0
            }
        }
    }
    return 0.0;
}

ReasoningResult KoncludeWrapper::execute_command(
    const std::string& command,
    const std::string& input_file,
    const std::string& output_file,
    const std::vector<std::string>& extra_args) {
    
    ReasoningResult result;
    auto start = std::chrono::high_resolution_clock::now();
    
    // Build command
    std::string cmd = build_command(command, input_file, output_file, extra_args);
    
    if (config_.verbose) {
        std::cout << "Executing: " << cmd << std::endl;
    }
    
    // Execute command and capture output
#ifdef _WIN32
    cmd += " 2>&1";
    FILE* pipe = _popen(cmd.c_str(), "r");
#else
    cmd += " 2>&1";
    FILE* pipe = popen(cmd.c_str(), "r");
#endif
    
    if (!pipe) {
        result.success = false;
        result.error_message = "Failed to execute Konclude command";
        return result;
    }
    
    // Read output
    std::array<char, 128> buffer;
    std::string output;
    while (fgets(buffer.data(), buffer.size(), pipe) != nullptr) {
        output += buffer.data();
        if (config_.verbose) {
            std::cout << buffer.data();
        }
    }
    
#ifdef _WIN32
    int exit_code = _pclose(pipe);
#else
    int exit_code = pclose(pipe);
#endif
    
    auto end = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double> elapsed = end - start;
    result.reasoning_time_seconds = elapsed.count();
    
    // Check exit code
    if (exit_code != 0) {
        result.success = false;
        result.error_message = "Konclude returned non-zero exit code: " + 
                              std::to_string(exit_code) + "\n" + output;
        return result;
    }
    
    // Check for error patterns in output
    if (output.find("Error") != std::string::npos ||
        output.find("Exception") != std::string::npos) {
        result.success = false;
        result.error_message = "Konclude reported an error:\n" + output;
        return result;
    }
    
    result.success = true;
    last_output_file_ = output_file;
    
    // Parse timing if available from Konclude's output
    double konclude_time = parse_timing_info(output);
    if (konclude_time > 0) {
        result.reasoning_time_seconds = konclude_time;
    }
    
    return result;
}

ReasoningResult KoncludeWrapper::check_consistency(const Ontology& ontology) {
    // Save ontology to temp file
    std::string input_file = save_to_temp_file(ontology);
    
    // Konclude doesn't have a direct consistency command, but we can use
    // satisfiability of owl:Thing or check if classification succeeds
    std::string output_file = config_.temp_dir + "/konclude_consistency_output.owl";
    
    ReasoningResult result = execute_command("classification", input_file, output_file);
    
    // Clean up temp file
    std::filesystem::remove(input_file);
    
    if (result.success) {
        // If classification succeeded, ontology is consistent
        result.is_consistent = true;
    } else {
        // Check if error indicates inconsistency
        if (result.error_message.find("inconsistent") != std::string::npos ||
            result.error_message.find("Inconsistent") != std::string::npos) {
            result.is_consistent = false;
            result.success = true; // Operation succeeded, just found inconsistency
        }
    }
    
    return result;
}

ReasoningResult KoncludeWrapper::classify(const Ontology& ontology) {
    // Save ontology to temp file
    std::string input_file = save_to_temp_file(ontology);
    std::string output_file = config_.temp_dir + "/konclude_classified.owl";
    
    ReasoningResult result = execute_command("classification", input_file, output_file);
    
    // Clean up input temp file
    std::filesystem::remove(input_file);
    
    return result;
}

ReasoningResult KoncludeWrapper::realize(const Ontology& ontology) {
    // Save ontology to temp file
    std::string input_file = save_to_temp_file(ontology);
    std::string output_file = config_.temp_dir + "/konclude_realized.owl";
    
    ReasoningResult result = execute_command("realization", input_file, output_file);
    
    // Clean up input temp file
    std::filesystem::remove(input_file);
    
    return result;
}

ReasoningResult KoncludeWrapper::check_satisfiability(
    const Ontology& ontology, 
    const IRI& class_iri) {
    
    // Save ontology to temp file
    std::string input_file = save_to_temp_file(ontology);
    std::string output_file = config_.temp_dir + "/konclude_satisfiability.owl";
    
    // Add the class IRI argument
    std::vector<std::string> extra_args = {"-x", class_iri.toString()};
    
    ReasoningResult result = execute_command("satisfiability", input_file, output_file, extra_args);
    
    // Clean up temp file
    std::filesystem::remove(input_file);
    
    if (result.success) {
        // Check output to determine satisfiability
        // Konclude will indicate if the class is satisfiable
        std::ifstream ifs(output_file);
        std::string output_content((std::istreambuf_iterator<char>(ifs)),
                                  std::istreambuf_iterator<char>());
        
        // Look for satisfiability indicators in output
        if (output_content.find("satisfiable") != std::string::npos) {
            result.is_consistent = true;
        } else if (output_content.find("unsatisfiable") != std::string::npos) {
            result.is_consistent = false;
        }
    }
    
    return result;
}

std::optional<Ontology> KoncludeWrapper::load_inferred_ontology() {
    if (last_output_file_.empty() || !std::filesystem::exists(last_output_file_)) {
        return std::nullopt;
    }
    
    try {
        // Parse the output file
        RDFXMLParser parser;
        Ontology inferred = parser.parseFromFile(last_output_file_);
        return inferred;
    } catch (const std::exception& e) {
        std::cerr << "Failed to load inferred ontology: " << e.what() << std::endl;
        return std::nullopt;
    }
}

} // namespace reasoner
} // namespace owl2
} // namespace ista
