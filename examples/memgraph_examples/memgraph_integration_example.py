"""
Memgraph Graph Database Integration Example

This example demonstrates how to populate a Memgraph graph database from an OWL2 ontology.

Memgraph is a high-performance, in-memory graph database that uses Cypher query language.
It's designed for real-time analytics and supports ACID transactions.

Mapping:
    OWL Individuals → Memgraph Nodes
    OWL Classes → Node Labels (types)
    Data Properties → Node Properties
    Object Properties → Relationships

Requirements:
    - Memgraph running (docker or local install)
    - neo4j Python driver: pip install neo4j
    - ista package with owl2 support

Start Memgraph:
    docker run -p 7687:7687 -p 7444:7444 memgraph/memgraph-platform

Then run this example.
"""

import sys
from ista import owl2

# Add parent directory to path to import memgraph_loader
sys.path.insert(0, "..")
from ista.memgraph_loader import MemgraphLoader

# Fix encoding for Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")


def create_medical_ontology():
    """Create a sample medical ontology for demonstration."""
    print("\n[Creating Sample Ontology]")

    iri_base = "http://example.org/medical"
    onto = owl2.Ontology(owl2.IRI(iri_base))
    onto.register_prefix("med", f"{iri_base}#")

    # Define classes
    patient_class = owl2.IRI(f"{iri_base}#Patient")
    disease_class = owl2.IRI(f"{iri_base}#Disease")
    drug_class = owl2.IRI(f"{iri_base}#Drug")
    doctor_class = owl2.IRI(f"{iri_base}#Doctor")

    for class_iri in [patient_class, disease_class, drug_class, doctor_class]:
        onto.add_axiom(owl2.Declaration(owl2.EntityType.CLASS, class_iri))

    # Define data properties
    name_prop = owl2.IRI(f"{iri_base}#name")
    age_prop = owl2.IRI(f"{iri_base}#age")
    severity_prop = owl2.IRI(f"{iri_base}#severity")
    dosage_prop = owl2.IRI(f"{iri_base}#dosage")
    specialty_prop = owl2.IRI(f"{iri_base}#specialty")

    for prop_iri in [name_prop, age_prop, severity_prop, dosage_prop, specialty_prop]:
        onto.add_axiom(owl2.Declaration(owl2.EntityType.DATA_PROPERTY, prop_iri))

    # Define object properties
    diagnoses_prop = owl2.IRI(f"{iri_base}#diagnoses")
    prescribes_prop = owl2.IRI(f"{iri_base}#prescribes")
    treats_prop = owl2.IRI(f"{iri_base}#treats")
    treatedBy_prop = owl2.IRI(f"{iri_base}#treatedBy")

    for prop_iri in [diagnoses_prop, prescribes_prop, treats_prop, treatedBy_prop]:
        onto.add_axiom(owl2.Declaration(owl2.EntityType.OBJECT_PROPERTY, prop_iri))

    # Create patients
    print("  Creating patients...")
    patients = []
    patient_data = [
        ("P001", "Alice Johnson", 45),
        ("P002", "Bob Smith", 62),
        ("P003", "Carol Williams", 38),
        ("P004", "David Brown", 55),
    ]

    for pid, pname, page in patient_data:
        patient_iri = owl2.IRI(f"{iri_base}#{pid}")
        patient = owl2.NamedIndividual(patient_iri)
        patients.append((pid, patient))

        onto.add_axiom(owl2.Declaration(owl2.EntityType.NAMED_INDIVIDUAL, patient_iri))
        onto.add_axiom(owl2.ClassAssertion(owl2.Class(patient_class), patient))
        onto.add_axiom(
            owl2.DataPropertyAssertion(
                owl2.DataProperty(name_prop), patient, owl2.Literal(pname)
            )
        )
        onto.add_axiom(
            owl2.DataPropertyAssertion(
                owl2.DataProperty(age_prop), patient, owl2.Literal(str(page))
            )
        )

    # Create diseases
    print("  Creating diseases...")
    diseases = []
    disease_data = [
        ("D001", "Hypertension", "moderate"),
        ("D002", "Diabetes Type 2", "severe"),
        ("D003", "Asthma", "mild"),
    ]

    for did, dname, severity in disease_data:
        disease_iri = owl2.IRI(f"{iri_base}#{did}")
        disease = owl2.NamedIndividual(disease_iri)
        diseases.append((did, disease))

        onto.add_axiom(owl2.Declaration(owl2.EntityType.NAMED_INDIVIDUAL, disease_iri))
        onto.add_axiom(owl2.ClassAssertion(owl2.Class(disease_class), disease))
        onto.add_axiom(
            owl2.DataPropertyAssertion(
                owl2.DataProperty(name_prop), disease, owl2.Literal(dname)
            )
        )
        onto.add_axiom(
            owl2.DataPropertyAssertion(
                owl2.DataProperty(severity_prop), disease, owl2.Literal(severity)
            )
        )

    # Create drugs
    print("  Creating drugs...")
    drugs = []
    drug_data = [
        ("DR001", "Lisinopril", "10mg daily"),
        ("DR002", "Metformin", "500mg twice daily"),
        ("DR003", "Albuterol", "As needed"),
    ]

    for drug_id, drug_name, drug_dosage in drug_data:
        drug_iri = owl2.IRI(f"{iri_base}#{drug_id}")
        drug = owl2.NamedIndividual(drug_iri)
        drugs.append((drug_id, drug))

        onto.add_axiom(owl2.Declaration(owl2.EntityType.NAMED_INDIVIDUAL, drug_iri))
        onto.add_axiom(owl2.ClassAssertion(owl2.Class(drug_class), drug))
        onto.add_axiom(
            owl2.DataPropertyAssertion(
                owl2.DataProperty(name_prop), drug, owl2.Literal(drug_name)
            )
        )
        onto.add_axiom(
            owl2.DataPropertyAssertion(
                owl2.DataProperty(dosage_prop), drug, owl2.Literal(drug_dosage)
            )
        )

    # Create doctors
    print("  Creating doctors...")
    doctors = []
    doctor_data = [
        ("DOC001", "Dr. Emily Chen", "Cardiology"),
        ("DOC002", "Dr. Michael Rodriguez", "Endocrinology"),
    ]

    for doc_id, doc_name, doc_specialty in doctor_data:
        doctor_iri = owl2.IRI(f"{iri_base}#{doc_id}")
        doctor = owl2.NamedIndividual(doctor_iri)
        doctors.append((doc_id, doctor))

        onto.add_axiom(owl2.Declaration(owl2.EntityType.NAMED_INDIVIDUAL, doctor_iri))
        onto.add_axiom(owl2.ClassAssertion(owl2.Class(doctor_class), doctor))
        onto.add_axiom(
            owl2.DataPropertyAssertion(
                owl2.DataProperty(name_prop), doctor, owl2.Literal(doc_name)
            )
        )
        onto.add_axiom(
            owl2.DataPropertyAssertion(
                owl2.DataProperty(specialty_prop), doctor, owl2.Literal(doc_specialty)
            )
        )

    # Create relationships
    print("  Creating relationships...")

    # Patient diagnoses
    onto.add_axiom(
        owl2.ObjectPropertyAssertion(
            owl2.ObjectProperty(diagnoses_prop), patients[0][1], diseases[0][1]
        )
    )  # Alice has Hypertension
    onto.add_axiom(
        owl2.ObjectPropertyAssertion(
            owl2.ObjectProperty(diagnoses_prop), patients[1][1], diseases[1][1]
        )
    )  # Bob has Diabetes
    onto.add_axiom(
        owl2.ObjectPropertyAssertion(
            owl2.ObjectProperty(diagnoses_prop), patients[2][1], diseases[2][1]
        )
    )  # Carol has Asthma
    onto.add_axiom(
        owl2.ObjectPropertyAssertion(
            owl2.ObjectProperty(diagnoses_prop), patients[3][1], diseases[0][1]
        )
    )  # David has Hypertension

    # Doctor treats patient
    onto.add_axiom(
        owl2.ObjectPropertyAssertion(
            owl2.ObjectProperty(treats_prop), doctors[0][1], patients[0][1]
        )
    )  # Dr. Chen treats Alice
    onto.add_axiom(
        owl2.ObjectPropertyAssertion(
            owl2.ObjectProperty(treats_prop), doctors[1][1], patients[1][1]
        )
    )  # Dr. Rodriguez treats Bob
    onto.add_axiom(
        owl2.ObjectPropertyAssertion(
            owl2.ObjectProperty(treats_prop), doctors[0][1], patients[3][1]
        )
    )  # Dr. Chen treats David

    # Doctor prescribes drug
    onto.add_axiom(
        owl2.ObjectPropertyAssertion(
            owl2.ObjectProperty(prescribes_prop), doctors[0][1], drugs[0][1]
        )
    )  # Dr. Chen prescribes Lisinopril
    onto.add_axiom(
        owl2.ObjectPropertyAssertion(
            owl2.ObjectProperty(prescribes_prop), doctors[1][1], drugs[1][1]
        )
    )  # Dr. Rodriguez prescribes Metformin

    print(f"✓ Created ontology with {onto.get_axiom_count()} axioms")
    print(f"  - {len(patient_data)} patients")
    print(f"  - {len(disease_data)} diseases")
    print(f"  - {len(drug_data)} drugs")
    print(f"  - {len(doctor_data)} doctors")

    return onto


def demonstrate_queries(loader: MemgraphLoader):
    """Demonstrate Cypher queries on the loaded graph."""
    print("\n[Demonstrating Cypher Queries]")

    # Query 1: Find all patients
    print("\n1. All Patients:")
    results = loader.execute_query("""
        MATCH (p:Patient)
        RETURN p.label as name, p.age as age
        ORDER BY p.age
    """)
    for record in results:
        print(f"   - {record['name']}, Age: {record['age']}")

    # Query 2: Find patients with their diseases
    print("\n2. Patient Diagnoses:")
    results = loader.execute_query("""
        MATCH (p:Patient)-[:diagnoses]->(d:Disease)
        RETURN p.label as patient, d.label as disease, d.severity as severity
        ORDER BY p.label
    """)
    for record in results:
        print(
            f"   - {record['patient']} has {record['disease']} ({record['severity']})"
        )

    # Query 3: Find doctors and their patients
    print("\n3. Doctor-Patient Relationships:")
    results = loader.execute_query("""
        MATCH (doc:Doctor)-[:treats]->(p:Patient)
        RETURN doc.label as doctor, doc.specialty as specialty,
               collect(p.label) as patients
    """)
    for record in results:
        print(f"   - {record['doctor']} ({record['specialty']})")
        for patient in record["patients"]:
            print(f"     → {patient}")

    # Query 4: Find treatment paths (doctor -> patient -> disease)
    print("\n4. Complete Treatment Paths:")
    results = loader.execute_query("""
        MATCH (doc:Doctor)-[:treats]->(p:Patient)-[:diagnoses]->(d:Disease)
        RETURN doc.label as doctor, p.label as patient, d.label as disease
        ORDER BY doc.label, p.label
    """)
    for record in results:
        print(f"   - {record['doctor']} → {record['patient']} → {record['disease']}")

    # Query 5: Find prescriptions
    print("\n5. Prescriptions:")
    results = loader.execute_query("""
        MATCH (doc:Doctor)-[:prescribes]->(drug:Drug)
        RETURN doc.label as doctor, drug.label as medication, drug.dosage as dosage
    """)
    for record in results:
        print(
            f"   - {record['doctor']} prescribes {record['medication']} ({record['dosage']})"
        )

    # Query 6: Graph statistics
    print("\n6. Graph Statistics:")
    results = loader.execute_query("""
        MATCH (n)
        RETURN labels(n)[1] as node_type, count(n) as count
        ORDER BY count DESC
    """)
    for record in results:
        print(f"   - {record['node_type']}: {record['count']} nodes")


def main():
    """Main execution function."""
    print("=" * 60)
    print("MEMGRAPH INTEGRATION EXAMPLE")
    print("=" * 60)

    # Check prerequisites
    if not owl2.is_available():
        print("ERROR: C++ OWL2 bindings are not available!")
        return 1

    print("✓ C++ OWL2 bindings available")

    # Create sample ontology
    print("\n[Step 1] Creating Sample Medical Ontology")
    onto = create_medical_ontology()

    # Display ontology statistics
    print(f"\nOntology Statistics:")
    print(onto.get_statistics())

    # Connect to Memgraph and load
    print("\n[Step 2] Connecting to Memgraph")
    print("Make sure Memgraph is running at bolt://localhost:7687")
    print("Start with: docker run -p 7687:7687 memgraph/memgraph-platform")

    try:
        with MemgraphLoader(uri="bolt://localhost:7687") as loader:
            print("✓ Connected to Memgraph")

            # Load ontology
            print("\n[Step 3] Loading Ontology into Memgraph")
            stats = loader.load_ontology(onto, clear_existing=True)

            # Demonstrate queries
            print("\n[Step 4] Querying the Graph")
            demonstrate_queries(loader)

    except Exception as e:
        print(f"\n✗ Error connecting to Memgraph: {e}")
        print("\nMake sure Memgraph is running:")
        print("  docker run -p 7687:7687 -p 7444:7444 memgraph/memgraph-platform")
        print("\nOr install Memgraph locally:")
        print("  https://memgraph.com/docs/getting-started")
        return 1

    print("\n" + "=" * 60)
    print("EXAMPLE COMPLETE")
    print("=" * 60)
    print("\nNext Steps:")
    print("1. Open Memgraph Lab at http://localhost:7444")
    print("2. Explore the graph visually")
    print("3. Run custom Cypher queries")
    print("4. Try the example queries above in Memgraph Lab")
    print("\nExample Cypher query to try:")
    print("  MATCH (p:Patient)-[r]->(d)")
    print("  RETURN p, r, d")

    return 0


if __name__ == "__main__":
    exit(main())
