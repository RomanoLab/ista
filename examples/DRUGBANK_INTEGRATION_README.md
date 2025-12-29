# DrugBank to NeuroKB Integration Guide

This guide explains how to integrate DrugBank drug relationships into the NeuroKB ontology.

## Overview

Four types of relationships can be added:
1. **Drug Indications** (drugTreatsDisease) - diseases a drug is used to treat
2. **Drug Contraindications** (drugContraindicatedForDisease) - diseases for which a drug is contraindicated
3. **Drug Adverse Events** (drugCausesAdverseEvent) - diseases/conditions caused as side effects
4. **Drug-Drug Interactions** (drugInteractsWithDrug) - major severity interactions between drugs

## Prerequisites

- DrugBank CSV files in `D:/data/drugbank/2025-11-19/`
- NeuroKB RDF file at `kg_projects/neurokb/neurokb-populated.rdf`
- Python with pandas and ista libraries installed

## Workflow

**IMPORTANT:** Use the `*_direct.py` scripts which directly modify the RDF file. The older scripts that use the ista RDF parser lose data because the parser only loads TBox (classes/properties) but not ABox (individuals/assertions).

### Option 1: Add Only Indications

```bash
cd D:\projects\ista\examples

# Step 1: Extract drug-disease indication mappings from DrugBank
python indication_map.py
# Output: drug_disease_mappings.csv (15,753 pairs)

# Step 2: Filter to only entities that exist in NeuroKB
python filter_mappings_by_ontology.py
# Output: drug_disease_mappings_filtered.csv (185 pairs)

# Step 3: Add relationships to ontology (DIRECT RDF MODIFICATION)
python add_drug_disease_relationships_direct.py
# Output: kg_projects/neurokb/neurokb-with-indications.rdf (246 MB - preserves all content)
```

### Option 2: Add Only Contraindications

```bash
cd D:\projects\ista\examples

# Step 1: Extract drug-disease contraindication mappings from DrugBank
python contraindication_map.py
# Output: drug_contraindication_mappings.csv (9,294 pairs)

# Step 2: Filter to only entities that exist in NeuroKB
python filter_contraindication_mappings_by_ontology.py
# Output: drug_contraindication_mappings_filtered.csv (166 pairs)

# Step 3: Add relationships to ontology (DIRECT RDF MODIFICATION)
python add_drug_contraindication_relationships_direct.py
# Output: kg_projects/neurokb/neurokb-with-contraindications.rdf (246 MB - preserves all content)
```

### Option 3: Add Indications + Contraindications

```bash
cd D:\projects\ista\examples

# Steps 1-2: Extract and filter indications
python indication_map.py
python filter_mappings_by_ontology.py

# Steps 3-4: Extract and filter contraindications
python contraindication_map.py
python filter_contraindication_mappings_by_ontology.py

# Step 5: Add both types of relationships (DIRECT RDF MODIFICATION)
python add_drug_relationships_combined_direct.py
# Output: kg_projects/neurokb/neurokb-with-drug-relationships.rdf
```

### Option 4: Add Adverse Events Only

```bash
cd D:\projects\ista\examples

# Step 1: Extract drug-disease adverse event mappings from DrugBank
python adverse_event_map.py
# Output: drug_adverse_event_mappings.csv (314,458 pairs)

# Step 2: Filter to only entities that exist in NeuroKB
python filter_adverse_event_mappings_by_ontology.py
# Output: drug_adverse_event_mappings_filtered.csv (142 pairs)

# Step 3: Add relationships to ontology (DIRECT RDF MODIFICATION)
python add_drug_adverse_event_relationships_direct.py
# Output: kg_projects/neurokb/neurokb-with-adverse-events.rdf
```

### Option 5: Add Drug Interactions Only

```bash
cd D:\projects\ista\examples

# Step 1: Extract major severity drug-drug interactions from DrugBank
python drug_interaction_map.py
# Output: drug_interaction_mappings.csv (154,684 pairs - major severity only)

# Step 2: Filter to only drugs that exist in NeuroKB
python filter_drug_interaction_mappings_by_ontology.py
# Output: drug_interaction_mappings_filtered.csv (152,780 pairs)

# Step 3: Add relationships to ontology (DIRECT RDF MODIFICATION)
python add_drug_interaction_relationships_direct.py
# Output: kg_projects/neurokb/neurokb-with-drug-interactions.rdf
```

### Option 6: Add Everything (Recommended)

```bash
cd D:\projects\ista\examples

# Extract and filter all relationship types
python indication_map.py
python filter_mappings_by_ontology.py
python contraindication_map.py
python filter_contraindication_mappings_by_ontology.py
python adverse_event_map.py
python filter_adverse_event_mappings_by_ontology.py
python drug_interaction_map.py
python filter_drug_interaction_mappings_by_ontology.py

# Add all relationships in one go (DIRECT RDF MODIFICATION)
python add_all_drug_relationships_direct.py
# Output: kg_projects/neurokb/neurokb-with-all-drug-relationships.rdf (280 MB)
```

## Script Descriptions

### Mapping Scripts

**`indication_map.py`**
- Reads DrugBank's `structured_indications.csv`
- Maps internal condition IDs to UMLS CUIs
- Outputs drug-disease indication pairs
- Filtering options: country, off-label status

**`contraindication_map.py`**
- Reads DrugBank's `structured_contraindications.csv` and `contraindication_conditions.csv`
- Maps internal condition IDs to UMLS CUIs
- Outputs drug-disease contraindication pairs
- Filtering options: country/region

**`adverse_event_map.py`**
- Reads DrugBank's `structured_adverse_effects.csv` and `adverse_effect_conditions.csv`
- Maps internal condition IDs to UMLS CUIs
- Outputs drug-disease adverse event pairs (side effects)
- Filtering options: country/region

**`drug_interaction_map.py`**
- Reads DrugBank's `structured_drug_interactions.csv`
- Filters for major severity interactions (severity = 2)
- Outputs drug-drug interaction pairs with both DrugBank IDs included
- Note: Interactions are already drug-to-drug, no disease mapping needed
- Filtering options: severity level (0=minor, 1=moderate, 2=major), evidence level

### Filtering Scripts

**`filter_mappings_by_ontology.py`**
- Reads neurokb RDF file to find existing drugs and diseases
- Filters indication mappings to only include entities in neurokb
- NeuroKB has 36,958 drugs but only 274 diseases (neurological focus)

**`filter_contraindication_mappings_by_ontology.py`**
- Same as above but for contraindications
- Ensures both drug and disease exist in the target ontology

**`filter_adverse_event_mappings_by_ontology.py`**
- Filters adverse event mappings to only include entities in neurokb
- Ensures both drug and disease exist

**`filter_drug_interaction_mappings_by_ontology.py`**
- Filters drug interaction mappings to only include drugs in neurokb
- Ensures both subject and affected drugs exist
- Very high pass-through rate (98.8%) because neurokb has comprehensive drug coverage

### Integration Scripts

**`add_drug_disease_relationships_example.py`**
- Adds `drugTreatsDisease` relationships (existing property in neurokb)
- Loads filtered indication mappings
- Adds ObjectPropertyAssertion axioms

**`add_drug_contraindication_relationships_example.py`**
- Creates new `drugContraindicatedForDisease` object property
- Sets domain: Chemical, range: Disease
- Loads filtered contraindication mappings
- Adds ObjectPropertyAssertion axioms

**`add_drug_relationships_combined_direct.py`**
- Direct RDF modification version of combined indications + contraindications
- Preserves all original content
- Single output file with both relationship types

**`add_drug_adverse_event_relationships_direct.py`**
- Creates new `drugCausesAdverseEvent` object property
- Direct RDF modification - preserves all original content
- Loads filtered adverse event mappings
- Adds ObjectPropertyAssertion axioms

**`add_drug_interaction_relationships_direct.py`**
- Creates new `drugInteractsWithDrug` object property (symmetric)
- Direct RDF modification - preserves all original content
- Loads filtered drug interaction mappings (major severity only)
- Adds 152,780 drug-drug interaction assertions

**`add_all_drug_relationships_direct.py`**
- All-in-one script that adds all four relationship types
- Creates all three new properties
- Preserves all original content
- Most comprehensive option (153,273 total relationships)

## Data Statistics

### After Filtering (entities in NeuroKB)

**Indications:**
- 185 drug-disease pairs
- 88 unique drugs
- 111 unique diseases

**Contraindications:**
- 166 drug-disease pairs
- 62 unique drugs
- 22 unique diseases

**Adverse Events:**
- 142 drug-disease pairs
- 72 unique drugs
- 16 unique diseases

**Drug Interactions (Major Severity):**
- 152,780 drug-drug pairs
- 3,017 unique drugs involved

**Total Relationships:** 153,273 when all four types are included

### Why Different Numbers?

**Drug-Disease relationships (indications, contraindications, adverse events):**
- NeuroKB contains only 274 diseases (neurological focus)
- DrugBank has mappings for 10,000+ diseases
- Most relationships are filtered out because the disease doesn't exist in NeuroKB

**Drug-Drug interactions:**
- NeuroKB contains 36,958 drugs (comprehensive)
- Very high coverage: 152,780 out of 154,684 major severity interactions preserved (98.8%)
- Only 41 drugs from interactions not in NeuroKB

## UMLS CUI Mapping

Both workflows map DrugBank's internal condition IDs to UMLS CUIs (Concept Unique Identifiers) because:

1. NeuroKB uses UMLS CUIs for disease identification
   - Disease individuals: `#disease_c0002395` (where C0002395 is the UMLS CUI)

2. DrugBank provides UMLS mappings in `condition_external_identifiers.csv`
   - No external services or downloads needed

3. Naming conventions in NeuroKB:
   - Drugs: `#drug_db00001` (DrugBank ID lowercased)
   - Diseases: `#disease_c0002395` (UMLS CUI lowercased)

## New Object Properties

The integration workflows create three new object properties:

```
drugContraindicatedForDisease
  Domain: Chemical
  Range: Disease
  SubPropertyOf: chemicalObjectProperty
  Purpose: Indicates a drug is contraindicated for a specific disease

drugCausesAdverseEvent
  Domain: Chemical
  Range: Disease
  SubPropertyOf: chemicalObjectProperty
  Purpose: Indicates a drug can cause an adverse event (side effect)
           manifesting as a specific disease or condition

drugInteractsWithDrug
  Domain: Chemical
  Range: Chemical
  SubPropertyOf: chemicalObjectProperty
  Type: SymmetricProperty
  Purpose: Indicates a major severity drug-drug interaction where one drug
           significantly affects the pharmacokinetics or pharmacodynamics
           of another, potentially causing serious adverse effects
```

These complement the existing `drugTreatsDisease` property in neurokb.

## Troubleshooting

### Issue: Output file is much smaller than input (data loss)

**Symptoms:**
- Input file: 243 MB
- Output file: 125 KB
- Individuals are missing from the output

**Cause:** The ista `RDFXMLParser` only loads the TBox (classes, properties, and their axioms) but not the ABox (individuals and their property assertions). When you serialize back with `RDFXMLSerializer`, you only get the TBox.

**Solution:** Use the `*_direct.py` scripts which directly modify the RDF file without round-tripping through the parser:
- `add_drug_disease_relationships_direct.py`
- `add_drug_contraindication_relationships_direct.py`
- `add_drug_relationships_combined_direct.py` (recommended)

These scripts:
1. Read the RDF file as text
2. Insert new property declarations after existing properties
3. Append new property assertions before the closing `</rdf:RDF>` tag
4. Preserve 100% of the original content

**Result:** Output file is 246 MB (original 243 MB + 3.5 MB of new relationships)

### Issue: "No individuals found" when using get_individuals()

**Cause:** The ista RDF parser doesn't extract individuals from typed RDF declarations

**Impact:** This doesn't affect the `*_direct.py` scripts since they don't use the parser for reading individuals

**Note:** The older `add_drug_disease_relationships_example.py` and similar scripts are deprecated due to this issue

## Output Files

All output files are saved to:
- CSV mappings: `examples/` directory
- Modified ontologies: `examples/kg_projects/neurokb/` directory

Files generated:
- `drug_disease_mappings.csv` - All indication mappings
- `drug_disease_mappings_filtered.csv` - Indications in neurokb
- `drug_contraindication_mappings.csv` - All contraindication mappings
- `drug_contraindication_mappings_filtered.csv` - Contraindications in neurokb
- `neurokb-with-indications.rdf` - Ontology with indications
- `neurokb-with-contraindications.rdf` - Ontology with contraindications
- `neurokb-with-drug-relationships.rdf` - Ontology with both (recommended)
