"""
Simplified version of load_neurokb_to_memgraph.py with better performance for relationship loading.

This version uses UNWIND-based batched queries instead of transactions to avoid timeout issues.
"""

import sys
sys.path.insert(0, '../memgraph_examples')

from load_neurokb_to_memgraph import RDFMemgraphLoader
from typing import List

class ImprovedRDFMemgraphLoader(RDFMemgraphLoader):
    """Improved loader with better relationship loading and OWL cleanup."""

    def cleanup_owl_labels(self):
        """Remove OWL standard labels and delete nodes with no meaningful labels."""
        print("\nCleaning up OWL standard labels...")
        import time
        start_time = time.time()

        owl_labels = ['DatatypeProperty', 'FunctionalProperty', 'Entity', 'Individual']

        with self.driver.session() as session:
            # Remove each OWL standard label from all nodes
            for label in owl_labels:
                try:
                    query = f"MATCH (n:{label}) REMOVE n:{label}"
                    result = session.run(query)
                    result.consume()
                    print(f"  Removed :{label} labels from nodes")
                except Exception as e:
                    print(f"  Warning: Failed to remove :{label} labels: {e}")

            # Delete nodes that have no labels remaining
            try:
                # First, count how many nodes will be deleted
                count_query = "MATCH (n) WHERE size(labels(n)) = 0 RETURN count(n) as count"
                result = session.run(count_query)
                delete_count = result.single()['count']

                if delete_count > 0:
                    print(f"  Deleting {delete_count:,} nodes with no remaining labels...")
                    delete_query = "MATCH (n) WHERE size(labels(n)) = 0 DETACH DELETE n"
                    session.run(delete_query)
                    print(f"  Deleted {delete_count:,} nodes")
                else:
                    print("  No nodes to delete (all have meaningful labels)")

            except Exception as e:
                print(f"  Warning: Failed to delete unlabeled nodes: {e}")

        elapsed = time.time() - start_time
        print(f"  Cleanup time: {elapsed:.2f}s")

    def load_relationships(self, relationships: List, batch_size: int = 1000):
        """Load relationships using UNWIND batching for better performance."""
        print(f"\nLoading {len(relationships):,} relationships...")
        import time
        start_time = time.time()

        total = len(relationships)
        errors = 0
        loaded = 0

        for i in range(0, total, batch_size):
            batch = relationships[i:i + batch_size]

            # Group relationships by type for efficient batching
            rels_by_type = {}
            for source_iri, prop_name, target_iri in batch:
                rel_type = self._sanitize_label(prop_name)
                if rel_type not in rels_by_type:
                    rels_by_type[rel_type] = []
                rels_by_type[rel_type].append({
                    'source': source_iri,
                    'target': target_iri
                })

            # Process each relationship type with batched UNWIND query
            with self.driver.session() as session:
                for rel_type, rels in rels_by_type.items():
                    try:
                        # Use UNWIND to create multiple relationships in one query
                        query = f"""
                        UNWIND $rels as rel
                        MATCH (a:Individual {{iri: rel.source}})
                        MATCH (b:Individual {{iri: rel.target}})
                        CREATE (a)-[:{rel_type}]->(b)
                        """
                        session.run(query, rels=rels)
                        loaded += len(rels)
                    except Exception as e:
                        errors += len(rels)
                        if errors <= 10:
                            print(f"  Warning: Batch failed for {rel_type}: {e}")

            if (i + batch_size) % 50000 == 0 or i + batch_size >= total:
                print(f"  Loaded {min(i + batch_size, total):,}/{total:,} relationships (successful: {loaded:,}, errors: {errors})")

        elapsed = time.time() - start_time
        print(f"  Time: {elapsed:.2f}s")
        if loaded > 0:
            print(f"  Rate: {loaded / elapsed:.0f} relationships/sec")
        if errors > 0:
            print(f"  Total errors: {errors:,}")

    def load_rdf_file(self, rdf_file: str, clear_existing: bool = True,
                     create_indexes: bool = True, batch_size: int = 1000):
        """
        Load an RDF/XML file into Memgraph with cleanup of OWL standard labels.

        Args:
            rdf_file: Path to RDF/XML file
            clear_existing: Whether to clear existing data
            create_indexes: Whether to create indexes
            batch_size: Batch size for loading

        Returns:
            Statistics dictionary
        """
        # Call parent class load_rdf_file
        stats = super().load_rdf_file(rdf_file, clear_existing, create_indexes, batch_size)

        # Clean up OWL standard labels
        self.cleanup_owl_labels()

        # Get updated statistics after cleanup
        print("\n" + "=" * 70)
        print("POST-CLEANUP STATISTICS")
        print("=" * 70)
        stats = self.get_statistics()

        print(f"\nDatabase Statistics (after cleanup):")
        print(f"  Nodes: {stats['nodes']:,}")
        print(f"  Relationships: {stats['relationships']:,}")
        print(f"  Node Labels ({len(stats['labels'])}): {', '.join(stats['labels'][:10])}")
        if len(stats['labels']) > 10:
            print(f"    ... and {len(stats['labels']) - 10} more")
        print(f"  Relationship Types ({len(stats['relationship_types'])}): {', '.join(stats['relationship_types'][:10])}")
        if len(stats['relationship_types']) > 10:
            print(f"    ... and {len(stats['relationship_types']) - 10} more")

        print("\n" + "=" * 70)

        return stats


if __name__ == "__main__":
    rdf_file = "../kg_projects/neurokb/neurokb-with-all-drug-relationships.rdf"

    from pathlib import Path
    if not Path(rdf_file).exists():
        print(f"Error: File not found: {rdf_file}")
        sys.exit(1)

    print(f"Loading: {rdf_file}")
    print(f"Connecting to Memgraph at bolt://localhost:7687")
    print()

    try:
        with ImprovedRDFMemgraphLoader() as loader:
            if not loader.test_connection():
                print("\nError: Cannot connect to Memgraph at bolt://localhost:7687")
                print("\nPlease start Memgraph first:")
                print("  docker run -p 7687:7687 -p 7444:7444 memgraph/memgraph-platform")
                sys.exit(1)

            stats = loader.load_rdf_file(rdf_file, batch_size=1000)

        print("\nSuccess! Your knowledge graph is now available in Memgraph.")
        print("\nAccess Memgraph Lab at: http://localhost:7444")

    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
