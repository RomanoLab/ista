from ista import FlatFileDatabaseParser, MySQLDatabaseParser

epa = FlatFileDatabaseParser()

ncbigene = FlatFileDatabaseParser("ncbigene", onto)
drugbank = FlatFileDatabaseParser("drugbank", onto)
hetionet = FlatFileDatabaseParser("hetionet", onto)
aopdb = MySQLDatabaseParser("aopdb", onto, mysql_config)
aopwiki = FlatFileDatabaseParser("aopwiki", onto)
tox21 = FlatFileDatabaseParser("tox21", onto)
disgenet = FlatFileDatabaseParser("disgenet", onto)


#####################
# EPA COMPTOX NODES #
#####################
epa.parse_node_type(
    node_type="Chemical",
    source_filename="PubChem_DTXSID_mapping_file.txt",
    fmt="tsv",
    parse_config={
        "iri_column_name": "DTXSID",
        "headers": True,
        "data_property_map": {
            "CID": onto.xrefPubchemCID,
            "SID": onto.xrefPubchemSID,
            "DTXSID": onto.xrefDTXSID,
        },
    },
    merge=False,
    skip=False
)
epa.parse_node_type(
    node_type="Chemical",
    source_filename="Dsstox_CAS_number_name.csv",
    fmt="csv",
    parse_config={
        "iri_column_name": "dsstox_substance_id",
        "headers": True,
        "data_property_map": {
            "casrn": onto.xrefCasRN,
            "preferred_name": onto.commonName,
            "dsstox_substance_id": onto.xrefDTXSID,
        },
        "merge_column": {
            "source_column_name": "dsstox_substance_id",
            "data_property": onto.xrefDTXSID,
        },
    },
    merge=True,
    skip=False
)
epa.parse_node_type(
    node_type="Chemical",
    source_filename="CUSTOM/chemical_maccs_fingerprints.tsv",
    fmt="tsv",
    parse_config={
        "iri_column_name": "DTXSID",
        "headers": True,
        "data_property_map": {
            "DTXSID": onto.xrefDTXSID,
            "MACCS": onto.maccs
        },
        "merge_column": {
            "source_column_name": "DTXSID",
            "data_property": onto.xrefDTXSID
        }
    },
    merge=True,
    skip_create_new_node=True,  # Don't create an empty chemical node with just a MACCS property if the CID isn't already in the ontology
    skip=False
)

##################
# CHEMICAL LISTS #
##################
epa.parse_node_type(
    node_type="ChemicalList",
    source_filename="CUSTOM/Chemical Lists.tsv",
    fmt="tsv",
    parse_config={
        "iri_column_name": "LIST_ACRONYM",
        "headers": True,
        "data_property_map": {
            "LIST_ACRONYM": onto.listAcronym,
            "LIST_NAME": onto.commonName,
            "LIST_DESCRIPTION": onto.listDescription
        },
        "data_transforms": {
            "LIST_ACRONYM": lambda x: x.split('/')[-1]
        }
    },
    merge=False,
    skip=False
)

###############################
# Chemical List relationships #
###############################
epa.parse_relationship_type(
    relationship_type=onto.listIncludesChemical,
    inverse_relationship_type=onto.chemicalInList,
    source_filename="CUSTOM/chemical_lists_relationships.tsv",
    fmt="tsv",
    parse_config = {
        "subject_node_type": onto.ChemicalList,
        "subject_column_name": "list_acronym",
        "subject_match_property": onto.listAcronym,
        "object_node_type": onto.Chemical,
        "object_column_name": "casrn",
        "object_match_property": onto.xrefCasRN,
        "headers": True
    },
    merge=True,
    skip=False
)