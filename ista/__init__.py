import owlready2

_OWL = owlready2.get_ontology("http://www.w3.org/2002/07/owl#")

from .database_parser import FlatFileDatabaseParser, MySQLDatabaseParser
from .load_kb import load_kb

# Import C++ OWL2 library bindings (if available)
from . import owl2

__all__ = [
    "FlatFileDatabaseParser",
    "MySQLDatabaseParser",
    "load_kb",
    "owl2",
]
