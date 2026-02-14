"""
ista_populate - Populate an OWL2 ontology from data sources via YAML mapping.

This module provides a CLI tool and Python API for building OWL2 ontologies
from tabular data sources (CSV, TSV, SQLite, MySQL, PostgreSQL) using a
declarative YAML mapping file. The YAML file specifies classes, properties,
data sources, and relationships — the DataLoader handles the rest.

Supported Output Formats
    - RDF/XML (.rdf, .owl, .xml)
    - Turtle (.ttl)
    - OWL Functional Syntax (.ofn)

Example CLI Usage
    .. code-block:: bash

        # Basic usage
        ista_populate -m mapping.yaml -o ontology.owl

        # Turtle output with custom IRI
        ista_populate -m mapping.yaml -o ontology.ttl -f turtle --iri http://example.org/my_ont

        # Quiet mode (no progress output)
        ista_populate -m mapping.yaml -o ontology.owl -q

Example Programmatic Usage
    >>> from ista.populate import populate
    >>> populate("mapping.yaml", "output.owl")
"""

import argparse
import os
import sys
from pathlib import Path
from typing import List, Optional

try:
    from ista import owl2

    HAS_OWL2 = owl2.is_available()
except ImportError:
    HAS_OWL2 = False

# Map CLI format names to serializers and file extensions
FORMAT_INFO = {
    "rdfxml": {"extensions": [".rdf", ".owl", ".xml"], "label": "RDF/XML"},
    "turtle": {"extensions": [".ttl"], "label": "Turtle"},
    "functional": {"extensions": [".ofn", ".fss"], "label": "OWL Functional Syntax"},
}

# Reverse mapping: extension -> format
EXTENSION_TO_FORMAT = {}
for fmt, info in FORMAT_INFO.items():
    for ext in info["extensions"]:
        EXTENSION_TO_FORMAT[ext] = fmt


def detect_output_format(filepath: str) -> Optional[str]:
    """
    Detect output serialization format from file extension.

    Parameters
    ----------
    filepath : str
        Output file path.

    Returns
    -------
    str or None
        Detected format name, or None if unknown.
    """
    ext = Path(filepath).suffix.lower()
    return EXTENSION_TO_FORMAT.get(ext)


def _serialize(ontology, output_path: str, fmt: str) -> None:
    """
    Serialize an ontology to a file in the requested format.

    Parameters
    ----------
    ontology : owl2.Ontology
        The populated ontology.
    output_path : str
        Destination file path.
    fmt : str
        One of ``"rdfxml"``, ``"turtle"``, ``"functional"``.

    Raises
    ------
    ValueError
        If *fmt* is not a supported format name.
    """
    if fmt == "rdfxml":
        owl2.RDFXMLSerializer.serialize_to_file(ontology, output_path)
    elif fmt == "turtle":
        owl2.TurtleSerializer.serialize_to_file(ontology, output_path)
    elif fmt == "functional":
        owl2.FunctionalSyntaxSerializer.serialize_to_file(ontology, output_path)
    else:
        raise ValueError(f"Unsupported output format: {fmt}")


def populate(
    mapping_path: str,
    output_path: str,
    fmt: str = "rdfxml",
    iri: Optional[str] = None,
    quiet: bool = False,
    verbose: bool = False,
) -> None:
    """
    Populate an ontology from a YAML mapping and serialize to a file.

    Parameters
    ----------
    mapping_path : str
        Path to the YAML mapping file.
    output_path : str
        Destination file path for the serialized ontology.
    fmt : str
        Output serialization format (``"rdfxml"``, ``"turtle"``, or
        ``"functional"``).
    iri : str, optional
        Override ontology IRI. If *None*, the ``base_iri`` declared in the
        YAML mapping is used.
    quiet : bool
        Suppress progress output.
    verbose : bool
        Show detailed output.

    Raises
    ------
    ImportError
        If the C++ OWL2 bindings are not available.
    FileNotFoundError
        If *mapping_path* does not exist.
    """
    if not HAS_OWL2:
        raise ImportError(
            "The ista OWL2 C++ bindings are required.\n"
            "Build with: pip install -e ."
        )

    mapping_file = Path(mapping_path)
    if not mapping_file.exists():
        raise FileNotFoundError(f"Mapping file not found: {mapping_path}")

    # Create ontology
    if iri:
        onto = owl2.Ontology(owl2.IRI(iri))
    else:
        onto = owl2.Ontology()

    # Load and execute mapping
    loader = owl2.DataLoader(onto)

    # Resolve mapping path relative to cwd
    abs_mapping = str(mapping_file.resolve())
    loader.load_mapping_spec(abs_mapping)

    if not quiet:
        print(f"Mapping:  {abs_mapping}")
        print(f"Output:   {output_path}")
        print(f"Format:   {FORMAT_INFO[fmt]['label']}")
        if iri:
            print(f"IRI:      {iri}")
        print()

    stats = loader.execute()

    if not quiet:
        print(stats.summary())
        print()
        print(onto.get_statistics())

    # Serialize
    _serialize(onto, output_path, fmt)

    if not quiet:
        print(f"\nOntology written to {output_path}")


def create_parser() -> argparse.ArgumentParser:
    """
    Create the argument parser for the ``ista_populate`` CLI.

    Returns
    -------
    argparse.ArgumentParser
        Configured argument parser.
    """
    parser = argparse.ArgumentParser(
        prog="ista_populate",
        description="Populate an OWL2 ontology from data sources via a YAML mapping file.",
        epilog="""\
Supported output formats:
  rdfxml      RDF/XML (.rdf, .owl, .xml)   [default]
  turtle      Turtle (.ttl)
  functional  OWL Functional Syntax (.ofn)

Examples:
  ista_populate -m mapping.yaml -o ontology.owl
  ista_populate -m mapping.yaml -o ontology.ttl -f turtle
  ista_populate -m mapping.yaml -o ontology.ofn -f functional --iri http://example.org/my_ont
""",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "-m",
        "--mapping",
        type=str,
        required=True,
        metavar="FILE",
        help="Path to YAML mapping file",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        required=True,
        metavar="FILE",
        help="Output ontology file path (.owl, .ttl, .ofn)",
    )
    parser.add_argument(
        "-f",
        "--format",
        type=str,
        choices=list(FORMAT_INFO.keys()),
        default=None,
        metavar="FORMAT",
        help="Output format (rdfxml, turtle, functional). Auto-detected from extension if not specified.",
    )
    parser.add_argument(
        "--iri",
        type=str,
        default=None,
        metavar="IRI",
        help="Override ontology IRI (default: use base_iri from YAML)",
    )

    verbosity = parser.add_mutually_exclusive_group()
    verbosity.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Suppress progress output",
    )
    verbosity.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Show detailed output",
    )

    return parser


def main(args: Optional[List[str]] = None) -> int:
    """
    Entry point for the ``ista_populate`` CLI.

    Parameters
    ----------
    args : list of str, optional
        Command-line arguments.  If *None*, ``sys.argv[1:]`` is used.

    Returns
    -------
    int
        Exit code — 0 on success, non-zero on error.
    """
    parser = create_parser()
    parsed = parser.parse_args(args)

    # Resolve output format
    fmt = parsed.format or detect_output_format(parsed.output)
    if fmt is None:
        print(
            f"Error: Cannot detect output format from extension "
            f"'{Path(parsed.output).suffix}'.",
            file=sys.stderr,
        )
        print(
            f"Use -f/--format to specify: {list(FORMAT_INFO.keys())}",
            file=sys.stderr,
        )
        return 1

    # Change working directory to the mapping file's parent so that relative
    # paths inside the YAML (e.g. ``../data/drugs.csv``) resolve correctly.
    mapping_path = Path(parsed.mapping).resolve()
    if not mapping_path.exists():
        print(f"Error: Mapping file not found: {parsed.mapping}", file=sys.stderr)
        return 1

    output_path = Path(parsed.output).resolve()
    original_cwd = os.getcwd()
    os.chdir(mapping_path.parent)

    try:
        populate(
            mapping_path=str(mapping_path),
            output_path=str(output_path),
            fmt=fmt,
            iri=parsed.iri,
            quiet=parsed.quiet,
            verbose=parsed.verbose,
        )
        return 0
    except ImportError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if parsed.verbose:
            import traceback

            traceback.print_exc()
        return 1
    finally:
        os.chdir(original_cwd)


if __name__ == "__main__":
    sys.exit(main())
