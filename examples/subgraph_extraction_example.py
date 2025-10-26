"""
Comprehensive example demonstrating C++ subgraph extraction features.

This example shows how to use the high-performance C++ OntologyFilter
to extract subgraphs from large knowledge graphs efficiently.

Examples
--------
Run all examples:
    >>> python subgraph_extraction_example.py

The script demonstrates:
- Filtering by disease to extract relevant subgraphs
- Extracting drug-target networks
- Finding paths between entities
- Comparing multiple diseases
- Random sampling
- Builder pattern for complex filters
- Performance benchmarking

Notes
-----
All subgraph extraction operations run in O(V+E) time with efficient
memory usage thanks to the C++ backend implementation.
"""

import sys

sys.path.insert(0, "../build/lib/python/Release")

from _libista_owl2 import (
    Ontology,
    IRI,
    Class,
    NamedIndividual,
    ObjectProperty,
    DataProperty,
    ClassAssertion,
    ObjectPropertyAssertion,
    DataPropertyAssertion,
    Literal,
    OntologyFilter,
    FilterCriteria,
    RDFXMLSerializer,
)


def create_biomedical_ontology():
    """
    Create a biomedical knowledge graph with diseases, genes, proteins, drugs, and pathways.

    Constructs a comprehensive biomedical ontology including:
    - 4 diseases (Alzheimer's, Parkinson's, Diabetes, Cancer)
    - 5 genes (APOE, BRCA1, INS, SNCA, TP53)
    - 5 proteins (ApoE, BRCA1, Insulin, Alpha-Synuclein, p53)
    - 4 drugs (Metformin, Levodopa, Donepezil, Tamoxifen)
    - 3 pathways (Glucose Metabolism, Apoptosis, DNA Repair)

    Returns
    -------
    Ontology
        A biomedical ontology with 46 axioms representing disease-gene-protein-drug
        relationships suitable for demonstrating subgraph extraction.

    Notes
    -----
    Relationships include:
    - Gene-disease associations (e.g., APOE associated with Alzheimer's)
    - Gene-protein encoding (e.g., APOE encodes ApoE protein)
    - Protein-pathway participation
    - Drug-target relationships
    - Drug-disease treatment relationships
    - Protein-protein interactions
    """
    print("Creating biomedical knowledge graph...")
    ont = Ontology(IRI("http://example.org/biomedical"))

    # Define classes
    disease_cls = Class(IRI("http://example.org/biomedical#Disease"))
    gene_cls = Class(IRI("http://example.org/biomedical#Gene"))
    protein_cls = Class(IRI("http://example.org/biomedical#Protein"))
    drug_cls = Class(IRI("http://example.org/biomedical#Drug"))
    pathway_cls = Class(IRI("http://example.org/biomedical#Pathway"))

    # Define object properties (relationships)
    associated_with = ObjectProperty(
        IRI("http://example.org/biomedical#associatedWith")
    )
    encodes = ObjectProperty(IRI("http://example.org/biomedical#encodes"))
    participates_in = ObjectProperty(
        IRI("http://example.org/biomedical#participatesIn")
    )
    targets = ObjectProperty(IRI("http://example.org/biomedical#targets"))
    treats = ObjectProperty(IRI("http://example.org/biomedical#treats"))
    interacts_with = ObjectProperty(IRI("http://example.org/biomedical#interactsWith"))

    # Define data properties
    name_prop = DataProperty(IRI("http://example.org/biomedical#name"))
    identifier_prop = DataProperty(IRI("http://example.org/biomedical#identifier"))

    # Create diseases
    alzheimers = NamedIndividual(IRI("http://example.org/biomedical#Alzheimers"))
    parkinsons = NamedIndividual(IRI("http://example.org/biomedical#Parkinsons"))
    diabetes = NamedIndividual(IRI("http://example.org/biomedical#Diabetes"))
    cancer = NamedIndividual(IRI("http://example.org/biomedical#Cancer"))

    # Create genes
    apoe = NamedIndividual(IRI("http://example.org/biomedical#APOE"))
    brca1 = NamedIndividual(IRI("http://example.org/biomedical#BRCA1"))
    ins = NamedIndividual(IRI("http://example.org/biomedical#INS"))
    snca = NamedIndividual(IRI("http://example.org/biomedical#SNCA"))
    tp53 = NamedIndividual(IRI("http://example.org/biomedical#TP53"))

    # Create proteins
    apoE_protein = NamedIndividual(IRI("http://example.org/biomedical#ApoEProtein"))
    brca1_protein = NamedIndividual(IRI("http://example.org/biomedical#BRCA1Protein"))
    insulin = NamedIndividual(IRI("http://example.org/biomedical#Insulin"))
    alpha_synuclein = NamedIndividual(
        IRI("http://example.org/biomedical#AlphaSynuclein")
    )
    p53 = NamedIndividual(IRI("http://example.org/biomedical#p53"))

    # Create drugs
    metformin = NamedIndividual(IRI("http://example.org/biomedical#Metformin"))
    levodopa = NamedIndividual(IRI("http://example.org/biomedical#Levodopa"))
    donepezil = NamedIndividual(IRI("http://example.org/biomedical#Donepezil"))
    tamoxifen = NamedIndividual(IRI("http://example.org/biomedical#Tamoxifen"))

    # Create pathways
    glucose_metabolism = NamedIndividual(
        IRI("http://example.org/biomedical#GlucoseMetabolism")
    )
    apoptosis = NamedIndividual(IRI("http://example.org/biomedical#Apoptosis"))
    dna_repair = NamedIndividual(IRI("http://example.org/biomedical#DNARepair"))

    # Add class assertions
    individuals_by_class = [
        (disease_cls, [alzheimers, parkinsons, diabetes, cancer]),
        (gene_cls, [apoe, brca1, ins, snca, tp53]),
        (protein_cls, [apoE_protein, brca1_protein, insulin, alpha_synuclein, p53]),
        (drug_cls, [metformin, levodopa, donepezil, tamoxifen]),
        (pathway_cls, [glucose_metabolism, apoptosis, dna_repair]),
    ]

    for cls, individuals in individuals_by_class:
        for individual in individuals:
            ont.add_axiom(ClassAssertion(cls, individual))

    # Add gene-disease associations
    ont.add_axiom(ObjectPropertyAssertion(associated_with, apoe, alzheimers))
    ont.add_axiom(ObjectPropertyAssertion(associated_with, brca1, cancer))
    ont.add_axiom(ObjectPropertyAssertion(associated_with, ins, diabetes))
    ont.add_axiom(ObjectPropertyAssertion(associated_with, snca, parkinsons))
    ont.add_axiom(ObjectPropertyAssertion(associated_with, tp53, cancer))

    # Add gene-protein relationships
    ont.add_axiom(ObjectPropertyAssertion(encodes, apoe, apoE_protein))
    ont.add_axiom(ObjectPropertyAssertion(encodes, brca1, brca1_protein))
    ont.add_axiom(ObjectPropertyAssertion(encodes, ins, insulin))
    ont.add_axiom(ObjectPropertyAssertion(encodes, snca, alpha_synuclein))
    ont.add_axiom(ObjectPropertyAssertion(encodes, tp53, p53))

    # Add protein-pathway relationships
    ont.add_axiom(ObjectPropertyAssertion(participates_in, insulin, glucose_metabolism))
    ont.add_axiom(ObjectPropertyAssertion(participates_in, p53, apoptosis))
    ont.add_axiom(ObjectPropertyAssertion(participates_in, brca1_protein, dna_repair))

    # Add drug-target relationships
    ont.add_axiom(ObjectPropertyAssertion(targets, metformin, insulin))
    ont.add_axiom(ObjectPropertyAssertion(targets, donepezil, apoE_protein))
    ont.add_axiom(ObjectPropertyAssertion(targets, tamoxifen, p53))

    # Add drug-disease relationships
    ont.add_axiom(ObjectPropertyAssertion(treats, metformin, diabetes))
    ont.add_axiom(ObjectPropertyAssertion(treats, levodopa, parkinsons))
    ont.add_axiom(ObjectPropertyAssertion(treats, donepezil, alzheimers))
    ont.add_axiom(ObjectPropertyAssertion(treats, tamoxifen, cancer))

    # Add protein interactions
    ont.add_axiom(ObjectPropertyAssertion(interacts_with, p53, brca1_protein))
    ont.add_axiom(ObjectPropertyAssertion(interacts_with, insulin, apoE_protein))

    # Add some data properties
    ont.add_axiom(
        DataPropertyAssertion(name_prop, alzheimers, Literal("Alzheimer's Disease"))
    )
    ont.add_axiom(DataPropertyAssertion(identifier_prop, apoe, Literal("APOE")))
    ont.add_axiom(DataPropertyAssertion(name_prop, metformin, Literal("Metformin")))

    print(f"Created ontology with {ont.get_axiom_count()} axioms")
    return ont


def example_1_filter_by_disease(ont):
    """
    Extract all information related to a specific disease.

    Demonstrates extracting a 2-hop neighborhood around Alzheimer's disease,
    which includes the disease, associated genes, encoded proteins, and
    targeting drugs.

    Parameters
    ----------
    ont : Ontology
        The biomedical ontology to filter.

    Notes
    -----
    The extracted subgraph is saved to 'alzheimers_subgraph.rdf' in RDF/XML format.
    A 2-hop neighborhood from a disease typically includes:
    - Hop 0: The disease itself
    - Hop 1: Associated genes, treating drugs
    - Hop 2: Proteins encoded by genes, targets of drugs
    """
    print("\n" + "=" * 70)
    print("Example 1: Extract Alzheimer's Disease Subgraph")
    print("=" * 70)

    # Create filter focused on Alzheimer's disease
    filter_obj = OntologyFilter(ont)
    alzheimers_iri = IRI("http://example.org/biomedical#Alzheimers")

    # Extract 2-hop neighborhood (disease -> genes -> proteins -> drugs)
    result = filter_obj.extract_neighborhood(alzheimers_iri, 2)

    print(
        f"Original ontology: {result.original_axiom_count} axioms, "
        f"{result.original_individual_count} individuals"
    )
    print(
        f"Alzheimer's subgraph: {result.filtered_axiom_count} axioms, "
        f"{result.filtered_individual_count} individuals"
    )
    print(f"\nIncluded individuals: {len(result.included_individuals)}")

    # Save to file
    rdf_content = RDFXMLSerializer.serialize(result.ontology)
    with open("alzheimers_subgraph.rdf", "w") as f:
        f.write(rdf_content)
    print("Saved to alzheimers_subgraph.rdf")


def example_2_filter_by_entity_type(ont):
    """
    Extract only drugs and their direct targets.

    Demonstrates filtering by entity class (Drug) and analyzing the
    neighborhood of each drug to identify its targets.

    Parameters
    ----------
    ont : Ontology
        The biomedical ontology to filter.

    Notes
    -----
    This example shows two approaches:
    1. filter_by_classes() to get all drugs
    2. get_neighbors() to find 1-hop neighbors of each drug
    """
    print("\n" + "=" * 70)
    print("Example 2: Extract Drug-Target Network")
    print("=" * 70)

    filter_obj = OntologyFilter(ont)
    drug_cls_iri = IRI("http://example.org/biomedical#Drug")

    # Get all drugs and their 1-hop neighbors (targets)
    result = filter_obj.filter_by_classes({drug_cls_iri})

    print(
        f"Drug network: {result.filtered_axiom_count} axioms, "
        f"{result.filtered_individual_count} individuals"
    )

    # Now expand to include immediate targets (1-hop)
    drug_individuals = ont.get_individuals_of_class(Class(drug_cls_iri))
    print(f"Found {len(drug_individuals)} drugs")

    # Extract neighborhood around all drugs
    all_drug_iris = {ind.get_iri() for ind in drug_individuals}
    expanded_result = filter_obj.filter_by_individuals(all_drug_iris)

    # Get 1-hop neighbors for each drug
    for drug in drug_individuals:
        neighbors = ont.get_neighbors(drug, 1)
        print(f"  {drug.get_iri().get_abbreviated()} has {len(neighbors)} neighbors")


def example_3_find_path(ont):
    """
    Find connection path between disease and drug.

    Demonstrates path finding between two entities in the knowledge graph.
    Uses BFS to find the shortest path from Diabetes to Metformin.

    Parameters
    ----------
    ont : Ontology
        The biomedical ontology to search.

    Notes
    -----
    The path typically includes intermediate entities:
    Diabetes -> (treats) -> Metformin (direct connection)
    The algorithm runs in O(V+E) time using BFS.
    """
    print("\n" + "=" * 70)
    print("Example 3: Find Path from Disease to Drug")
    print("=" * 70)

    filter_obj = OntologyFilter(ont)

    # Find path from Diabetes to Metformin
    diabetes_iri = IRI("http://example.org/biomedical#Diabetes")
    metformin_iri = IRI("http://example.org/biomedical#Metformin")

    # Check if path exists
    diabetes = NamedIndividual(diabetes_iri)
    metformin = NamedIndividual(metformin_iri)
    has_path = ont.has_path(diabetes, metformin)

    print(f"Path exists from Diabetes to Metformin: {has_path}")

    if has_path:
        result = filter_obj.extract_path(diabetes_iri, metformin_iri)
        print(f"Path subgraph contains {result.filtered_individual_count} individuals")
        print(f"Path axioms: {result.filtered_axiom_count}")
        print("\nIndividuals in path:")
        for iri in result.included_individuals:
            print(f"  - {iri.get_abbreviated()}")


def example_4_multi_disease_analysis(ont):
    """
    Compare multiple diseases.

    Demonstrates extracting and comparing 2-hop neighborhoods for multiple
    diseases to analyze their relative complexity and connectivity.

    Parameters
    ----------
    ont : Ontology
        The biomedical ontology to analyze.

    Notes
    -----
    Larger neighborhoods may indicate:
    - More associated genes
    - More treatment options
    - More complex molecular mechanisms
    - Better-studied diseases
    """
    print("\n" + "=" * 70)
    print("Example 4: Multi-Disease Comparison")
    print("=" * 70)

    filter_obj = OntologyFilter(ont)

    diseases = [
        ("Alzheimers", IRI("http://example.org/biomedical#Alzheimers")),
        ("Parkinsons", IRI("http://example.org/biomedical#Parkinsons")),
        ("Diabetes", IRI("http://example.org/biomedical#Diabetes")),
        ("Cancer", IRI("http://example.org/biomedical#Cancer")),
    ]

    print("\nDisease neighborhood sizes (2-hop):")
    for name, iri in diseases:
        result = filter_obj.extract_neighborhood(iri, 2)
        print(
            f"  {name:15} {result.filtered_individual_count} individuals, "
            f"{result.filtered_axiom_count} axioms"
        )


def example_5_random_sampling(ont):
    """
    Random sampling for analysis.

    Demonstrates random sampling of individuals from the ontology for
    statistical analysis or testing purposes.

    Parameters
    ----------
    ont : Ontology
        The biomedical ontology to sample from.

    Notes
    -----
    Uses a fixed seed (42) for reproducible sampling. Random sampling is
    useful for creating test datasets or performing statistical analysis
    on large knowledge graphs.
    """
    print("\n" + "=" * 70)
    print("Example 5: Random Sampling")
    print("=" * 70)

    filter_obj = OntologyFilter(ont)

    # Create random samples of different sizes
    for sample_size in [5, 10, 15]:
        result = filter_obj.random_sample(sample_size, seed=42)
        print(
            f"Sample of {sample_size} individuals: "
            f"{result.filtered_axiom_count} axioms, "
            f"{result.filtered_individual_count} actual individuals"
        )


def example_6_builder_pattern(ont):
    """
    Using builder pattern for complex filters.

    Demonstrates the builder pattern API for creating complex, composable
    filters by chaining method calls.

    Parameters
    ----------
    ont : Ontology
        The biomedical ontology to filter.

    Notes
    -----
    The builder pattern allows for fluent, readable filter construction:
    - with_classes() to specify entity types
    - with_individuals() to specify specific entities
    - with_max_depth() to limit traversal depth
    - execute() to apply the filter
    """
    print("\n" + "=" * 70)
    print("Example 6: Complex Filtering with Builder Pattern")
    print("=" * 70)

    # Create a complex filter: all genes associated with cancer
    cancer_gene_filter = (
        OntologyFilter(ont)
        .with_classes({IRI("http://example.org/biomedical#Gene")})
        .with_max_depth(1)
    )

    result = cancer_gene_filter.execute()
    print(
        f"Gene subgraph: {result.filtered_individual_count} individuals, "
        f"{result.filtered_axiom_count} axioms"
    )


def example_7_performance_comparison(ont):
    """
    Demonstrate performance with larger operations.

    Benchmarks the performance of various subgraph extraction operations
    to showcase the efficiency of the C++ backend.

    Parameters
    ----------
    ont : Ontology
        The biomedical ontology to benchmark.

    Notes
    -----
    All operations leverage optimized C++ algorithms:
    - Neighborhood extraction: O(V+E) BFS traversal
    - Path finding: O(V+E) BFS with early termination
    - Hash-based lookups: O(1) average case

    Performance is excellent even on this small graph and scales well
    to much larger knowledge graphs.
    """
    print("\n" + "=" * 70)
    print("Example 7: Performance Demonstration")
    print("=" * 70)

    import time

    filter_obj = OntologyFilter(ont)

    # Time a complex neighborhood extraction
    start = time.time()
    result = filter_obj.extract_neighborhood(
        IRI("http://example.org/biomedical#Cancer"), 3
    )
    elapsed = time.time() - start

    print(f"Extracted 3-hop neighborhood in {elapsed * 1000:.2f}ms")
    print(
        f"Result: {result.filtered_individual_count} individuals, "
        f"{result.filtered_axiom_count} axioms"
    )

    # Time multiple path extractions
    start = time.time()
    paths_found = 0
    for i in range(10):
        alzheimers = IRI("http://example.org/biomedical#Alzheimers")
        metformin = IRI("http://example.org/biomedical#Metformin")
        result = filter_obj.extract_path(alzheimers, metformin)
        if result.filtered_individual_count > 0:
            paths_found += 1
    elapsed = time.time() - start

    print(
        f"Performed 10 path searches in {elapsed * 1000:.2f}ms "
        f"({elapsed * 100:.2f}ms per search)"
    )


def main():
    """
    Run all subgraph extraction examples.

    Executes a comprehensive suite of examples demonstrating various
    subgraph extraction techniques on a biomedical knowledge graph.

    Examples
    --------
    Run from the examples directory:
        >>> python subgraph_extraction_example.py

    Notes
    -----
    Creates a biomedical ontology and runs 7 examples:
    1. Disease-focused subgraph extraction
    2. Drug-target network extraction
    3. Path finding between entities
    4. Multi-disease comparison
    5. Random sampling
    6. Builder pattern usage
    7. Performance benchmarking

    All examples use the high-performance C++ OntologyFilter backend.
    """
    print("Biomedical Knowledge Graph - Subgraph Extraction Examples")
    print("=" * 70)

    # Create the ontology
    ont = create_biomedical_ontology()

    # Run all examples
    example_1_filter_by_disease(ont)
    example_2_filter_by_entity_type(ont)
    example_3_find_path(ont)
    example_4_multi_disease_analysis(ont)
    example_5_random_sampling(ont)
    example_6_builder_pattern(ont)
    example_7_performance_comparison(ont)

    print("\n" + "=" * 70)
    print("All examples completed successfully!")
    print("=" * 70)
    print("\nKey Features Demonstrated:")
    print("  ✓ Neighborhood extraction (k-hop)")
    print("  ✓ Path finding between entities")
    print("  ✓ Filtering by class membership")
    print("  ✓ Filtering by specific individuals")
    print("  ✓ Random sampling")
    print("  ✓ Builder pattern for complex filters")
    print("  ✓ High-performance C++ backend")
    print("\nAll operations run in O(V+E) time with efficient memory usage.")


if __name__ == "__main__":
    main()
