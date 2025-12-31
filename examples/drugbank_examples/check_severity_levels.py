import pandas as pd

df = pd.read_csv('D:/data/drugbank/2025-11-19/structured_drug_interactions.csv',
                 usecols=['severity', 'summary'])

for sev in [0, 1, 2]:
    print(f'\n=== Severity {sev} ===')
    samples = df[df['severity']==sev]['summary'].head(5).tolist()
    for s in samples:
        # Show first 120 chars
        print(f'- {s[:120]}')

print(f"\n=== Counts ===")
print(df['severity'].value_counts().sort_index())
