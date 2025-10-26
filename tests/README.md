# Tests Directory

This directory contains test files for the ista package, specifically for testing the C++ OWL2 library bindings.

## Test Files

### Python Test Scripts

- **`test_simple_bindings.py`** - Tests basic Python bindings functionality
  - Tests IRI, Class, ObjectProperty, DataProperty creation
  - Tests axiom creation (Declaration, SubClassOf, ClassAssertion, etc.)
  - Tests ontology manipulation
  - Tests serialization to RDF/XML and Functional Syntax
  - Creates test output files for verification

- **`test_parser.py`** - Tests RDF/XML parser functionality
  - Tests parsing RDF/XML files
  - Tests round-trip (create → serialize → parse → verify)
  - Verifies axiom preservation and correctness

- **`test_subgraph.py`** - Tests high-performance subgraph extraction
  - Tests `OntologyFilter` functionality
  - Tests filtering by individuals, classes
  - Tests neighborhood extraction (k-hop BFS)
  - Tests path finding between individuals
  - Tests random sampling
  - Tests convenience methods on Ontology class

### Test Output Files

Generated files from running tests (gitignored):

- `*.rdf` - RDF/XML serialization output
- `*.owl` - OWL file output
- `*.ofn` - Functional Syntax output

## Running Tests

### Individual Test Files

```bash
# From repository root
python tests/test_simple_bindings.py
python tests/test_parser.py
python tests/test_subgraph.py
```

### Running All Tests

```bash
# Run all tests
cd tests
for test in test_*.py; do
    echo "Running $test..."
    python "$test"
done
```

## Prerequisites

The C++ extension must be built before running tests:

```bash
# Option 1: Install in development mode
pip install -e .

# Option 2: Manual build
mkdir build && cd build
cmake .. -DBUILD_PYTHON_BINDINGS=ON
cmake --build . --config Release
```

## Test Coverage

The tests cover:

- ✓ Core OWL2 types (IRI, Literal, Entity)
- ✓ Entity creation (Class, ObjectProperty, DataProperty, NamedIndividual)
- ✓ Class expressions (NamedClass)
- ✓ Axiom types (Declaration, SubClassOf, ClassAssertion, PropertyAssertion, etc.)
- ✓ Ontology container operations
- ✓ RDF/XML serialization
- ✓ Functional Syntax serialization
- ✓ RDF/XML parsing
- ✓ Round-trip preservation
- ✓ Subgraph extraction and filtering
- ✓ Graph traversal algorithms (BFS, path finding)

## Notes

- Tests use the public `ista.owl2` API (not `_libista_owl2` directly)
- Test output files are automatically generated and can be inspected
- All tests should pass without errors when the C++ extension is properly built
