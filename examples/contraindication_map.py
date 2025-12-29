"""
Drug-Disease Contraindication Mapper

This script reads DrugBank's structured contraindications data and maps it to UMLS CUIs
(Concept Unique Identifiers) which are used in the neurokb ontology.

The mapping process:
1. Loads structured drug contraindications from DrugBank
2. Maps internal drug IDs to DrugBank IDs (e.g., DB00001)
3. Maps contraindication IDs to condition IDs via contraindication_conditions
4. Maps internal condition IDs to UMLS CUIs via condition_external_identifiers
5. Returns a DataFrame with drugbank_id and umls_cui columns

Requirements:
    - pandas
    - DrugBank CSV files in D:/data/drugbank/2025-11-19/

Output:
    DataFrame with columns: drugbank_id, disease_id (UMLS CUI format)
"""

import pandas as pd
from pathlib import Path

# DrugBank data directory
DRUGBANK_DIR = Path("D:/data/drugbank/2025-11-19")


def load_drug_contraindication_mappings(countries: list = None):
    """
    Load drug-disease contraindication mappings from DrugBank.

    Parameters
    ----------
    countries : list, optional
        List of countries/regions to filter by (e.g., ['US', 'Canada']).
        If None, include all countries.

    Returns
    -------
    pd.DataFrame
        DataFrame with columns:
        - drugbank_id: DrugBank ID (e.g., 'DB00001')
        - disease_id: UMLS CUI (e.g., 'C0002395')
        - disease_name: Common name of the disease
        - region: Country/region where contraindication applies
    """

    print("Loading DrugBank contraindication files...")

    # Load structured contraindications
    contraindications = pd.read_csv(
        DRUGBANK_DIR / "structured_contraindications.csv",
        usecols=['id', 'drug_id', 'region']
    )
    print(f"  Loaded {len(contraindications):,} contraindications")

    # Load contraindication-condition relationships
    contraind_conditions = pd.read_csv(
        DRUGBANK_DIR / "contraindication_conditions.csv",
        usecols=['contraindication_id', 'condition_id', 'relationship']
    )
    # Filter to only patient conditions (not co-administered drugs, etc.)
    contraind_conditions = contraind_conditions[
        contraind_conditions['relationship'] == 'patient_condition'
    ]
    print(f"  Loaded {len(contraind_conditions):,} contraindication-condition links")

    # Load drugs to get DrugBank IDs
    drugs = pd.read_csv(
        DRUGBANK_DIR / "drugs.csv",
        usecols=['id', 'drugbank_id']
    )
    print(f"  Loaded {len(drugs):,} drugs")

    # Load conditions to get disease names
    conditions = pd.read_csv(
        DRUGBANK_DIR / "conditions.csv",
        usecols=['id', 'title', 'is_disease']
    )
    print(f"  Loaded {len(conditions):,} conditions")

    # Load UMLS CUI mappings
    external_ids = pd.read_csv(
        DRUGBANK_DIR / "condition_external_identifiers.csv"
    )
    # Filter to only UMLS CUI mappings
    umls_mappings = external_ids[external_ids['identifier_type'] == 'umls'].copy()
    # Extract CUI from format "cui/C0002395" -> "C0002395"
    umls_mappings['umls_cui'] = umls_mappings['identifier'].str.replace('cui/', '', regex=False)
    print(f"  Loaded {len(umls_mappings):,} UMLS CUI mappings")

    print("\nBuilding drug-disease contraindication mappings...")

    # Join contraindications with contraindication-conditions
    df = contraindications.merge(
        contraind_conditions,
        left_on='id',
        right_on='contraindication_id',
        how='inner'
    )

    # Join with drugs to get DrugBank IDs
    df = df.merge(
        drugs[['id', 'drugbank_id']],
        left_on='drug_id',
        right_on='id',
        how='inner',
        suffixes=('', '_drug')
    )

    # Join with conditions to get disease names
    df = df.merge(
        conditions[['id', 'title', 'is_disease']],
        left_on='condition_id',
        right_on='id',
        how='inner',
        suffixes=('', '_condition')
    )

    # Join with UMLS mappings
    df = df.merge(
        umls_mappings[['condition_id', 'umls_cui']],
        on='condition_id',
        how='inner'
    )

    print(f"  Total drug-disease contraindication pairs with UMLS CUIs: {len(df):,}")

    # Apply filters
    if countries is not None:
        df = df[df['region'].isin(countries)]
        print(f"  After filtering by countries {countries}: {len(df):,}")

    # Only keep actual diseases (not symptoms or procedures)
    df = df[df['is_disease'] == 1]
    print(f"  After filtering to diseases only: {len(df):,}")

    # Select and rename columns for output
    result = df[[
        'drugbank_id',
        'umls_cui',
        'title',
        'region'
    ]].copy()

    result = result.rename(columns={
        'umls_cui': 'disease_id',
        'title': 'disease_name'
    })

    # Remove duplicates (same drug-disease pair from multiple sources)
    result = result.drop_duplicates(subset=['drugbank_id', 'disease_id'])

    print(f"\nFinal dataset: {len(result):,} unique drug-disease contraindication pairs")
    print(f"  Unique drugs: {result['drugbank_id'].nunique():,}")
    print(f"  Unique diseases: {result['disease_id'].nunique():,}")

    return result


def save_for_neurokb_integration(df: pd.DataFrame, output_file: str = "drug_contraindication_mappings.csv"):
    """
    Save a simplified version for direct use with the neurokb integration example.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame from load_drug_contraindication_mappings()
    output_file : str
        Output filename
    """
    # Keep only the columns needed for the integration example
    simple_df = df[['drugbank_id', 'disease_id']].copy()
    simple_df.to_csv(output_file, index=False)
    print(f"\nSaved simplified mapping to: {output_file}")
    return simple_df


if __name__ == "__main__":
    # Example usage: Load all drug-disease contraindication mappings
    print("=" * 60)
    print("DrugBank Drug-Disease Contraindication Mapper")
    print("=" * 60)
    print()

    # Load mappings with default settings (all contraindications)
    df_all = load_drug_contraindication_mappings()

    print("\n" + "=" * 60)
    print("Sample of mappings:")
    print("=" * 60)
    print(df_all.head(10).to_string(index=False))

    # Save simplified version for neurokb integration
    simple_df = save_for_neurokb_integration(df_all, "drug_contraindication_mappings.csv")

    print("\n" + "=" * 60)
    print("Filtering Examples")
    print("=" * 60)

    # Example: Only US contraindications
    print("\n1. US contraindications only:")
    df_us = load_drug_contraindication_mappings(countries=['US'])

    print("\n" + "=" * 60)
    print("Disease Examples")
    print("=" * 60)
    # Show some example diseases with their CUIs
    disease_examples = df_all[['disease_id', 'disease_name']].drop_duplicates().head(20)
    print(disease_examples.to_string(index=False))

    print("\nDone! You can now use 'drug_contraindication_mappings.csv' with the neurokb integration example.")
