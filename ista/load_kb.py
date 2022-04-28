import neo4j
import os, sys

def _print_header_info():
    header = """
This function loads an `ista` knowledge base into Neo4j.

Before continuing, you need to prepare an empty graph database with the correct
configuration and plugins.

Press Enter/Return to continue.
    """[1:]
    print(header)
    input()

    install = """
If you haven't done so already, create a new (empty) Neo4j database. v4.4.0 is
recommended, but other versions may work - just be aware that they have not been
tested yet. If you are using Neo4j Desktop, you'll probably want to make this
new database inside of a new Project.

IF YOU SET A PASSWORD, MAKE SURE TO REMEMBER WHAT IT IS!

(OPTIONAL)
Before starting the database for the first time, open the settings.json file and
make the following changes, which increase Neo4j's memory limits:
    dbms.memory.heap.initial_size=2048m
    dbms.memory.heap.max_size=4G
    dbms.memory.pagecache.size=2048m
For smaller knowledge bases, these may not be necessary.

Install the `Neosemantics (n10s)` library. If you are doing so manually (e.g.,
when running Neo4j Server rather than Neo4j Desktop), make sure you are using a
compatible version. You might also want to add the Graph Data Science Library
and APOC library, both of which add nice features to the graph database.

Now, start the graph database.

When you are sure it is running, press Enter/Return to continue.
    """[1:]
    print(install)
    input()

class SimpleGraphDBDriver():

    def __init__(self, uri, user, password):
        self.driver = neo4j.GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def query(self, cypher_query: str):
        print("  RUNNING QUERY:")
        print(f"   {cypher_query}")
        with self.driver.session() as session:
            res = session.write_transaction(self._run_transaction, cypher_query)
            return res

    @staticmethod
    def _run_transaction(tx, qry):
        result = tx.run(qry)
        return result

def load_kb(rdf_filepath: str):
    """Load a graph knowledge base created using `ista` into Neoj4.

    This function will provide a list of prerequisite steps to make sure the
    use has a clean/empty database running with the correct configuration and
    plugins installed.
    """
    _print_header_info()

    print("Python will now connect to Neo4j and perform the rest of the setup")
    print("automatically.")
    print()
    print("Please provide authentication details for the (new) database:")
    my_uri = input("Neo4j URI [default: `bolt://localhost:7687`]: ")
    my_username = input("Neo4j username [default: `neo4j`]: ")
    my_password = input("Neo4j password: ")

    if my_uri == '':
        my_uri = 'bolt://localhost:7687'
    if my_username == '':
        my_username = 'neo4j'

    db = SimpleGraphDBDriver(my_uri, my_username, my_password)

    if os.name == 'nt':
        fname_format = rdf_filepath.replace('\\', '\\\\')
    else:
        fname_format = rdf_filepath

    db.query("MATCH (n) DETACH DELETE n;")

    try:
        db.query("CREATE CONSTRAINT n10s_unique_uri ON (r:Resource) ASSERT r.uri IS UNIQUE;")
    except neo4j.exceptions.ClientError:
        print("Constraint already exists - skipping.")
    db.query("CALL n10s.graphconfig.init();")
    db.query("CALL n10s.graphconfig.set({applyNeo4jNaming: true, handleVocabUris: 'IGNORE'});")
    db.query(f"CALL n10s.rdf.import.fetch(\"file:///{fname_format}\", \"RDF/XML\");")

    print()
    print("Database contents loaded; performing post-install cleanup...")

    db.query("MATCH (n:Resource) REMOVE n:Resource;")
    db.query("MATCH (n:NamedIndividual) REMOVE n:NamedIndividual;")
    db.query("MATCH (n:AllDisjointClasses) REMOVE n:AllDisjointClasses;")
    db.query("MATCH (n:AllDisjointProperties) REMOVE n:AllDisjointProperties;")
    db.query("MATCH (n:DatatypeProperty) REMOVE n:DatatypeProperty;")
    db.query("MATCH (n:FunctionalProperty) REMOVE n:FunctionalProperty;")
    db.query("MATCH (n:ObjectProperty) REMOVE n:ObjectProperty;")
    db.query("MATCH (n:AnnotationProperty) REMOVE n:AnnotationProperty;")
    db.query("MATCH (n:SymmetricProperty) REMOVE n:SymmetricProperty;")
    db.query("MATCH (n:_GraphConfig) REMOVE n:_GraphConfig;")
    db.query("MATCH (n:Ontology) REMOVE n:Ontology;")
    db.query("MATCH (n:Restriction) REMOVE n:Restriction;")
    db.query("MATCH (n:Class) REMOVE n:Class;")
    db.query("MATCH (n) WHERE size(labels(n)) = 0 DETACH DELETE n;") # Removes nodes without labels