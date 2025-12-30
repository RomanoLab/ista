# Ista Test Suite

This directory contains the test suite for the ista library.

## Running Tests

### Install Test Dependencies

```bash
# Install all test dependencies
pip install -e ".[test]"

# Or install development dependencies (includes docs)
pip install -e ".[dev]"
```

### Run All Tests

```bash
# Run all tests with coverage
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_owl2_parsers.py

# Run specific test class
pytest tests/test_owl2_parsers.py::TestTurtleParser

# Run specific test
pytest tests/test_owl2_parsers.py::TestTurtleParser::test_parser_exists
```

### Test Coverage

```bash
# Run tests with coverage report
pytest --cov=ista --cov-report=html

# View coverage report
# Open htmlcov/index.html in browser

# Generate XML coverage (for CI/CD)
pytest --cov=ista --cov-report=xml
```

### Test Markers

Tests are organized with markers:

```bash
# Run only parser tests
pytest -m parser

# Run only serializer tests
pytest -m serializer

# Run only unit tests (fast)
pytest -m unit

# Skip slow tests
pytest -m "not slow"
```

## Test Organization

```
tests/
├── test_owl2_parsers.py      # Parser binding tests
├── test_owl2_serializers.py  # Serializer binding tests
├── test_simple_bindings.py   # Core bindings tests
├── test_parser.py            # Parser functionality tests
├── test_subgraph.py          # Subgraph extraction tests
└── README.md                 # This file
```

## Test Coverage Requirements

**Per CLAUDE.md**: Code coverage is a requirement, not just something that is good to have. Every line of executable code must be covered by tests.

### Current Coverage Status

- ✅ Parser bindings - All new parsers tested
- ✅ Serializer bindings - All new serializers tested
- ⏳ Full implementation coverage - In progress

### Adding New Tests

When adding new features:

1. **Create test file** in `tests/` with pattern `test_*.py`
2. **Write tests** using pytest conventions
3. **Add markers** for organization
4. **Run coverage** to ensure all lines are covered
5. **Update this README** with coverage status

Example test:

```python
import pytest
from ista import owl2

class TestMyFeature:
    """Tests for my new feature."""
    
    def test_feature_exists(self):
        """Test that feature exists."""
        assert hasattr(owl2, 'MyFeature')
    
    def test_feature_works(self):
        """Test that feature works correctly."""
        result = owl2.MyFeature()
        assert result is not None
```

## Continuous Integration

Tests should be run automatically on:
- Every commit (pre-commit hook)
- Every pull request (CI/CD)
- Before release

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: |
          pip install -e ".[test]"
      - name: Run tests
        run: |
          pytest --cov=ista --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

## Test Best Practices

### Naming Conventions
- Test files: `test_*.py`
- Test classes: `Test*`
- Test functions: `test_*`

### Test Structure
```python
def test_descriptive_name():
    """Clear docstring describing what is tested."""
    # Arrange - Set up test data
    data = setup_test_data()
    
    # Act - Execute the code being tested
    result = function_under_test(data)
    
    # Assert - Verify the results
    assert result == expected_value
```

### Markers
Add markers to organize tests:
```python
@pytest.mark.slow
def test_large_dataset():
    """Test with large dataset (marked as slow)."""
    pass

@pytest.mark.parser
def test_parser_feature():
    """Test parser feature (marked as parser)."""
    pass
```

### Fixtures
Use fixtures for shared setup:
```python
@pytest.fixture
def sample_ontology():
    """Create sample ontology for testing."""
    onto = owl2.Ontology(owl2.IRI("http://example.org/test"))
    return onto

def test_with_ontology(sample_ontology):
    """Test using fixture."""
    assert sample_ontology.get_axiom_count() == 0
```

## Coverage Goals

### Short-term (Current Release)
- ✅ All Python bindings tested (100%)
- ✅ Core parser/serializer APIs tested (100%)
- ⏳ Edge cases and error handling (Target: 90%)

### Long-term
- All executable lines covered (Target: 95%+)
- All branches covered (Target: 90%+)
- Integration tests for all major workflows
- Performance regression tests

## Troubleshooting

### Tests fail with "No module named 'ista'"
```bash
# Install package in development mode
pip install -e .
```

### Coverage report missing files
```bash
# Ensure source is installed in editable mode
pip install -e .

# Run with explicit source
pytest --cov=ista --cov-report=term-missing
```

### Tests timeout
```bash
# Increase timeout (default 300s)
pytest --timeout=600
```

## More Information

- Pytest documentation: https://docs.pytest.org/
- Coverage.py documentation: https://coverage.readthedocs.io/
- CLAUDE.md: Project-specific testing requirements
