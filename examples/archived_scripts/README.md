# Archived Scripts

This directory contains older iteration scripts that have been superseded by consolidated versions. These scripts are kept for reference purposes but are no longer maintained.

## Superseded By

### Drug Relationship Scripts
All of these have been replaced by the consolidated scripts in `../drugbank_examples/`:

**Old scripts (17 files):**
- `add_all_drug_relationships_direct.py`
- `add_drug_adverse_event_relationships_direct.py`
- `add_drug_contraindication_relationships_direct.py`
- `add_drug_contraindication_relationships_example.py`
- `add_drug_disease_relationships_direct.py`
- `add_drug_disease_relationships_example.py`
- `add_drug_interaction_relationships_direct.py`
- `add_drug_relationships_combined_direct.py`
- `add_drug_relationships_combined_example.py`
- `adverse_event_map.py`
- `contraindication_map.py`
- `drug_interaction_map.py`
- `indication_map.py`
- `filter_adverse_event_mappings_by_ontology.py`
- `filter_contraindication_mappings_by_ontology.py`
- `filter_drug_interaction_mappings_by_ontology.py`
- `filter_mappings_by_ontology.py`

**Replaced by (2 files):**
- `../drugbank_examples/add_drug_relationships.py` - Single script handles all relationship types
- `../drugbank_examples/filter_drug_mappings.py` - Single script handles all filtering

### Debug/Test Scripts
These were temporary debugging scripts during development:

- `debug_ontology_iris.py` - IRI debugging
- `debug_rdf_roundtrip.py` - RDF serialization debugging
- `simple_iri_test.py` - Basic IRI tests
- `test_new_api.py` - API transition testing
- `test_rdf_parsing.py` - RDF parser testing
- `test_rdf_parsing_for_memgraph.py` - Memgraph-specific parsing tests

**Replaced by:**
- Proper test suite in `../tests/`
- Example scripts that demonstrate correct usage

## Using These Scripts

⚠️ **Warning:** These scripts may not work with the current API as they were written for earlier versions. Use the new consolidated scripts instead.

If you need to reference the old implementation for some reason, these scripts show the evolution of the codebase.
