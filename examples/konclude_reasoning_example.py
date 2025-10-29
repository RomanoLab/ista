"""
Konclude Reasoner Integration Example

This example demonstrates how to integrate the Konclude OWL2 reasoner with ISTA.
Konclude is a high-performance, parallel tableau-based reasoner for OWL 2 DL.

Requirements:
    - Konclude installed and accessible in PATH (or specify path)
    - ista package with owl2 support

Download Konclude from: https://github.com/konclude/Konclude
"""

import os
import subprocess
import sys
import tempfile
from ista import owl2


class KoncludeReasoner:
    """
    Python wrapper for Konclude OWL2 reasoner.

    Provides high-level interface for reasoning tasks:
    - Consistency checking
    - Classification (compute class hierarchy)
    - Realization (compute instance types)
    - Satisfiability checking
    """

    def __init__(self, konclude_path="Konclude", worker_threads=-1, verbose=False):
        """
        Initialize Konclude wrapper.

        Args:
            konclude_path: Path to Konclude executable (default: "Konclude" in PATH)
            worker_threads: Number of worker threads (-1 for auto)
            verbose: Enable verbose output
        """
        self.konclude_path = konclude_path
        self.worker_threads = worker_threads
        self.verbose = verbose
        self.last_output_file = None

    def is_available(self):
        """Check if Konclude is available."""
        try:
            result = subprocess.run(
                [self.konclude_path, "--help"], capture_output=True, timeout=5
            )
            return result.returncode == 0
        except (subprocess.SubprocessError, FileNotFoundError):
            return False

    def _save_ontology(self, ontology, prefix="ista_konclude"):
        """Save ontology to temporary file."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".owl", prefix=prefix, delete=False
        ) as f:
            temp_file = f.name

        # Serialize to OWL 2 XML format (Konclude's preferred format)
        owl2.RDFXMLSerializer.serialize_to_file(ontology, temp_file)
        return temp_file

    def _build_command(self, command, input_file, output_file, extra_args=None):
        """Build Konclude command line."""
        cmd = [self.konclude_path, command, "-i", input_file]

        if output_file:
            cmd.extend(["-o", output_file])

        # Worker threads
        if self.worker_threads > 0:
            cmd.extend(["-w", str(self.worker_threads)])
        elif self.worker_threads == -1:
            cmd.extend(["-w", "AUTO"])

        # Verbose output
        if self.verbose:
            cmd.append("-v")

        # Extra arguments
        if extra_args:
            cmd.extend(extra_args)

        return cmd

    def _execute_command(self, cmd):
        """Execute Konclude command and return results."""
        if self.verbose:
            print(f"Executing: {' '.join(cmd)}")

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
            )

            if self.verbose and result.stdout:
                print(result.stdout)

            if result.returncode != 0:
                error_msg = result.stderr or result.stdout or "Unknown error"
                return {
                    "success": False,
                    "error": f"Konclude failed with exit code {result.returncode}: {error_msg}",
                }

            return {"success": True, "stdout": result.stdout, "stderr": result.stderr}

        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Konclude timed out"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def check_consistency(self, ontology):
        """
        Check if the ontology is consistent.

        Args:
            ontology: The owl2.Ontology to check

        Returns:
            dict with keys: success, consistent, time (optional)
        """
        print("\n--- Checking Consistency ---")

        input_file = self._save_ontology(ontology, "consistency")
        output_file = tempfile.mktemp(suffix=".owl", prefix="konclude_out_")

        try:
            cmd = self._build_command("classification", input_file, output_file)
            result = self._execute_command(cmd)

            if result["success"]:
                # If classification succeeds, ontology is consistent
                print("✓ Ontology is CONSISTENT")
                return {"success": True, "consistent": True}
            else:
                # Check if error indicates inconsistency
                error = result.get("error", "").lower()
                if "inconsistent" in error:
                    print("✗ Ontology is INCONSISTENT")
                    return {"success": True, "consistent": False}
                else:
                    print(f"✗ Error: {result.get('error')}")
                    return {"success": False, "error": result.get("error")}
        finally:
            # Clean up
            if os.path.exists(input_file):
                os.remove(input_file)
            if os.path.exists(output_file):
                os.remove(output_file)

    def classify(self, ontology):
        """
        Classify the ontology (compute class hierarchy with inferred subclass axioms).

        Args:
            ontology: The owl2.Ontology to classify

        Returns:
            dict with keys: success, inferred_ontology (if successful)
        """
        print("\n--- Running Classification ---")

        input_file = self._save_ontology(ontology, "classify")
        output_file = tempfile.mktemp(suffix=".owl", prefix="konclude_classified_")

        try:
            cmd = self._build_command("classification", input_file, output_file)
            result = self._execute_command(cmd)

            if result["success"]:
                print("✓ Classification completed successfully")
                self.last_output_file = output_file

                # Load inferred ontology
                try:
                    inferred = owl2.RDFXMLParser.parse_from_file(output_file)
                    print(
                        f"  Inferred ontology has {inferred.get_axiom_count()} axioms"
                    )
                    return {"success": True, "inferred_ontology": inferred}
                except Exception as e:
                    print(f"✗ Failed to parse inferred ontology: {e}")
                    return {"success": False, "error": f"Failed to parse output: {e}"}
            else:
                print(f"✗ Classification failed: {result.get('error')}")
                return {"success": False, "error": result.get("error")}
        finally:
            # Clean up input file
            if os.path.exists(input_file):
                os.remove(input_file)
            # Keep output file if successful, for inspection

    def realize(self, ontology):
        """
        Realize the ontology (compute most specific classes for all individuals).

        Args:
            ontology: The owl2.Ontology to realize

        Returns:
            dict with keys: success, inferred_ontology (if successful)
        """
        print("\n--- Running Realization ---")

        input_file = self._save_ontology(ontology, "realize")
        output_file = tempfile.mktemp(suffix=".owl", prefix="konclude_realized_")

        try:
            cmd = self._build_command("realization", input_file, output_file)
            result = self._execute_command(cmd)

            if result["success"]:
                print("✓ Realization completed successfully")
                self.last_output_file = output_file

                # Load inferred ontology
                try:
                    inferred = owl2.RDFXMLParser.parse_from_file(output_file)
                    print(
                        f"  Inferred ontology has {inferred.get_axiom_count()} axioms"
                    )
                    return {"success": True, "inferred_ontology": inferred}
                except Exception as e:
                    print(f"✗ Failed to parse inferred ontology: {e}")
                    return {"success": False, "error": f"Failed to parse output: {e}"}
            else:
                print(f"✗ Realization failed: {result.get('error')}")
                return {"success": False, "error": result.get("error")}
        finally:
            # Clean up input file
            if os.path.exists(input_file):
                os.remove(input_file)

    def check_satisfiability(self, ontology, class_iri):
        """
        Check if a specific class is satisfiable.

        Args:
            ontology: The owl2.Ontology context
            class_iri: IRI of the class to check

        Returns:
            dict with keys: success, satisfiable
        """
        print(f"\n--- Checking Satisfiability of {class_iri.get_abbreviated()} ---")

        input_file = self._save_ontology(ontology, "satisfiability")
        output_file = tempfile.mktemp(suffix=".owl", prefix="konclude_sat_")

        try:
            cmd = self._build_command(
                "satisfiability",
                input_file,
                output_file,
                ["-x", class_iri.get_full_iri()],
            )
            result = self._execute_command(cmd)

            if result["success"]:
                # Parse output to determine satisfiability
                output = result.get("stdout", "") + result.get("stderr", "")

                if (
                    "satisfiable" in output.lower()
                    and "unsatisfiable" not in output.lower()
                ):
                    print("✓ Class is SATISFIABLE")
                    return {"success": True, "satisfiable": True}
                elif "unsatisfiable" in output.lower():
                    print("✗ Class is UNSATISFIABLE")
                    return {"success": True, "satisfiable": False}
                else:
                    print("? Satisfiability result unclear")
                    return {
                        "success": False,
                        "error": "Could not determine satisfiability",
                    }
            else:
                print(f"✗ Satisfiability check failed: {result.get('error')}")
                return {"success": False, "error": result.get("error")}
        finally:
            # Clean up
            if os.path.exists(input_file):
                os.remove(input_file)
            if os.path.exists(output_file):
                os.remove(output_file)


def create_test_ontology():
    """Create a sample ontology for testing reasoning."""
    iri_base = "http://example.org/animals"
    onto = owl2.Ontology(owl2.IRI(iri_base))
    onto.register_prefix("animals", f"{iri_base}#")

    # Define classes
    animal = owl2.IRI(f"{iri_base}#Animal")
    mammal = owl2.IRI(f"{iri_base}#Mammal")
    dog = owl2.IRI(f"{iri_base}#Dog")
    cat = owl2.IRI(f"{iri_base}#Cat")

    # Declare classes
    for class_iri in [animal, mammal, dog, cat]:
        onto.add_axiom(owl2.Declaration(owl2.EntityType.CLASS, class_iri))

    # Build class hierarchy
    # Mammal ⊑ Animal
    onto.add_axiom(
        owl2.SubClassOf(
            owl2.NamedClass(owl2.Class(mammal)), owl2.NamedClass(owl2.Class(animal))
        )
    )

    # Dog ⊑ Mammal
    onto.add_axiom(
        owl2.SubClassOf(
            owl2.NamedClass(owl2.Class(dog)), owl2.NamedClass(owl2.Class(mammal))
        )
    )

    # Cat ⊑ Mammal
    onto.add_axiom(
        owl2.SubClassOf(
            owl2.NamedClass(owl2.Class(cat)), owl2.NamedClass(owl2.Class(mammal))
        )
    )

    # Create some individuals
    fido_iri = owl2.IRI(f"{iri_base}#Fido")
    fido = owl2.NamedIndividual(fido_iri)
    onto.add_axiom(owl2.Declaration(owl2.EntityType.NAMED_INDIVIDUAL, fido_iri))
    onto.add_axiom(owl2.ClassAssertion(owl2.Class(dog), fido))

    whiskers_iri = owl2.IRI(f"{iri_base}#Whiskers")
    whiskers = owl2.NamedIndividual(whiskers_iri)
    onto.add_axiom(owl2.Declaration(owl2.EntityType.NAMED_INDIVIDUAL, whiskers_iri))
    onto.add_axiom(owl2.ClassAssertion(owl2.Class(cat), whiskers))

    print("✓ Created test ontology:")
    print(f"  - 4 classes: Animal, Mammal, Dog, Cat")
    print(f"  - 2 individuals: Fido (Dog), Whiskers (Cat)")
    print(f"  - Class hierarchy: Dog ⊑ Mammal ⊑ Animal")

    return onto, {"animal": animal, "mammal": mammal, "dog": dog, "cat": cat}


def main():
    """Main execution function."""
    print("=" * 60)
    print("KONCLUDE OWL2 REASONER INTEGRATION EXAMPLE")
    print("=" * 60)

    # Check prerequisites
    if not owl2.is_available():
        print("ERROR: C++ OWL2 bindings are not available!")
        print("Please build the C++ extension first.")
        return 1

    print("✓ C++ OWL2 bindings available")

    # Initialize reasoner
    # If Konclude is not in PATH, specify full path:
    # reasoner = KoncludeReasoner(konclude_path="/path/to/Konclude")
    reasoner = KoncludeReasoner(worker_threads=-1, verbose=True)

    if not reasoner.is_available():
        print("\n" + "=" * 60)
        print("ERROR: Konclude is not available!")
        print("=" * 60)
        print("\nPlease install Konclude:")
        print("  1. Download from: https://github.com/konclude/Konclude")
        print("  2. Add to PATH or specify path in KoncludeReasoner()")
        print("\nAlternative download: https://www.derivo.de/products/konclude/")
        return 1

    print("✓ Konclude reasoner available\n")

    # Create test ontology
    print("\n[Step 1] Creating test ontology...")
    onto, classes = create_test_ontology()

    print(f"\nOriginal ontology statistics:")
    print(onto.get_statistics())

    # Perform reasoning tasks
    print("\n[Step 2] Running reasoning tasks...")

    # 1. Consistency checking
    consistency_result = reasoner.check_consistency(onto)

    # 2. Classification
    classification_result = reasoner.classify(onto)

    if classification_result["success"]:
        inferred = classification_result["inferred_ontology"]
        print(f"\n  Original axioms: {onto.get_axiom_count()}")
        print(f"  Inferred axioms: {inferred.get_axiom_count()}")

        # The inferred ontology contains the original plus inferred subclass relationships
        # including transitive closures (e.g., Dog ⊑ Animal inferred from Dog ⊑ Mammal ⊑ Animal)

    # 3. Realization
    realization_result = reasoner.realize(onto)

    if realization_result["success"]:
        realized = realization_result["inferred_ontology"]
        # The realized ontology includes inferred type assertions
        # e.g., Fido is inferred to be a Mammal and Animal (not just Dog)
        print(f"\n  Realized ontology axioms: {realized.get_axiom_count()}")

    # 4. Satisfiability checking
    sat_result = reasoner.check_satisfiability(onto, classes["dog"])

    print("\n" + "=" * 60)
    print("REASONING SUMMARY")
    print("=" * 60)
    print(
        f"Consistency Check: {'✓ PASSED' if consistency_result.get('consistent') else '✗ FAILED'}"
    )
    print(
        f"Classification: {'✓ COMPLETED' if classification_result.get('success') else '✗ FAILED'}"
    )
    print(
        f"Realization: {'✓ COMPLETED' if realization_result.get('success') else '✗ FAILED'}"
    )
    print(
        f"Satisfiability: {'✓ SATISFIABLE' if sat_result.get('satisfiable') else '✗ UNSATISFIABLE'}"
    )
    print("=" * 60)

    print("\nKey Benefits of Konclude:")
    print("  • High-performance parallel reasoning")
    print("  • Full OWL 2 DL support")
    print("  • Scalable to large ontologies")
    print("  • Easy command-line integration")

    return 0


if __name__ == "__main__":
    # Fix encoding for Windows
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding="utf-8")

    exit(main())
