"""
Toy Example: Dynamic Ontology Population from Flat Files

This example demonstrates how to dynamically create ontology instances from CSV files.
We'll create a simple library catalog ontology and populate it with books and authors from CSV files.

Requirements:
    - ista package installed
    - Sample CSV files (auto-generated in this script)
"""

import os
from ista import owl2, FlatFileDatabaseParser


def create_sample_data():
    """Create sample CSV files for the example."""
    data_dir = "flatfile_data"
    os.makedirs(data_dir, exist_ok=True)

    # Create authors.csv
    authors_csv = """author_id,name,birth_year,nationality
AUTH001,Jane Austen,1775,British
AUTH002,Mark Twain,1835,American
AUTH003,Gabriel García Márquez,1927,Colombian
AUTH004,Virginia Woolf,1882,British
AUTH005,Haruki Murakami,1949,Japanese
"""

    with open(os.path.join(data_dir, "authors.csv"), "w") as f:
        f.write(authors_csv)

    # Create books.csv
    books_csv = """book_id,title,publication_year,genre,pages
BOOK001,Pride and Prejudice,1813,Romance,432
BOOK002,Adventures of Huckleberry Finn,1884,Adventure,366
BOOK003,One Hundred Years of Solitude,1967,Magical Realism,417
BOOK004,Mrs Dalloway,1925,Modernist,194
BOOK005,Norwegian Wood,1987,Romance,296
BOOK006,Sense and Sensibility,1811,Romance,409
BOOK007,The Adventures of Tom Sawyer,1876,Adventure,274
"""

    with open(os.path.join(data_dir, "books.csv"), "w") as f:
        f.write(books_csv)

    # Create authorship.csv (relationships between books and authors)
    authorship_csv = """book_id,author_id
BOOK001,AUTH001
BOOK002,AUTH002
BOOK003,AUTH003
BOOK004,AUTH004
BOOK005,AUTH005
BOOK006,AUTH001
BOOK007,AUTH002
"""

    with open(os.path.join(data_dir, "authorship.csv"), "w") as f:
        f.write(authorship_csv)

    print(f"✓ Sample data created in '{data_dir}/' directory")
    return data_dir


def create_library_ontology():
    """Create a simple library catalog ontology structure."""
    # Create ontology
    iri_base = "http://example.org/library"
    onto = owl2.Ontology(owl2.IRI(iri_base))

    # Define classes
    author_class = owl2.Class(owl2.IRI(f"{iri_base}#Author"))
    book_class = owl2.Class(owl2.IRI(f"{iri_base}#Book"))

    onto.add_axiom(owl2.Declaration(author_class))
    onto.add_axiom(owl2.Declaration(book_class))

    # Define data properties for Author
    name_prop = owl2.DataProperty(owl2.IRI(f"{iri_base}#name"))
    birth_year_prop = owl2.DataProperty(owl2.IRI(f"{iri_base}#birthYear"))
    nationality_prop = owl2.DataProperty(owl2.IRI(f"{iri_base}#nationality"))
    author_id_prop = owl2.DataProperty(owl2.IRI(f"{iri_base}#authorID"))

    # Define data properties for Book
    title_prop = owl2.DataProperty(owl2.IRI(f"{iri_base}#title"))
    pub_year_prop = owl2.DataProperty(owl2.IRI(f"{iri_base}#publicationYear"))
    genre_prop = owl2.DataProperty(owl2.IRI(f"{iri_base}#genre"))
    pages_prop = owl2.DataProperty(owl2.IRI(f"{iri_base}#pages"))
    book_id_prop = owl2.DataProperty(owl2.IRI(f"{iri_base}#bookID"))

    # Define object property for authorship relationship
    written_by_prop = owl2.ObjectProperty(owl2.IRI(f"{iri_base}#writtenBy"))

    # Declare all properties
    for prop in [
        name_prop,
        birth_year_prop,
        nationality_prop,
        author_id_prop,
        title_prop,
        pub_year_prop,
        genre_prop,
        pages_prop,
        book_id_prop,
        written_by_prop,
    ]:
        onto.add_axiom(owl2.Declaration(prop))

    print("✓ Library ontology structure created")
    return onto, {
        "Author": author_class,
        "Book": book_class,
        "name": name_prop,
        "birthYear": birth_year_prop,
        "nationality": nationality_prop,
        "authorID": author_id_prop,
        "title": title_prop,
        "publicationYear": pub_year_prop,
        "genre": genre_prop,
        "pages": pages_prop,
        "bookID": book_id_prop,
        "writtenBy": written_by_prop,
    }


def populate_from_flat_files(onto, props, data_dir):
    """Populate the ontology from CSV files using FlatFileDatabaseParser."""

    # Initialize the parser
    parser = FlatFileDatabaseParser("library_catalog", onto, data_dir)

    print("\n--- Parsing Authors from CSV ---")
    # Parse authors from authors.csv
    parser.parse_node_type(
        node_type="Author",
        source_filename="authors.csv",
        fmt="csv",
        parse_config={
            "iri_column_name": "author_id",  # Use author_id as unique identifier
            "headers": True,
            "data_property_map": {
                "author_id": props["authorID"],
                "name": props["name"],
                "birth_year": props["birthYear"],
                "nationality": props["nationality"],
            },
            "data_transforms": {
                "birth_year": int,  # Convert birth_year to integer
            },
        },
        merge=False,
        skip=False,
    )

    print("\n--- Parsing Books from CSV ---")
    # Parse books from books.csv
    parser.parse_node_type(
        node_type="Book",
        source_filename="books.csv",
        fmt="csv",
        parse_config={
            "iri_column_name": "book_id",
            "headers": True,
            "data_property_map": {
                "book_id": props["bookID"],
                "title": props["title"],
                "publication_year": props["publicationYear"],
                "genre": props["genre"],
                "pages": props["pages"],
            },
            "data_transforms": {"publication_year": int, "pages": int},
        },
        merge=False,
        skip=False,
    )

    print("\n--- Parsing Authorship Relationships from CSV ---")
    # Parse authorship relationships from authorship.csv
    parser.parse_relationship_type(
        relationship_type=props["writtenBy"],
        source_filename="authorship.csv",
        fmt="csv",
        parse_config={
            "headers": True,
            "subject_node_type": props["Book"],
            "subject_column_name": "book_id",
            "subject_match_property": props["bookID"],
            "object_node_type": props["Author"],
            "object_column_name": "author_id",
            "object_match_property": props["authorID"],
        },
        merge=False,
        skip=False,
    )

    print("✓ Ontology populated from CSV files")


def print_ontology_stats(onto):
    """Print statistics about the populated ontology."""
    print("\n" + "=" * 60)
    print("ONTOLOGY STATISTICS")
    print("=" * 60)

    # Count individuals
    individuals = set()
    classes_used = {}
    data_props = 0
    object_props = 0

    for axiom in onto.get_axioms():
        axiom_type = type(axiom).__name__

        if axiom_type == "ClassAssertion":
            individual = str(axiom.get_individual())
            individuals.add(individual)
            class_name = str(axiom.get_class_expression()).split("#")[-1]
            classes_used[class_name] = classes_used.get(class_name, 0) + 1

        elif axiom_type == "DataPropertyAssertion":
            data_props += 1

        elif axiom_type == "ObjectPropertyAssertion":
            object_props += 1

    print(f"Total Individuals: {len(individuals)}")
    print(f"\nIndividuals by Class:")
    for class_name, count in sorted(classes_used.items()):
        print(f"  - {class_name}: {count}")

    print(f"\nTotal Data Property Assertions: {data_props}")
    print(f"Total Object Property Assertions: {object_props}")
    print("=" * 60)


def main():
    """Main execution function."""
    print("=" * 60)
    print("FLAT FILE ONTOLOGY POPULATION EXAMPLE")
    print("=" * 60)
    print("\nThis example demonstrates dynamic creation of ontology instances")
    print("from CSV files. We'll create a simple library catalog.\n")

    # Step 1: Create sample data files
    print("\n[Step 1] Creating sample CSV files...")
    data_dir = create_sample_data()

    # Step 2: Create ontology structure
    print("\n[Step 2] Creating ontology structure...")
    onto, props = create_library_ontology()

    # Step 3: Populate ontology from flat files
    print("\n[Step 3] Populating ontology from CSV files...")
    populate_from_flat_files(onto, props, data_dir)

    # Step 4: Display statistics
    print_ontology_stats(onto)

    # Step 5: Serialize the populated ontology
    print("\n[Step 4] Serializing populated ontology...")
    output_file = "library_catalog_populated.rdf"
    serializer = owl2.RDFXMLSerializer()
    with open(output_file, "w") as f:
        f.write(serializer.serialize(onto))
    print(f"✓ Ontology saved to '{output_file}'")

    # Step 6: Show a few sample individuals
    print("\n[Step 5] Sample Individuals Created:")
    print("-" * 60)

    sample_count = 0
    current_individual = None
    properties = []

    for axiom in onto.get_axioms():
        axiom_type = type(axiom).__name__

        if axiom_type == "ClassAssertion":
            if current_individual and properties:
                print(f"\n{current_individual}")
                for prop in properties:
                    print(f"  {prop}")
                sample_count += 1
                if sample_count >= 3:
                    break

            individual_iri = str(axiom.get_individual())
            individual_name = individual_iri.split("#")[-1]
            class_name = str(axiom.get_class_expression()).split("#")[-1]
            current_individual = f"Individual: {individual_name} (type: {class_name})"
            properties = []

        elif current_individual and axiom_type == "DataPropertyAssertion":
            individual_iri = str(axiom.get_subject())
            if individual_iri.split("#")[-1] in current_individual:
                prop_name = str(axiom.get_property()).split("#")[-1]
                value = str(axiom.get_object())
                properties.append(f"- {prop_name}: {value}")

    # Print the last individual if we haven't reached 3 yet
    if current_individual and properties and sample_count < 3:
        print(f"\n{current_individual}")
        for prop in properties:
            print(f"  {prop}")

    print("\n" + "=" * 60)
    print("Example completed successfully!")
    print("=" * 60)
    print("\nKey Takeaways:")
    print("1. FlatFileDatabaseParser can load CSV/TSV/XLSX files")
    print("2. parse_node_type() creates instances from rows")
    print("3. parse_relationship_type() creates links between instances")
    print("4. Data transforms allow type conversion and cleaning")
    print("5. Results in a fully populated OWL2 ontology")
    print("\nTry modifying the CSV files and re-running to see changes!")


if __name__ == "__main__":
    main()
