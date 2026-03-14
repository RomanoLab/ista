"""
ista_populate - Populate an OWL2 ontology from data sources via YAML mapping.

This module provides a CLI tool and Python API for building OWL2 ontologies
from tabular data sources (CSV, TSV, SQLite, MySQL, PostgreSQL) using a
declarative YAML mapping file. The YAML file specifies classes, properties,
data sources, and relationships -- the DataLoader handles the rest.

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
import re
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

# File-based source types (as opposed to database sources)
_FILE_SOURCE_TYPES = {"csv", "tsv"}


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

def _error(msg: str) -> None:
    """Print an error to stderr."""
    print(f"ERROR: {msg}", file=sys.stderr)


_ENV_VAR_RE = re.compile(r"\$\{([^}]+)\}")


def _validate_sources(spec, verbose: bool = False) -> List[str]:
    """Pre-flight validation of data sources in a mapping spec.

    Checks file-based sources for existence and warns about unresolved
    environment variables. Database sources are checked for unresolved
    variables in connection parameters.

    Parameters
    ----------
    spec : owl2.DataMappingSpec
        The loaded (and env-resolved) mapping specification.
    verbose : bool
        If True, print resolved paths for all sources.

    Returns
    -------
    list of str
        Human-readable problem descriptions (one per source issue).
    """
    problems = []

    for name, source in spec.sources.items():
        src_type = source.type
        src_path = source.path

        # Check for unresolved environment variables in path
        unresolved = _ENV_VAR_RE.findall(src_path)
        if unresolved:
            for var in unresolved:
                problems.append(
                    f"Source '{name}': environment variable ${{{var}}} is not "
                    f"set (raw path: {src_path})"
                )
            continue

        if src_type in _FILE_SOURCE_TYPES:
            resolved = Path(src_path).resolve()
            if verbose:
                print(f"  Source '{name}' ({src_type}): {resolved}")
            if not resolved.exists():
                problems.append(
                    f"Source '{name}' ({src_type}): file not found at "
                    f"{resolved}"
                )
            elif resolved.stat().st_size == 0:
                problems.append(
                    f"Source '{name}' ({src_type}): file is empty: {resolved}"
                )
        else:
            # Database source -- cannot validate connectivity pre-flight
            if verbose:
                conn_info = ""
                if hasattr(source, "connection") and source.connection:
                    c = source.connection
                    host = c.host if c.host else "?"
                    db = c.database if c.database else "?"
                    conn_info = f" -> {host}/{db}"
                print(
                    f"  Source '{name}' ({src_type}): database connection"
                    f"{conn_info} (not validated until execution)"
                )

    return problems


def _print_mapping_results(stats, verbose: bool = False) -> None:
    """Print per-mapping execution results.

    Parameters
    ----------
    stats : owl2.LoadingStats
        Stats from the loading operation (with ``mapping_results``).
    verbose : bool
        If True, print all mappings. Otherwise only print failures and
        zero-result mappings.
    """
    if not hasattr(stats, "mapping_results") or not stats.mapping_results:
        return

    print("\nPer-mapping results:")
    for mr in stats.mapping_results:
        if mr.error_detail:
            status = f"FAILED: {mr.error_detail}"
        elif mr.kind == "create":
            status = f"{mr.items_created} created"
        elif mr.kind == "enrich":
            status = f"{mr.items_created} enriched"
        else:
            status = f"{mr.items_created} relationships"

        if mr.rows_skipped > 0:
            status += f", {mr.rows_skipped} skipped"
        if mr.rows_processed > 0:
            status += f" ({mr.rows_processed} rows)"

        show = verbose or mr.error_detail or mr.items_created == 0
        if show:
            label = f"  [{mr.kind.upper():12s}] {mr.name}"
            print(f"{label}")
            print(f"{'':16s}source: {mr.source}  ->  {status}")
    print()


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

    spec = loader.mapping_spec()

    if not quiet:
        print(f"Mapping:  {abs_mapping}")
        print(f"Output:   {output_path}")
        print(f"Format:   {FORMAT_INFO[fmt]['label']}")
        if iri:
            print(f"IRI:      {iri}")

        n_node = len(spec.get_all_node_mappings())
        n_rel = len(spec.relationship_mappings)
        n_src = len(spec.sources)
        print(f"Sources:  {n_src}  |  Node mappings: {n_node}  |  "
              f"Relationship mappings: {n_rel}")
        print()

    # --- Pre-flight validation ---
    if verbose:
        print("Validating data sources...")
    source_problems = _validate_sources(spec, verbose=verbose)
    if source_problems:
        print(f"\n{len(source_problems)} data source problem(s):")
        for msg in source_problems:
            print(f"  - {msg}")
    elif verbose:
        print("  All data sources validated successfully.")
    print()

    # --- Execute ---
    stats = loader.execute()

    # --- Per-mapping results (verbose or when there are problems) ---
    if verbose or stats.individuals_created == 0 or stats.errors > 0:
        _print_mapping_results(stats, verbose=verbose)

    if not quiet:
        print(stats.summary())

    # --- Report errors from execution ---
    if stats.errors > 0:
        print()
        print(f"{stats.errors} error(s) during population:")
        for msg in stats.error_messages:
            print(f"  - {msg}")

    # --- Warn if population produced nothing ---
    if stats.individuals_created == 0:
        print()
        if stats.errors > 0 or source_problems:
            print("No individuals were created. "
                  "The output ontology will be empty.")
        else:
            print(
                "No individuals were created. The output ontology will be "
                "empty.\n"
                "  Possible causes:\n"
                "  - Column names in the YAML don't match the source headers\n"
                "  - Filters excluded all rows\n"
                "  Run with -v/--verbose for detailed source path information."
            )

    if stats.relationships_created == 0 and stats.individuals_created > 0:
        n_rel = len(spec.relationship_mappings)
        if n_rel > 0:
            print(
                f"\nNo relationships were created despite {n_rel} relationship "
                f"mapping(s) in the spec. Check that match properties align "
                f"between node and relationship mappings."
            )

    if not quiet:
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
        help="Show detailed output including resolved source paths",
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
        Exit code -- 0 on success, 1 on error, 2 on partial failure.
    """
    parser = create_parser()
    parsed = parser.parse_args(args)

    # Resolve output format
    fmt = parsed.format or detect_output_format(parsed.output)
    if fmt is None:
        _error(
            f"Cannot detect output format from extension "
            f"'{Path(parsed.output).suffix}'.\n"
            f"Use -f/--format to specify: {list(FORMAT_INFO.keys())}"
        )
        return 1

    # Change working directory to the mapping file's parent so that relative
    # paths inside the YAML (e.g. ``../data/drugs.csv``) resolve correctly.
    mapping_path = Path(parsed.mapping).resolve()
    if not mapping_path.exists():
        _error(f"Mapping file not found: {parsed.mapping}")
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
    except ImportError as e:
        _error(str(e))
        return 1
    except Exception as e:
        _error(str(e))
        if parsed.verbose:
            import traceback

            traceback.print_exc()
        return 1
    finally:
        os.chdir(original_cwd)

    # Return code based on what happened
    # (populate already printed all warnings/errors)
    return 0


if __name__ == "__main__":
    sys.exit(main())
