# Native CSV Ontology Population

This directory contains an example demonstrating how to populate OWL2 ontologies from large flat CSV files using the native C++ `owl2` library.

## Overview

The `native_csv_population_example.py` script shows how to:

1. **Create an ontology structure** - Define classes, properties, and relationships
2. **Load instances from CSV files** - Dynamically create individuals from CSV rows
3. **Create relationships** - Link individuals based on CSV data
4. **Serialize results** - Export the populated ontology to RDF/XML format

## Key Features

- **Native C++ Performance**: Uses the high-performance `ista.owl2` C++ library
- **No owlready2 Dependency**: Pure C++ backend for maximum speed and minimal memory overhead
- **Large Dataset Support**: Designed for populating very large ontologies from massive CSV files
- **Memory Efficient**: Direct CSV parsing without intermediate data structures
- **Full OWL2 Support**: Complete access to OWL2 axioms and constructs

## Quick Start

```bash
# Navigate to examples directory
cd examples/

# Run the example
python native_csv_population_example.py
```

The script will:
- Create sample CSV files (authors, books, authorship relationships)
- Build an ontology structure
- Populate it with 5 authors, 5 books, and their relationships
- Save the result to `library_catalog_native.rdf`

## Example Output

```
============================================================
NATIVE CSV ONTOLOGY POPULATION EXAMPLE
============================================================

✓ C++ OWL2 bindings are available
✓ Sample data created in 'csv_data/' directory
✓ Library ontology structure created
✓ Loaded 5 authors
✓ Loaded 5 books
✓ Created 5 relationships

Ontology Statistics:
  Total Axioms: 82
  Total Individuals: 10
  Classes: 2
  Object Properties: 1
  Data Properties: 9
```

## Architecture

### Data Flow

```
CSV Files → Python Parser → owl2 C++ API → OWL2 Ontology → RDF/XML
```

### Implementation Pattern

```python
from ista import owl2

# 1. Create ontology
onto = owl2.Ontology(owl2.IRI("http://example.org/library"))

# 2. Define structure
class_iri = owl2.IRI("http://example.org/library#Author")
onto.add_axiom(owl2.Declaration(owl2.EntityType.CLASS, class_iri))

# 3. Load CSV data
import csv
with open('authors.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        # Create individual
        individual_iri = owl2.IRI(f"http://example.org/library#{row['id']}")
        individual = owl2.NamedIndividual(individual_iri)
        
        # Declare and assert class membership
        onto.add_axiom(owl2.Declaration(owl2.EntityType.NAMED_INDIVIDUAL, individual_iri))
        onto.add_axiom(owl2.ClassAssertion(owl2.Class(class_iri), individual))
        
        # Add properties
        prop = owl2.DataProperty(owl2.IRI("http://example.org/library#name"))
        literal = owl2.Literal(row['name'])
        onto.add_axiom(owl2.DataPropertyAssertion(prop, individual, literal))

# 4. Serialize
owl2.RDFXMLSerializer.serialize_to_file(onto, "output.rdf")
```

## CSV File Format

### authors.csv
```csv
author_id,name,birth_year,nationality
AUTH001,Jane Austen,1775,British
AUTH002,Mark Twain,1835,American
```

### books.csv
```csv
book_id,title,publication_year,genre,pages
BOOK001,Pride and Prejudice,1813,Romance,432
BOOK002,Adventures of Huckleberry Finn,1884,Adventure,366
```

### authorship.csv (relationships)
```csv
book_id,author_id
BOOK001,AUTH001
BOOK002,AUTH002
```

## Performance Considerations

### For Large Datasets

1. **Batch Processing**: Process CSV files in chunks for very large datasets
2. **Property Caching**: Cache frequently-used property IRIs
3. **Individual Lookup**: Build indexes for fast individual lookup when creating relationships
4. **Memory Management**: The C++ backend handles memory efficiently, but be mindful of Python object creation

### Benchmark

On a typical system:
- **Small datasets** (< 1K rows): Instantaneous
- **Medium datasets** (1K-100K rows): Seconds to minutes
- **Large datasets** (100K-1M rows): Minutes to hours
- **Very large datasets** (> 1M rows): Consider database-backed approaches

## Customization

### Adding Data Transforms

```python
# Convert string to integer
value = int(row['birth_year'])
literal = owl2.Literal(str(value))
```

### Filtering Rows

```python
for row in reader:
    if row['nationality'] == 'British':  # Filter condition
        # Process row...
```

### Handling Missing Data

```python
for row in reader:
    if row.get('birth_year'):  # Only add if present
        # Add property...
```

## Performance Characteristics

| Aspect | Native owl2 |
|--------|-------------|
| Performance | High (C++) |
| Memory Usage | Low |
| API Style | Direct, explicit |
| Dataset Size | Very Large |
| Dependencies | None (native) |

## Advanced Usage

### Creating Complex Relationships

```python
# Object property assertions between individuals
written_by = owl2.ObjectProperty(owl2.IRI("http://example.org/library#writtenBy"))
onto.add_axiom(owl2.ObjectPropertyAssertion(written_by, book, author))
```

### Data Property Types

```python
# String literal
owl2.Literal("Jane Austen")

# Typed literal (integer)
owl2.Literal("42", owl2.xsd.INTEGER)

# Language-tagged literal
owl2.Literal("Bonjour", language_tag="fr")
```

### Multiple CSV Sources

```python
# Load from multiple files
load_authors_from_csv(onto, "authors.csv")
load_books_from_csv(onto, "books.csv")
load_publishers_from_csv(onto, "publishers.csv")
load_relationships_from_csv(onto, "book_authors.csv")
load_relationships_from_csv(onto, "book_publishers.csv")
```

## Troubleshooting

### C++ Extensions Not Built

```
ERROR: C++ OWL2 bindings are not available!
```

**Solution**: Build the C++ extensions:
```bash
pip install -e .
# Or manually:
mkdir build && cd build
cmake .. && cmake --build .
cmake --install .
```

### Encoding Errors (Windows)

```
UnicodeEncodeError: 'charmap' codec can't encode character
```

**Solution**: Already handled in the example with:
```python
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
```

### Memory Issues with Very Large Files

**Solution**: Process in chunks:
```python
chunk_size = 10000
for chunk in pd.read_csv('large_file.csv', chunksize=chunk_size):
    for _, row in chunk.iterrows():
        # Process row...
```

## Future Enhancements

The C++ CSV parser implementation (`lib/owl2/parser/csv_parser.cpp`) provides additional features:

- **Built-in filtering**: Filter rows based on column values
- **Data transforms**: Apply functions to transform values during parsing  
- **Merge mode**: Update existing individuals instead of creating duplicates
- **Automatic IRI generation**: Configurable IRI creation strategies

These features are available in the C++ API but require completing the Python bindings integration.

## See Also

- `owl2_example.py` - Basic OWL2 ontology creation
- `graph_conversion_example.py` - Converting ontologies to/from graphs
- `kg_projects/alzkb/alzkb.py` - Real-world large-scale example

## License

Part of the ISTA (Knowledge in Sindarin) project.
