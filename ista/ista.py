import argparse
import glob
import os
import pathlib
import sys

from ista import owl2
parser = argparse.ArgumentParser(
    description="Ista - a toolkit for building graph knowledge bases."
)
parser.add_argument("-i", "--ontology_file", type=str, required=True)
parser.add_argument("-o", "--output_file", type=str, required=True)
parser.add_argument("-c", "--config_directory", type=pathlib.Path, default=".")
parser.add_argument("-d", "--data_directory", type=pathlib.Path)
parser.add_argument("-m", "--mysql_config", type=argparse.FileType("r"), required=False)
parser.add_argument("-H", "--mysql_host")
parser.add_argument("-u", "--mysql_username")
parser.add_argument("-p", "--mysql_password")
parser.add_argument("-s", "--mysql_socket")
parser.add_argument("-v", "--verbose")  # not yet implemented


def main():
    args = parser.parse_args()

    onto_file = args.ontology_file
    output_file = args.output_file

    # Load ontology using ista.owl2 RDFXMLParser
    onto = owl2.RDFXMLParser.parse_from_file(onto_file)

    mysql_config = dict()
    mysql_config["host"] = args.mysql_host
    mysql_config["user"] = args.mysql_username
    mysql_config["passwd"] = args.mysql_password
    if args.mysql_socket is not None:
        mysql_config["socket"] = args.mysql_socket

    # loop over the configuration blocks
    print(f"{os.path.abspath(args.config_directory)}/*.py")
    glob.glob(f"{os.path.abspath(args.config_directory)}/*.py")

    # Save the ontology to a new file using RDFXMLSerializer
    serializer = owl2.RDFXMLSerializer()
    rdf_content = serializer.serialize(onto)

    with open(output_file, "w") as fp:
        fp.write(rdf_content)

    sys.exit(0)


if __name__ == "__main__":
if __name__=="__main__":
    main()
