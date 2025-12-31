# DrugBank Integration Examples

This directory contains scripts and data for integrating DrugBank drug information into knowledge graphs like NeuroKB.

## Scripts

### add_drug_relationships.py
Consolidated script for adding drug relationships to ontologies. Replaces the 17 individual scripts that were previously scattered.

```bash
# Add all drug relationships
python add_drug_relationships.py --type all --input ../kg_projects/neurokb/neurokb.rdf

# Add specific relationship types
python add_drug_relationships.py --type indications --input neurokb.rdf
python add_drug_relationships.py --type interactions --input neurokb.rdf
python add_drug_relationships.py --type adverse-events --input neurokb.rdf
python add_drug_relationships.py --type contraindications --input neurokb.rdf
```

### filter_drug_mappings.py
Filters drug mapping CSV files to only include entries where entities exist in the ontology.

```bash
# Filter all mappings
python filter_drug_mappings.py --type all --ontology neurokb.rdf

# Filter specific mappings
python filter_drug_mappings.py --type indications --ontology neurokb.rdf
```

### check_severity_levels.py
Utility to check and analyze severity levels in drug interaction data.

## Data Files

- `drug_disease_mappings.csv` / `drug_disease_mappings_filtered.csv` - Drug-disease indication mappings
- `drug_interaction_mappings.csv` / `drug_interaction_mappings_filtered.csv` - Drug-drug interaction mappings
- `drug_adverse_event_mappings.csv` / `drug_adverse_event_mappings_filtered.csv` - Drug adverse event mappings
- `drug_contraindication_mappings.csv` / `drug_contraindication_mappings_filtered.csv` - Drug contraindication mappings

The `*_filtered.csv` versions contain only entries where both entities exist in the target ontology.

## Documentation

See the main examples directory for:
- `DRUGBANK_INTEGRATION_README.md` - Detailed integration instructions
- `COMPLETE_WORKFLOW.md` - Complete workflow for building knowledge graphs

## Legacy Scripts

Old individual scripts have been moved to `../archived_scripts/` for reference but are superseded by the consolidated scripts above.
