import owlready2

_OWL = owlready2.get_ontology("http://www.w3.org/2002/07/owl#")

def safe_add_property(entity, prop, value):
    """Add a value to a property slot on a node.

    Importantly, the method below is compatible with both functional and
    non-functional properties. If a property is functional, it either
    creates a new list or extends an existing list.

    This function cuts down on boilerplate code considerably when setting
    many property values in the ontology.
    """
    if value is None:
        return
    if _OWL.FunctionalProperty in prop.is_a:
        setattr(entity, prop._python_name, value)
    else:
        if len(getattr(entity, prop._python_name)) == 0:
            setattr(entity, prop._python_name, [value])
        else:
            if value not in getattr(entity, prop._python_name):
                getattr(entity, prop._python_name).append(value)


def get_onto_class_by_node_type(ont: owlready2.namespace.Ontology, node_label: str):
    """Get an object corresponding to an ontology class given the node label.

    `owlready2` doesn't make it easy to dynamically retrieve ontology classes.
    This uses some (relatively unsafe) string manipulation to hack together a
    solution.

    Notes
    -----
    This should be refactored if/when a better solution is available!
    """
    matches = [c for c in onto.classes() if str(c).split(".")[-1] == node_label]
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


def safe_make_individual_name(
    indiv_name: str, indiv_class: owlready2.entity.ThingClass
):
    """Generate a (hopefully unique) descriptive name for an ontology
    individual based on the IRI column.

    Whitespaces are replaced with underscores, the class name is prepended, and
    everything is converted to lowercase.
    """
    try:
        cl = indiv_class.name.lower()
    except AttributeError:
        ipdb.set_trace()
        print()
    if type(indiv_name) == str:
        nm = indiv_name.strip().replace(" ", "_").lower()
    else:
        nm = indiv_name
    return "{0}_{1}".format(cl, nm)