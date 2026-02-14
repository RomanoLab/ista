# Import C++ OWL2 library bindings (if available)
from . import owl2
from .database_parser import FlatFileDatabaseParser, MySQLDatabaseParser

# Lazy imports for modules with heavy optional dependencies (neo4j)
def __getattr__(name):
    if name == "load_kb":
        from .load_kb import load_kb
        return load_kb
    if name == "MemgraphLoader":
        from .memgraph_loader import MemgraphLoader
        return MemgraphLoader
    if name == "load_ontology_to_memgraph":
        from .memgraph_loader import load_ontology_to_memgraph
        return load_ontology_to_memgraph
    if name == "load_rdf_to_memgraph":
        from .memgraph_loader import load_rdf_to_memgraph
        return load_rdf_to_memgraph
    if name == "OWL2MemgraphLoader":
        from .owl2memgraph import OWL2MemgraphLoader
        return OWL2MemgraphLoader
    if name == "RDFMemgraphLoader":
        from .owl2memgraph import RDFMemgraphLoader
        return RDFMemgraphLoader
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = [
    "FlatFileDatabaseParser",
    "MemgraphLoader",
    "MySQLDatabaseParser",
    "OWL2MemgraphLoader",
    "RDFMemgraphLoader",
    "load_kb",
    "load_ontology_to_memgraph",
    "load_rdf_to_memgraph",
    "owl2",
]
