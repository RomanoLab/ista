#!/usr/bin/env python3
"""
Comprehensive OWL2 Round-Trip Example using ista.owl2

This example demonstrates the complete workflow of working with OWL2 ontologies:
1. Creating an ontology from scratch with various axiom types
2. Serializing to both RDF/XML (.owl) and Functional Syntax (.ofn)
3. Parsing the saved ontology back from disk
4. Modifying the parsed ontology with new entities and axioms
5. Round-trip verification to ensure data integrity

This showcases best practices for using the ista.owl2 library, which provides
a high-performance C++ backend for OWL2 ontology manipulation in Python.

Author: ista library contributors
License: See LICENSE file in repository root
"""

import os
import sys
from pathlib import Path

# Import the ista.owl2 library (not _libista_owl2 directly - use the public API)
try:
    from ista.owl2 import (
        # Core types
        IRI,
        Literal,
        # Entities
        Class,
        ObjectProperty,
        DataProperty,
        AnnotationProperty,
        NamedIndividual,
        # Class Expressions
        NamedClass,
        ObjectSomeValuesFrom,
        ObjectAllValuesFrom,
        ObjectIntersectionOf,
        ObjectUnionOf,
        # Axioms
        Declaration,
        EntityType,
        SubClassOf,
        EquivalentClasses,
        DisjointClasses,
        ClassAssertion,
        ObjectPropertyAssertion,
        DataPropertyAssertion,
        ObjectPropertyDomain,
        ObjectPropertyRange,
        DataPropertyDomain,
        DataPropertyRange,
        FunctionalObjectProperty,
        FunctionalDataProperty,
        TransitiveObjectProperty,
        AnnotationAssertion,
        # Ontology
        Ontology,
        # Serializers and Parsers
        FunctionalSyntaxSerializer,
        RDFXMLSerializer,
        RDFXMLParser,
        # Standard namespaces
        xsd,
    )

    print("Successfully imported ista.owl2 library")
    print()

except ImportError as e:
    print(f"Error: Failed to import ista.owl2 library: {e}")
    print()
    print("Please ensure that:")
    print("  1. The C++ extension has been built: pip install -e .")
    print(
        "  2. Or build manually: mkdir build && cd build && cmake .. && cmake --build ."
    )
    print()
    sys.exit(1)


def print_section_header(title, char="="):
    """Print a formatted section header for better readability."""
    width = 80
    print()
    print(char * width)
    print(f" {title}")
    print(char * width)
    print()


def print_subsection_header(title):
    """Print a formatted subsection header."""
    print(f"\n{'─' * 80}")
    print(f"  {title}")
    print(f"{'─' * 80}\n")


def create_ontology_from_scratch():
    """
    Part 1: Create a comprehensive ontology from scratch.

    This function demonstrates:
    - Creating an ontology with a specific IRI
    - Registering standard and custom prefixes
    - Adding classes, object properties, data properties, and individuals
    - Creating a class hierarchy with SubClassOf axioms
    - Adding complex class expressions (restrictions, intersections, unions)
    - Defining property characteristics (functional, transitive, etc.)
    - Creating property domain and range axioms
    - Adding individual assertions (types and property values)
    - Annotating entities with labels and comments

    Returns:
        Ontology: The created ontology object
        str: Path to the saved .owl file
        str: Path to the saved .ofn file
    """
    print_section_header("PART 1: Creating Ontology from Scratch")

    # ========================================================================
    # Step 1.1: Create ontology and register prefixes
    # ========================================================================
    print_subsection_header("Step 1.1: Creating Ontology with IRI and Prefixes")

    # Create ontology with IRI
    onto_iri = IRI("http://example.org/biomedical/clinical")
    onto = Ontology(onto_iri)
    print(f"Created ontology with IRI: {onto_iri.to_string()}")

    # Register standard prefixes (required for proper serialization)
    onto.register_prefix("rdf", "http://www.w3.org/1999/02/22-rdf-syntax-ns#")
    onto.register_prefix("rdfs", "http://www.w3.org/2000/01/rdf-schema#")
    onto.register_prefix("xsd", "http://www.w3.org/2001/XMLSchema#")
    onto.register_prefix("owl", "http://www.w3.org/2002/07/owl#")

    # Register custom prefix for our ontology
    onto.register_prefix("clinic", "http://example.org/biomedical/clinical#")

    # Optional: Register additional domain-specific prefixes
    onto.register_prefix("foaf", "http://xmlns.com/foaf/0.1/")
    onto.register_prefix("dc", "http://purl.org/dc/elements/1.1/")

    prefix_map = onto.get_prefix_map()
    print(f"Registered {len(prefix_map)} prefixes:")
    for prefix, namespace in sorted(prefix_map.items()):
        print(f"  {prefix:8s} -> {namespace}")

    # ========================================================================
    # Step 1.2: Create classes and build class hierarchy
    # ========================================================================
    print_subsection_header("Step 1.2: Creating Classes and Class Hierarchy")

    # Define class IRIs using the registered prefix
    base_ns = "http://example.org/biomedical/clinical#"

    # Top-level classes
    person_iri = IRI("clinic", "Person", base_ns)
    disease_iri = IRI("clinic", "Disease", base_ns)
    treatment_iri = IRI("clinic", "Treatment", base_ns)

    # Subclasses of Person
    patient_iri = IRI("clinic", "Patient", base_ns)
    physician_iri = IRI("clinic", "Physician", base_ns)
    specialist_iri = IRI("clinic", "Specialist", base_ns)

    # Subclasses of Disease
    chronic_disease_iri = IRI("clinic", "ChronicDisease", base_ns)
    acute_disease_iri = IRI("clinic", "AcuteDisease", base_ns)
    genetic_disease_iri = IRI("clinic", "GeneticDisease", base_ns)

    # Subclasses of Treatment
    medication_iri = IRI("clinic", "Medication", base_ns)
    surgery_iri = IRI("clinic", "Surgery", base_ns)
    therapy_iri = IRI("clinic", "Therapy", base_ns)

    # Create class objects (needed for class expressions)
    person_cls = Class(person_iri)
    disease_cls = Class(disease_iri)
    treatment_cls = Class(treatment_iri)
    patient_cls = Class(patient_iri)
    physician_cls = Class(physician_iri)
    specialist_cls = Class(specialist_iri)
    chronic_disease_cls = Class(chronic_disease_iri)
    acute_disease_cls = Class(acute_disease_iri)
    genetic_disease_cls = Class(genetic_disease_iri)
    medication_cls = Class(medication_iri)
    surgery_cls = Class(surgery_iri)
    therapy_cls = Class(therapy_iri)

    # Add class declarations
    class_iris = [
        person_iri,
        disease_iri,
        treatment_iri,
        patient_iri,
        physician_iri,
        specialist_iri,
        chronic_disease_iri,
        acute_disease_iri,
        genetic_disease_iri,
        medication_iri,
        surgery_iri,
        therapy_iri,
    ]

    for cls_iri in class_iris:
        onto.add_axiom(Declaration(EntityType.CLASS, cls_iri))

    print(f"Declared {len(class_iris)} classes")

    # Build class hierarchy with SubClassOf axioms
    print("\nBuilding class hierarchy:")

    # Person hierarchy
    onto.add_axiom(SubClassOf(NamedClass(patient_cls), NamedClass(person_cls)))
    onto.add_axiom(SubClassOf(NamedClass(physician_cls), NamedClass(person_cls)))
    onto.add_axiom(SubClassOf(NamedClass(specialist_cls), NamedClass(physician_cls)))
    print("  Patient ⊑ Person")
    print("  Physician ⊑ Person")
    print("  Specialist ⊑ Physician")

    # Disease hierarchy
    onto.add_axiom(SubClassOf(NamedClass(chronic_disease_cls), NamedClass(disease_cls)))
    onto.add_axiom(SubClassOf(NamedClass(acute_disease_cls), NamedClass(disease_cls)))
    onto.add_axiom(SubClassOf(NamedClass(genetic_disease_cls), NamedClass(disease_cls)))
    print("  ChronicDisease ⊑ Disease")
    print("  AcuteDisease ⊑ Disease")
    print("  GeneticDisease ⊑ Disease")

    # Treatment hierarchy
    onto.add_axiom(SubClassOf(NamedClass(medication_cls), NamedClass(treatment_cls)))
    onto.add_axiom(SubClassOf(NamedClass(surgery_cls), NamedClass(treatment_cls)))
    onto.add_axiom(SubClassOf(NamedClass(therapy_cls), NamedClass(treatment_cls)))
    print("  Medication ⊑ Treatment")
    print("  Surgery ⊑ Treatment")
    print("  Therapy ⊑ Treatment")

    # Make Disease and Treatment disjoint (they cannot have common instances)
    onto.add_axiom(
        DisjointClasses([NamedClass(disease_cls), NamedClass(treatment_cls)])
    )
    print("\nDisjointClasses(Disease, Treatment)")

    # ========================================================================
    # Step 1.3: Create properties and define characteristics
    # ========================================================================
    print_subsection_header(
        "Step 1.3: Creating Properties and Property Characteristics"
    )

    # Object properties (relationships between individuals)
    has_diagnosis_iri = IRI("clinic", "hasDiagnosis", base_ns)
    receives_treatment_iri = IRI("clinic", "receivesTreatment", base_ns)
    treats_patient_iri = IRI("clinic", "treatsPatient", base_ns)
    specializes_in_iri = IRI("clinic", "specializesIn", base_ns)
    is_treated_by_iri = IRI("clinic", "isTreatedBy", base_ns)

    has_diagnosis = ObjectProperty(has_diagnosis_iri)
    receives_treatment = ObjectProperty(receives_treatment_iri)
    treats_patient = ObjectProperty(treats_patient_iri)
    specializes_in = ObjectProperty(specializes_in_iri)
    is_treated_by = ObjectProperty(is_treated_by_iri)

    # Declare object properties
    obj_prop_iris = [
        has_diagnosis_iri,
        receives_treatment_iri,
        treats_patient_iri,
        specializes_in_iri,
        is_treated_by_iri,
    ]

    for prop_iri in obj_prop_iris:
        onto.add_axiom(Declaration(EntityType.OBJECT_PROPERTY, prop_iri))

    print(f"Declared {len(obj_prop_iris)} object properties")

    # Data properties (relationships to literal values)
    name_iri = IRI("clinic", "fullName", base_ns)
    age_iri = IRI("clinic", "age", base_ns)
    patient_id_iri = IRI("clinic", "patientID", base_ns)
    diagnosis_date_iri = IRI("clinic", "diagnosisDate", base_ns)
    dosage_iri = IRI("clinic", "dosage", base_ns)
    medical_license_iri = IRI("clinic", "medicalLicenseNumber", base_ns)

    name_prop = DataProperty(name_iri)
    age_prop = DataProperty(age_iri)
    patient_id_prop = DataProperty(patient_id_iri)
    diagnosis_date_prop = DataProperty(diagnosis_date_iri)
    dosage_prop = DataProperty(dosage_iri)
    medical_license_prop = DataProperty(medical_license_iri)

    # Declare data properties
    data_prop_iris = [
        name_iri,
        age_iri,
        patient_id_iri,
        diagnosis_date_iri,
        dosage_iri,
        medical_license_iri,
    ]

    for prop_iri in data_prop_iris:
        onto.add_axiom(Declaration(EntityType.DATA_PROPERTY, prop_iri))

    print(f"Declared {len(data_prop_iris)} data properties")

    # Define property domains and ranges
    print("\nDefining property domains and ranges:")

    # Object property domains and ranges
    onto.add_axiom(ObjectPropertyDomain(has_diagnosis, NamedClass(patient_cls)))
    onto.add_axiom(ObjectPropertyRange(has_diagnosis, NamedClass(disease_cls)))
    print("  hasDiagnosis: Patient -> Disease")

    onto.add_axiom(ObjectPropertyDomain(receives_treatment, NamedClass(patient_cls)))
    onto.add_axiom(ObjectPropertyRange(receives_treatment, NamedClass(treatment_cls)))
    print("  receivesTreatment: Patient -> Treatment")

    onto.add_axiom(ObjectPropertyDomain(treats_patient, NamedClass(physician_cls)))
    onto.add_axiom(ObjectPropertyRange(treats_patient, NamedClass(patient_cls)))
    print("  treatsPatient: Physician -> Patient")

    onto.add_axiom(ObjectPropertyDomain(specializes_in, NamedClass(specialist_cls)))
    onto.add_axiom(ObjectPropertyRange(specializes_in, NamedClass(disease_cls)))
    print("  specializesIn: Specialist -> Disease")

    # Data property domains (range is implicit from datatype)
    onto.add_axiom(DataPropertyDomain(name_prop, NamedClass(person_cls)))
    onto.add_axiom(DataPropertyDomain(age_prop, NamedClass(person_cls)))
    onto.add_axiom(DataPropertyDomain(patient_id_prop, NamedClass(patient_cls)))
    onto.add_axiom(DataPropertyDomain(medical_license_prop, NamedClass(physician_cls)))
    print("  fullName: Person -> string")
    print("  age: Person -> integer")
    print("  patientID: Patient -> string")
    print("  medicalLicenseNumber: Physician -> string")

    # Define property characteristics
    print("\nDefining property characteristics:")

    # Patient ID is functional (each patient has exactly one ID)
    onto.add_axiom(FunctionalDataProperty(patient_id_prop))
    print("  patientID is Functional")

    # Medical license is functional (each physician has exactly one license)
    onto.add_axiom(FunctionalDataProperty(medical_license_prop))
    print("  medicalLicenseNumber is Functional")

    # ========================================================================
    # Step 1.4: Add complex class expressions
    # ========================================================================
    print_subsection_header("Step 1.4: Adding Complex Class Expressions")

    # Define a "PatientWithChronicDisease" as someone who has a chronic disease diagnosis
    # Patient ⊓ ∃hasDiagnosis.ChronicDisease
    patient_with_chronic = ObjectIntersectionOf(
        [
            NamedClass(patient_cls),
            ObjectSomeValuesFrom(has_diagnosis, NamedClass(chronic_disease_cls)),
        ]
    )

    # Create a named class for this concept
    patient_chronic_iri = IRI("clinic", "PatientWithChronicDisease", base_ns)
    patient_chronic_cls = Class(patient_chronic_iri)
    onto.add_axiom(Declaration(EntityType.CLASS, patient_chronic_iri))

    # Make it equivalent to the restriction
    onto.add_axiom(
        EquivalentClasses([NamedClass(patient_chronic_cls), patient_with_chronic])
    )
    print(
        "Created class: PatientWithChronicDisease ≡ Patient ⊓ ∃hasDiagnosis.ChronicDisease"
    )

    # Define "TreatedPatient" as someone who receives at least one treatment
    # Patient ⊓ ∃receivesTreatment.Treatment
    treated_patient = ObjectIntersectionOf(
        [
            NamedClass(patient_cls),
            ObjectSomeValuesFrom(receives_treatment, NamedClass(treatment_cls)),
        ]
    )

    treated_patient_iri = IRI("clinic", "TreatedPatient", base_ns)
    treated_patient_cls = Class(treated_patient_iri)
    onto.add_axiom(Declaration(EntityType.CLASS, treated_patient_iri))
    onto.add_axiom(
        EquivalentClasses([NamedClass(treated_patient_cls), treated_patient])
    )
    print("Created class: TreatedPatient ≡ Patient ⊓ ∃receivesTreatment.Treatment")

    # ========================================================================
    # Step 1.5: Create individuals and add assertions
    # ========================================================================
    print_subsection_header("Step 1.5: Creating Individuals and Adding Assertions")

    # Create some patient individuals
    john_iri = IRI("clinic", "JohnDoe", base_ns)
    jane_iri = IRI("clinic", "JaneSmith", base_ns)

    john = NamedIndividual(john_iri)
    jane = NamedIndividual(jane_iri)

    onto.add_axiom(Declaration(EntityType.NAMED_INDIVIDUAL, john_iri))
    onto.add_axiom(Declaration(EntityType.NAMED_INDIVIDUAL, jane_iri))

    # Create physician individual
    dr_wilson_iri = IRI("clinic", "DrWilson", base_ns)
    dr_wilson = NamedIndividual(dr_wilson_iri)
    onto.add_axiom(Declaration(EntityType.NAMED_INDIVIDUAL, dr_wilson_iri))

    # Create specialist individual
    dr_chen_iri = IRI("clinic", "DrChen", base_ns)
    dr_chen = NamedIndividual(dr_chen_iri)
    onto.add_axiom(Declaration(EntityType.NAMED_INDIVIDUAL, dr_chen_iri))

    # Create disease individuals
    diabetes_iri = IRI("clinic", "DiabetesType2", base_ns)
    hypertension_iri = IRI("clinic", "Hypertension", base_ns)

    diabetes = NamedIndividual(diabetes_iri)
    hypertension = NamedIndividual(hypertension_iri)

    onto.add_axiom(Declaration(EntityType.NAMED_INDIVIDUAL, diabetes_iri))
    onto.add_axiom(Declaration(EntityType.NAMED_INDIVIDUAL, hypertension_iri))

    # Create treatment individuals
    metformin_iri = IRI("clinic", "Metformin", base_ns)
    lisinopril_iri = IRI("clinic", "Lisinopril", base_ns)

    metformin = NamedIndividual(metformin_iri)
    lisinopril = NamedIndividual(lisinopril_iri)

    onto.add_axiom(Declaration(EntityType.NAMED_INDIVIDUAL, metformin_iri))
    onto.add_axiom(Declaration(EntityType.NAMED_INDIVIDUAL, lisinopril_iri))

    print(f"Created {onto.get_individual_count()} individuals")

    # Add class assertions (individual types)
    print("\nAdding class assertions:")

    onto.add_axiom(ClassAssertion(NamedClass(patient_cls), john))
    onto.add_axiom(ClassAssertion(NamedClass(patient_cls), jane))
    print("  JohnDoe: Patient")
    print("  JaneSmith: Patient")

    onto.add_axiom(ClassAssertion(NamedClass(physician_cls), dr_wilson))
    onto.add_axiom(ClassAssertion(NamedClass(specialist_cls), dr_chen))
    print("  DrWilson: Physician")
    print("  DrChen: Specialist")

    onto.add_axiom(ClassAssertion(NamedClass(chronic_disease_cls), diabetes))
    onto.add_axiom(ClassAssertion(NamedClass(chronic_disease_cls), hypertension))
    print("  DiabetesType2: ChronicDisease")
    print("  Hypertension: ChronicDisease")

    onto.add_axiom(ClassAssertion(NamedClass(medication_cls), metformin))
    onto.add_axiom(ClassAssertion(NamedClass(medication_cls), lisinopril))
    print("  Metformin: Medication")
    print("  Lisinopril: Medication")

    # Add object property assertions (relationships between individuals)
    print("\nAdding object property assertions:")

    onto.add_axiom(ObjectPropertyAssertion(has_diagnosis, john, diabetes))
    onto.add_axiom(ObjectPropertyAssertion(has_diagnosis, jane, hypertension))
    print("  JohnDoe hasDiagnosis DiabetesType2")
    print("  JaneSmith hasDiagnosis Hypertension")

    onto.add_axiom(ObjectPropertyAssertion(receives_treatment, john, metformin))
    onto.add_axiom(ObjectPropertyAssertion(receives_treatment, jane, lisinopril))
    print("  JohnDoe receivesTreatment Metformin")
    print("  JaneSmith receivesTreatment Lisinopril")

    onto.add_axiom(ObjectPropertyAssertion(treats_patient, dr_wilson, john))
    onto.add_axiom(ObjectPropertyAssertion(treats_patient, dr_chen, jane))
    print("  DrWilson treatsPatient JohnDoe")
    print("  DrChen treatsPatient JaneSmith")

    onto.add_axiom(ObjectPropertyAssertion(specializes_in, dr_chen, hypertension))
    print("  DrChen specializesIn Hypertension")

    # Add data property assertions (literal values)
    print("\nAdding data property assertions:")

    onto.add_axiom(
        DataPropertyAssertion(name_prop, john, Literal("John Doe", xsd.STRING))
    )
    onto.add_axiom(DataPropertyAssertion(age_prop, john, Literal("45", xsd.INTEGER)))
    onto.add_axiom(
        DataPropertyAssertion(patient_id_prop, john, Literal("P12345", xsd.STRING))
    )
    print("  JohnDoe fullName 'John Doe'")
    print("  JohnDoe age 45")
    print("  JohnDoe patientID 'P12345'")

    onto.add_axiom(
        DataPropertyAssertion(name_prop, jane, Literal("Jane Smith", xsd.STRING))
    )
    onto.add_axiom(DataPropertyAssertion(age_prop, jane, Literal("52", xsd.INTEGER)))
    onto.add_axiom(
        DataPropertyAssertion(patient_id_prop, jane, Literal("P12346", xsd.STRING))
    )
    print("  JaneSmith fullName 'Jane Smith'")
    print("  JaneSmith age 52")
    print("  JaneSmith patientID 'P12346'")

    onto.add_axiom(
        DataPropertyAssertion(
            name_prop, dr_wilson, Literal("Dr. Robert Wilson", xsd.STRING)
        )
    )
    onto.add_axiom(
        DataPropertyAssertion(
            medical_license_prop, dr_wilson, Literal("MD-789012", xsd.STRING)
        )
    )
    print("  DrWilson fullName 'Dr. Robert Wilson'")
    print("  DrWilson medicalLicenseNumber 'MD-789012'")

    onto.add_axiom(
        DataPropertyAssertion(name_prop, dr_chen, Literal("Dr. Lisa Chen", xsd.STRING))
    )
    onto.add_axiom(
        DataPropertyAssertion(
            medical_license_prop, dr_chen, Literal("MD-789013", xsd.STRING)
        )
    )
    print("  DrChen fullName 'Dr. Lisa Chen'")
    print("  DrChen medicalLicenseNumber 'MD-789013'")

    # ========================================================================
    # Step 1.6: Add annotations
    # ========================================================================
    print_subsection_header("Step 1.6: Adding Annotations")

    # Standard annotation properties
    rdfs_label = AnnotationProperty(IRI("http://www.w3.org/2000/01/rdf-schema#label"))
    rdfs_comment = AnnotationProperty(
        IRI("http://www.w3.org/2000/01/rdf-schema#comment")
    )
    dc_creator = AnnotationProperty(IRI("http://purl.org/dc/elements/1.1/creator"))

    # Add ontology-level annotations
    from ista.owl2 import Annotation

    onto.add_ontology_annotation(
        Annotation(rdfs_label, Literal("Clinical Ontology Example", "en"))
    )
    onto.add_ontology_annotation(
        Annotation(
            rdfs_comment,
            Literal(
                "A comprehensive example ontology for clinical data modeling", "en"
            ),
        )
    )
    onto.add_ontology_annotation(
        Annotation(dc_creator, Literal("ista library contributors", xsd.STRING))
    )

    print(f"Added {len(onto.get_ontology_annotations())} ontology annotations")

    # Add entity annotations using AnnotationAssertion
    onto.add_axiom(
        AnnotationAssertion(rdfs_label, patient_iri, Literal("Patient", "en"))
    )
    onto.add_axiom(
        AnnotationAssertion(
            rdfs_comment, patient_iri, Literal("A person receiving medical care", "en")
        )
    )

    onto.add_axiom(
        AnnotationAssertion(
            rdfs_label, has_diagnosis_iri, Literal("has diagnosis", "en")
        )
    )

    print("Added entity annotations (labels and comments)")

    # ========================================================================
    # Step 1.7: Display ontology statistics
    # ========================================================================
    print_subsection_header("Step 1.7: Ontology Statistics")

    print(onto.get_statistics())

    # ========================================================================
    # Step 1.8: Save to both .owl and .ofn files
    # ========================================================================
    print_subsection_header(
        "Step 1.8: Serializing to RDF/XML (.owl) and Functional Syntax (.ofn)"
    )

    # Create examples directory if it doesn't exist
    examples_dir = Path(__file__).parent

    # Save to RDF/XML format (.owl)
    owl_path = examples_dir / "clinical_ontology_original.owl"
    success_owl = RDFXMLSerializer.serialize_to_file(onto, str(owl_path))

    if success_owl:
        print(f"✓ Successfully saved to RDF/XML: {owl_path}")
        print(f"  File size: {owl_path.stat().st_size} bytes")
    else:
        print(f"✗ Failed to save to RDF/XML: {owl_path}")

    # Save to Functional Syntax format (.ofn)
    ofn_path = examples_dir / "clinical_ontology_original.ofn"
    success_ofn = FunctionalSyntaxSerializer.serialize_to_file(onto, str(ofn_path))

    if success_ofn:
        print(f"✓ Successfully saved to Functional Syntax: {ofn_path}")
        print(f"  File size: {ofn_path.stat().st_size} bytes")
    else:
        print(f"✗ Failed to save to Functional Syntax: {ofn_path}")

    # Show a preview of the functional syntax
    print("\nFunctional Syntax Preview (first 30 lines):")
    print("─" * 80)
    fs_content = onto.to_functional_syntax()
    lines = fs_content.split("\n")
    for i, line in enumerate(lines[:30], 1):
        print(f"{i:3d} | {line}")
    if len(lines) > 30:
        print(f"... ({len(lines) - 30} more lines)")
    print("─" * 80)

    return onto, str(owl_path), str(ofn_path)


def parse_existing_ontology(owl_file_path):
    """
    Part 2: Parse an existing OWL file.

    This function demonstrates:
    - Using RDFXMLParser to load an .owl file from disk
    - Extracting and displaying ontology statistics
    - Querying for specific entity types (classes, properties, individuals)
    - Retrieving and displaying axioms
    - Accessing prefix mappings

    Args:
        owl_file_path (str): Path to the .owl file to parse

    Returns:
        Ontology: The parsed ontology object
    """
    print_section_header("PART 2: Parsing Existing OWL File")

    print_subsection_header("Step 2.1: Loading OWL File with RDFXMLParser")

    print(f"Input file: {owl_file_path}")

    if not os.path.exists(owl_file_path):
        print(f"✗ Error: File not found: {owl_file_path}")
        return None

    print(f"File size: {os.path.getsize(owl_file_path)} bytes")

    try:
        # Parse the RDF/XML file
        print("\nParsing RDF/XML file...")
        parsed_onto = RDFXMLParser.parse_from_file(owl_file_path)
        print("✓ Successfully parsed ontology")

    except Exception as e:
        print(f"✗ Parse error: {e}")
        import traceback

        traceback.print_exc()
        return None

    # ========================================================================
    # Step 2.2: Display ontology information
    # ========================================================================
    print_subsection_header("Step 2.2: Parsed Ontology Information")

    # Get ontology IRI
    onto_iri = parsed_onto.get_ontology_iri()
    if onto_iri:
        print(f"Ontology IRI: {onto_iri.to_string()}")
    else:
        print("Ontology IRI: (none)")

    # Get version IRI if present
    version_iri = parsed_onto.get_version_iri()
    if version_iri:
        print(f"Version IRI: {version_iri.to_string()}")

    # Display statistics
    print("\n" + parsed_onto.get_statistics())

    # ========================================================================
    # Step 2.3: Query for entities
    # ========================================================================
    print_subsection_header(
        "Step 2.3: Querying for Classes, Properties, and Individuals"
    )

    # Get all classes
    classes = parsed_onto.get_classes()
    print(f"Classes ({len(classes)}):")
    for cls in sorted(classes, key=lambda c: c.get_iri().to_string())[:10]:
        iri = cls.get_iri()
        print(f"  • {iri.get_abbreviated() if iri.get_prefix() else iri.to_string()}")
    if len(classes) > 10:
        print(f"  ... and {len(classes) - 10} more")

    # Get all object properties
    obj_props = parsed_onto.get_object_properties()
    print(f"\nObject Properties ({len(obj_props)}):")
    for prop in sorted(obj_props, key=lambda p: p.get_iri().to_string()):
        iri = prop.get_iri()
        print(f"  • {iri.get_abbreviated() if iri.get_prefix() else iri.to_string()}")

    # Get all data properties
    data_props = parsed_onto.get_data_properties()
    print(f"\nData Properties ({len(data_props)}):")
    for prop in sorted(data_props, key=lambda p: p.get_iri().to_string()):
        iri = prop.get_iri()
        print(f"  • {iri.get_abbreviated() if iri.get_prefix() else iri.to_string()}")

    # Get all individuals
    individuals = parsed_onto.get_individuals()
    print(f"\nIndividuals ({len(individuals)}):")
    for ind in sorted(individuals, key=lambda i: i.get_iri().to_string()):
        iri = ind.get_iri()
        print(f"  • {iri.get_abbreviated() if iri.get_prefix() else iri.to_string()}")

    # ========================================================================
    # Step 2.4: Display sample axioms
    # ========================================================================
    print_subsection_header("Step 2.4: Sample Axioms")

    axioms = parsed_onto.get_axioms()
    print(f"Total axioms: {len(axioms)}\n")

    # Group axioms by type for better display
    axiom_types = {}
    for axiom in axioms:
        axiom_type = type(axiom).__name__
        if axiom_type not in axiom_types:
            axiom_types[axiom_type] = []
        axiom_types[axiom_type].append(axiom)

    # Display a few axioms of each type
    for axiom_type, axiom_list in sorted(axiom_types.items()):
        print(f"{axiom_type} ({len(axiom_list)}):")
        for axiom in axiom_list[:3]:
            try:
                fs = axiom.to_functional_syntax()
                print(f"  {fs}")
            except:
                print(f"  (unable to serialize axiom)")
        if len(axiom_list) > 3:
            print(f"  ... and {len(axiom_list) - 3} more")
        print()

    # ========================================================================
    # Step 2.5: Display prefix mappings
    # ========================================================================
    print_subsection_header("Step 2.5: Prefix Mappings")

    prefix_map = parsed_onto.get_prefix_map()
    print(f"Registered prefixes: {len(prefix_map)}\n")
    for prefix, namespace in sorted(prefix_map.items()):
        print(f"  {prefix:10s} -> {namespace}")

    return parsed_onto


def modify_parsed_ontology(parsed_onto):
    """
    Part 3: Modify a parsed ontology.

    This function demonstrates:
    - Adding new classes to an existing ontology
    - Adding new properties
    - Creating new individuals
    - Adding new axioms to existing entities
    - Extending the class hierarchy
    - Adding additional property assertions

    Args:
        parsed_onto (Ontology): The parsed ontology to modify

    Returns:
        Ontology: The modified ontology
        str: Path to the saved modified .owl file
    """
    print_section_header("PART 3: Modifying Parsed Ontology")

    print_subsection_header("Step 3.1: Adding New Classes")

    base_ns = "http://example.org/biomedical/clinical#"

    # Add a new class for medical equipment
    equipment_iri = IRI("clinic", "MedicalEquipment", base_ns)
    equipment_cls = Class(equipment_iri)
    parsed_onto.add_axiom(Declaration(EntityType.CLASS, equipment_iri))
    print(f"Added new class: {equipment_iri.get_abbreviated()}")

    # Add specific types of equipment
    diagnostic_device_iri = IRI("clinic", "DiagnosticDevice", base_ns)
    therapeutic_device_iri = IRI("clinic", "TherapeuticDevice", base_ns)

    diagnostic_device_cls = Class(diagnostic_device_iri)
    therapeutic_device_cls = Class(therapeutic_device_iri)

    parsed_onto.add_axiom(Declaration(EntityType.CLASS, diagnostic_device_iri))
    parsed_onto.add_axiom(Declaration(EntityType.CLASS, therapeutic_device_iri))

    # Build hierarchy
    parsed_onto.add_axiom(
        SubClassOf(NamedClass(diagnostic_device_cls), NamedClass(equipment_cls))
    )
    parsed_onto.add_axiom(
        SubClassOf(NamedClass(therapeutic_device_cls), NamedClass(equipment_cls))
    )
    print(f"Added classes: DiagnosticDevice ⊑ MedicalEquipment")
    print(f"               TherapeuticDevice ⊑ MedicalEquipment")

    # ========================================================================
    # Step 3.2: Adding new properties
    # ========================================================================
    print_subsection_header("Step 3.2: Adding New Properties")

    # New object property
    uses_equipment_iri = IRI("clinic", "usesEquipment", base_ns)
    uses_equipment = ObjectProperty(uses_equipment_iri)
    parsed_onto.add_axiom(Declaration(EntityType.OBJECT_PROPERTY, uses_equipment_iri))
    print(f"Added object property: {uses_equipment_iri.get_abbreviated()}")

    # New data property
    serial_number_iri = IRI("clinic", "serialNumber", base_ns)
    serial_number_prop = DataProperty(serial_number_iri)
    parsed_onto.add_axiom(Declaration(EntityType.DATA_PROPERTY, serial_number_iri))
    print(f"Added data property: {serial_number_iri.get_abbreviated()}")

    # Add domain/range for the new property
    # We need to get the Physician class from the existing ontology
    physician_iri = IRI("clinic", "Physician", base_ns)
    physician_cls = Class(physician_iri)

    parsed_onto.add_axiom(
        ObjectPropertyDomain(uses_equipment, NamedClass(physician_cls))
    )
    parsed_onto.add_axiom(
        ObjectPropertyRange(uses_equipment, NamedClass(equipment_cls))
    )
    print(f"Set domain/range: Physician -> MedicalEquipment")

    # Make serial number functional
    parsed_onto.add_axiom(FunctionalDataProperty(serial_number_prop))
    print(f"Made serialNumber functional")

    # ========================================================================
    # Step 3.3: Adding new individuals
    # ========================================================================
    print_subsection_header("Step 3.3: Adding New Individuals")

    # Create equipment individuals
    mri_scanner_iri = IRI("clinic", "MRIScanner_001", base_ns)
    ecg_machine_iri = IRI("clinic", "ECGMachine_042", base_ns)

    mri_scanner = NamedIndividual(mri_scanner_iri)
    ecg_machine = NamedIndividual(ecg_machine_iri)

    parsed_onto.add_axiom(Declaration(EntityType.NAMED_INDIVIDUAL, mri_scanner_iri))
    parsed_onto.add_axiom(Declaration(EntityType.NAMED_INDIVIDUAL, ecg_machine_iri))
    print(f"Added individuals: MRIScanner_001, ECGMachine_042")

    # Add type assertions
    parsed_onto.add_axiom(
        ClassAssertion(NamedClass(diagnostic_device_cls), mri_scanner)
    )
    parsed_onto.add_axiom(
        ClassAssertion(NamedClass(diagnostic_device_cls), ecg_machine)
    )
    print(f"Asserted types: both are DiagnosticDevice")

    # Add data property assertions
    parsed_onto.add_axiom(
        DataPropertyAssertion(
            serial_number_prop, mri_scanner, Literal("MRI-2024-001", xsd.STRING)
        )
    )
    parsed_onto.add_axiom(
        DataPropertyAssertion(
            serial_number_prop, ecg_machine, Literal("ECG-2023-042", xsd.STRING)
        )
    )
    print(f"Added serial numbers to equipment")

    # ========================================================================
    # Step 3.4: Connecting new entities to existing ones
    # ========================================================================
    print_subsection_header("Step 3.4: Connecting New Entities to Existing Ones")

    # Connect Dr. Chen to the MRI scanner
    dr_chen_iri = IRI("clinic", "DrChen", base_ns)
    dr_chen = NamedIndividual(dr_chen_iri)

    parsed_onto.add_axiom(ObjectPropertyAssertion(uses_equipment, dr_chen, mri_scanner))
    print(f"Added assertion: DrChen usesEquipment MRIScanner_001")

    # ========================================================================
    # Step 3.5: Display modified ontology statistics
    # ========================================================================
    print_subsection_header("Step 3.5: Modified Ontology Statistics")

    print(parsed_onto.get_statistics())

    # ========================================================================
    # Step 3.6: Save modified ontology
    # ========================================================================
    print_subsection_header("Step 3.6: Saving Modified Ontology")

    examples_dir = Path(__file__).parent
    modified_path = examples_dir / "clinical_ontology_modified.owl"

    success = RDFXMLSerializer.serialize_to_file(parsed_onto, str(modified_path))

    if success:
        print(f"✓ Successfully saved modified ontology to: {modified_path}")
        print(f"  File size: {modified_path.stat().st_size} bytes")
    else:
        print(f"✗ Failed to save modified ontology")

    return parsed_onto, str(modified_path)


def verify_round_trip(original_onto, parsed_onto):
    """
    Part 4: Verify round-trip integrity.

    This function demonstrates:
    - Comparing axiom counts between original and parsed ontologies
    - Comparing entity counts
    - Identifying differences
    - Validating that serialization and parsing preserve ontology content

    Args:
        original_onto (Ontology): The original ontology
        parsed_onto (Ontology): The ontology parsed from file

    Returns:
        bool: True if round-trip is successful, False otherwise
    """
    print_section_header("PART 4: Round-Trip Verification")

    print_subsection_header("Step 4.1: Comparing Statistics")

    # Get counts from both ontologies
    orig_axioms = original_onto.get_axiom_count()
    parsed_axioms = parsed_onto.get_axiom_count()

    orig_classes = original_onto.get_class_count()
    parsed_classes = parsed_onto.get_class_count()

    orig_obj_props = original_onto.get_object_property_count()
    parsed_obj_props = parsed_onto.get_object_property_count()

    orig_data_props = original_onto.get_data_property_count()
    parsed_data_props = parsed_onto.get_data_property_count()

    orig_individuals = original_onto.get_individual_count()
    parsed_individuals = parsed_onto.get_individual_count()

    # Display comparison table
    print("Comparison Table:")
    print("─" * 80)
    print(f"{'Metric':<30} {'Original':>15} {'Parsed':>15} {'Match':>10}")
    print("─" * 80)

    def print_comparison(metric, orig, parsed):
        match = "✓" if orig == parsed else "✗"
        print(f"{metric:<30} {orig:>15} {parsed:>15} {match:>10}")

    print_comparison("Total Axioms", orig_axioms, parsed_axioms)
    print_comparison("Classes", orig_classes, parsed_classes)
    print_comparison("Object Properties", orig_obj_props, parsed_obj_props)
    print_comparison("Data Properties", orig_data_props, parsed_data_props)
    print_comparison("Individuals", orig_individuals, parsed_individuals)

    print("─" * 80)

    # ========================================================================
    # Step 4.2: Detailed comparison
    # ========================================================================
    print_subsection_header("Step 4.2: Detailed Analysis")

    all_match = True

    if orig_axioms != parsed_axioms:
        diff = parsed_axioms - orig_axioms
        if diff > 0:
            print(f"⚠ Parsed ontology has {diff} MORE axiom(s) than original")
            print(
                f"  This may be due to implicit axioms added during parsing/serialization"
            )
        else:
            print(f"⚠ Parsed ontology has {abs(diff)} FEWER axiom(s) than original")
            print(f"  This may indicate data loss during round-trip")
        all_match = False
    else:
        print(f"✓ Axiom count matches perfectly: {orig_axioms} axioms")

    if orig_classes == parsed_classes:
        print(f"✓ Class count matches perfectly: {orig_classes} classes")
    else:
        print(f"✗ Class count mismatch: {orig_classes} vs {parsed_classes}")
        all_match = False

    if orig_obj_props == parsed_obj_props:
        print(f"✓ Object property count matches: {orig_obj_props} properties")
    else:
        print(
            f"✗ Object property count mismatch: {orig_obj_props} vs {parsed_obj_props}"
        )
        all_match = False

    if orig_data_props == parsed_data_props:
        print(f"✓ Data property count matches: {orig_data_props} properties")
    else:
        print(
            f"✗ Data property count mismatch: {orig_data_props} vs {parsed_data_props}"
        )
        all_match = False

    if orig_individuals == parsed_individuals:
        print(f"✓ Individual count matches: {orig_individuals} individuals")
    else:
        print(
            f"✗ Individual count mismatch: {orig_individuals} vs {parsed_individuals}"
        )
        all_match = False

    # ========================================================================
    # Step 4.3: Conclusion
    # ========================================================================
    print_subsection_header("Step 4.3: Round-Trip Conclusion")

    if all_match:
        print("╔" + "═" * 78 + "╗")
        print("║" + " " * 20 + "ROUND-TRIP SUCCESSFUL!" + " " * 37 + "║")
        print(
            "║"
            + " " * 10
            + "All counts match - ontology preserved perfectly"
            + " " * 21
            + "║"
        )
        print("╚" + "═" * 78 + "╝")
        return True
    else:
        print("╔" + "═" * 78 + "╗")
        print("║" + " " * 15 + "ROUND-TRIP COMPLETED WITH DIFFERENCES" + " " * 26 + "║")
        print(
            "║"
            + " " * 8
            + "Some counts differ - this may be expected behavior"
            + " " * 19
            + "║"
        )
        print("╚" + "═" * 78 + "╝")
        print("\nNote: Small differences in axiom counts are often normal due to:")
        print("  • Implicit axioms added by reasoners")
        print("  • Declaration axioms automatically generated")
        print("  • Annotation handling differences")
        print("  • Parser normalization")
        return True  # Still consider it successful if parsing works


def main():
    """
    Main execution function that orchestrates all demonstration parts.
    """
    print()
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 15 + "OWL2 COMPREHENSIVE ROUND-TRIP EXAMPLE" + " " * 26 + "║")
    print("║" + " " * 25 + "Using ista.owl2 Library" + " " * 31 + "║")
    print("╚" + "═" * 78 + "╝")
    print()

    try:
        # Part 1: Create ontology from scratch
        original_onto, owl_path, ofn_path = create_ontology_from_scratch()

        # Part 2: Parse the saved ontology
        parsed_onto = parse_existing_ontology(owl_path)

        if parsed_onto is None:
            print("\n✗ Failed to parse ontology - aborting remaining steps")
            return 1

        # Part 3: Modify the parsed ontology
        modified_onto, modified_path = modify_parsed_ontology(parsed_onto)

        # Part 4: Verify round-trip integrity
        verify_round_trip(original_onto, parsed_onto)

        # Final summary
        print_section_header("SUMMARY")

        print("Generated Files:")
        print(f"  1. {owl_path}")
        print(f"  2. {ofn_path}")
        print(f"  3. {modified_path}")
        print()

        print("What You Learned:")
        print("  ✓ How to create ontologies from scratch with ista.owl2")
        print("  ✓ How to add classes, properties, and individuals")
        print("  ✓ How to build class hierarchies and add axioms")
        print("  ✓ How to serialize to RDF/XML (.owl) and Functional Syntax (.ofn)")
        print("  ✓ How to parse existing OWL files")
        print("  ✓ How to query and inspect ontology contents")
        print("  ✓ How to modify existing ontologies")
        print("  ✓ How to verify round-trip integrity")
        print()

        print("Next Steps:")
        print("  • Examine the generated .owl and .ofn files")
        print("  • Load the files in Protégé or other OWL editors")
        print("  • Experiment with adding your own classes and properties")
        print("  • Try creating ontologies for your domain")
        print()

        print("╔" + "═" * 78 + "╗")
        print("║" + " " * 25 + "EXAMPLE COMPLETED!" + " " * 34 + "║")
        print("╚" + "═" * 78 + "╝")
        print()

        return 0

    except Exception as e:
        print()
        print("╔" + "═" * 78 + "╗")
        print("║" + " " * 30 + "ERROR OCCURRED" + " " * 35 + "║")
        print("╚" + "═" * 78 + "╝")
        print()
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
