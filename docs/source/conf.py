# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys
from unittest.mock import MagicMock

# Add the project root to sys.path for importing Python modules
sys.path.insert(0, os.path.abspath("../.."))


# Mock the C++ extension module if it's not available
# This allows documentation to be built without compiling the C++ bindings

# Define all the classes that should exist in the C++ extension
MOCK_CLASSES = [
    "IRI",
    "Literal",
    "Entity",
    "EntityType",
    "Class",
    "ObjectProperty",
    "DataProperty",
    "NamedIndividual",
    "ClassExpression",
    "NamedClass",
    "Axiom",
    "Declaration",
    "SubClassOf",
    "EquivalentClasses",
    "DisjointClasses",
    "ClassAssertion",
    "ObjectPropertyAssertion",
    "DataPropertyAssertion",
    "NegativeObjectPropertyAssertion",
    "NegativeDataPropertyAssertion",
    "ObjectPropertyDomain",
    "ObjectPropertyRange",
    "DataPropertyDomain",
    "DataPropertyRange",
    "FunctionalObjectProperty",
    "FunctionalDataProperty",
    "InverseFunctionalObjectProperty",
    "TransitiveObjectProperty",
    "SymmetricObjectProperty",
    "AsymmetricObjectProperty",
    "ReflexiveObjectProperty",
    "IrreflexiveObjectProperty",
    "SubObjectPropertyOf",
    "SubDataPropertyOf",
    "EquivalentObjectProperties",
    "EquivalentDataProperties",
    "DisjointObjectProperties",
    "DisjointDataProperties",
    "InverseObjectProperties",
    "ObjectIntersectionOf",
    "ObjectUnionOf",
    "ObjectComplementOf",
    "ObjectSomeValuesFrom",
    "ObjectAllValuesFrom",
    "ObjectHasValue",
    "ObjectHasSelf",
    "ObjectMinCardinality",
    "ObjectMaxCardinality",
    "ObjectExactCardinality",
    "DataSomeValuesFrom",
    "DataAllValuesFrom",
    "DataHasValue",
    "DataMinCardinality",
    "DataMaxCardinality",
    "DataExactCardinality",
    "Ontology",
    "FunctionalSyntaxSerializer",
    "FunctionalSyntaxParser",
    "RDFXMLSerializer",
    "RDFXMLParser",
    "RDFXMLParseException",
    "OntologyFilter",
    "FilterCriteria",
    "FilterResult",
    "AnnotationAssertion",
    "AnnotationProperty",
    "SubAnnotationPropertyOf",
    "AnnotationPropertyDomain",
    "AnnotationPropertyRange",
]

MOCK_CONSTANTS = {
    "CLASS": "CLASS",
    "OBJECT_PROPERTY": "OBJECT_PROPERTY",
    "DATA_PROPERTY": "DATA_PROPERTY",
    "NAMED_INDIVIDUAL": "NAMED_INDIVIDUAL",
    "DATATYPE": "DATATYPE",
    "ANNOTATION_PROPERTY": "ANNOTATION_PROPERTY",
    "xsd": MagicMock(),
}


class MockCppModule:
    """Mock module for C++ extension when not available."""

    __name__ = "_libista_owl2"
    __file__ = "_libista_owl2.so"

    def __init__(self):
        # Add all mock classes
        for class_name in MOCK_CLASSES:
            setattr(
                self,
                class_name,
                type(
                    class_name,
                    (object,),
                    {
                        "__module__": "_libista_owl2",
                        "__doc__": f"{class_name} class from C++ extension",
                    },
                ),
            )

        # Add constants
        for const_name, const_value in MOCK_CONSTANTS.items():
            setattr(self, const_name, const_value)

        # Set __all__ for "from module import *"
        self.__all__ = MOCK_CLASSES + list(MOCK_CONSTANTS.keys())

    def __getattr__(self, name):
        # Return MagicMock for any other attributes
        return MagicMock()


# Mock the C++ extension module
sys.modules["_libista_owl2"] = MockCppModule()

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "ista"
copyright = "2025, ista Contributors"
author = "ista Contributors"
release = "0.1.0"
version = "0.1"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    # Sphinx built-in extensions
    "sphinx.ext.autodoc",  # Auto-generate docs from docstrings
    "sphinx.ext.autosummary",  # Generate summary tables
    "sphinx.ext.viewcode",  # Add links to source code
    "sphinx.ext.napoleon",  # Support for NumPy and Google style docstrings
    "sphinx.ext.intersphinx",  # Link to other project documentation
    "sphinx.ext.todo",  # Support TODO items
    "sphinx.ext.coverage",  # Coverage checking
    "sphinx.ext.mathjax",  # Math support
    # Third-party extensions
    "numpydoc",  # NumPy-style docstrings
    "breathe",  # C++ documentation via Doxygen
]

# Autosummary settings
autosummary_generate = True
autosummary_imported_members = True

# Napoleon settings for NumPy-style docstrings
napoleon_google_docstring = False
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = True
napoleon_use_admonition_for_notes = True
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_preprocess_types = False
napoleon_type_aliases = None
napoleon_attr_annotations = True

# Numpydoc settings
numpydoc_show_class_members = True
numpydoc_show_inherited_class_members = False
numpydoc_class_members_toctree = True
numpydoc_citation_re = "[a-z0-9_.-]+"
numpydoc_attributes_as_param_list = True
numpydoc_xref_param_type = True
numpydoc_xref_aliases = {}
numpydoc_xref_ignore = {"optional", "type_without_description", "BadException"}

# Breathe configuration for C++ documentation
breathe_projects = {"ista": os.path.abspath("../doxygen/xml")}
breathe_default_project = "ista"
breathe_default_members = ("members", "undoc-members")
breathe_show_define_initializer = True
breathe_show_enumvalue_initializer = True

# Intersphinx mapping
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "numpy": ("https://numpy.org/doc/stable/", None),
    "pandas": ("https://pandas.pydata.org/docs/", None),
    "networkx": ("https://networkx.org/documentation/stable/", None),
}

templates_path = ["_templates"]
exclude_patterns = []

language = "en"

# The master toctree document
master_doc = "index"

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "furo"
html_static_path = ["_static"]

html_title = f"{project} {release}"
html_short_title = project

html_theme_options = {
    "sidebar_hide_name": False,
    "navigation_with_keys": True,
    "top_of_page_button": "edit",
    "source_repository": "https://github.com/JDRomano2/ista",  # Update with actual repo
    "source_branch": "master",
    "source_directory": "docs/source/",
}

# -- Options for todo extension ----------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/extensions/todo.html#configuration

todo_include_todos = True

# -- Autodoc configuration ---------------------------------------------------

autodoc_default_options = {
    "members": True,
    "member-order": "bysource",
    "special-members": "__init__",
    "undoc-members": True,
    "exclude-members": "__weakref__",
}

# Don't show module paths in documentation
add_module_names = False

# -- Options for LaTeX output ------------------------------------------------

latex_elements = {
    "papersize": "letterpaper",
    "pointsize": "10pt",
}

latex_documents = [
    (master_doc, "ista.tex", "ista Documentation", "ista Contributors", "manual"),
]
