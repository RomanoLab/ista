# Ista Documentation

This directory contains the source files for building the ista library documentation.

## Building Documentation

### Prerequisites

```bash
pip install sphinx sphinx-rtd-theme breathe numpydoc myst-parser
```

### Quick Build

```bash
cd docs
sphinx-build -b html source build/html
```

Output will be in `build/html/index.html`

### Full Build (with C++ API)

```bash
cd docs
doxygen Doxyfile
sphinx-build -b html source build/html
```

## Documentation Structure

```
docs/
├── source/               # Sphinx source files
│   ├── api/             # Python API reference
│   ├── cpp_api/         # C++ API reference
│   ├── user_guide/      # User guides and tutorials
│   └── conf.py          # Sphinx configuration
├── Doxyfile             # Doxygen configuration
└── build/               # Generated documentation (not in git)
```

## Common Issues

### "Unknown document" errors
Install myst-parser for Markdown support:
```bash
pip install myst-parser
```

### Module import errors
Install the package in development mode:
```bash
cd /path/to/ista
pip install -e .
```

### Breathe/Doxygen warnings
Generate Doxygen XML first:
```bash
cd docs && doxygen Doxyfile
```

## Documentation Status

### Python API
- ✅ Core OWL 2 classes (IRI, Literal, Entity types, etc.)
- ✅ All axiom types
- ✅ Ontology container with full API
- ✅ All parsers (RDFXMLParser fully implemented, others are stubs)
- ✅ All serializers (RDFXMLSerializer, FunctionalSyntaxSerializer fully implemented, others are stubs)
- ✅ CSV parser (fully implemented)
- ✅ Subgraph extraction (OntologyFilter)

### C++ API
- ✅ Complete Doxygen comments in all header files
- ✅ Comprehensive reference documentation for core, parsers, serializers
- ✅ Code examples and best practices

## Adding New Documentation

### For Python Classes

1. Add pybind11 bindings with docstrings in `lib/python/bindings_simple.cpp`
2. Add to appropriate RST file in `docs/source/api/`
3. Use NumPy-style docstrings

### For C++ Classes

1. Add Doxygen comments to header file (`@brief`, `@param`, `@return`)
2. Add to appropriate RST file in `docs/source/cpp_api/`
3. Ensure Doxyfile includes the file's directory

## Related Files

- **Integration guides**: `README_CSV_POPULATION.md`, `README_KONCLUDE_INTEGRATION.md`, `README_MEMGRAPH_INTEGRATION.md`
- **IDE setup**: `IDE_SETUP.md`
- **Main project README**: `../README.md`

## More Information

- Sphinx documentation: https://www.sphinx-doc.org/
- Breathe (C++ bridge): https://breathe.readthedocs.io/
- MyST Parser (Markdown): https://myst-parser.readthedocs.io/
- NumPy docstring guide: https://numpydoc.readthedocs.io/
