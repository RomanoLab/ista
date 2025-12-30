import ipdb

from . import owl2


def safe_add_property(ontology, entity, prop, value):
    """Add a value to a property slot on a node.

    Importantly, the method below is compatible with both functional and
    non-functional properties. If a property is functional, it replaces
    the existing value; otherwise, it adds the value.

    This function cuts down on boilerplate code considerably when setting
    many property values in the ontology.

    Args:
        ontology: The ista.owl2.Ontology instance
        entity: The NamedIndividual to add the property to
        prop: The property (DataProperty or ObjectProperty)
        value: The value to add (Literal for data properties, NamedIndividual for object properties)
    """
    if value is None:
        return

    # Determine if this is a data property or object property and check if functional
    is_data_prop = isinstance(prop, owl2.DataProperty)
    is_obj_prop = isinstance(prop, owl2.ObjectProperty)

    if is_data_prop:
        is_functional = ontology.is_functional_data_property(prop)
        # Check if value already exists
        existing = ontology.get_data_property_assertions_for_property(prop)
        already_has_value = any(
            subj == entity and val == value for subj, val in existing
        )

        if not already_has_value:
            ontology.add_data_property_assertion(entity, prop, value)

    elif is_obj_prop:
        is_functional = ontology.is_functional_object_property(prop)
        # Check if value already exists
        existing = ontology.get_object_property_assertions_for_property(prop)
        already_has_value = any(
            subj == entity and obj == value for subj, obj in existing
        )

        if not already_has_value:
            ontology.add_object_property_assertion(entity, prop, value)

    else:
        raise TypeError(
            f"Property must be DataProperty or ObjectProperty, got {type(prop)}"
        )


def get_onto_class_by_node_type(ont: owl2.Ontology, node_label: str):
    """Get an object corresponding to an ontology class given the node label.

    This searches through the ontology's classes and matches by local name.

    Args:
        ont: The ista.owl2.Ontology instance
        node_label: The local name of the class to find

    Returns:
        The matching Class object, or None if not found

    Raises:
        ValueError: If multiple classes match the node_label
    """
    matches = [
        c for c in ont.get_classes() if c.get_iri().get_local_name() == node_label
    ]
    if len(matches) == 1:
        return matches[0]
    elif len(matches) == 0:
        return None
    else:
        raise ValueError(
            "Error: Something is wrong with your ontology's class hierarchy! Check for duplicate classes with '{0}' in the name".format(
                node_label
            )
        )


def safe_make_individual_name(indiv_name: str, indiv_class: owl2.Class):
    """Generate a (hopefully unique) descriptive name for an ontology
    individual based on the IRI column.

    Whitespaces are replaced with underscores, the class name is prepended, and
    everything is converted to lowercase.

    Args:
        indiv_name: The base name for the individual
        indiv_class: The ista.owl2.Class

    Returns:
        A formatted string: "classname_individualname"
    """
    try:
        cl = indiv_class.get_iri().get_local_name().lower()
    except AttributeError:
        ipdb.set_trace()
        print()
    if type(indiv_name) == str:
        nm = indiv_name.strip().replace(" ", "_").lower()
    else:
        nm = str(indiv_name)
    return "{0}_{1}".format(cl, nm)


def print_onto_stats(onto: owl2.Ontology):
    """Print summary statistics for an OWL2 ontology.

    Args:
        onto: The ista.owl2.Ontology instance
    """

    print()
    print("*******************")
    print("ONTOLOGY STATISTICS")
    print("*******************")
    print()

    # Get all classes and properties
    ont_classes = list(onto.get_classes())
    ont_object_properties = list(onto.get_object_properties())

    # individuals
    print("Individual counts:")
    for cl in ont_classes:
        name = cl.get_iri().get_local_name()
        instances = onto.get_individuals_of_class(cl)
        this_class_count = len(instances)
        if this_class_count > 0:
            print(f"{name}: {this_class_count}")

    # relationships
    print()
    print("Relationship counts:")
    for op in ont_object_properties:
        name = op.get_iri().get_local_name()
        relations = onto.get_object_property_assertions_for_property(op)
        this_op_count = len(relations)
        if this_op_count > 0:
            print(f"{name}: {this_op_count}")
