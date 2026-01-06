"""
PharmaTox Knowledge Graph Builder

This script demonstrates how to build a biomedical knowledge graph using ISTA's
owl2 library. It loads an ontology and populates it with data from multiple
sources (CSV, TSV, SQLite).

IMPORTANT: This is a TOY EXAMPLE using SYNTHETIC DATA for testing and
demonstration purposes only. The relationships between drugs, genes, diseases,
etc. are fictitious and should NOT be used for any real biomedical research.
"""

import csv
import os
import sqlite3
import sys
from pathlib import Path
from typing import Any, Dict

# Fix encoding for Windows console
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

from ista import owl2


def load_csv(filepath: str) -> list:
    """Load a CSV file and return list of row dictionaries."""
    with open(filepath, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)


def load_tsv(filepath: str) -> list:
    """Load a TSV file and return list of row dictionaries."""
    with open(filepath, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        return list(reader)


def load_sqlite_table(db_path: str, table_name: str) -> list:
    """Load a SQLite table and return list of row dictionaries."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


class PharmaToxBuilder:
    """Builder class for the PharmaTox knowledge graph."""

    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.iri_base = "http://example.org/pharmatox"
        self.onto = None
        self.iris = {}

        # Track created individuals for relationship mapping
        self.individuals = {
            "Drug": {},
            "Gene": {},
            "Disease": {},
            "Pathway": {},
            "AdverseEvent": {},
            "DrugClass": {},
            "CellType": {},
        }

    def create_ontology_structure(self):
        """Create the ontology with all class and property declarations."""
        print("\n[Step 1] Creating ontology structure...")

        self.onto = owl2.Ontology(owl2.IRI(self.iri_base))
        self.onto.register_prefix("ptox", f"{self.iri_base}#")

        # Define classes
        classes = [
            "Drug",
            "Gene",
            "Disease",
            "Pathway",
            "AdverseEvent",
            "DrugClass",
            "CellType",
            "Assay",
        ]
        for cls_name in classes:
            iri = owl2.IRI(f"{self.iri_base}#{cls_name}")
            self.onto.add_axiom(owl2.Declaration(owl2.EntityType.CLASS, iri))
            self.iris[f"class_{cls_name}"] = iri

        # Define data properties
        data_properties = [
            "commonName",
            "xrefDrugbank",
            "xrefCasRN",
            "xrefPubchemCID",
            "xrefNcbiGene",
            "geneSymbol",
            "xrefUmlsCUI",
            "xrefMeSH",
            "xrefReactome",
            "xrefMeddra",
            "severity",
            "xrefCL",
            "ld50Value",
            "ld50Units",
            "assayResult",
        ]
        for prop_name in data_properties:
            iri = owl2.IRI(f"{self.iri_base}#{prop_name}")
            self.onto.add_axiom(owl2.Declaration(owl2.EntityType.DATA_PROPERTY, iri))
            self.iris[f"dp_{prop_name}"] = iri

        # Define object properties
        object_properties = [
            "drugTreatsDisease",
            "drugCausesAdverseEvent",
            "drugInClass",
            "drugTargetsGene",
            "geneAssociatesWithDisease",
            "geneInPathway",
            "geneExpressedInCellType",
            "pathwayInvolvedInDisease",
            "drugTestedInAssay",
            "assayTargetsGene",
        ]
        for prop_name in object_properties:
            iri = owl2.IRI(f"{self.iri_base}#{prop_name}")
            self.onto.add_axiom(owl2.Declaration(owl2.EntityType.OBJECT_PROPERTY, iri))
            self.iris[f"op_{prop_name}"] = iri

        print(f"  Created {len(classes)} classes")
        print(f"  Created {len(data_properties)} data properties")
        print(f"  Created {len(object_properties)} object properties")

    def add_individual(
        self, class_name: str, local_id: str, data_props: Dict[str, Any]
    ) -> owl2.NamedIndividual:
        """Add an individual with its class assertion and data properties."""
        # Create individual IRI
        individual_iri = owl2.IRI(f"{self.iri_base}#{local_id}")
        individual = owl2.NamedIndividual(individual_iri)

        # Declare individual
        self.onto.add_axiom(
            owl2.Declaration(owl2.EntityType.NAMED_INDIVIDUAL, individual_iri)
        )

        # Add class assertion
        class_obj = owl2.Class(self.iris[f"class_{class_name}"])
        self.onto.add_axiom(owl2.ClassAssertion(class_obj, individual))

        # Add data properties
        for prop_name, value in data_props.items():
            if value is None or value == "" or value == "None":
                continue
            prop = owl2.DataProperty(self.iris[f"dp_{prop_name}"])
            literal = owl2.Literal(str(value))
            self.onto.add_axiom(owl2.DataPropertyAssertion(prop, individual, literal))

        return individual

    def add_relationship(
        self, prop_name: str, subject: owl2.NamedIndividual, obj: owl2.NamedIndividual
    ):
        """Add an object property assertion."""
        prop = owl2.ObjectProperty(self.iris[f"op_{prop_name}"])
        self.onto.add_axiom(owl2.ObjectPropertyAssertion(prop, subject, obj))

    def load_drugs(self):
        """Load drugs from CSV and toxicity enrichment."""
        print("\n[Step 2a] Loading Drugs...")

        # Load primary drug data
        drugs = load_csv(self.data_dir / "drugs.csv")
        for row in drugs:
            individual = self.add_individual(
                "Drug",
                row["drugbank_id"],
                {
                    "xrefDrugbank": row["drugbank_id"],
                    "commonName": row["common_name"],
                    "xrefCasRN": row["cas_number"],
                    "xrefPubchemCID": row["pubchem_cid"],
                },
            )
            self.individuals["Drug"][row["drugbank_id"]] = individual
            # Also index by CAS for toxicity enrichment
            if row["cas_number"]:
                self.individuals["Drug"][f"cas:{row['cas_number']}"] = individual

        print(f"  Loaded {len(drugs)} drugs")

        # Load toxicity enrichment data
        print("  Enriching with toxicity data...")
        toxicity = load_csv(self.data_dir / "drug_toxicity.csv")
        enriched = 0
        for row in toxicity:
            cas_key = f"cas:{row['cas_number']}"
            if cas_key in self.individuals["Drug"]:
                individual = self.individuals["Drug"][cas_key]
                if row["ld50_value"]:
                    prop = owl2.DataProperty(self.iris["dp_ld50Value"])
                    literal = owl2.Literal(row["ld50_value"])
                    self.onto.add_axiom(
                        owl2.DataPropertyAssertion(prop, individual, literal)
                    )
                if row["ld50_units"]:
                    prop = owl2.DataProperty(self.iris["dp_ld50Units"])
                    literal = owl2.Literal(row["ld50_units"])
                    self.onto.add_axiom(
                        owl2.DataPropertyAssertion(prop, individual, literal)
                    )
                enriched += 1
        print(f"  Enriched {enriched} drugs with toxicity data")

    def load_genes(self):
        """Load genes from TSV."""
        print("\n[Step 2b] Loading Genes...")

        genes = load_tsv(self.data_dir / "genes.tsv")
        for row in genes:
            individual = self.add_individual(
                "Gene",
                row["gene_symbol"],
                {
                    "xrefNcbiGene": row["ncbi_gene_id"],
                    "geneSymbol": row["gene_symbol"],
                    "commonName": row["common_name"],
                },
            )
            self.individuals["Gene"][row["gene_symbol"]] = individual
            # Also index by NCBI ID for relationship mapping
            self.individuals["Gene"][int(row["ncbi_gene_id"])] = individual

        print(f"  Loaded {len(genes)} genes")

    def load_diseases(self):
        """Load diseases from TSV."""
        print("\n[Step 2c] Loading Diseases...")

        diseases = load_tsv(self.data_dir / "diseases.tsv")
        for row in diseases:
            individual = self.add_individual(
                "Disease",
                row["umls_cui"],
                {
                    "xrefUmlsCUI": row["umls_cui"],
                    "xrefMeSH": row["mesh_id"],
                    "commonName": row["common_name"],
                },
            )
            self.individuals["Disease"][row["umls_cui"]] = individual

        print(f"  Loaded {len(diseases)} diseases")

    def load_pathways(self):
        """Load pathways from TSV."""
        print("\n[Step 2d] Loading Pathways...")

        pathways = load_tsv(self.data_dir / "pathways.tsv")
        for row in pathways:
            individual = self.add_individual(
                "Pathway",
                row["reactome_id"],
                {
                    "xrefReactome": row["reactome_id"],
                    "commonName": row["pathway_name"],
                },
            )
            self.individuals["Pathway"][row["reactome_id"]] = individual

        print(f"  Loaded {len(pathways)} pathways")

    def load_drug_classes(self):
        """Load drug classes (derived from drugs.csv)."""
        print("\n[Step 2e] Loading Drug Classes...")

        drugs = load_csv(self.data_dir / "drugs.csv")
        unique_classes = set(row["drug_class"] for row in drugs)

        for drug_class in unique_classes:
            # Create a safe IRI-friendly ID
            class_id = drug_class.replace(" ", "_")
            individual = self.add_individual(
                "DrugClass",
                class_id,
                {
                    "commonName": drug_class,
                },
            )
            self.individuals["DrugClass"][drug_class] = individual

        print(f"  Loaded {len(unique_classes)} drug classes")

    def load_sqlite_entities(self):
        """Load entities from SQLite database."""
        print("\n[Step 2f] Loading entities from SQLite...")

        db_path = self.data_dir / "pharmatox.db"

        # Load adverse events
        adverse_events = load_sqlite_table(str(db_path), "adverse_events")
        for row in adverse_events:
            individual = self.add_individual(
                "AdverseEvent",
                row["meddra_id"],
                {
                    "xrefMeddra": row["meddra_id"],
                    "commonName": row["event_name"],
                    "severity": row["severity"],
                },
            )
            self.individuals["AdverseEvent"][row["meddra_id"]] = individual
        print(f"  Loaded {len(adverse_events)} adverse events")

        # Load cell types
        cell_types = load_sqlite_table(str(db_path), "cell_types")
        for row in cell_types:
            # Clean up CL ID for IRI (replace : with _)
            safe_id = row["cl_id"].replace(":", "_")
            individual = self.add_individual(
                "CellType",
                safe_id,
                {
                    "xrefCL": row["cl_id"],
                    "commonName": row["cell_name"],
                },
            )
            self.individuals["CellType"][row["cl_id"]] = individual
        print(f"  Loaded {len(cell_types)} cell types")

    def load_relationships(self):
        """Load all relationships from various sources."""
        print("\n[Step 3] Loading Relationships...")

        db_path = self.data_dir / "pharmatox.db"

        # Drug -> DrugClass (from CSV)
        drugs = load_csv(self.data_dir / "drugs.csv")
        count = 0
        for row in drugs:
            drug = self.individuals["Drug"].get(row["drugbank_id"])
            drug_class = self.individuals["DrugClass"].get(row["drug_class"])
            if drug and drug_class:
                self.add_relationship("drugInClass", drug, drug_class)
                count += 1
        print(f"  drugInClass: {count} relationships")

        # Drug -> Disease (treats)
        drug_disease = load_sqlite_table(str(db_path), "drug_treats_disease")
        count = 0
        for row in drug_disease:
            drug = self.individuals["Drug"].get(row["drugbank_id"])
            disease = self.individuals["Disease"].get(row["umls_cui"])
            if drug and disease:
                self.add_relationship("drugTreatsDisease", drug, disease)
                count += 1
        print(f"  drugTreatsDisease: {count} relationships")

        # Drug -> Gene (targets)
        drug_gene = load_sqlite_table(str(db_path), "drug_targets_gene")
        count = 0
        for row in drug_gene:
            drug = self.individuals["Drug"].get(row["drugbank_id"])
            gene = self.individuals["Gene"].get(row["ncbi_gene_id"])
            if drug and gene:
                self.add_relationship("drugTargetsGene", drug, gene)
                count += 1
        print(f"  drugTargetsGene: {count} relationships")

        # Gene -> Disease (associates)
        gene_disease = load_sqlite_table(str(db_path), "gene_disease_association")
        count = 0
        for row in gene_disease:
            gene = self.individuals["Gene"].get(row["ncbi_gene_id"])
            disease = self.individuals["Disease"].get(row["umls_cui"])
            if gene and disease:
                self.add_relationship("geneAssociatesWithDisease", gene, disease)
                count += 1
        print(f"  geneAssociatesWithDisease: {count} relationships")

        # Gene -> Pathway
        gene_pathway = load_sqlite_table(str(db_path), "gene_pathway")
        count = 0
        for row in gene_pathway:
            gene = self.individuals["Gene"].get(row["ncbi_gene_id"])
            pathway = self.individuals["Pathway"].get(row["reactome_id"])
            if gene and pathway:
                self.add_relationship("geneInPathway", gene, pathway)
                count += 1
        print(f"  geneInPathway: {count} relationships")

        # Drug -> AdverseEvent
        drug_ae = load_sqlite_table(str(db_path), "drug_adverse_event")
        count = 0
        for row in drug_ae:
            drug = self.individuals["Drug"].get(row["drugbank_id"])
            ae = self.individuals["AdverseEvent"].get(row["meddra_id"])
            if drug and ae:
                self.add_relationship("drugCausesAdverseEvent", drug, ae)
                count += 1
        print(f"  drugCausesAdverseEvent: {count} relationships")

        # Gene -> CellType (expression)
        gene_expr = load_sqlite_table(str(db_path), "gene_expression")
        count = 0
        for row in gene_expr:
            gene = self.individuals["Gene"].get(row["ncbi_gene_id"])
            cell_type = self.individuals["CellType"].get(row["cl_id"])
            if gene and cell_type:
                self.add_relationship("geneExpressedInCellType", gene, cell_type)
                count += 1
        print(f"  geneExpressedInCellType: {count} relationships")

    def print_statistics(self):
        """Print ontology statistics."""
        print("\n" + "=" * 60)
        print("PHARMATOX KNOWLEDGE GRAPH STATISTICS")
        print("=" * 60)
        print(self.onto.get_statistics())

        print("\nIndividuals by type:")
        for entity_type, individuals in self.individuals.items():
            # Count unique individuals (not aliases like cas:xxx)
            unique = len(
                [k for k in individuals.keys() if not str(k).startswith("cas:")]
            )
            print(f"  {entity_type}: {unique}")
        print("=" * 60)

    def save(self, output_path: str):
        """Save the ontology to file."""
        print(f"\n[Step 4] Saving ontology to {output_path}...")
        owl2.RDFXMLSerializer.serialize_to_file(self.onto, output_path)
        print("  Done!")

    def build(self):
        """Execute the full build process."""
        self.create_ontology_structure()
        self.load_drugs()
        self.load_genes()
        self.load_diseases()
        self.load_pathways()
        self.load_drug_classes()
        self.load_sqlite_entities()
        self.load_relationships()
        self.print_statistics()


def main():
    """Main entry point."""
    print("=" * 60)
    print("PHARMATOX KNOWLEDGE GRAPH BUILDER")
    print("=" * 60)
    print("\nThis example demonstrates building a biomedical knowledge graph")
    print("from multiple data sources using ISTA's owl2 library.")
    print("\nIMPORTANT: This is a TOY EXAMPLE with SYNTHETIC DATA!")
    print("Do not use for real biomedical research.\n")

    # Check if owl2 is available
    if not owl2.is_available():
        print("ERROR: C++ OWL2 bindings are not available!")
        print("Please build the C++ extension first.")
        return 1

    print("C++ OWL2 bindings are available\n")

    # Determine paths
    script_dir = Path(__file__).parent
    example_dir = script_dir.parent
    data_dir = example_dir / "data"
    output_file = example_dir / "pharmatox_populated.owl"

    # Check that data exists
    if not (data_dir / "pharmatox.db").exists():
        print("Database not found. Creating it first...")
        import subprocess

        subprocess.run([sys.executable, script_dir / "create_sqlite_db.py"])

    # Build the knowledge graph
    builder = PharmaToxBuilder(data_dir)
    builder.build()
    builder.save(str(output_file))

    print("\n" + "=" * 60)
    print("BUILD COMPLETE!")
    print("=" * 60)
    print(f"\nOutput: {output_file}")
    print("\nThe knowledge graph contains:")
    print("  - Drugs with toxicity annotations")
    print("  - Genes with pathway memberships")
    print("  - Diseases with gene associations")
    print("  - Drug-disease treatment relationships")
    print("  - Drug-gene target interactions")
    print("  - Adverse event associations")
    print("  - Cell type expression data")

    return 0


if __name__ == "__main__":
    sys.exit(main())
