"""
Test RDF parsing for Memgraph loading (dry run - no database connection needed)

This script tests parsing the RDF file and shows what would be loaded into Memgraph,
without actually connecting to the database.
"""

import xml.etree.ElementTree as ET
from collections import defaultdict, Counter
import time
import re

# RDF namespaces
NS = {
    'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
    'owl': 'http://www.w3.org/2002/07/owl#',
}


def extract_fragment(iri: str) -> str:
    """Extract fragment from IRI."""
    if '#' in iri:
        return iri.split('#')[-1]
    elif '/' in iri:
        return iri.split('/')[-1]
    return iri


def parse_rdf_file(rdf_file: str):
    """Parse RDF file and show statistics."""
    print(f"Parsing: {rdf_file}")
    print()
    start_time = time.time()

    tree = ET.parse(rdf_file)
    root = tree.getroot()

    # Get ontology base
    ont_elem = root.find('owl:Ontology', NS)
    base_namespace = ''
    if ont_elem is not None:
        base_namespace = ont_elem.get('{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about', '')
        if base_namespace and not base_namespace.endswith('#'):
            base_namespace += '#'

    print(f"Base namespace: {base_namespace}")
    print()

    # Storage
    individuals = {}
    relationships = []
    type_counter = Counter()
    property_counter = Counter()

    # Skip metadata elements
    skip_types = {'Ontology', 'Class', 'ObjectProperty', 'DataProperty', 'AnnotationProperty'}

    for elem in root:
        tag = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag

        if tag in skip_types:
            continue

        iri = elem.get('{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about')
        if not iri:
            continue

        # Convert relative IRI
        if iri.startswith('#'):
            iri = base_namespace.rstrip('#') + iri

        # Initialize individual
        if iri not in individuals:
            individuals[iri] = {
                'types': set(),
                'properties': {},
                'label': extract_fragment(iri)
            }

        # Add type from element tag
        if tag not in ['NamedIndividual', 'Description']:
            individuals[iri]['types'].add(tag)
            type_counter[tag] += 1

        # Process properties
        for child in elem:
            child_tag = child.tag.split('}')[-1] if '}' in child.tag else child.tag

            # rdf:type
            if child_tag == 'type':
                type_iri = child.get('{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource', '')
                if type_iri:
                    type_name = extract_fragment(type_iri)
                    if type_name and type_name != 'NamedIndividual':
                        individuals[iri]['types'].add(type_name)
                        type_counter[type_name] += 1

            # Object property (has rdf:resource)
            elif '{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource' in child.attrib:
                target_iri = child.get('{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource')

                if target_iri.startswith('#'):
                    target_iri = base_namespace.rstrip('#') + target_iri

                relationships.append((iri, child_tag, target_iri))
                property_counter[child_tag] += 1

            # Data property (has text)
            elif child.text:
                prop_name = child_tag
                individuals[iri]['properties'][prop_name] = child.text.strip()

    elapsed = time.time() - start_time

    print("=" * 70)
    print("PARSING RESULTS")
    print("=" * 70)
    print()
    print(f"Parse time: {elapsed:.2f}s")
    print(f"Total individuals: {len(individuals):,}")
    print(f"Total relationships: {len(relationships):,}")
    print()

    print("=" * 70)
    print("TOP 20 NODE TYPES (Labels)")
    print("=" * 70)
    for type_name, count in type_counter.most_common(20):
        print(f"  {type_name:40s} {count:,}")
    print()

    print("=" * 70)
    print("TOP 20 RELATIONSHIP TYPES")
    print("=" * 70)
    for prop_name, count in property_counter.most_common(20):
        print(f"  {prop_name:40s} {count:,}")
    print()

    # Sample individuals
    print("=" * 70)
    print("SAMPLE INDIVIDUALS (first 5)")
    print("=" * 70)
    for i, (iri, data) in enumerate(list(individuals.items())[:5]):
        print(f"\n{i+1}. {data['label']}")
        print(f"   IRI: {iri}")
        print(f"   Types: {', '.join(data['types']) if data['types'] else 'None'}")
        print(f"   Properties: {len(data['properties'])}")
        if data['properties']:
            # Show first 3 properties
            for prop_name, prop_value in list(data['properties'].items())[:3]:
                value_preview = str(prop_value)[:50]
                print(f"     {prop_name}: {value_preview}")
    print()

    # Sample relationships
    print("=" * 70)
    print("SAMPLE RELATIONSHIPS (first 10)")
    print("=" * 70)
    for i, (source, prop, target) in enumerate(relationships[:10]):
        source_label = extract_fragment(source)
        target_label = extract_fragment(target)
        print(f"  {i+1}. ({source_label})-[:{prop}]->({target_label})")
    print()

    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"This RDF file would create:")
    print(f"  - {len(individuals):,} nodes in Memgraph")
    print(f"  - {len(relationships):,} relationships in Memgraph")
    print(f"  - {len(type_counter)} different node labels/types")
    print(f"  - {len(property_counter)} different relationship types")
    print()
    print("To load into Memgraph:")
    print("  1. Install neo4j driver: pip install neo4j")
    print("  2. Start Memgraph: docker run -p 7687:7687 -p 7444:7444 memgraph/memgraph-platform")
    print("  3. Run: python load_neurokb_to_memgraph.py")


if __name__ == "__main__":
    import sys
    from pathlib import Path

    # Default file
    rdf_file = "kg_projects/neurokb/neurokb-with-all-drug-relationships.rdf"

    # Allow specifying different file
    if len(sys.argv) > 1:
        rdf_file = sys.argv[1]

    # Check if file exists
    if not Path(rdf_file).exists():
        print(f"Error: File not found: {rdf_file}")
        print("\nAvailable neurokb files:")
        neurokb_dir = Path("kg_projects/neurokb")
        if neurokb_dir.exists():
            for f in sorted(neurokb_dir.glob("neurokb-with-*.rdf")):
                size_mb = f.stat().st_size / (1024 * 1024)
                print(f"  {f.name} ({size_mb:.1f} MB)")
        sys.exit(1)

    # Parse and show statistics
    parse_rdf_file(rdf_file)
