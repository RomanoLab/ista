C++ Library Guide
=================

The ista C++ library provides a high-performance native implementation for working with
OWL2 ontologies. This guide covers the main features and usage patterns of the C++ API.

Overview
--------

The C++ library is organized into namespaces:

- **ista::owl2** - Core OWL2 types and structures
- **ista::serializers** - Serialization functionality
- **ista::parsers** - Parsing functionality

All C++ components are located in the ``lib/owl2`` directory and use modern C++20 features.

Requirements
------------

- C++20 compatible compiler (GCC 10+, Clang 11+, MSVC 2019+)
- CMake 3.15 or higher
- Standard library with C++20 support

Building
--------

The C++ library can be built as part of the ista project:

.. code-block:: bash

    mkdir build
    cd build
    cmake ..
    cmake --build .

Or integrated into your own CMake project:

.. code-block:: cmake

    add_subdirectory(lib/owl2)
    target_link_libraries(your_target PRIVATE ista_owl2)

Core Types
----------

IRI (Internationalized Resource Identifier)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: cpp

    #include "iri.hpp"

    using namespace ista::owl2;

    // Create IRI from full string
    IRI iri1("http://example.org/ontology#Disease");

    // Create IRI with prefix
    IRI iri2("ex", "Disease", "http://example.org/ontology#");

    // Get components
    std::string ns = iri1.getNamespace();
    std::string name = iri1.getShortForm();
    std::string full = iri1.toString();

    // Comparison
    if (iri1 == iri2) {
        // IRIs are equal
    }

Literal
~~~~~~~

Literals represent data values:

.. code-block:: cpp

    #include "literal.hpp"

    // String literal
    Literal name("Alzheimer's Disease");

    // Typed literal
    IRI xsd_int("xsd", "integer", "http://www.w3.org/2001/XMLSchema#");
    Literal age("65", xsd_int);

    // Language-tagged literal
    Literal label("Disease", "en");

    // Access properties
    std::string value = name.getLexicalValue();
    std::optional<std::string> lang = label.getLanguage();
    std::optional<IRI> dtype = age.getDatatype();

Entity Types
------------

Class
~~~~~

.. code-block:: cpp

    #include "class.hpp"

    // Create a class
    IRI disease_iri("ex", "Disease", "http://example.org/");
    Class disease(disease_iri);

    // Use in axioms
    Declaration decl(EntityType::CLASS, disease_iri);

ObjectProperty
~~~~~~~~~~~~~~

.. code-block:: cpp

    #include "object_property.hpp"

    // Create object property
    IRI causes_iri("ex", "causes", "http://example.org/");
    ObjectProperty causes(causes_iri);

    // Property characteristics
    TransitiveObjectProperty trans(causes);
    AsymmetricObjectProperty asym(causes);

DataProperty
~~~~~~~~~~~~

.. code-block:: cpp

    #include "data_property.hpp"

    // Create data property
    IRI age_iri("ex", "hasAge", "http://example.org/");
    DataProperty has_age(age_iri);

    // Domain and range
    DataPropertyDomain domain(has_age, person_class);
    DataPropertyRange range(has_age, xsd_integer);

NamedIndividual
~~~~~~~~~~~~~~~

.. code-block:: cpp

    #include "named_individual.hpp"

    // Create individual
    IRI john_iri("ex", "John", "http://example.org/");
    NamedIndividual john(john_iri);

    // Class assertion
    ClassAssertion assertion(person_class, john);

Ontology Container
------------------

The Ontology class manages collections of axioms:

.. code-block:: cpp

    #include "ontology.hpp"

    // Create ontology
    IRI ont_iri("http://example.org/biomedical");
    Ontology ont(ont_iri);

    // Add axioms
    IRI disease_iri("ex", "Disease", "http://example.org/");
    ont.addAxiom(std::make_shared<Declaration>(EntityType::CLASS, disease_iri));

    // Query axioms
    size_t count = ont.getAxiomCount();
    auto axioms = ont.getAxioms();

    // Check containment
    bool has = ont.containsAxiom(axiom_ptr);

    // Remove axiom
    ont.removeAxiom(axiom_ptr);

Axiom Types
-----------

Declaration Axioms
~~~~~~~~~~~~~~~~~~

.. code-block:: cpp

    // Declare entities
    Declaration class_decl(EntityType::CLASS, disease_iri);
    Declaration prop_decl(EntityType::OBJECT_PROPERTY, causes_iri);
    Declaration data_decl(EntityType::DATA_PROPERTY, age_iri);
    Declaration ind_decl(EntityType::NAMED_INDIVIDUAL, john_iri);

Class Axioms
~~~~~~~~~~~~

.. code-block:: cpp

    #include "class_axiom.hpp"

    // Subclass relationship
    SubClassOf subclass(alzheimers, disease);

    // Equivalent classes
    EquivalentClasses equiv({class1, class2, class3});

    // Disjoint classes
    DisjointClasses disjoint({class1, class2});

Property Axioms
~~~~~~~~~~~~~~~

.. code-block:: cpp

    // Subproperty
    SubObjectPropertyOf sub_prop(child_prop, parent_prop);

    // Equivalent properties
    EquivalentObjectProperties equiv_props({prop1, prop2});

    // Inverse properties
    InverseObjectProperties inverse(prop1, prop2);

    // Property domain and range
    ObjectPropertyDomain domain(prop, class1);
    ObjectPropertyRange range(prop, class2);

Assertion Axioms
~~~~~~~~~~~~~~~~

.. code-block:: cpp

    // Class membership
    ClassAssertion class_assert(disease, john);

    // Object property assertion
    ObjectPropertyAssertion obj_assert(knows, john, mary);

    // Data property assertion
    Literal age_val("30");
    DataPropertyAssertion data_assert(has_age, john, age_val);

    // Negative assertions
    NegativeObjectPropertyAssertion neg_obj(knows, john, mary);
    NegativeDataPropertyAssertion neg_data(has_age, john, age_val);

Class Expressions
-----------------

Complex class expressions:

.. code-block:: cpp

    #include "class_expression.hpp"

    // Intersection (AND)
    ObjectIntersectionOf intersection({class1, class2, class3});

    // Union (OR)
    ObjectUnionOf union_expr({class1, class2});

    // Complement (NOT)
    ObjectComplementOf complement(class1);

    // Existential restriction (∃R.C)
    ObjectSomeValuesFrom some_values(has_part, protein);

    // Universal restriction (∀R.C)
    ObjectAllValuesFrom all_values(has_part, protein);

    // Cardinality restrictions
    ObjectMinCardinality min_card(2, has_part, protein);
    ObjectMaxCardinality max_card(5, has_part, protein);
    ObjectExactCardinality exact_card(3, has_part, protein);

Annotations
-----------

.. code-block:: cpp

    #include "annotation.hpp"

    // Create annotation property
    IRI rdfs_label("rdfs", "label", "http://www.w3.org/2000/01/rdf-schema#");

    // Create annotation
    Literal label_value("Disease", "en");
    Annotation anno(rdfs_label, label_value);

    // Annotation assertion
    AnnotationAssertion assert(rdfs_label, disease_iri, label_value);

Memory Management
-----------------

The C++ library uses smart pointers for automatic memory management:

.. code-block:: cpp

    #include <memory>

    // Axioms are stored as shared_ptr
    auto axiom = std::make_shared<Declaration>(EntityType::CLASS, iri);
    ont.addAxiom(axiom);

    // Safe to pass around
    auto axioms = ont.getAxioms();
    for (const auto& ax : axioms) {
        // Process axiom
        if (auto decl = std::dynamic_pointer_cast<Declaration>(ax)) {
            // Handle declaration
        }
    }

Type Safety
-----------

The library uses strong typing and enums:

.. code-block:: cpp

    // Entity types
    enum class EntityType {
        CLASS,
        OBJECT_PROPERTY,
        DATA_PROPERTY,
        ANNOTATION_PROPERTY,
        NAMED_INDIVIDUAL,
        DATATYPE
    };

    // Axiom types can be checked at runtime
    if (axiom->getAxiomType() == AxiomType::DECLARATION) {
        // Handle declaration
    }

Error Handling
--------------

The library uses exceptions for error handling:

.. code-block:: cpp

    try {
        Ontology ont = parser.parse("input.ofn");
    } catch (const ParseException& e) {
        std::cerr << "Parse error: " << e.what() << std::endl;
    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << std::endl;
    }

Best Practices
--------------

1. **Use Smart Pointers**: Always use ``std::shared_ptr`` for axioms
2. **RAII Pattern**: Let destructors handle cleanup automatically
3. **Const Correctness**: Use const references for read-only access
4. **Move Semantics**: Use ``std::move`` for large objects when appropriate
5. **Exception Safety**: Wrap parsing operations in try-catch blocks

Example: Building an Ontology
------------------------------

Complete example of building an ontology in C++:

.. code-block:: cpp

    #include "ontology.hpp"
    #include "class.hpp"
    #include "object_property.hpp"
    #include "axioms.hpp"
    #include <memory>
    #include <string>

    int main() {
        // Create ontology
        IRI base("http://example.org/bio#");
        IRI ont_iri("http://example.org/bio#ontology");
        Ontology ont(ont_iri);

        // Helper for creating IRIs
        auto make_iri = [&base](const std::string& name) {
            return IRI("bio", name, base.toString());
        };

        // Define classes
        IRI protein_iri = make_iri("Protein");
        IRI enzyme_iri = make_iri("Enzyme");

        Class protein(protein_iri);
        Class enzyme(enzyme_iri);

        // Add declarations
        ont.addAxiom(std::make_shared<Declaration>(
            EntityType::CLASS, protein_iri));
        ont.addAxiom(std::make_shared<Declaration>(
            EntityType::CLASS, enzyme_iri));

        // Add subclass relationship
        ont.addAxiom(std::make_shared<SubClassOf>(enzyme, protein));

        // Add annotation
        IRI rdfs_label("rdfs", "label",
                      "http://www.w3.org/2000/01/rdf-schema#");
        Literal label_value("Protein", "en");
        ont.addAxiom(std::make_shared<AnnotationAssertion>(
            rdfs_label, protein_iri, label_value));

        // Print statistics
        std::cout << "Axiom count: " << ont.getAxiomCount() << std::endl;

        return 0;
    }

Integration with Python
-----------------------

The C++ library can be wrapped with pybind11 for Python integration:

.. code-block:: cpp

    #include <pybind11/pybind11.h>
    #include "ontology.hpp"

    namespace py = pybind11;

    PYBIND11_MODULE(owl2_cpp, m) {
        py::class_<IRI>(m, "IRI")
            .def(py::init<const std::string&>())
            .def("toString", &IRI::toString)
            .def("getShortForm", &IRI::getShortForm);

        py::class_<Ontology>(m, "Ontology")
            .def(py::init<const IRI&>())
            .def("addAxiom", &Ontology::addAxiom)
            .def("getAxiomCount", &Ontology::getAxiomCount);
    }

Performance Considerations
--------------------------

- **Batch Operations**: Add multiple axioms before serialization
- **Reserve Capacity**: Use vector.reserve() for known sizes
- **Move Semantics**: Prefer std::move for large transfers
- **Const References**: Use const& for read-only parameters
- **Smart Pointer Overhead**: Minimal with shared_ptr

See Also
--------

- :doc:`../cpp_api/index` - Complete C++ API reference
- :doc:`python_library` - Python library guide
- :doc:`owl2_interfaces` - OWL2 interface documentation
