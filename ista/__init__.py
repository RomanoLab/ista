import owlready2

_OWL = owlready2.get_ontology("http://www.w3.org/2002/07/owl#")

from .database_parser import FlatFileDatabaseParser, MySQLDatabaseParser