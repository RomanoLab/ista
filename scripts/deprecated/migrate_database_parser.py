"""
Script to migrate database_parser.py from owlready2 to ista.owl2
"""

import re

# Read the file
with open("ista/database_parser.py", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Fix type hint in __init__
content = re.sub(
    r"def __init__\(self, name, onto: owlready2\.namespace\.Ontology\):",
    r"def __init__(self, name, onto: owl2.Ontology):",
    content,
)

# 2. Fix _merge_node - individual creation
content = re.sub(
    r"new_or_matched_individual = cl\(\s*safe_make_individual_name\(individual_name, cl\)\s*\)",
    """# Create IRI for new individual
            individual_iri_str = safe_make_individual_name(individual_name, cl)
            onto_iri = self.ont.get_ontology_iri()
            if onto_iri:
                base_iri = onto_iri.value().get_namespace()
            else:
                base_iri = "http://example.org/onto#"
            individual_iri = owl2.IRI(base_iri + individual_iri_str)
            new_or_matched_individual = self.ont.create_individual(cl, individual_iri)""",
    content,
    flags=re.MULTILINE,
)

# 3. Fix _merge_node - class assertion
content = re.sub(
    r"new_or_matched_individual\.is_a\.append\(\s*get_onto_class_by_node_type\(self\.ont, node_type\)\s*\)",
    """new_class = get_onto_class_by_node_type(self.ont, node_type)
                self.ont.add_class_assertion(new_or_matched_individual, new_class)""",
    content,
)

# 4. Fix _merge_node - property addition
content = re.sub(
    r"safe_add_property\(new_or_matched_individual, d_prop, fields\[field\]\)",
    r"value = owl2.Literal(fields[field]) if fields[field] is not None else None\n                safe_add_property(self.ont, new_or_matched_individual, d_prop, value)",
    content,
)

# 5. Fix _write_new_node - individual creation
content = re.sub(
    r"new_individual = cl\(safe_make_individual_name\(individual_name, cl\)\)",
    """# Create IRI for new individual
        individual_iri_str = safe_make_individual_name(individual_name, cl)
        onto_iri = self.ont.get_ontology_iri()
        if onto_iri:
            base_iri = onto_iri.value().get_namespace()
        else:
            base_iri = "http://example.org/onto#"
        individual_iri = owl2.IRI(base_iri + individual_iri_str)
        new_individual = self.ont.create_individual(cl, individual_iri)""",
    content,
)

# 6. Fix _write_new_node - property addition
content = re.sub(
    r"(\s+)safe_add_property\(new_individual, d_prop, fields\[field\]\)",
    r"\1value = owl2.Literal(fields[field]) if fields[field] is not None else None\n\1safe_add_property(self.ont, new_individual, d_prop, value)",
    content,
)

# 7. Fix search patterns - subject match
content = re.sub(
    r"subject_match = self\.ont\.search\(\*\*\{sub_match_prop_name: sid\}\)",
    r"""subject_match = self.ont.search_by_data_property(
                        parse_config["subject_match_property"],
                        owl2.Literal(sid)
                    )""",
    content,
)

# 8. Fix search patterns - object match
content = re.sub(
    r"object_match = self\.ont\.search\(\*\*\{obj_match_prop_name: oid\}\)",
    r"""object_match = self.ont.search_by_data_property(
                        parse_config["object_match_property"],
                        owl2.Literal(oid)
                    )""",
    content,
)

# 9. Fix property assertions - object properties
content = re.sub(
    r"safe_add_property\(sm, relationship_type, om\)",
    r"safe_add_property(self.ont, sm, relationship_type, om)",
    content,
)
content = re.sub(
    r"safe_add_property\(om, inverse_relationship_type, sm\)",
    r"safe_add_property(self.ont, om, inverse_relationship_type, sm)",
    content,
)

# 10. Fix property assertions - in loops with subject_match/object_match
content = re.sub(
    r"safe_add_property\(subject_match\[0\], relationship_type, object_match\[0\]\)",
    r"safe_add_property(self.ont, subject_match[0], relationship_type, object_match[0])",
    content,
)
content = re.sub(
    r"safe_add_property\(object_match\[0\], inverse_relationship_type, subject_match\[0\]\)",
    r"safe_add_property(self.ont, object_match[0], inverse_relationship_type, subject_match[0])",
    content,
)

# Write the result
with open("ista/database_parser.py", "w", encoding="utf-8") as f:
    f.write(content)

print("Migration complete!")
print("Updated ista/database_parser.py")
