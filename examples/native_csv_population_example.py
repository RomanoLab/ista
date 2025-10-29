"""
Native CSV Ontology Population Example

This example demonstrates how to dynamically create ontology instances from CSV files
using the native C++ owl2 library (no owlready2 dependency).

We'll create a simple library catalog ontology and populate it with books and authors from CSV files.
"""

import os
import csv
import sys
from ista import owl2

# Fix encoding for Windows console
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")


def create_sample_data():
    """Create sample CSV files for the example."""
    data_dir = "csv_data"
    os.makedirs(data_dir, exist_ok=True)

    # Create authors.csv
    with open(os.path.join(data_dir, "authors.csv"), "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["author_id", "name", "birth_year", "nationality"])
        writer.writerow(["AUTH001", "Jane Austen", "1775", "British"])
        writer.writerow(["AUTH002", "Mark Twain", "1835", "American"])
        writer.writerow(["AUTH003", "Gabriel García Márquez", "1927", "Colombian"])
        writer.writerow(["AUTH004", "Virginia Woolf", "1882", "British"])
        writer.writerow(["AUTH005", "Haruki Murakami", "1949", "Japanese"])

    # Create books.csv
    with open(os.path.join(data_dir, "books.csv"), "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["book_id", "title", "publication_year", "genre", "pages"])
        writer.writerow(["BOOK001", "Pride and Prejudice", "1813", "Romance", "432"])
        writer.writerow(
            ["BOOK002", "Adventures of Huckleberry Finn", "1884", "Adventure", "366"]
        )
        writer.writerow(
            [
                "BOOK003",
                "One Hundred Years of Solitude",
                "1967",
                "Magical Realism",
                "417",
            ]
        )
        writer.writerow(["BOOK004", "Mrs Dalloway", "1925", "Modernist", "194"])
        writer.writerow(["BOOK005", "Norwegian Wood", "1987", "Romance", "296"])

    # Create authorship.csv (relationships)
    with open(os.path.join(data_dir, "authorship.csv"), "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["book_id", "author_id"])
        writer.writerow(["BOOK001", "AUTH001"])
        writer.writerow(["BOOK002", "AUTH002"])
        writer.writerow(["BOOK003", "AUTH003"])
        writer.writerow(["BOOK004", "AUTH004"])
        writer.writerow(["BOOK005", "AUTH005"])

    print(f"✓ Sample data created in '{data_dir}/' directory")
    return data_dir


def create_library_ontology():
    """Create a simple library catalog ontology structure."""
    iri_base = "http://example.org/library"
    onto = owl2.Ontology(owl2.IRI(iri_base))

    # Register prefix
    onto.register_prefix("lib", f"{iri_base}#")

    # Define classes
    author_class_iri = owl2.IRI(f"{iri_base}#Author")
    book_class_iri = owl2.IRI(f"{iri_base}#Book")

    onto.add_axiom(owl2.Declaration(owl2.EntityType.CLASS, author_class_iri))
    onto.add_axiom(owl2.Declaration(owl2.EntityType.CLASS, book_class_iri))

    # Define data properties
    properties = {
        "authorID": owl2.IRI(f"{iri_base}#authorID"),
        "name": owl2.IRI(f"{iri_base}#name"),
        "birthYear": owl2.IRI(f"{iri_base}#birthYear"),
        "nationality": owl2.IRI(f"{iri_base}#nationality"),
        "bookID": owl2.IRI(f"{iri_base}#bookID"),
        "title": owl2.IRI(f"{iri_base}#title"),
        "publicationYear": owl2.IRI(f"{iri_base}#publicationYear"),
        "genre": owl2.IRI(f"{iri_base}#genre"),
        "pages": owl2.IRI(f"{iri_base}#pages"),
    }

    for prop_iri in properties.values():
        onto.add_axiom(owl2.Declaration(owl2.EntityType.DATA_PROPERTY, prop_iri))

    # Define object property
    written_by_iri = owl2.IRI(f"{iri_base}#writtenBy")
    onto.add_axiom(owl2.Declaration(owl2.EntityType.OBJECT_PROPERTY, written_by_iri))

    print("✓ Library ontology structure created")
    return (
        onto,
        iri_base,
        {
            "author_class": author_class_iri,
            "book_class": book_class_iri,
            **properties,
            "writtenBy": written_by_iri,
        },
    )


def load_authors_from_csv(onto, iri_base, iris, filename):
    """Load authors from CSV file."""
    print(f"\n--- Loading Authors from {filename} ---")

    author_class = owl2.Class(iris["author_class"])
    count = 0

    with open(filename, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Create individual IRI
            individual_iri = owl2.IRI(f"{iri_base}#{row['author_id']}")
            individual = owl2.NamedIndividual(individual_iri)

            # Declare individual
            onto.add_axiom(
                owl2.Declaration(owl2.EntityType.NAMED_INDIVIDUAL, individual_iri)
            )

            # Add class assertion (ClassAssertion takes Class directly, not NamedClass)
            onto.add_axiom(owl2.ClassAssertion(author_class, individual))

            # Add data properties
            props_to_add = [
                (iris["authorID"], row["author_id"]),
                (iris["name"], row["name"]),
                (iris["birthYear"], row["birth_year"]),
                (iris["nationality"], row["nationality"]),
            ]

            for prop_iri, value in props_to_add:
                prop = owl2.DataProperty(prop_iri)
                literal = owl2.Literal(value)
                onto.add_axiom(owl2.DataPropertyAssertion(prop, individual, literal))

            count += 1
            print(f"  Created: {row['name']}")

    print(f"✓ Loaded {count} authors")
    return count


def load_books_from_csv(onto, iri_base, iris, filename):
    """Load books from CSV file."""
    print(f"\n--- Loading Books from {filename} ---")

    book_class = owl2.Class(iris["book_class"])
    count = 0

    with open(filename, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Create individual IRI
            individual_iri = owl2.IRI(f"{iri_base}#{row['book_id']}")
            individual = owl2.NamedIndividual(individual_iri)

            # Declare individual
            onto.add_axiom(
                owl2.Declaration(owl2.EntityType.NAMED_INDIVIDUAL, individual_iri)
            )

            # Add class assertion (ClassAssertion takes Class directly, not NamedClass)
            onto.add_axiom(owl2.ClassAssertion(book_class, individual))

            # Add data properties
            props_to_add = [
                (iris["bookID"], row["book_id"]),
                (iris["title"], row["title"]),
                (iris["publicationYear"], row["publication_year"]),
                (iris["genre"], row["genre"]),
                (iris["pages"], row["pages"]),
            ]

            for prop_iri, value in props_to_add:
                prop = owl2.DataProperty(prop_iri)
                literal = owl2.Literal(value)
                onto.add_axiom(owl2.DataPropertyAssertion(prop, individual, literal))

            count += 1
            print(f"  Created: {row['title']}")

    print(f"✓ Loaded {count} books")
    return count


def load_authorship_from_csv(onto, iri_base, iris, filename):
    """Load authorship relationships from CSV file."""
    print(f"\n--- Loading Authorship Relationships from {filename} ---")

    # Create a lookup for finding individuals by their ID property
    def find_individual_by_property(prop_iri, value):
        for axiom in onto.get_axioms():
            if axiom.get_axiom_type() == "DataPropertyAssertion":
                dpa = axiom
                if dpa.get_property().get_iri() == prop_iri:
                    if dpa.get_target().get_lexical_form() == value:
                        return dpa.get_source()
        return None

    count = 0
    written_by_prop = owl2.ObjectProperty(iris["writtenBy"])

    with open(filename, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Find the book and author individuals
            book_iri = owl2.IRI(f"{iri_base}#{row['book_id']}")
            author_iri = owl2.IRI(f"{iri_base}#{row['author_id']}")

            book_individual = owl2.NamedIndividual(book_iri)
            author_individual = owl2.NamedIndividual(author_iri)

            # Create object property assertion
            onto.add_axiom(
                owl2.ObjectPropertyAssertion(
                    written_by_prop, book_individual, author_individual
                )
            )

            count += 1
            print(f"  Linked: {row['book_id']} → {row['author_id']}")

    print(f"✓ Created {count} relationships")
    return count


def print_ontology_stats(onto):
    """Print statistics about the populated ontology."""
    print("\n" + "=" * 60)
    print("ONTOLOGY STATISTICS")
    print("=" * 60)
    print(onto.get_statistics())
    print("=" * 60)


def main():
    """Main execution function."""
    print("=" * 60)
    print("NATIVE CSV ONTOLOGY POPULATION EXAMPLE")
    print("=" * 60)
    print("\nThis example demonstrates dynamic creation of ontology instances")
    print("from CSV files using the native C++ owl2 library.\n")

    # Check if owl2 is available
    if not owl2.is_available():
        print("ERROR: C++ OWL2 bindings are not available!")
        print("Please build the C++ extension first:")
        print("  - pip install -e .")
        print("  - Or: mkdir build && cd build && cmake .. && cmake --build .")
        return 1

    print("✓ C++ OWL2 bindings are available\n")

    # Step 1: Create sample data files
    print("[Step 1] Creating sample CSV files...")
    data_dir = create_sample_data()

    # Step 2: Create ontology structure
    print("\n[Step 2] Creating ontology structure...")
    onto, iri_base, iris = create_library_ontology()

    # Step 3: Populate ontology from CSV files
    print("\n[Step 3] Populating ontology from CSV files...")
    author_count = load_authors_from_csv(
        onto, iri_base, iris, os.path.join(data_dir, "authors.csv")
    )
    book_count = load_books_from_csv(
        onto, iri_base, iris, os.path.join(data_dir, "books.csv")
    )
    rel_count = load_authorship_from_csv(
        onto, iri_base, iris, os.path.join(data_dir, "authorship.csv")
    )

    # Step 4: Display statistics
    print_ontology_stats(onto)

    # Step 5: Serialize the populated ontology
    print("\n[Step 4] Serializing populated ontology...")
    output_file = "library_catalog_native.rdf"
    owl2.RDFXMLSerializer.serialize_to_file(onto, output_file)
    print(f"✓ Ontology saved to '{output_file}'")

    print("\n" + "=" * 60)
    print("Example completed successfully!")
    print("=" * 60)
    print(f"\nCreated:")
    print(f"  - {author_count} authors")
    print(f"  - {book_count} books")
    print(f"  - {rel_count} relationships")
    print(f"\nKey Points:")
    print("  1. Uses native C++ owl2 API (no owlready2)")
    print("  2. High-performance for large datasets")
    print("  3. Direct memory-efficient CSV parsing")
    print("  4. Full OWL2 ontology support")
    print("\nTry modifying the CSV files and re-running!")

    return 0


if __name__ == "__main__":
    exit(main())
