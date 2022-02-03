import os, sys
import glob
import pathlib
import argparse
import pathlib
from ista import _OWL

import owlready2

parser = argparse.ArgumentParser(description='Ista - a toolkit for building graph knowledge bases.')
parser.add_argument('-i', '--ontology_file', type=argparse.FileType('r'), default=sys.stdin)
parser.add_argument('-o', '--output_file', type=argparse.FileType('w'), default=sys.stdout)
parser.add_argument('-c', '--config_directory', type=pathlib.Path, default='.')
parser.add_argument('-d', '--data_directory', type=pathlib.Path)
parser.add_argument('-m', '--mysql_config', type=argparse.FileType('r'), required=False)
parser.add_argument('-H', '--mysql_host')
parser.add_argument('-u', '--mysql_username')
parser.add_argument('-p', '--mysql_password')
parser.add_argument('-s', '--mysql_socket')
parser.add_argument('-v', '--verbose')  # not yet implemented

def main():
    args = parser.parse_args()

    onto_file = args.ontology_file
    output_file = args.output_file

    onto = owlready2.get_ontology(f"file://{onto_file.name}").load()

    mysql_config = dict()
    mysql_config["host"] = args.mysql_host
    mysql_config["user"] = args.mysql_username
    mysql_config["passwd"] = args.mysql_password
    if args.mysql_socket is not None:
        mysql_config["socket"] = args.mysql_socket

    # loop over the configuration blocks
    print(f"{os.path.abspath(args.config_directory)}/*.py")
    glob.glob(f"{os.path.abspath(args.config_directory)}/*.py")

    # Save the ontology to a new file
    with open(output_file, "wb") as fp:
        onto.save(file=fp, format="rdfxml")

    sys.exit(0)

if __name__=="__main__":
    main()