# Konclude OWL2 Reasoner Integration

This directory contains a complete integration of the **Konclude** OWL2 reasoner with the ISTA ontology library.

Konclude is a high-performance, parallel, tableau-based reasoner for OWL 2 DL that supports the full expressivity of the Description Logic SROIQV(D).

## Overview

The integration provides:

- **C++ Wrapper** (`lib/owl2/reasoner/konclude_wrapper.hpp/cpp`) - Direct C++ interface to Konclude
- **Python Interface** (`examples/konclude_reasoning_example.py`) - High-level Python API
- **Command-line Integration** - Seamless execution of Konclude reasoning tasks
- **Full OWL 2 Support** - Consistency, classification, realization, satisfiability

## Quick Start

### 1. Install Konclude

#### Option A: Download Pre-built Binary
```bash
# Linux
wget https://github.com/konclude/Konclude/releases/download/v0.7.0-1251/Konclude-v0.7.0-1251-Linux-x64-GCC-Static.zip
unzip Konclude-*.zip
sudo mv Konclude /usr/local/bin/

# macOS
# Download from GitHub releases and add to PATH

# Windows
# Download from GitHub releases
# Add to PATH or specify full path in code
```

#### Option B: Build from Source
```bash
git clone https://github.com/konclude/Konclude.git
cd Konclude
# Follow build instructions in repository
# Requires Qt framework
```

### 2. Verify Installation

```bash
Konclude --help
```

### 3. Run Example

```bash
cd examples/
python konclude_reasoning_example.py
```

## Python Usage

### Basic Example

```python
from ista import owl2
from konclude_reasoning_example import KoncludeReasoner

# Create ontology
onto = owl2.Ontology(owl2.IRI("http://example.org/test"))
# ... add classes, individuals, axioms ...

# Initialize reasoner
reasoner = KoncludeReasoner()

# Check consistency
result = reasoner.check_consistency(onto)
if result['consistent']:
    print("Ontology is consistent!")

# Classify (compute class hierarchy)
result = reasoner.classify(onto)
if result['success']:
    inferred_onto = result['inferred_ontology']
    print(f"Inferred {inferred_onto.get_axiom_count()} axioms")

# Realize (compute instance types)
result = reasoner.realize(onto)
if result['success']:
    realized_onto = result['inferred_ontology']
    # Contains inferred class assertions for individuals

# Check satisfiability
class_iri = owl2.IRI("http://example.org/test#MyClass")
result = reasoner.check_satisfiability(onto, class_iri)
if result['satisfiable']:
    print("Class is satisfiable")
```

### Advanced Configuration

```python
# Specify Konclude path
reasoner = KoncludeReasoner(
    konclude_path="/usr/local/bin/Konclude",
    worker_threads=4,      # Use 4 threads (-1 for auto)
    verbose=True           # Show Konclude output
)

# Check if available
if not reasoner.is_available():
    print("Konclude not found!")
```

## C++ Usage

The C++ wrapper provides the same functionality at the library level:

```cpp
#include "owl2/reasoner/konclude_wrapper.hpp"

using namespace ista::owl2::reasoner;

// Create configuration
KoncludeConfig config;
config.konclude_path = "/usr/local/bin/Konclude";
config.worker_threads = 4;
config.verbose = true;

// Initialize wrapper
KoncludeWrapper reasoner(config);

// Check consistency
Ontology onto = ...;
ReasoningResult result = reasoner.check_consistency(onto);
if (result.success && result.is_consistent) {
    std::cout << "Ontology is consistent!" << std::endl;
}

// Classify
result = reasoner.classify(onto);
if (result.success) {
    // Load inferred ontology
    auto inferred = reasoner.load_inferred_ontology();
    if (inferred.has_value()) {
        std::cout << "Inferred axioms: " 
                  << inferred->get_axiom_count() << std::endl;
    }
}

// Realize
result = reasoner.realize(onto);

// Check satisfiability
IRI class_iri("http://example.org/test#MyClass");
result = reasoner.check_satisfiability(onto, class_iri);
```

## Reasoning Tasks

### 1. Consistency Checking

Verifies that the ontology is logically consistent (has at least one model).

```python
result = reasoner.check_consistency(onto)
# Returns: {'success': bool, 'consistent': bool}
```

**Use Cases:**
- Validate ontology before deployment
- Detect logical contradictions
- Ensure modeling errors haven't been introduced

### 2. Classification

Computes the complete class hierarchy by inferring all subclass relationships.

```python
result = reasoner.classify(onto)
# Returns: {'success': bool, 'inferred_ontology': Ontology}
```

**What It Infers:**
- Transitive closure of subclass axioms
- Equivalent classes
- All implicit subsumption relationships

**Example:**
```
Given:    Dog ⊑ Mammal
          Mammal ⊑ Animal
          
Infers:   Dog ⊑ Animal  (transitive closure)
```

### 3. Realization

Computes the most specific classes for each individual.

```python
result = reasoner.realize(onto)
# Returns: {'success': bool, 'inferred_ontology': Ontology}
```

**What It Infers:**
- Direct types for all individuals
- All indirect types through class hierarchy

**Example:**
```
Given:    Fido : Dog
          Dog ⊑ Mammal
          Mammal ⊑ Animal
          
Infers:   Fido : Mammal  (indirect type)
          Fido : Animal  (indirect type)
```

### 4. Satisfiability Checking

Checks if a class can have instances (is not logically contradictory).

```python
result = reasoner.check_satisfiability(onto, class_iri)
# Returns: {'success': bool, 'satisfiable': bool}
```

**Use Cases:**
- Detect impossible class definitions
- Validate complex class expressions
- Find modeling errors in restrictions

## Performance

Konclude is designed for high performance:

| Ontology Size | Classification Time | Notes |
|---------------|---------------------|-------|
| Small (< 1K axioms) | < 1 second | Instantaneous |
| Medium (1K-10K axioms) | 1-10 seconds | Fast |
| Large (10K-100K axioms) | 10-60 seconds | Efficient |
| Very Large (> 100K axioms) | Minutes | Parallel processing helps |

### Performance Tuning

```python
# Use multiple worker threads
reasoner = KoncludeReasoner(worker_threads=8)

# Let Konclude auto-detect cores
reasoner = KoncludeReasoner(worker_threads=-1)

# For very large ontologies, increase system resources
# Konclude will automatically use available memory
```

## Integration Patterns

### Pattern 1: Inline Reasoning

Perform reasoning as part of your workflow:

```python
# Build ontology
onto = build_my_ontology()

# Validate consistency
if not reasoner.check_consistency(onto)['consistent']:
    raise ValueError("Ontology is inconsistent!")

# Classify and use inferred hierarchy
result = reasoner.classify(onto)
inferred = result['inferred_ontology']

# Proceed with inferred knowledge
process_ontology(inferred)
```

### Pattern 2: Preprocessing Pipeline

Use reasoning as a preprocessing step:

```python
# Load base ontology
base_onto = load_ontology("base.owl")

# Populate from data
populate_from_csv(base_onto, "data.csv")

# Realize to infer instance types
result = reasoner.realize(base_onto)
enriched = result['inferred_ontology']

# Export enriched ontology
owl2.RDFXMLSerializer.serialize_to_file(enriched, "enriched.owl")
```

### Pattern 3: Validation Service

Create a validation service:

```python
def validate_ontology(ontology_file):
    onto = owl2.RDFXMLParser.parse_from_file(ontology_file)
    reasoner = KoncludeReasoner()
    
    result = reasoner.check_consistency(onto)
    return {
        'valid': result['consistent'],
        'errors': [] if result['consistent'] else ['Ontology is inconsistent']
    }
```

## Troubleshooting

### Konclude Not Found

```
ERROR: Konclude is not available!
```

**Solutions:**
1. Add Konclude to PATH
2. Specify full path: `KoncludeReasoner(konclude_path="/full/path/to/Konclude")`
3. Download from: https://github.com/konclude/Konclude/releases

### Command Timeout

```
Konclude timed out
```

**Solutions:**
- Increase timeout in code: Modify `timeout=300` in `_execute_command()`
- Use more worker threads: `KoncludeReasoner(worker_threads=8)`
- Simplify ontology or use EL profile

### Memory Issues

```
Konclude crashed or killed
```

**Solutions:**
- Increase system memory
- Reduce ontology size
- Use OWL 2 EL profile (more efficient)
- Consider ELK reasoner for EL ontologies

### Parsing Errors

```
Failed to parse inferred ontology
```

**Solutions:**
- Check Konclude output for errors (use `verbose=True`)
- Verify input ontology is valid OWL 2
- Ensure serialization format is correct

## Command-Line Interface

You can also use Konclude directly from the command line:

```bash
# Consistency checking (via classification)
Konclude classification -i input.owl -o output.owl

# Classification with parallel workers
Konclude classification -i input.owl -o output.owl -w AUTO

# Realization
Konclude realization -i input.owl -o realized.owl

# Satisfiability checking
Konclude satisfiability -i input.owl -x "http://example.org/MyClass"

# With timing information
Konclude classification -i input.owl -o output.owl -v
```

## Comparison with Other Reasoners

| Feature | Konclude | HermiT | FaCT++ | ELK |
|---------|----------|--------|---------|-----|
| Language | C++ | Java | C++ | Java |
| OWL 2 Profile | Full DL | Full DL | Full DL | EL only |
| Parallel | Yes | No | No | Yes |
| Performance | Excellent | Good | Good | Excellent* |
| Integration | CLI | OWLAPI | CLI/JNI | OWLAPI |
| Active | Yes | Yes | Limited | Yes |

\* For EL profile only

### When to Use Konclude

**Use Konclude when:**
- You need high performance
- Working with large ontologies
- Require parallel processing
- Need full OWL 2 DL expressivity
- Working in C++ environment

**Consider alternatives when:**
- Using only OWL 2 EL (use ELK - faster for EL)
- Need tight Java integration (use HermiT via OWLAPI)
- Require interactive reasoning (use Protégé with built-in reasoners)

## Advanced Topics

### Custom IRI Resolution

For ontologies with imports:

```python
# Konclude will attempt to resolve imports
# Ensure imported ontologies are accessible
# Or pre-merge imports before reasoning
```

### OWLlink Protocol

Konclude also supports OWLlink for client-server reasoning:

```bash
# Start Konclude as OWLlink server
Konclude owllinkserver -p 8080

# Send OWLlink requests via HTTP
curl -X POST http://localhost:8080 -d @request.xml
```

### SPARQL Endpoint

Konclude can serve as a SPARQL endpoint:

```bash
# Start SPARQL server
Konclude sparqlserver -i ontology.owl -p 8080

# Query via HTTP POST
curl -X POST http://localhost:8080 \
  -H "Content-Type: application/sparql-query" \
  -d "SELECT ?s ?p ?o WHERE { ?s ?p ?o } LIMIT 10"
```

## Building the C++ Wrapper

To compile the C++ Konclude wrapper into ISTA:

```bash
# The wrapper is already in the source tree
cd build/
cmake ..
cmake --build . --config Release

# The wrapper will be compiled into libista
# Python bindings can be added to bindings_simple.cpp
```

## Example Output

```
============================================================
KONCLUDE OWL2 REASONER INTEGRATION EXAMPLE
============================================================

✓ C++ OWL2 bindings available
✓ Konclude reasoner available

[Step 1] Creating test ontology...
✓ Created test ontology:
  - 4 classes: Animal, Mammal, Dog, Cat
  - 2 individuals: Fido (Dog), Whiskers (Cat)
  - Class hierarchy: Dog ⊑ Mammal ⊑ Animal

Original ontology statistics:
  Total Axioms: 12
  Classes: 4
  Individuals: 2

[Step 2] Running reasoning tasks...

--- Checking Consistency ---
✓ Ontology is CONSISTENT

--- Running Classification ---
✓ Classification completed successfully
  Original axioms: 12
  Inferred axioms: 15

--- Running Realization ---
✓ Realization completed successfully
  Realized ontology axioms: 18

--- Checking Satisfiability of Dog ---
✓ Class is SATISFIABLE

============================================================
REASONING SUMMARY
============================================================
Consistency Check: ✓ PASSED
Classification: ✓ COMPLETED
Realization: ✓ COMPLETED
Satisfiability: ✓ SATISFIABLE
============================================================
```

## Resources

- **Konclude GitHub**: https://github.com/konclude/Konclude
- **Konclude Website**: https://www.derivo.de/products/konclude/
- **OWL 2 Specification**: https://www.w3.org/TR/owl2-overview/
- **Description Logic**: https://en.wikipedia.org/wiki/Description_logic

## License

The Konclude wrapper integration is part of ISTA. Konclude itself is licensed under LGPLv3.

## See Also

- `native_csv_population_example.py` - Populating ontologies from CSV
- `owl2_example.py` - Basic OWL2 ontology creation
- `graph_conversion_example.py` - Converting ontologies to graphs
