"""
Drug-Drug Interaction Mapper

This script reads DrugBank's structured drug interactions data and filters for
major severity interactions (severity = 2).

The mapping process:
1. Loads structured drug interactions from DrugBank
2. Filters for major severity interactions (severity = 2)
3. Extracts DrugBank IDs for both subject and affected drugs
4. Returns a DataFrame with subject_drugbank_id and affected_drugbank_id columns

Requirements:
    - pandas
    - DrugBank CSV files in D:/data/drugbank/2025-11-19/

Output:
    DataFrame with columns: subject_drugbank_id, affected_drugbank_id, summary, action
"""

import pandas as pd
from pathlib import Path

# DrugBank data directory
DRUGBANK_DIR = Path("D:/data/drugbank/2025-11-19")


def load_drug_interaction_mappings(
    min_severity: int = 2,
    evidence_level: int = None
):
    """
    Load drug-drug interaction mappings from DrugBank.

    Parameters
    ----------
    min_severity : int, optional
        Minimum severity level to include (default: 2 = major).
        Severity levels:
        - 0: Minor (monitoring recommended)
        - 1: Moderate (risk of adverse effects)
        - 2: Major (serious risk, e.g., infection, toxicity)
    evidence_level : int, optional
        Filter by evidence level (1 = highest quality).
        If None, include all evidence levels.

    Returns
    -------
    pd.DataFrame
        DataFrame with columns:
        - subject_drugbank_id: DrugBank ID of subject drug
        - affected_drugbank_id: DrugBank ID of affected drug
        - subject_drug_name: Name of subject drug
        - affected_drug_name: Name of affected drug
        - severity: Severity level (0-2)
        - evidence_level: Evidence quality level
        - summary: Brief description of interaction
        - action: Type of interaction effect
    """

    print("Loading DrugBank drug interaction file...")

    # Load structured drug interactions
    # Only load the columns we need to reduce memory usage
    interactions = pd.read_csv(
        DRUGBANK_DIR / "structured_drug_interactions.csv",
        usecols=[
            'subject_drug_drugbank_id',
            'subject_drug_name',
            'affected_drug_drugbank_id',
            'affected_drug_name',
            'summary',
            'severity',
            'evidence_level',
            'action'
        ],
        low_memory=False  # Suppress mixed type warning
    )
    print(f"  Loaded {len(interactions):,} drug interactions")

    print("\nFiltering interactions...")

    # Filter by severity
    if min_severity is not None:
        interactions = interactions[interactions['severity'] >= min_severity]
        print(f"  After filtering by severity >= {min_severity}: {len(interactions):,}")

    # Filter by evidence level if specified
    if evidence_level is not None:
        interactions = interactions[interactions['evidence_level'] == evidence_level]
        print(f"  After filtering by evidence_level = {evidence_level}: {len(interactions):,}")

    # Remove rows with missing DrugBank IDs
    interactions = interactions.dropna(subset=['subject_drug_drugbank_id', 'affected_drug_drugbank_id'])
    print(f"  After removing missing IDs: {len(interactions):,}")

    # Rename columns for clarity
    result = interactions.rename(columns={
        'subject_drug_drugbank_id': 'subject_drugbank_id',
        'affected_drug_drugbank_id': 'affected_drugbank_id'
    })

    # Remove duplicates (same drug pair)
    result = result.drop_duplicates(subset=['subject_drugbank_id', 'affected_drugbank_id'])

    print(f"\nFinal dataset: {len(result):,} unique drug-drug interaction pairs")
    print(f"  Unique subject drugs: {result['subject_drugbank_id'].nunique():,}")
    print(f"  Unique affected drugs: {result['affected_drugbank_id'].nunique():,}")

    # Show severity distribution
    print(f"\nSeverity distribution:")
    for sev in sorted(result['severity'].unique()):
        count = (result['severity'] == sev).sum()
        sev_name = {0: "Minor", 1: "Moderate", 2: "Major"}.get(sev, "Unknown")
        print(f"  Severity {sev} ({sev_name}): {count:,}")

    return result


def save_for_neurokb_integration(df: pd.DataFrame, output_file: str = "drug_interaction_mappings.csv"):
    """
    Save a simplified version for direct use with the neurokb integration example.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame from load_drug_interaction_mappings()
    output_file : str
        Output filename
    """
    # Keep only the columns needed for the integration example
    simple_df = df[['subject_drugbank_id', 'affected_drugbank_id']].copy()
    simple_df.to_csv(output_file, index=False)
    print(f"\nSaved simplified mapping to: {output_file}")
    return simple_df


if __name__ == "__main__":
    # Example usage: Load major severity drug-drug interactions
    print("=" * 60)
    print("DrugBank Drug-Drug Interaction Mapper (Major Severity)")
    print("=" * 60)
    print()

    # Load mappings with major severity only (severity = 2)
    df_major = load_drug_interaction_mappings(min_severity=2)

    print("\n" + "=" * 60)
    print("Sample of major severity interactions:")
    print("=" * 60)
    print(df_major[['subject_drugbank_id', 'affected_drugbank_id', 'summary']].head(10).to_string(index=False))

    # Save simplified version for neurokb integration
    simple_df = save_for_neurokb_integration(df_major, "drug_interaction_mappings.csv")

    print("\n" + "=" * 60)
    print("Filtering Examples")
    print("=" * 60)

    # Example 1: All severities
    print("\n1. All severity levels:")
    df_all = load_drug_interaction_mappings(min_severity=0)

    # Example 2: Moderate and above
    print("\n2. Moderate and major severity (>= 1):")
    df_moderate = load_drug_interaction_mappings(min_severity=1)

    # Example 3: Major with highest evidence
    print("\n3. Major severity with evidence level 1 (highest quality):")
    df_major_high_evidence = load_drug_interaction_mappings(min_severity=2, evidence_level=1)

    print("\n" + "=" * 60)
    print("Action Types in Major Interactions")
    print("=" * 60)
    # Show action type distribution
    action_counts = df_major['action'].value_counts().head(10)
    print(action_counts.to_string())

    print("\nDone! You can now use 'drug_interaction_mappings.csv' with the neurokb integration example.")
