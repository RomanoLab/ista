"""Preprocess DrugBank CSV files into flat tables for ista_populate.

This script joins multi-table DrugBank relationships (indications,
adverse effects, contraindications) into single TSV files that ista
can load directly. It also builds a drug lookup table with DrugBank IDs,
ADMET properties, and other metadata.

Usage
-----
    python preprocess_drugbank.py <drugbank_data_dir> <output_dir>

Example
-------
    python preprocess_drugbank.py D:/data/drugbank/2025-11-19 D:/data/drugbank/2025-11-19/CUSTOM
"""

import csv
import os
import sys
from pathlib import Path


def load_csv_dict(filepath, key_col, val_cols=None):
    """Load a CSV into a dict keyed by key_col."""
    result = {}
    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        for row in reader:
            k = row.get(key_col, "")
            if not k:
                continue
            if val_cols:
                result[k] = {c: row.get(c, "") for c in val_cols}
            else:
                result[k] = row
    return result


def build_drug_lookup(data_dir):
    """Build drug_id -> drugbank_id mapping from drugs.csv."""
    drugs = {}
    path = data_dir / "drugs.csv"
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        for row in reader:
            drugs[row["id"]] = {
                "drugbank_id": row["drugbank_id"],
                "name": row["name"],
                "cas_number": row.get("cas_number", ""),
            }
    return drugs


def build_condition_umls(data_dir):
    """Build condition_id -> UMLS CUI mapping."""
    umls = {}
    path = data_dir / "condition_external_identifiers.csv"
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("identifier_type") == "umls":
                cid = row["condition_id"]
                # identifier is like "cui/C0002395" - extract the CUI
                raw = row.get("identifier", "")
                cui = raw.split("/")[-1] if "/" in raw else raw
                if cui and cid not in umls:
                    umls[cid] = cui
    return umls


def build_condition_names(data_dir):
    """Build condition_id -> title mapping."""
    names = {}
    path = data_dir / "conditions.csv"
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        for row in reader:
            names[row["id"]] = row.get("title", "")
    return names


def preprocess_indications(data_dir, out_dir, drugs, umls, cond_names):
    """Join indications: drug_drugbank_id, condition_umls_cui, kind."""
    out_path = out_dir / "indications_flat.tsv"
    written = 0
    with open(out_path, "w", encoding="utf-8", newline="") as f:
        f.write("drugbank_id\tumls_cui\tcondition_name\tkind\n")
        with open(data_dir / "structured_indications.csv", "r",
                  encoding="utf-8", errors="replace") as inf:
            reader = csv.DictReader(inf)
            for row in reader:
                drug = drugs.get(row.get("drug_id", ""))
                if not drug:
                    continue
                cond_id = row.get("reference_id", "")
                cui = umls.get(cond_id, "")
                if not cui:
                    continue
                name = cond_names.get(cond_id, "")
                kind = row.get("kind", "")
                f.write(f"{drug['drugbank_id']}\t{cui}\t{name}\t{kind}\n")
                written += 1
    print(f"  Indications: {written} rows -> {out_path.name}")


def preprocess_adverse_effects(data_dir, out_dir, drugs, umls, cond_names):
    """Join adverse effects: drug_drugbank_id, condition_umls_cui."""
    # First build adverse_effect_id -> condition_id mapping
    ae_cond = {}
    with open(data_dir / "adverse_effect_conditions.csv", "r",
              encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        for row in reader:
            ae_id = row.get("adverse_effect_id", "")
            cond_id = row.get("condition_id", "")
            if ae_id and cond_id:
                ae_cond[ae_id] = cond_id

    out_path = out_dir / "adverse_effects_flat.tsv"
    written = 0
    with open(out_path, "w", encoding="utf-8", newline="") as f:
        f.write("drugbank_id\tumls_cui\tcondition_name\n")
        with open(data_dir / "structured_adverse_effects.csv", "r",
                  encoding="utf-8", errors="replace") as inf:
            reader = csv.DictReader(inf)
            for row in reader:
                drug = drugs.get(row.get("drug_id", ""))
                if not drug:
                    continue
                ae_id = row.get("id", "")
                cond_id = ae_cond.get(ae_id, "")
                cui = umls.get(cond_id, "")
                if not cui:
                    continue
                name = cond_names.get(cond_id, "")
                f.write(f"{drug['drugbank_id']}\t{cui}\t{name}\n")
                written += 1
    print(f"  Adverse effects: {written} rows -> {out_path.name}")


def preprocess_contraindications(data_dir, out_dir, drugs, umls, cond_names):
    """Join contraindications: drug_drugbank_id, condition_umls_cui."""
    ci_cond = {}
    with open(data_dir / "contraindication_conditions.csv", "r",
              encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        for row in reader:
            ci_id = row.get("contraindication_id", "")
            cond_id = row.get("condition_id", "")
            if ci_id and cond_id:
                ci_cond[ci_id] = cond_id

    out_path = out_dir / "contraindications_flat.tsv"
    written = 0
    with open(out_path, "w", encoding="utf-8", newline="") as f:
        f.write("drugbank_id\tumls_cui\tcondition_name\n")
        with open(data_dir / "structured_contraindications.csv", "r",
                  encoding="utf-8", errors="replace") as inf:
            reader = csv.DictReader(inf)
            for row in reader:
                drug = drugs.get(row.get("drug_id", ""))
                if not drug:
                    continue
                ci_id = row.get("id", "")
                cond_id = ci_cond.get(ci_id, "")
                cui = umls.get(cond_id, "")
                if not cui:
                    continue
                name = cond_names.get(cond_id, "")
                f.write(f"{drug['drugbank_id']}\t{cui}\t{name}\n")
                written += 1
    print(f"  Contraindications: {written} rows -> {out_path.name}")


def preprocess_admet(data_dir, out_dir, drugs):
    """Join ADMET properties with drugbank_id."""
    out_path = out_dir / "admet_flat.tsv"
    written = 0
    with open(out_path, "w", encoding="utf-8", newline="") as f:
        f.write("drugbank_id\tbbb\tbbb_probability\n")
        with open(data_dir / "drug_predicted_admet_properties.csv", "r",
                  encoding="utf-8", errors="replace") as inf:
            reader = csv.DictReader(inf)
            for row in reader:
                drug = drugs.get(row.get("drug_id", ""))
                if not drug:
                    continue
                bbb = row.get("bbb", "")
                bbb_prob = row.get("bbb_probability", "")
                if bbb or bbb_prob:
                    f.write(f"{drug['drugbank_id']}\t{bbb}\t{bbb_prob}\n")
                    written += 1
    print(f"  ADMET (BBB): {written} rows -> {out_path.name}")


def main():
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <drugbank_data_dir> <output_dir>")
        sys.exit(1)

    data_dir = Path(sys.argv[1])
    out_dir = Path(sys.argv[2])
    out_dir.mkdir(parents=True, exist_ok=True)

    print("Loading lookup tables...")
    drugs = build_drug_lookup(data_dir)
    print(f"  {len(drugs)} drugs loaded")
    umls = build_condition_umls(data_dir)
    print(f"  {len(umls)} condition -> UMLS mappings loaded")
    cond_names = build_condition_names(data_dir)
    print(f"  {len(cond_names)} condition names loaded")

    print("\nPreprocessing...")
    preprocess_indications(data_dir, out_dir, drugs, umls, cond_names)
    preprocess_adverse_effects(data_dir, out_dir, drugs, umls, cond_names)
    preprocess_contraindications(data_dir, out_dir, drugs, umls, cond_names)
    preprocess_admet(data_dir, out_dir, drugs)

    print("\nDone! Preprocessed files saved to:", out_dir)


if __name__ == "__main__":
    main()
