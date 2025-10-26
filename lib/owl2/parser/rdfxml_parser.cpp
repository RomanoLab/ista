#include "rdfxml_parser.hpp"
#include "pugixml.hpp"
#include <fstream>
#include <sstream>
#include <algorithm>

namespace ista {
namespace owl2 {

// ============================================================================
// Internal Parser Implementation
// ============================================================================

class RDFXMLParser::Parser {
public:
    explicit Parser(const std::string& rdfxml_content)
        : content_(rdfxml_content) {}
    
    Ontology parse() {
        // Parse XML document
        pugi::xml_parse_result result = doc_.load_string(content_.c_str());
        if (!result) {
            throw RDFXMLParseException(
                std::string("XML parsing failed: ") + result.description());
        }
        
        // Find RDF root element
        rdf_root_ = doc_.child("rdf:RDF");
        if (!rdf_root_) {
            rdf_root_ = doc_.child("RDF");
            if (!rdf_root_) {
                throw RDFXMLParseException("No rdf:RDF root element found");
            }
        }
        
        // Extract namespaces
        extractNamespaces();
        
        // Create ontology
        Ontology ontology;
        
        // Parse ontology header
        parseOntologyHeader(ontology);
        
        // Register prefixes in ontology
        for (const auto& [prefix, uri] : namespaces_) {
            ontology.registerPrefix(prefix, uri);
        }
        
        // Parse axioms - first pass: declarations
        parseDeclarations(ontology);
        
        // Second pass: other axioms
        parseAxioms(ontology);
        
        return ontology;
    }

private:
    std::string content_;
    pugi::xml_document doc_;
    pugi::xml_node rdf_root_;
    std::unordered_map<std::string, std::string> namespaces_;
    
    // Standard namespace URIs
    const std::string RDF_NS = "http://www.w3.org/1999/02/22-rdf-syntax-ns#";
    const std::string RDFS_NS = "http://www.w3.org/2000/01/rdf-schema#";
    const std::string OWL_NS = "http://www.w3.org/2002/07/owl#";
    const std::string XSD_NS = "http://www.w3.org/2001/XMLSchema#";
    
    // ========================================================================
    // Namespace handling
    // ========================================================================
    
    void extractNamespaces() {
        // Extract xmlns declarations from root element
        for (pugi::xml_attribute attr = rdf_root_.first_attribute(); attr; attr = attr.next_attribute()) {
            std::string attr_name = attr.name();
            if (attr_name.find("xmlns:") == 0) {
                std::string prefix = attr_name.substr(6);
                std::string uri = attr.value();
                namespaces_[prefix] = uri;
            } else if (attr_name == "xmlns") {
                namespaces_[""] = attr.value();
            }
        }
        
        // Ensure standard namespaces are registered
        if (namespaces_.find("rdf") == namespaces_.end()) {
            namespaces_["rdf"] = RDF_NS;
        }
        if (namespaces_.find("rdfs") == namespaces_.end()) {
            namespaces_["rdfs"] = RDFS_NS;
        }
        if (namespaces_.find("owl") == namespaces_.end()) {
            namespaces_["owl"] = OWL_NS;
        }
        if (namespaces_.find("xsd") == namespaces_.end()) {
            namespaces_["xsd"] = XSD_NS;
        }
    }
    
    IRI resolveIRI(const std::string& iri_string) {
        // Check if it's a QName (prefix:localName)
        size_t colon_pos = iri_string.find(':');
        if (colon_pos != std::string::npos && colon_pos > 0) {
            std::string prefix = iri_string.substr(0, colon_pos);
            std::string local_name = iri_string.substr(colon_pos + 1);
            
            // Check if prefix is registered
            auto it = namespaces_.find(prefix);
            if (it != namespaces_.end()) {
                std::string full_iri = it->second + local_name;
                return IRI(prefix, local_name, it->second);
            }
        }
        
        // Otherwise, treat as full IRI
        return IRI(iri_string);
    }
    
    std::string getAttributeIRI(const pugi::xml_node& node, const char* attr_name) {
        pugi::xml_attribute attr = node.attribute(attr_name);
        if (!attr) {
            throw RDFXMLParseException(
                std::string("Missing required attribute: ") + attr_name);
        }
        return attr.value();
    }
    
    std::optional<std::string> getOptionalAttributeIRI(const pugi::xml_node& node, const char* attr_name) {
        pugi::xml_attribute attr = node.attribute(attr_name);
        if (attr) {
            return attr.value();
        }
        return std::nullopt;
    }
    
    // ========================================================================
    // Ontology header parsing
    // ========================================================================
    
    void parseOntologyHeader(Ontology& ontology) {
        // Find owl:Ontology element
        for (pugi::xml_node child : rdf_root_.children()) {
            std::string node_name = child.name();
            
            if (node_name == "owl:Ontology" || node_name == "Ontology") {
                // Get ontology IRI
                auto about = getOptionalAttributeIRI(child, "rdf:about");
                if (!about.has_value()) {
                    about = getOptionalAttributeIRI(child, "about");
                }
                
                if (about.has_value()) {
                    ontology.setOntologyIRI(resolveIRI(about.value()));
                }
                
                // Parse ontology properties
                for (pugi::xml_node prop : child.children()) {
                    std::string prop_name = prop.name();
                    
                    if (prop_name == "owl:versionIRI" || prop_name == "versionIRI") {
                        auto resource = getOptionalAttributeIRI(prop, "rdf:resource");
                        if (!resource.has_value()) {
                            resource = getOptionalAttributeIRI(prop, "resource");
                        }
                        if (resource.has_value()) {
                            ontology.setVersionIRI(resolveIRI(resource.value()));
                        }
                    } else if (prop_name == "owl:imports" || prop_name == "imports") {
                        auto resource = getOptionalAttributeIRI(prop, "rdf:resource");
                        if (!resource.has_value()) {
                            resource = getOptionalAttributeIRI(prop, "resource");
                        }
                        if (resource.has_value()) {
                            ontology.addImport(resolveIRI(resource.value()));
                        }
                    } else {
                        // Ontology annotation
                        parseOntologyAnnotation(ontology, prop);
                    }
                }
                
                break; // Only process first owl:Ontology element
            }
        }
    }
    
    void parseOntologyAnnotation(Ontology& ontology, const pugi::xml_node& node) {
        std::string node_name = node.name();
        
        // Determine annotation property IRI
        IRI property_iri = resolveNodeName(node_name);
        AnnotationProperty prop(property_iri);
        
        // Get annotation value
        AnnotationValue value = parseAnnotationValue(node);
        
        // Create annotation
        Annotation annotation(prop, value);
        ontology.addOntologyAnnotation(annotation);
    }
    
    // ========================================================================
    // Entity declarations
    // ========================================================================
    
    void parseDeclarations(Ontology& ontology) {
        for (pugi::xml_node child : rdf_root_.children()) {
            std::string node_name = child.name();
            
            Declaration::EntityType entity_type;
            bool is_declaration = false;
            
            if (node_name == "owl:Class" || node_name == "Class") {
                entity_type = Declaration::EntityType::CLASS;
                is_declaration = true;
            } else if (node_name == "owl:ObjectProperty" || node_name == "ObjectProperty") {
                entity_type = Declaration::EntityType::OBJECT_PROPERTY;
                is_declaration = true;
            } else if (node_name == "owl:DatatypeProperty" || node_name == "DatatypeProperty") {
                entity_type = Declaration::EntityType::DATA_PROPERTY;
                is_declaration = true;
            } else if (node_name == "owl:AnnotationProperty" || node_name == "AnnotationProperty") {
                entity_type = Declaration::EntityType::ANNOTATION_PROPERTY;
                is_declaration = true;
            } else if (node_name == "owl:NamedIndividual" || node_name == "NamedIndividual") {
                entity_type = Declaration::EntityType::NAMED_INDIVIDUAL;
                is_declaration = true;
            } else if (node_name == "rdfs:Datatype" || node_name == "Datatype") {
                entity_type = Declaration::EntityType::DATATYPE;
                is_declaration = true;
            }
            
            if (is_declaration) {
                // Get IRI
                auto about = getOptionalAttributeIRI(child, "rdf:about");
                if (!about.has_value()) {
                    about = getOptionalAttributeIRI(child, "about");
                }
                
                if (about.has_value()) {
                    IRI entity_iri = resolveIRI(about.value());
                    auto decl = std::make_shared<Declaration>(entity_type, entity_iri);
                    
                    // Parse annotations on declaration
                    parseAnnotations(child, decl);
                    
                    ontology.addAxiom(decl);
                }
            }
        }
    }
    
    // ========================================================================
    // Axiom parsing
    // ========================================================================
    
    void parseAxioms(Ontology& ontology) {
        for (pugi::xml_node child : rdf_root_.children()) {
            std::string node_name = child.name();
            
            if (node_name == "owl:Class" || node_name == "Class") {
                parseClassAxioms(ontology, child);
            } else if (node_name == "owl:ObjectProperty" || node_name == "ObjectProperty") {
                parseObjectPropertyAxioms(ontology, child);
            } else if (node_name == "owl:DatatypeProperty" || node_name == "DatatypeProperty") {
                parseDataPropertyAxioms(ontology, child);
            } else if (node_name == "owl:NamedIndividual" || node_name == "NamedIndividual") {
                parseIndividualAxioms(ontology, child);
            } else if (node_name == "owl:AllDisjointClasses" || node_name == "AllDisjointClasses") {
                parseDisjointClasses(ontology, child);
            } else if (node_name == "rdf:Description" || node_name == "Description") {
                parseDescriptionAxioms(ontology, child);
            }
        }
    }
    
    void parseClassAxioms(Ontology& ontology, const pugi::xml_node& node) {
        auto about = getOptionalAttributeIRI(node, "rdf:about");
        if (!about.has_value()) {
            about = getOptionalAttributeIRI(node, "about");
        }
        
        if (!about.has_value()) {
            return; // Skip anonymous classes for now
        }
        
        IRI class_iri = resolveIRI(about.value());
        Class cls(class_iri);
        auto named_class = std::make_shared<NamedClass>(cls);
        
        // Parse properties
        for (pugi::xml_node prop : node.children()) {
            std::string prop_name = prop.name();
            
            if (prop_name == "rdfs:subClassOf" || prop_name == "subClassOf") {
                parseSubClassOf(ontology, named_class, prop);
            } else if (prop_name == "owl:equivalentClass" || prop_name == "equivalentClass") {
                parseEquivalentClass(ontology, named_class, prop);
            }
        }
    }
    
    void parseSubClassOf(Ontology& ontology, const ClassExpressionPtr& subclass, const pugi::xml_node& node) {
        ClassExpressionPtr superclass = parseClassExpression(node);
        if (superclass) {
            auto axiom = std::make_shared<SubClassOf>(subclass, superclass);
            parseAnnotations(node, axiom);
            ontology.addAxiom(axiom);
        }
    }
    
    void parseEquivalentClass(Ontology& ontology, const ClassExpressionPtr& cls1, const pugi::xml_node& node) {
        ClassExpressionPtr cls2 = parseClassExpression(node);
        if (cls2) {
            std::vector<ClassExpressionPtr> classes = {cls1, cls2};
            auto axiom = std::make_shared<EquivalentClasses>(classes);
            parseAnnotations(node, axiom);
            ontology.addAxiom(axiom);
        }
    }
    
    void parseDisjointClasses(Ontology& ontology, const pugi::xml_node& node) {
        std::vector<ClassExpressionPtr> classes;
        
        // Find owl:members
        for (pugi::xml_node child : node.children()) {
            std::string child_name = child.name();
            if (child_name == "owl:members" || child_name == "members") {
                // Parse collection
                for (pugi::xml_node member : child.children()) {
                    auto member_about = getOptionalAttributeIRI(member, "rdf:about");
                    if (!member_about.has_value()) {
                        member_about = getOptionalAttributeIRI(member, "about");
                    }
                    if (member_about.has_value()) {
                        IRI member_iri = resolveIRI(member_about.value());
                        Class member_class(member_iri);
                        classes.push_back(std::make_shared<NamedClass>(member_class));
                    }
                }
            }
        }
        
        if (classes.size() >= 2) {
            auto axiom = std::make_shared<DisjointClasses>(classes);
            parseAnnotations(node, axiom);
            ontology.addAxiom(axiom);
        }
    }
    
    void parseObjectPropertyAxioms(Ontology& ontology, const pugi::xml_node& node) {
        auto about = getOptionalAttributeIRI(node, "rdf:about");
        if (!about.has_value()) {
            about = getOptionalAttributeIRI(node, "about");
        }
        
        if (!about.has_value()) {
            return;
        }
        
        IRI prop_iri = resolveIRI(about.value());
        ObjectProperty prop(prop_iri);
        
        // Parse properties
        for (pugi::xml_node child : node.children()) {
            std::string child_name = child.name();
            
            if (child_name == "rdf:type" || child_name == "type") {
                auto resource = getOptionalAttributeIRI(child, "rdf:resource");
                if (!resource.has_value()) {
                    resource = getOptionalAttributeIRI(child, "resource");
                }
                
                if (resource.has_value()) {
                    std::string type_iri = resource.value();
                    
                    if (type_iri == OWL_NS + "FunctionalProperty" || type_iri == "owl:FunctionalProperty") {
                        auto axiom = std::make_shared<FunctionalObjectProperty>(prop);
                        parseAnnotations(child, axiom);
                        ontology.addAxiom(axiom);
                    } else if (type_iri == OWL_NS + "InverseFunctionalProperty" || type_iri == "owl:InverseFunctionalProperty") {
                        auto axiom = std::make_shared<InverseFunctionalObjectProperty>(prop);
                        parseAnnotations(child, axiom);
                        ontology.addAxiom(axiom);
                    } else if (type_iri == OWL_NS + "TransitiveProperty" || type_iri == "owl:TransitiveProperty") {
                        auto axiom = std::make_shared<TransitiveObjectProperty>(prop);
                        parseAnnotations(child, axiom);
                        ontology.addAxiom(axiom);
                    } else if (type_iri == OWL_NS + "SymmetricProperty" || type_iri == "owl:SymmetricProperty") {
                        auto axiom = std::make_shared<SymmetricObjectProperty>(prop);
                        parseAnnotations(child, axiom);
                        ontology.addAxiom(axiom);
                    } else if (type_iri == OWL_NS + "AsymmetricProperty" || type_iri == "owl:AsymmetricProperty") {
                        auto axiom = std::make_shared<AsymmetricObjectProperty>(prop);
                        parseAnnotations(child, axiom);
                        ontology.addAxiom(axiom);
                    } else if (type_iri == OWL_NS + "ReflexiveProperty" || type_iri == "owl:ReflexiveProperty") {
                        auto axiom = std::make_shared<ReflexiveObjectProperty>(prop);
                        parseAnnotations(child, axiom);
                        ontology.addAxiom(axiom);
                    } else if (type_iri == OWL_NS + "IrreflexiveProperty" || type_iri == "owl:IrreflexiveProperty") {
                        auto axiom = std::make_shared<IrreflexiveObjectProperty>(prop);
                        parseAnnotations(child, axiom);
                        ontology.addAxiom(axiom);
                    }
                }
            } else if (child_name == "rdfs:subPropertyOf" || child_name == "subPropertyOf") {
                auto resource = getOptionalAttributeIRI(child, "rdf:resource");
                if (!resource.has_value()) {
                    resource = getOptionalAttributeIRI(child, "resource");
                }
                
                if (resource.has_value()) {
                    IRI super_prop_iri = resolveIRI(resource.value());
                    ObjectProperty super_prop(super_prop_iri);
                    auto axiom = std::make_shared<SubObjectPropertyOf>(prop, super_prop);
                    parseAnnotations(child, axiom);
                    ontology.addAxiom(axiom);
                }
            } else if (child_name == "rdfs:domain" || child_name == "domain") {
                ClassExpressionPtr domain = parseClassExpression(child);
                if (domain) {
                    auto axiom = std::make_shared<ObjectPropertyDomain>(prop, domain);
                    parseAnnotations(child, axiom);
                    ontology.addAxiom(axiom);
                }
            } else if (child_name == "rdfs:range" || child_name == "range") {
                ClassExpressionPtr range = parseClassExpression(child);
                if (range) {
                    auto axiom = std::make_shared<ObjectPropertyRange>(prop, range);
                    parseAnnotations(child, axiom);
                    ontology.addAxiom(axiom);
                }
            }
        }
    }
    
    void parseDataPropertyAxioms(Ontology& ontology, const pugi::xml_node& node) {
        auto about = getOptionalAttributeIRI(node, "rdf:about");
        if (!about.has_value()) {
            about = getOptionalAttributeIRI(node, "about");
        }
        
        if (!about.has_value()) {
            return;
        }
        
        IRI prop_iri = resolveIRI(about.value());
        DataProperty prop(prop_iri);
        
        // Parse properties
        for (pugi::xml_node child : node.children()) {
            std::string child_name = child.name();
            
            if (child_name == "rdf:type" || child_name == "type") {
                auto resource = getOptionalAttributeIRI(child, "rdf:resource");
                if (!resource.has_value()) {
                    resource = getOptionalAttributeIRI(child, "resource");
                }
                
                if (resource.has_value()) {
                    std::string type_iri = resource.value();
                    
                    if (type_iri == OWL_NS + "FunctionalProperty" || type_iri == "owl:FunctionalProperty") {
                        auto axiom = std::make_shared<FunctionalDataProperty>(prop);
                        parseAnnotations(child, axiom);
                        ontology.addAxiom(axiom);
                    }
                }
            } else if (child_name == "rdfs:subPropertyOf" || child_name == "subPropertyOf") {
                auto resource = getOptionalAttributeIRI(child, "rdf:resource");
                if (!resource.has_value()) {
                    resource = getOptionalAttributeIRI(child, "resource");
                }
                
                if (resource.has_value()) {
                    IRI super_prop_iri = resolveIRI(resource.value());
                    DataProperty super_prop(super_prop_iri);
                    auto axiom = std::make_shared<SubDataPropertyOf>(prop, super_prop);
                    parseAnnotations(child, axiom);
                    ontology.addAxiom(axiom);
                }
            } else if (child_name == "rdfs:domain" || child_name == "domain") {
                ClassExpressionPtr domain = parseClassExpression(child);
                if (domain) {
                    auto axiom = std::make_shared<DataPropertyDomain>(prop, domain);
                    parseAnnotations(child, axiom);
                    ontology.addAxiom(axiom);
                }
            } else if (child_name == "rdfs:range" || child_name == "range") {
                auto resource = getOptionalAttributeIRI(child, "rdf:resource");
                if (!resource.has_value()) {
                    resource = getOptionalAttributeIRI(child, "resource");
                }
                
                if (resource.has_value()) {
                    IRI datatype_iri = resolveIRI(resource.value());
                    Datatype dt(datatype_iri);
                    auto range = std::make_shared<NamedDatatype>(dt);
                    auto axiom = std::make_shared<DataPropertyRange>(prop, range);
                    parseAnnotations(child, axiom);
                    ontology.addAxiom(axiom);
                }
            }
        }
    }
    
    void parseIndividualAxioms(Ontology& ontology, const pugi::xml_node& node) {
        auto about = getOptionalAttributeIRI(node, "rdf:about");
        if (!about.has_value()) {
            about = getOptionalAttributeIRI(node, "about");
        }
        
        if (!about.has_value()) {
            return;
        }
        
        IRI ind_iri = resolveIRI(about.value());
        NamedIndividual ind(ind_iri);
        
        // Parse properties
        for (pugi::xml_node child : node.children()) {
            std::string child_name = child.name();
            
            if (child_name == "rdf:type" || child_name == "type") {
                ClassExpressionPtr cls = parseClassExpression(child);
                if (cls) {
                    auto axiom = std::make_shared<ClassAssertion>(cls, ind);
                    parseAnnotations(child, axiom);
                    ontology.addAxiom(axiom);
                }
            } else {
                // Check if it's a property assertion
                parsePropertyAssertion(ontology, ind, child);
            }
        }
    }
    
    void parseDescriptionAxioms(Ontology& ontology, const pugi::xml_node& node) {
        auto about = getOptionalAttributeIRI(node, "rdf:about");
        if (!about.has_value()) {
            about = getOptionalAttributeIRI(node, "about");
        }
        
        if (!about.has_value()) {
            return;
        }
        
        IRI subject_iri = resolveIRI(about.value());
        
        // Parse properties - these are likely annotation assertions
        for (pugi::xml_node child : node.children()) {
            std::string child_name = child.name();
            
            // Parse as annotation assertion
            IRI prop_iri = resolveNodeName(child_name);
            AnnotationProperty prop(prop_iri);
            AnnotationValue value = parseAnnotationValue(child);
            
            auto axiom = std::make_shared<AnnotationAssertion>(prop, subject_iri, value);
            parseAnnotations(child, axiom);
            ontology.addAxiom(axiom);
        }
    }
    
    void parsePropertyAssertion(Ontology& ontology, const NamedIndividual& ind, const pugi::xml_node& node) {
        std::string prop_name = node.name();
        IRI prop_iri = resolveNodeName(prop_name);
        
        // Check if it's a resource (object property) or literal (data property)
        auto resource = getOptionalAttributeIRI(node, "rdf:resource");
        if (!resource.has_value()) {
            resource = getOptionalAttributeIRI(node, "resource");
        }
        
        if (resource.has_value()) {
            // Object property assertion
            IRI target_iri = resolveIRI(resource.value());
            NamedIndividual target(target_iri);
            ObjectProperty prop(prop_iri);
            
            auto axiom = std::make_shared<ObjectPropertyAssertion>(prop, ind, target);
            parseAnnotations(node, axiom);
            ontology.addAxiom(axiom);
        } else {
            // Data property assertion
            std::string text = node.child_value();
            if (!text.empty()) {
                DataProperty prop(prop_iri);
                Literal literal = parseLiteral(node);
                
                auto axiom = std::make_shared<DataPropertyAssertion>(prop, ind, literal);
                parseAnnotations(node, axiom);
                ontology.addAxiom(axiom);
            }
        }
    }
    
    // ========================================================================
    // Class expression parsing
    // ========================================================================
    
    ClassExpressionPtr parseClassExpression(const pugi::xml_node& node) {
        // Check for rdf:resource attribute (named class)
        auto resource = getOptionalAttributeIRI(node, "rdf:resource");
        if (!resource.has_value()) {
            resource = getOptionalAttributeIRI(node, "resource");
        }
        
        if (resource.has_value()) {
            IRI class_iri = resolveIRI(resource.value());
            Class cls(class_iri);
            return std::make_shared<NamedClass>(cls);
        }
        
        // Check for nested class expression
        for (pugi::xml_node child : node.children()) {
            std::string child_name = child.name();
            
            if (child_name == "owl:Class" || child_name == "Class") {
                auto about = getOptionalAttributeIRI(child, "rdf:about");
                if (!about.has_value()) {
                    about = getOptionalAttributeIRI(child, "about");
                }
                
                if (about.has_value()) {
                    IRI class_iri = resolveIRI(about.value());
                    Class cls(class_iri);
                    return std::make_shared<NamedClass>(cls);
                }
                
                // Check for complex class expression
                return parseComplexClassExpression(child);
            } else if (child_name == "owl:Restriction" || child_name == "Restriction") {
                return parseRestriction(child);
            }
        }
        
        return nullptr;
    }
    
    ClassExpressionPtr parseComplexClassExpression(const pugi::xml_node& node) {
        for (pugi::xml_node child : node.children()) {
            std::string child_name = child.name();
            
            if (child_name == "owl:intersectionOf" || child_name == "intersectionOf") {
                return parseIntersectionOf(child);
            } else if (child_name == "owl:unionOf" || child_name == "unionOf") {
                return parseUnionOf(child);
            }
        }
        
        return nullptr;
    }
    
    ClassExpressionPtr parseRestriction(const pugi::xml_node& node) {
        IRI property_iri("");
        ClassExpressionPtr filler = nullptr;
        std::string restriction_type;
        
        for (pugi::xml_node child : node.children()) {
            std::string child_name = child.name();
            
            if (child_name == "owl:onProperty" || child_name == "onProperty") {
                auto resource = getOptionalAttributeIRI(child, "rdf:resource");
                if (!resource.has_value()) {
                    resource = getOptionalAttributeIRI(child, "resource");
                }
                if (resource.has_value()) {
                    property_iri = resolveIRI(resource.value());
                }
            } else if (child_name == "owl:someValuesFrom" || child_name == "someValuesFrom") {
                restriction_type = "someValuesFrom";
                filler = parseClassExpression(child);
            } else if (child_name == "owl:allValuesFrom" || child_name == "allValuesFrom") {
                restriction_type = "allValuesFrom";
                filler = parseClassExpression(child);
            }
        }
        
        if (property_iri.getFullIRI().empty() || !filler) {
            return nullptr;
        }
        
        ObjectProperty prop(property_iri);
        
        if (restriction_type == "someValuesFrom") {
            return std::make_shared<ObjectSomeValuesFrom>(prop, filler);
        } else if (restriction_type == "allValuesFrom") {
            return std::make_shared<ObjectAllValuesFrom>(prop, filler);
        }
        
        return nullptr;
    }
    
    ClassExpressionPtr parseIntersectionOf(const pugi::xml_node& node) {
        std::vector<ClassExpressionPtr> operands;
        
        // Parse collection
        for (pugi::xml_node child : node.children()) {
            ClassExpressionPtr operand = parseClassExpression(child);
            if (operand) {
                operands.push_back(operand);
            }
        }
        
        if (operands.empty()) {
            return nullptr;
        }
        
        return std::make_shared<ObjectIntersectionOf>(operands);
    }
    
    ClassExpressionPtr parseUnionOf(const pugi::xml_node& node) {
        std::vector<ClassExpressionPtr> operands;
        
        // Parse collection
        for (pugi::xml_node child : node.children()) {
            ClassExpressionPtr operand = parseClassExpression(child);
            if (operand) {
                operands.push_back(operand);
            }
        }
        
        if (operands.empty()) {
            return nullptr;
        }
        
        return std::make_shared<ObjectUnionOf>(operands);
    }
    
    // ========================================================================
    // Annotation parsing
    // ========================================================================
    
    void parseAnnotations(const pugi::xml_node& node, const AxiomPtr& axiom) {
        // For now, we skip nested annotations on axioms
        // This could be extended to parse rdfs:label, rdfs:comment, etc.
        // on the axiom itself
    }
    
    AnnotationValue parseAnnotationValue(const pugi::xml_node& node) {
        // Check for resource
        auto resource = getOptionalAttributeIRI(node, "rdf:resource");
        if (!resource.has_value()) {
            resource = getOptionalAttributeIRI(node, "resource");
        }
        
        if (resource.has_value()) {
            return resolveIRI(resource.value());
        }
        
        // Check for node ID (anonymous individual)
        auto node_id = getOptionalAttributeIRI(node, "rdf:nodeID");
        if (!node_id.has_value()) {
            node_id = getOptionalAttributeIRI(node, "nodeID");
        }
        
        if (node_id.has_value()) {
            return AnonymousIndividual(node_id.value());
        }
        
        // Otherwise, it's a literal
        return parseLiteral(node);
    }
    
    Literal parseLiteral(const pugi::xml_node& node) {
        std::string text = node.child_value();
        
        // Check for language tag
        auto lang = getOptionalAttributeIRI(node, "xml:lang");
        if (lang.has_value()) {
            return Literal(text, lang.value());
        }
        
        // Check for datatype
        auto datatype = getOptionalAttributeIRI(node, "rdf:datatype");
        if (!datatype.has_value()) {
            datatype = getOptionalAttributeIRI(node, "datatype");
        }
        
        if (datatype.has_value()) {
            IRI datatype_iri = resolveIRI(datatype.value());
            return Literal(text, datatype_iri);
        }
        
        // Plain literal
        return Literal(text);
    }
    
    IRI resolveNodeName(const std::string& node_name) {
        // Split on colon
        size_t colon_pos = node_name.find(':');
        if (colon_pos != std::string::npos) {
            std::string prefix = node_name.substr(0, colon_pos);
            std::string local_name = node_name.substr(colon_pos + 1);
            
            auto it = namespaces_.find(prefix);
            if (it != namespaces_.end()) {
                return IRI(prefix, local_name, it->second);
            }
        }
        
        // Full IRI
        return IRI(node_name);
    }
};

// ============================================================================
// Public API Implementation
// ============================================================================

Ontology RDFXMLParser::parse(const std::string& rdfxml_content) {
    Parser parser(rdfxml_content);
    return parser.parse();
}

Ontology RDFXMLParser::parseFromFile(const std::string& filename) {
    std::ifstream file(filename);
    if (!file.is_open()) {
        throw RDFXMLParseException("Cannot open file: " + filename);
    }
    
    std::stringstream buffer;
    buffer << file.rdbuf();
    file.close();
    
    return parse(buffer.str());
}

} // namespace owl2
} // namespace ista
