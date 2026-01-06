"""
Script to create the PharmaTox SQLite database with synthetic sample data.

This is a TOY EXAMPLE using SYNTHETIC DATA for testing and demonstration
purposes only. The relationships between drugs, genes, diseases, etc. are
fictitious and should NOT be used for any real biomedical research.
"""

import os
import sqlite3
from pathlib import Path


def create_database(db_path: str) -> None:
    """Create the PharmaTox SQLite database with synthetic sample data."""

    # Remove existing database
    if os.path.exists(db_path):
        os.remove(db_path)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create tables
    cursor.executescript("""
        -- Adverse Events entity table
        CREATE TABLE adverse_events (
            meddra_id TEXT PRIMARY KEY,
            event_name TEXT NOT NULL,
            severity TEXT NOT NULL
        );

        -- Cell Types entity table
        CREATE TABLE cell_types (
            cl_id TEXT PRIMARY KEY,
            cell_name TEXT NOT NULL
        );

        -- Drug treats Disease relationship
        CREATE TABLE drug_treats_disease (
            drugbank_id TEXT NOT NULL,
            umls_cui TEXT NOT NULL,
            evidence_level TEXT,
            PRIMARY KEY (drugbank_id, umls_cui)
        );

        -- Drug targets Gene relationship
        CREATE TABLE drug_targets_gene (
            drugbank_id TEXT NOT NULL,
            ncbi_gene_id INTEGER NOT NULL,
            action_type TEXT,
            PRIMARY KEY (drugbank_id, ncbi_gene_id)
        );

        -- Gene-Disease association relationship
        CREATE TABLE gene_disease_association (
            ncbi_gene_id INTEGER NOT NULL,
            umls_cui TEXT NOT NULL,
            association_score REAL,
            PRIMARY KEY (ncbi_gene_id, umls_cui)
        );

        -- Gene-Pathway relationship
        CREATE TABLE gene_pathway (
            ncbi_gene_id INTEGER NOT NULL,
            reactome_id TEXT NOT NULL,
            PRIMARY KEY (ncbi_gene_id, reactome_id)
        );

        -- Drug causes Adverse Event relationship
        CREATE TABLE drug_adverse_event (
            drugbank_id TEXT NOT NULL,
            meddra_id TEXT NOT NULL,
            frequency TEXT,
            PRIMARY KEY (drugbank_id, meddra_id)
        );

        -- Gene expression in Cell Type relationship
        CREATE TABLE gene_expression (
            ncbi_gene_id INTEGER NOT NULL,
            cl_id TEXT NOT NULL,
            expression_level TEXT,
            PRIMARY KEY (ncbi_gene_id, cl_id)
        );
    """)

    # Insert Adverse Events (8 events)
    adverse_events = [
        ("10019211", "Headache", "mild"),
        ("10028813", "Nausea", "mild"),
        ("10047700", "Vomiting", "moderate"),
        ("10012735", "Diarrhea", "mild"),
        ("10016256", "Fatigue", "mild"),
        ("10037660", "Rash", "moderate"),
        ("10002855", "Anemia", "moderate"),
        ("10020772", "Hypotension", "severe"),
    ]
    cursor.executemany("INSERT INTO adverse_events VALUES (?, ?, ?)", adverse_events)

    # Insert Cell Types (5 types)
    cell_types = [
        ("CL:0000084", "T cell"),
        ("CL:0000236", "B cell"),
        ("CL:0000182", "Hepatocyte"),
        ("CL:0000540", "Neuron"),
        ("CL:0002548", "Cardiomyocyte"),
    ]
    cursor.executemany("INSERT INTO cell_types VALUES (?, ?)", cell_types)

    # Insert Drug-Disease relationships (15 rows)
    # NOTE: These are SYNTHETIC relationships for demonstration only
    drug_disease = [
        ("DB00001", "C0007107", "high"),  # Lepirudin - Cardiovascular
        ("DB00001", "C0027051", "high"),  # Lepirudin - MI
        ("DB00002", "C0006826", "high"),  # Cetuximab - Cancer
        ("DB00006", "C0007107", "high"),  # Bivalirudin - Cardiovascular
        ("DB00006", "C0027051", "high"),  # Bivalirudin - MI
        ("DB00014", "C0006826", "high"),  # Goserelin - Cancer
        ("DB00035", "C0011849", "moderate"),  # Desmopressin - Diabetes
        ("DB00091", "C0006826", "moderate"),  # Cyclosporine - Cancer
        ("DB00104", "C0006826", "high"),  # Octreotide - Cancer
        ("DB00104", "C0024623", "moderate"),  # Octreotide - GI
        ("DB00115", "C0002395", "low"),  # Cyanocobalamin - Alzheimer
        ("DB00091", "C0002395", "low"),  # Cyclosporine - Alzheimer
        ("DB00050", "C0006826", "moderate"),  # Cetrorelix - Cancer
        ("DB00006", "C0020538", "moderate"),  # Bivalirudin - Hypertension
        ("DB00001", "C0020538", "moderate"),  # Lepirudin - Hypertension
    ]
    cursor.executemany("INSERT INTO drug_treats_disease VALUES (?, ?, ?)", drug_disease)

    # Insert Drug-Gene targets (18 rows)
    # NOTE: These are SYNTHETIC relationships for demonstration only
    drug_gene = [
        ("DB00001", 2147, "inhibitor"),  # Lepirudin - F2
        ("DB00002", 1956, "inhibitor"),  # Cetuximab - EGFR
        ("DB00006", 2147, "inhibitor"),  # Bivalirudin - F2
        ("DB00014", 3479, "modulator"),  # Goserelin - IGF1
        ("DB00091", 5743, "inhibitor"),  # Cyclosporine - PTGS2
        ("DB00091", 1565, "substrate"),  # Cyclosporine - CYP2D6
        ("DB00091", 1544, "substrate"),  # Cyclosporine - CYP1A2
        ("DB00104", 3479, "inhibitor"),  # Octreotide - IGF1
        ("DB00104", 207, "modulator"),  # Octreotide - AKT1
        ("DB00002", 5594, "inhibitor"),  # Cetuximab - MAPK1
        ("DB00002", 207, "inhibitor"),  # Cetuximab - AKT1
        ("DB00050", 3479, "antagonist"),  # Cetrorelix - IGF1
        ("DB00035", 4846, "modulator"),  # Desmopressin - NOS3
        ("DB00115", 1029, "modulator"),  # Cyanocobalamin - CDKN2A
        ("DB00001", 5972, "inhibitor"),  # Lepirudin - REN
        ("DB00006", 5972, "inhibitor"),  # Bivalirudin - REN
        ("DB00091", 7157, "modulator"),  # Cyclosporine - TP53
        ("DB00014", 7157, "modulator"),  # Goserelin - TP53
    ]
    cursor.executemany("INSERT INTO drug_targets_gene VALUES (?, ?, ?)", drug_gene)

    # Insert Gene-Disease associations (20 rows)
    # NOTE: These are SYNTHETIC relationships for demonstration only
    gene_disease = [
        (2147, "C0007107", 0.85),  # F2 - Cardiovascular
        (2147, "C0027051", 0.92),  # F2 - MI
        (5972, "C0020538", 0.88),  # REN - Hypertension
        (1956, "C0006826", 0.95),  # EGFR - Cancer
        (3479, "C0011849", 0.78),  # IGF1 - Diabetes
        (3479, "C0006826", 0.72),  # IGF1 - Cancer
        (5743, "C0007107", 0.65),  # PTGS2 - Cardiovascular
        (1565, "C0024623", 0.55),  # CYP2D6 - GI
        (207, "C0006826", 0.91),  # AKT1 - Cancer
        (207, "C0011849", 0.68),  # AKT1 - Diabetes
        (4846, "C0007107", 0.82),  # NOS3 - Cardiovascular
        (4846, "C0020538", 0.79),  # NOS3 - Hypertension
        (5594, "C0006826", 0.88),  # MAPK1 - Cancer
        (1029, "C0006826", 0.94),  # CDKN2A - Cancer
        (7157, "C0006826", 0.97),  # TP53 - Cancer
        (7157, "C0002395", 0.45),  # TP53 - Alzheimer
        (1544, "C0024623", 0.52),  # CYP1A2 - GI
        (5594, "C0002395", 0.38),  # MAPK1 - Alzheimer
        (207, "C0002395", 0.42),  # AKT1 - Alzheimer
        (5972, "C0007107", 0.81),  # REN - Cardiovascular
    ]
    cursor.executemany(
        "INSERT INTO gene_disease_association VALUES (?, ?, ?)", gene_disease
    )

    # Insert Gene-Pathway relationships (15 rows)
    gene_pathway = [
        (2147, "R-HSA-76002"),  # F2 - Platelet activation
        (5972, "R-HSA-76002"),  # REN - Platelet activation
        (1956, "R-HSA-177929"),  # EGFR - EGFR Signaling
        (1956, "R-HSA-2219528"),  # EGFR - PI3K/AKT
        (207, "R-HSA-2219528"),  # AKT1 - PI3K/AKT
        (207, "R-HSA-177929"),  # AKT1 - EGFR Signaling
        (3479, "R-HSA-2219528"),  # IGF1 - PI3K/AKT
        (5594, "R-HSA-177929"),  # MAPK1 - EGFR Signaling
        (5743, "R-HSA-1430728"),  # PTGS2 - Metabolism
        (1565, "R-HSA-1430728"),  # CYP2D6 - Metabolism
        (1544, "R-HSA-1430728"),  # CYP1A2 - Metabolism
        (4846, "R-HSA-76002"),  # NOS3 - Platelet activation
        (7157, "R-HSA-74160"),  # TP53 - Gene expression
        (1029, "R-HSA-74160"),  # CDKN2A - Gene expression
        (3479, "R-HSA-392499"),  # IGF1 - Metabolism of proteins
    ]
    cursor.executemany("INSERT INTO gene_pathway VALUES (?, ?)", gene_pathway)

    # Insert Drug-Adverse Event relationships (20 rows)
    # NOTE: These are SYNTHETIC relationships for demonstration only
    drug_adverse = [
        ("DB00001", "10020772", "common"),  # Lepirudin - Hypotension
        ("DB00001", "10002855", "uncommon"),  # Lepirudin - Anemia
        ("DB00002", "10037660", "common"),  # Cetuximab - Rash
        ("DB00002", "10012735", "common"),  # Cetuximab - Diarrhea
        ("DB00002", "10016256", "common"),  # Cetuximab - Fatigue
        ("DB00006", "10020772", "uncommon"),  # Bivalirudin - Hypotension
        ("DB00006", "10019211", "common"),  # Bivalirudin - Headache
        ("DB00014", "10019211", "common"),  # Goserelin - Headache
        ("DB00014", "10028813", "common"),  # Goserelin - Nausea
        ("DB00091", "10028813", "common"),  # Cyclosporine - Nausea
        ("DB00091", "10019211", "common"),  # Cyclosporine - Headache
        ("DB00091", "10037660", "uncommon"),  # Cyclosporine - Rash
        ("DB00104", "10028813", "common"),  # Octreotide - Nausea
        ("DB00104", "10012735", "common"),  # Octreotide - Diarrhea
        ("DB00104", "10047700", "uncommon"),  # Octreotide - Vomiting
        ("DB00035", "10019211", "uncommon"),  # Desmopressin - Headache
        ("DB00050", "10028813", "common"),  # Cetrorelix - Nausea
        ("DB00115", "10012735", "rare"),  # Cyanocobalamin - Diarrhea
        ("DB00129", "10028813", "rare"),  # Ornithine - Nausea
        ("DB00001", "10019211", "common"),  # Lepirudin - Headache
    ]
    cursor.executemany("INSERT INTO drug_adverse_event VALUES (?, ?, ?)", drug_adverse)

    # Insert Gene expression in Cell Types (12 rows)
    gene_expression = [
        (2147, "CL:0000182", "high"),  # F2 - Hepatocyte
        (5972, "CL:0000182", "high"),  # REN - Hepatocyte
        (1956, "CL:0000084", "moderate"),  # EGFR - T cell
        (1956, "CL:0000540", "high"),  # EGFR - Neuron
        (207, "CL:0000084", "high"),  # AKT1 - T cell
        (207, "CL:0000236", "high"),  # AKT1 - B cell
        (4846, "CL:0002548", "high"),  # NOS3 - Cardiomyocyte
        (7157, "CL:0000084", "moderate"),  # TP53 - T cell
        (7157, "CL:0000182", "moderate"),  # TP53 - Hepatocyte
        (5594, "CL:0000540", "high"),  # MAPK1 - Neuron
        (3479, "CL:0000182", "high"),  # IGF1 - Hepatocyte
        (1565, "CL:0000182", "high"),  # CYP2D6 - Hepatocyte
    ]
    cursor.executemany("INSERT INTO gene_expression VALUES (?, ?, ?)", gene_expression)

    conn.commit()
    conn.close()
    print(f"Created database: {db_path}")

    # Print summary
    print("\nDatabase contents:")
    print(f"  - adverse_events: {len(adverse_events)} rows")
    print(f"  - cell_types: {len(cell_types)} rows")
    print(f"  - drug_treats_disease: {len(drug_disease)} rows")
    print(f"  - drug_targets_gene: {len(drug_gene)} rows")
    print(f"  - gene_disease_association: {len(gene_disease)} rows")
    print(f"  - gene_pathway: {len(gene_pathway)} rows")
    print(f"  - drug_adverse_event: {len(drug_adverse)} rows")
    print(f"  - gene_expression: {len(gene_expression)} rows")


if __name__ == "__main__":
    # Get the script directory and construct database path
    script_dir = Path(__file__).parent
    data_dir = script_dir.parent / "data"
    db_path = data_dir / "pharmatox.db"

    create_database(str(db_path))
