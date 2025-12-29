"""
Debug script to check what's being loaded and saved during RDF roundtrip
"""

import sys
from pathlib import Path

# Add parent directory to path to import ista
sys.path.insert(0, str(Path(__file__).parent.parent))

from ista import owl2

print("=" * 70)
print("Testing RDF Roundtrip - What Gets Loaded and Saved?")
print("=" * 70)

# Load the original file
input_file = "kg_projects/neurokb/neurokb-populated.rdf"
print(f"\nInput file: {input_file}")
print(f"Input file size: {Path(input_file).stat().st_size:,} bytes")

print("\nLoading ontology...")
onto = owl2.RDFXMLParser.parse_from_file(input_file)

print("\nOntology loaded. Statistics:")
stats = onto.get_statistics()
print(stats)

print(f"\nAxiom count: {onto.get_axiom_count():,}")

# Try serializing it back immediately (no modifications)
output_file = "test_roundtrip_output.rdf"
print(f"\nSerializing back to: {output_file}")
owl2.RDFXMLSerializer.serialize_to_file(onto, output_file)

output_size = Path(output_file).stat().st_size
print(f"Output file size: {output_size:,} bytes")

input_size = Path(input_file).stat().st_size
print(f"\nSize comparison:")
print(f"  Input:  {input_size:,} bytes")
print(f"  Output: {output_size:,} bytes")
print(f"  Loss:   {input_size - output_size:,} bytes ({100 * (1 - output_size/input_size):.1f}% lost)")

print("\nChecking output file content...")
with open(output_file, 'r', encoding='utf-8') as f:
    content = f.read()

import re
drugs_in_output = len(re.findall(r'<Drug rdf:about=', content))
diseases_in_output = len(re.findall(r'<Disease rdf:about=', content))

print(f"  Drugs in output: {drugs_in_output}")
print(f"  Diseases in output: {diseases_in_output}")

print("\nConclusion:")
if output_size < input_size * 0.5:
    print("  ⚠️  WARNING: Significant data loss during roundtrip!")
    print("  The RDF parser may not be loading all axiom types.")
    print("  Individual declarations and property assertions may be missing.")
else:
    print("  ✓ Roundtrip preserved most content")
