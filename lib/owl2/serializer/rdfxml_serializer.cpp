#include "rdfxml_serializer.hpp"
#include <fstream>
#include <algorithm>
#include <sstream>

namespace ista {
namespace owl2 {

// ============================================================================
// Public API
// ============================================================================

std::string RDFXMLSerializer::serialize(const Ontology& ontology) {
    Builder builder(ontology);
    return builder.build();
}

bool RDFXMLSerializer::serializeToFile(const Ontology& ontology, const std::string& filename) {
    std::string xml = serialize(ontology);
    std::ofstream file(filename);
    if (!file.is_open()) {
        return false;
    }
    file << xml;
    file.close();
    return true;
}

// ============================================================================
// Builder Implementation
// ============================================================================

RDFXMLSerializer::Builder::Builder(const Ontology& ontology)
    : ontology_(ontology), blank_node_counter_(0) {
    registerStandardNamespaces();
    registerOntologyNamespaces();
}

std::string RDFXMLSerializer::Builder::build() {
    writeXMLDeclaration();
    writeRDFHeader();
    writeOntologyHeader();
    writeAxioms();
    writeRDFFooter();
    return xml_.str();
}

void RDFXMLSerializer::Builder::writeXMLDeclaration() {
    xml_ << "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n";
}

void RDFXMLSerializer::Builder::writeRDFHeader() {
    xml_ << "<rdf:RDF";
    
    // Write namespace declarations
    for (const auto& [prefix, ns] : namespaces_) {
        xml_ << "\n    xmlns:" << prefix << "=\"" << escapeXML(ns) << "\"";
    }
    
    xml_ << ">\n\n";
}

void RDFXMLSerializer::Builder::writeOntologyHeader() {
    auto ontology_iri = ontology_.getOntologyIRI();
    if (ontology_iri.has_value()) {
        xml_ << "    <owl:Ontology rdf:about=\"" << escapeXML(ontology_iri.value().getFullIRI()) << "\"";
        
        auto version_iri = ontology_.getVersionIRI();
        if (version_iri.has_value()) {
            xml_ << ">\n";
            xml_ << "        <owl:versionIRI rdf:resource=\"" << escapeXML(version_iri.value().getFullIRI()) << "\"/>\n";
            
            // Write imports
            for (const auto& import_iri : ontology_.getImports()) {
                xml_ << "        <owl:imports rdf:resource=\"" << escapeXML(import_iri.getFullIRI()) << "\"/>\n";
            }
            
            // Write ontology annotations
            writeAnnotations(ontology_.getOntologyAnnotations(), "        ");
            
            xml_ << "    </owl:Ontology>\n\n";
        } else {
            // No version IRI, check for imports or annotations
            if (!ontology_.getImports().empty() || !ontology_.getOntologyAnnotations().empty()) {
                xml_ << ">\n";
                
                for (const auto& import_iri : ontology_.getImports()) {
                    xml_ << "        <owl:imports rdf:resource=\"" << escapeXML(import_iri.getFullIRI()) << "\"/>\n";
                }
                
                writeAnnotations(ontology_.getOntologyAnnotations(), "        ");
                
                xml_ << "    </owl:Ontology>\n\n";
            } else {
                xml_ << "/>\n\n";
            }
        }
    }
}

void RDFXMLSerializer::Builder::writeAxioms() {
    auto axioms = ontology_.getAxioms();
    
    for (const auto& axiom : axioms) {
        std::string axiom_type = axiom->getAxiomType();
        
        // Declaration axioms
        if (axiom_type == "Declaration") {
            writeDeclaration(std::dynamic_pointer_cast<Declaration>(axiom));
        }
        // Class axioms
        else if (axiom_type == "SubClassOf") {
            writeSubClassOf(std::dynamic_pointer_cast<SubClassOf>(axiom));
        }
        else if (axiom_type == "EquivalentClasses") {
            writeEquivalentClasses(std::dynamic_pointer_cast<EquivalentClasses>(axiom));
        }
        else if (axiom_type == "DisjointClasses") {
            writeDisjointClasses(std::dynamic_pointer_cast<DisjointClasses>(axiom));
        }
        // Object property axioms
        else if (axiom_type == "SubObjectPropertyOf") {
            writeSubObjectPropertyOf(std::dynamic_pointer_cast<SubObjectPropertyOf>(axiom));
        }
        else if (axiom_type == "ObjectPropertyDomain") {
            writeObjectPropertyDomain(std::dynamic_pointer_cast<ObjectPropertyDomain>(axiom));
        }
        else if (axiom_type == "ObjectPropertyRange") {
            writeObjectPropertyRange(std::dynamic_pointer_cast<ObjectPropertyRange>(axiom));
        }
        else if (axiom_type == "FunctionalObjectProperty") {
            writeFunctionalObjectProperty(std::dynamic_pointer_cast<FunctionalObjectProperty>(axiom));
        }
        else if (axiom_type == "InverseFunctionalObjectProperty") {
            writeInverseFunctionalObjectProperty(std::dynamic_pointer_cast<InverseFunctionalObjectProperty>(axiom));
        }
        else if (axiom_type == "TransitiveObjectProperty") {
            writeTransitiveObjectProperty(std::dynamic_pointer_cast<TransitiveObjectProperty>(axiom));
        }
        else if (axiom_type == "SymmetricObjectProperty") {
            writeSymmetricObjectProperty(std::dynamic_pointer_cast<SymmetricObjectProperty>(axiom));
        }
        else if (axiom_type == "AsymmetricObjectProperty") {
            writeAsymmetricObjectProperty(std::dynamic_pointer_cast<AsymmetricObjectProperty>(axiom));
        }
        else if (axiom_type == "ReflexiveObjectProperty") {
            writeReflexiveObjectProperty(std::dynamic_pointer_cast<ReflexiveObjectProperty>(axiom));
        }
        else if (axiom_type == "IrreflexiveObjectProperty") {
            writeIrreflexiveObjectProperty(std::dynamic_pointer_cast<IrreflexiveObjectProperty>(axiom));
        }
        // Data property axioms
        else if (axiom_type == "SubDataPropertyOf") {
            writeSubDataPropertyOf(std::dynamic_pointer_cast<SubDataPropertyOf>(axiom));
        }
        else if (axiom_type == "DataPropertyDomain") {
            writeDataPropertyDomain(std::dynamic_pointer_cast<DataPropertyDomain>(axiom));
        }
        else if (axiom_type == "DataPropertyRange") {
            writeDataPropertyRange(std::dynamic_pointer_cast<DataPropertyRange>(axiom));
        }
        else if (axiom_type == "FunctionalDataProperty") {
            writeFunctionalDataProperty(std::dynamic_pointer_cast<FunctionalDataProperty>(axiom));
        }
        // Assertion axioms
        else if (axiom_type == "ClassAssertion") {
            writeClassAssertion(std::dynamic_pointer_cast<ClassAssertion>(axiom));
        }
        else if (axiom_type == "ObjectPropertyAssertion") {
            writeObjectPropertyAssertion(std::dynamic_pointer_cast<ObjectPropertyAssertion>(axiom));
        }
        else if (axiom_type == "DataPropertyAssertion") {
            writeDataPropertyAssertion(std::dynamic_pointer_cast<DataPropertyAssertion>(axiom));
        }
        // Annotation axioms
        else if (axiom_type == "AnnotationAssertion") {
            writeAnnotationAssertion(std::dynamic_pointer_cast<AnnotationAssertion>(axiom));
        }
    }
}

void RDFXMLSerializer::Builder::writeRDFFooter() {
    xml_ << "</rdf:RDF>\n";
}

// ============================================================================
// Declaration Axioms
// ============================================================================

void RDFXMLSerializer::Builder::writeDeclaration(const std::shared_ptr<Declaration>& axiom) {
    if (!axiom) return;
    
    std::string entity_type;
    switch (axiom->getEntityType()) {
        case Declaration::EntityType::CLASS:
            entity_type = "owl:Class";
            break;
        case Declaration::EntityType::OBJECT_PROPERTY:
            entity_type = "owl:ObjectProperty";
            break;
        case Declaration::EntityType::DATA_PROPERTY:
            entity_type = "owl:DatatypeProperty";
            break;
        case Declaration::EntityType::ANNOTATION_PROPERTY:
            entity_type = "owl:AnnotationProperty";
            break;
        case Declaration::EntityType::NAMED_INDIVIDUAL:
            entity_type = "owl:NamedIndividual";
            break;
        case Declaration::EntityType::DATATYPE:
            entity_type = "rdfs:Datatype";
            break;
        default:
            return;
    }
    
    std::string qname = getQName(axiom->getIRI());
    
    if (axiom->hasAnnotations()) {
        xml_ << "    <" << entity_type << " rdf:about=\"" << escapeXML(axiom->getIRI().getFullIRI()) << "\">\n";
        writeAnnotations(axiom->getAnnotations(), "        ");
        xml_ << "    </" << entity_type << ">\n\n";
    } else {
        xml_ << "    <" << entity_type << " rdf:about=\"" << escapeXML(axiom->getIRI().getFullIRI()) << "\"/>\n\n";
    }
}

// ============================================================================
// Class Axioms
// ============================================================================

void RDFXMLSerializer::Builder::writeSubClassOf(const std::shared_ptr<SubClassOf>& axiom) {
    if (!axiom) return;
    
    auto subclass = axiom->getSubClass();
    auto superclass = axiom->getSuperClass();
    
    // For named subclass
    if (subclass->getExpressionType() == "NamedClass") {
        auto named_sub = std::dynamic_pointer_cast<NamedClass>(subclass);
        xml_ << "    <owl:Class rdf:about=\"" << escapeXML(named_sub->getClass().getIRI().getFullIRI()) << "\">\n";
        
        // Write subClassOf relationship
        if (superclass->getExpressionType() == "NamedClass") {
            auto named_super = std::dynamic_pointer_cast<NamedClass>(superclass);
            xml_ << "        <rdfs:subClassOf rdf:resource=\"" << escapeXML(named_super->getClass().getIRI().getFullIRI()) << "\"/>\n";
        } else {
            // Complex class expression
            xml_ << "        <rdfs:subClassOf>\n";
            writeClassExpression(superclass, "            ");
            xml_ << "        </rdfs:subClassOf>\n";
        }
        
        writeAnnotations(axiom->getAnnotations(), "        ");
        xml_ << "    </owl:Class>\n\n";
    } else {
        // Complex subclass expression - use blank node
        xml_ << "    <owl:Class>\n";
        xml_ << "        <owl:equivalentClass>\n";
        writeClassExpression(subclass, "            ");
        xml_ << "        </owl:equivalentClass>\n";
        xml_ << "        <rdfs:subClassOf>\n";
        writeClassExpression(superclass, "            ");
        xml_ << "        </rdfs:subClassOf>\n";
        writeAnnotations(axiom->getAnnotations(), "        ");
        xml_ << "    </owl:Class>\n\n";
    }
}

void RDFXMLSerializer::Builder::writeEquivalentClasses(const std::shared_ptr<EquivalentClasses>& axiom) {
    if (!axiom) return;
    
    auto class_expressions = axiom->getClassExpressions();
    if (class_expressions.size() < 2) return;
    
    auto first = class_expressions[0];
    
    if (first->getExpressionType() == "NamedClass") {
        auto named = std::dynamic_pointer_cast<NamedClass>(first);
        xml_ << "    <owl:Class rdf:about=\"" << escapeXML(named->getClass().getIRI().getFullIRI()) << "\">\n";
        
        for (size_t i = 1; i < class_expressions.size(); ++i) {
            if (class_expressions[i]->getExpressionType() == "NamedClass") {
                auto named_eq = std::dynamic_pointer_cast<NamedClass>(class_expressions[i]);
                xml_ << "        <owl:equivalentClass rdf:resource=\"" << escapeXML(named_eq->getClass().getIRI().getFullIRI()) << "\"/>\n";
            } else {
                xml_ << "        <owl:equivalentClass>\n";
                writeClassExpression(class_expressions[i], "            ");
                xml_ << "        </owl:equivalentClass>\n";
            }
        }
        
        writeAnnotations(axiom->getAnnotations(), "        ");
        xml_ << "    </owl:Class>\n\n";
    }
}

void RDFXMLSerializer::Builder::writeDisjointClasses(const std::shared_ptr<DisjointClasses>& axiom) {
    if (!axiom) return;
    
    auto class_expressions = axiom->getClassExpressions();
    if (class_expressions.size() < 2) return;
    
    xml_ << "    <owl:AllDisjointClasses>\n";
    xml_ << "        <owl:members rdf:parseType=\"Collection\">\n";
    
    for (const auto& expr : class_expressions) {
        if (expr->getExpressionType() == "NamedClass") {
            auto named = std::dynamic_pointer_cast<NamedClass>(expr);
            xml_ << "            <owl:Class rdf:about=\"" << escapeXML(named->getClass().getIRI().getFullIRI()) << "\"/>\n";
        } else {
            writeClassExpression(expr, "            ");
        }
    }
    
    xml_ << "        </owl:members>\n";
    writeAnnotations(axiom->getAnnotations(), "        ");
    xml_ << "    </owl:AllDisjointClasses>\n\n";
}

// ============================================================================
// Object Property Axioms
// ============================================================================

void RDFXMLSerializer::Builder::writeSubObjectPropertyOf(const std::shared_ptr<SubObjectPropertyOf>& axiom) {
    if (!axiom) return;
    
    auto sub_prop_opt = axiom->getSubProperty();
    auto super_prop = axiom->getSuperProperty();
    
    if (!sub_prop_opt.has_value()) return;
    
    auto sub_prop = sub_prop_opt.value();
    
    // Handle simple object property (not inverse)
    if (std::holds_alternative<ObjectProperty>(sub_prop)) {
        auto prop = std::get<ObjectProperty>(sub_prop);
        xml_ << "    <owl:ObjectProperty rdf:about=\"" << escapeXML(prop.getIRI().getFullIRI()) << "\">\n";
        
        if (std::holds_alternative<ObjectProperty>(super_prop)) {
            auto super = std::get<ObjectProperty>(super_prop);
            xml_ << "        <rdfs:subPropertyOf rdf:resource=\"" << escapeXML(super.getIRI().getFullIRI()) << "\"/>\n";
        }
        
        writeAnnotations(axiom->getAnnotations(), "        ");
        xml_ << "    </owl:ObjectProperty>\n\n";
    }
}

void RDFXMLSerializer::Builder::writeObjectPropertyDomain(const std::shared_ptr<ObjectPropertyDomain>& axiom) {
    if (!axiom) return;
    
    auto prop_expr = axiom->getProperty();
    auto domain = axiom->getDomain();
    
    if (std::holds_alternative<ObjectProperty>(prop_expr)) {
        auto prop = std::get<ObjectProperty>(prop_expr);
        xml_ << "    <owl:ObjectProperty rdf:about=\"" << escapeXML(prop.getIRI().getFullIRI()) << "\">\n";
        
        if (domain->getExpressionType() == "NamedClass") {
            auto named = std::dynamic_pointer_cast<NamedClass>(domain);
            xml_ << "        <rdfs:domain rdf:resource=\"" << escapeXML(named->getClass().getIRI().getFullIRI()) << "\"/>\n";
        } else {
            xml_ << "        <rdfs:domain>\n";
            writeClassExpression(domain, "            ");
            xml_ << "        </rdfs:domain>\n";
        }
        
        writeAnnotations(axiom->getAnnotations(), "        ");
        xml_ << "    </owl:ObjectProperty>\n\n";
    }
}

void RDFXMLSerializer::Builder::writeObjectPropertyRange(const std::shared_ptr<ObjectPropertyRange>& axiom) {
    if (!axiom) return;
    
    auto prop_expr = axiom->getProperty();
    auto range = axiom->getRange();
    
    if (std::holds_alternative<ObjectProperty>(prop_expr)) {
        auto prop = std::get<ObjectProperty>(prop_expr);
        xml_ << "    <owl:ObjectProperty rdf:about=\"" << escapeXML(prop.getIRI().getFullIRI()) << "\">\n";
        
        if (range->getExpressionType() == "NamedClass") {
            auto named = std::dynamic_pointer_cast<NamedClass>(range);
            xml_ << "        <rdfs:range rdf:resource=\"" << escapeXML(named->getClass().getIRI().getFullIRI()) << "\"/>\n";
        } else {
            xml_ << "        <rdfs:range>\n";
            writeClassExpression(range, "            ");
            xml_ << "        </rdfs:range>\n";
        }
        
        writeAnnotations(axiom->getAnnotations(), "        ");
        xml_ << "    </owl:ObjectProperty>\n\n";
    }
}

void RDFXMLSerializer::Builder::writeFunctionalObjectProperty(const std::shared_ptr<FunctionalObjectProperty>& axiom) {
    if (!axiom) return;
    
    auto prop_expr = axiom->getProperty();
    
    if (std::holds_alternative<ObjectProperty>(prop_expr)) {
        auto prop = std::get<ObjectProperty>(prop_expr);
        xml_ << "    <owl:ObjectProperty rdf:about=\"" << escapeXML(prop.getIRI().getFullIRI()) << "\">\n";
        xml_ << "        <rdf:type rdf:resource=\"http://www.w3.org/2002/07/owl#FunctionalProperty\"/>\n";
        writeAnnotations(axiom->getAnnotations(), "        ");
        xml_ << "    </owl:ObjectProperty>\n\n";
    }
}

void RDFXMLSerializer::Builder::writeInverseFunctionalObjectProperty(const std::shared_ptr<InverseFunctionalObjectProperty>& axiom) {
    if (!axiom) return;
    
    auto prop_expr = axiom->getProperty();
    
    if (std::holds_alternative<ObjectProperty>(prop_expr)) {
        auto prop = std::get<ObjectProperty>(prop_expr);
        xml_ << "    <owl:ObjectProperty rdf:about=\"" << escapeXML(prop.getIRI().getFullIRI()) << "\">\n";
        xml_ << "        <rdf:type rdf:resource=\"http://www.w3.org/2002/07/owl#InverseFunctionalProperty\"/>\n";
        writeAnnotations(axiom->getAnnotations(), "        ");
        xml_ << "    </owl:ObjectProperty>\n\n";
    }
}

void RDFXMLSerializer::Builder::writeTransitiveObjectProperty(const std::shared_ptr<TransitiveObjectProperty>& axiom) {
    if (!axiom) return;
    
    auto prop_expr = axiom->getProperty();
    
    if (std::holds_alternative<ObjectProperty>(prop_expr)) {
        auto prop = std::get<ObjectProperty>(prop_expr);
        xml_ << "    <owl:ObjectProperty rdf:about=\"" << escapeXML(prop.getIRI().getFullIRI()) << "\">\n";
        xml_ << "        <rdf:type rdf:resource=\"http://www.w3.org/2002/07/owl#TransitiveProperty\"/>\n";
        writeAnnotations(axiom->getAnnotations(), "        ");
        xml_ << "    </owl:ObjectProperty>\n\n";
    }
}

void RDFXMLSerializer::Builder::writeSymmetricObjectProperty(const std::shared_ptr<SymmetricObjectProperty>& axiom) {
    if (!axiom) return;
    
    auto prop_expr = axiom->getProperty();
    
    if (std::holds_alternative<ObjectProperty>(prop_expr)) {
        auto prop = std::get<ObjectProperty>(prop_expr);
        xml_ << "    <owl:ObjectProperty rdf:about=\"" << escapeXML(prop.getIRI().getFullIRI()) << "\">\n";
        xml_ << "        <rdf:type rdf:resource=\"http://www.w3.org/2002/07/owl#SymmetricProperty\"/>\n";
        writeAnnotations(axiom->getAnnotations(), "        ");
        xml_ << "    </owl:ObjectProperty>\n\n";
    }
}

void RDFXMLSerializer::Builder::writeAsymmetricObjectProperty(const std::shared_ptr<AsymmetricObjectProperty>& axiom) {
    if (!axiom) return;
    
    auto prop_expr = axiom->getProperty();
    
    if (std::holds_alternative<ObjectProperty>(prop_expr)) {
        auto prop = std::get<ObjectProperty>(prop_expr);
        xml_ << "    <owl:ObjectProperty rdf:about=\"" << escapeXML(prop.getIRI().getFullIRI()) << "\">\n";
        xml_ << "        <rdf:type rdf:resource=\"http://www.w3.org/2002/07/owl#AsymmetricProperty\"/>\n";
        writeAnnotations(axiom->getAnnotations(), "        ");
        xml_ << "    </owl:ObjectProperty>\n\n";
    }
}

void RDFXMLSerializer::Builder::writeReflexiveObjectProperty(const std::shared_ptr<ReflexiveObjectProperty>& axiom) {
    if (!axiom) return;
    
    auto prop_expr = axiom->getProperty();
    
    if (std::holds_alternative<ObjectProperty>(prop_expr)) {
        auto prop = std::get<ObjectProperty>(prop_expr);
        xml_ << "    <owl:ObjectProperty rdf:about=\"" << escapeXML(prop.getIRI().getFullIRI()) << "\">\n";
        xml_ << "        <rdf:type rdf:resource=\"http://www.w3.org/2002/07/owl#ReflexiveProperty\"/>\n";
        writeAnnotations(axiom->getAnnotations(), "        ");
        xml_ << "    </owl:ObjectProperty>\n\n";
    }
}

void RDFXMLSerializer::Builder::writeIrreflexiveObjectProperty(const std::shared_ptr<IrreflexiveObjectProperty>& axiom) {
    if (!axiom) return;
    
    auto prop_expr = axiom->getProperty();
    
    if (std::holds_alternative<ObjectProperty>(prop_expr)) {
        auto prop = std::get<ObjectProperty>(prop_expr);
        xml_ << "    <owl:ObjectProperty rdf:about=\"" << escapeXML(prop.getIRI().getFullIRI()) << "\">\n";
        xml_ << "        <rdf:type rdf:resource=\"http://www.w3.org/2002/07/owl#IrreflexiveProperty\"/>\n";
        writeAnnotations(axiom->getAnnotations(), "        ");
        xml_ << "    </owl:ObjectProperty>\n\n";
    }
}

// ============================================================================
// Data Property Axioms
// ============================================================================

void RDFXMLSerializer::Builder::writeSubDataPropertyOf(const std::shared_ptr<SubDataPropertyOf>& axiom) {
    if (!axiom) return;
    
    auto sub_prop = axiom->getSubProperty();
    auto super_prop = axiom->getSuperProperty();
    
    xml_ << "    <owl:DatatypeProperty rdf:about=\"" << escapeXML(sub_prop.getIRI().getFullIRI()) << "\">\n";
    xml_ << "        <rdfs:subPropertyOf rdf:resource=\"" << escapeXML(super_prop.getIRI().getFullIRI()) << "\"/>\n";
    writeAnnotations(axiom->getAnnotations(), "        ");
    xml_ << "    </owl:DatatypeProperty>\n\n";
}

void RDFXMLSerializer::Builder::writeDataPropertyDomain(const std::shared_ptr<DataPropertyDomain>& axiom) {
    if (!axiom) return;
    
    auto prop = axiom->getProperty();
    auto domain = axiom->getDomain();
    
    xml_ << "    <owl:DatatypeProperty rdf:about=\"" << escapeXML(prop.getIRI().getFullIRI()) << "\">\n";
    
    if (domain->getExpressionType() == "NamedClass") {
        auto named = std::dynamic_pointer_cast<NamedClass>(domain);
        xml_ << "        <rdfs:domain rdf:resource=\"" << escapeXML(named->getClass().getIRI().getFullIRI()) << "\"/>\n";
    } else {
        xml_ << "        <rdfs:domain>\n";
        writeClassExpression(domain, "            ");
        xml_ << "        </rdfs:domain>\n";
    }
    
    writeAnnotations(axiom->getAnnotations(), "        ");
    xml_ << "    </owl:DatatypeProperty>\n\n";
}

void RDFXMLSerializer::Builder::writeDataPropertyRange(const std::shared_ptr<DataPropertyRange>& axiom) {
    if (!axiom) return;
    
    auto prop = axiom->getProperty();
    auto range = axiom->getRange();
    
    xml_ << "    <owl:DatatypeProperty rdf:about=\"" << escapeXML(prop.getIRI().getFullIRI()) << "\">\n";
    
    // For now, handle simple datatype ranges
    if (range && range->getDataRangeType() == "NamedDatatype") {
        auto named_dt = std::dynamic_pointer_cast<NamedDatatype>(range);
        if (named_dt) {
            xml_ << "        <rdfs:range rdf:resource=\"" << escapeXML(named_dt->getDatatype().getIRI().getFullIRI()) << "\"/>\n";
        }
    }
    
    writeAnnotations(axiom->getAnnotations(), "        ");
    xml_ << "    </owl:DatatypeProperty>\n\n";
}

void RDFXMLSerializer::Builder::writeFunctionalDataProperty(const std::shared_ptr<FunctionalDataProperty>& axiom) {
    if (!axiom) return;
    
    auto prop = axiom->getProperty();
    
    xml_ << "    <owl:DatatypeProperty rdf:about=\"" << escapeXML(prop.getIRI().getFullIRI()) << "\">\n";
    xml_ << "        <rdf:type rdf:resource=\"http://www.w3.org/2002/07/owl#FunctionalProperty\"/>\n";
    writeAnnotations(axiom->getAnnotations(), "        ");
    xml_ << "    </owl:DatatypeProperty>\n\n";
}

// ============================================================================
// Assertion Axioms
// ============================================================================

void RDFXMLSerializer::Builder::writeClassAssertion(const std::shared_ptr<ClassAssertion>& axiom) {
    if (!axiom) return;
    
    auto class_expr = axiom->getClassExpression();
    auto individual = axiom->getIndividual();
    
    std::string ind_str = formatIndividual(individual);
    
    if (class_expr->getExpressionType() == "NamedClass") {
        auto named = std::dynamic_pointer_cast<NamedClass>(class_expr);
        xml_ << "    <owl:NamedIndividual rdf:about=\"" << ind_str << "\">\n";
        xml_ << "        <rdf:type rdf:resource=\"" << escapeXML(named->getClass().getIRI().getFullIRI()) << "\"/>\n";
        writeAnnotations(axiom->getAnnotations(), "        ");
        xml_ << "    </owl:NamedIndividual>\n\n";
    } else {
        xml_ << "    <owl:NamedIndividual rdf:about=\"" << ind_str << "\">\n";
        xml_ << "        <rdf:type>\n";
        writeClassExpression(class_expr, "            ");
        xml_ << "        </rdf:type>\n";
        writeAnnotations(axiom->getAnnotations(), "        ");
        xml_ << "    </owl:NamedIndividual>\n\n";
    }
}

void RDFXMLSerializer::Builder::writeObjectPropertyAssertion(const std::shared_ptr<ObjectPropertyAssertion>& axiom) {
    if (!axiom) return;
    
    auto prop_expr = axiom->getProperty();
    auto source = axiom->getSource();
    auto target = axiom->getTarget();
    
    std::string source_str = formatIndividual(source);
    std::string target_str = formatIndividual(target);
    
    if (std::holds_alternative<ObjectProperty>(prop_expr)) {
        auto prop = std::get<ObjectProperty>(prop_expr);
        std::string prop_qname = getQName(prop.getIRI());
        
        xml_ << "    <owl:NamedIndividual rdf:about=\"" << source_str << "\">\n";
        xml_ << "        <" << prop_qname << " rdf:resource=\"" << target_str << "\"/>\n";
        writeAnnotations(axiom->getAnnotations(), "        ");
        xml_ << "    </owl:NamedIndividual>\n\n";
    }
}

void RDFXMLSerializer::Builder::writeDataPropertyAssertion(const std::shared_ptr<DataPropertyAssertion>& axiom) {
    if (!axiom) return;
    
    auto prop = axiom->getProperty();
    auto source = axiom->getSource();
    auto target = axiom->getTarget();
    
    std::string source_str = formatIndividual(source);
    std::string prop_qname = getQName(prop.getIRI());
    std::string literal_str = formatLiteral(target);
    
    xml_ << "    <owl:NamedIndividual rdf:about=\"" << source_str << "\">\n";
    xml_ << "        <" << prop_qname << ">" << literal_str << "</" << prop_qname << ">\n";
    writeAnnotations(axiom->getAnnotations(), "        ");
    xml_ << "    </owl:NamedIndividual>\n\n";
}

// ============================================================================
// Annotation Axioms
// ============================================================================

void RDFXMLSerializer::Builder::writeAnnotationAssertion(const std::shared_ptr<AnnotationAssertion>& axiom) {
    if (!axiom) return;
    
    auto prop = axiom->getProperty();
    auto subject = axiom->getSubject();
    auto value = axiom->getValue();
    
    std::string subject_str;
    if (std::holds_alternative<IRI>(subject)) {
        subject_str = escapeXML(std::get<IRI>(subject).getFullIRI());
    } else {
        auto anon = std::get<AnonymousIndividual>(subject);
        subject_str = "_:" + anon.getNodeID();
    }
    
    std::string prop_qname = getQName(prop.getIRI());
    
    // Determine value format
    std::string value_str;
    bool is_resource = false;
    
    if (std::holds_alternative<IRI>(value)) {
        value_str = escapeXML(std::get<IRI>(value).getFullIRI());
        is_resource = true;
    } else if (std::holds_alternative<Literal>(value)) {
        value_str = formatLiteral(std::get<Literal>(value));
        is_resource = false;
    } else {
        auto anon = std::get<AnonymousIndividual>(value);
        value_str = "_:" + anon.getNodeID();
        is_resource = true;
    }
    
    xml_ << "    <rdf:Description rdf:about=\"" << subject_str << "\">\n";
    if (is_resource) {
        xml_ << "        <" << prop_qname << " rdf:resource=\"" << value_str << "\"/>\n";
    } else {
        xml_ << "        <" << prop_qname << ">" << value_str << "</" << prop_qname << ">\n";
    }
    writeAnnotations(axiom->getAnnotations(), "        ");
    xml_ << "    </rdf:Description>\n\n";
}

// ============================================================================
// Class Expression Serialization
// ============================================================================

void RDFXMLSerializer::Builder::writeClassExpression(const ClassExpressionPtr& expr, const std::string& indent) {
    if (!expr) return;
    
    std::string expr_type = expr->getExpressionType();
    
    if (expr_type == "NamedClass") {
        auto named = std::dynamic_pointer_cast<NamedClass>(expr);
        xml_ << indent << "<owl:Class rdf:about=\"" << escapeXML(named->getClass().getIRI().getFullIRI()) << "\"/>\n";
    }
    else if (expr_type == "ObjectIntersectionOf") {
        auto intersection = std::dynamic_pointer_cast<ObjectIntersectionOf>(expr);
        xml_ << indent << "<owl:Class>\n";
        xml_ << indent << "    <owl:intersectionOf rdf:parseType=\"Collection\">\n";
        for (const auto& operand : intersection->getOperands()) {
            writeClassExpression(operand, indent + "        ");
        }
        xml_ << indent << "    </owl:intersectionOf>\n";
        xml_ << indent << "</owl:Class>\n";
    }
    else if (expr_type == "ObjectUnionOf") {
        auto union_expr = std::dynamic_pointer_cast<ObjectUnionOf>(expr);
        xml_ << indent << "<owl:Class>\n";
        xml_ << indent << "    <owl:unionOf rdf:parseType=\"Collection\">\n";
        for (const auto& operand : union_expr->getOperands()) {
            writeClassExpression(operand, indent + "        ");
        }
        xml_ << indent << "    </owl:unionOf>\n";
        xml_ << indent << "</owl:Class>\n";
    }
    else if (expr_type == "ObjectSomeValuesFrom") {
        auto some = std::dynamic_pointer_cast<ObjectSomeValuesFrom>(expr);
        xml_ << indent << "<owl:Restriction>\n";
        xml_ << indent << "    <owl:onProperty rdf:resource=\"" << escapeXML(some->getProperty().getIRI().getFullIRI()) << "\"/>\n";
        xml_ << indent << "    <owl:someValuesFrom>\n";
        writeClassExpression(some->getFiller(), indent + "        ");
        xml_ << indent << "    </owl:someValuesFrom>\n";
        xml_ << indent << "</owl:Restriction>\n";
    }
    else if (expr_type == "ObjectAllValuesFrom") {
        auto all = std::dynamic_pointer_cast<ObjectAllValuesFrom>(expr);
        xml_ << indent << "<owl:Restriction>\n";
        xml_ << indent << "    <owl:onProperty rdf:resource=\"" << escapeXML(all->getProperty().getIRI().getFullIRI()) << "\"/>\n";
        xml_ << indent << "    <owl:allValuesFrom>\n";
        writeClassExpression(all->getFiller(), indent + "        ");
        xml_ << indent << "    </owl:allValuesFrom>\n";
        xml_ << indent << "</owl:Restriction>\n";
    }
}

// ============================================================================
// Helper Functions
// ============================================================================

std::string RDFXMLSerializer::Builder::escapeXML(const std::string& str) const {
    std::string result;
    result.reserve(str.size());
    
    for (char c : str) {
        switch (c) {
            case '&':  result += "&amp;"; break;
            case '<':  result += "&lt;"; break;
            case '>':  result += "&gt;"; break;
            case '"':  result += "&quot;"; break;
            case '\'': result += "&apos;"; break;
            default:   result += c; break;
        }
    }
    
    return result;
}

std::string RDFXMLSerializer::Builder::getQName(const IRI& iri) const {
    std::string full_iri = iri.getFullIRI();
    
    // Try to find a matching namespace
    for (const auto& [prefix, ns] : namespaces_) {
        if (full_iri.find(ns) == 0) {
            std::string local_name = full_iri.substr(ns.length());
            return prefix + ":" + local_name;
        }
    }
    
    // No prefix found, return full IRI
    return full_iri;
}

std::string RDFXMLSerializer::Builder::getNamespacePrefix(const std::string& ns) const {
    for (const auto& [prefix, namespace_uri] : namespaces_) {
        if (namespace_uri == ns) {
            return prefix;
        }
    }
    return "";
}

void RDFXMLSerializer::Builder::registerStandardNamespaces() {
    namespaces_["rdf"] = "http://www.w3.org/1999/02/22-rdf-syntax-ns#";
    namespaces_["rdfs"] = "http://www.w3.org/2000/01/rdf-schema#";
    namespaces_["owl"] = "http://www.w3.org/2002/07/owl#";
    namespaces_["xsd"] = "http://www.w3.org/2001/XMLSchema#";
    namespaces_["xml"] = "http://www.w3.org/XML/1998/namespace";
}

void RDFXMLSerializer::Builder::registerOntologyNamespaces() {
    auto prefix_map = ontology_.getPrefixMap();
    for (const auto& [prefix, ns] : prefix_map) {
        // Don't override standard namespaces
        if (namespaces_.find(prefix) == namespaces_.end()) {
            namespaces_[prefix] = ns;
        }
    }
}

std::string RDFXMLSerializer::Builder::formatLiteral(const Literal& literal) const {
    std::string lexical = escapeXML(literal.getLexicalForm());
    
    if (literal.hasLanguageTag()) {
        // Language-tagged literal - note: in RDF/XML, language tags are attributes
        // For content, we just return the escaped lexical form
        // The caller should handle the xml:lang attribute
        return lexical;
    } else if (literal.isTyped()) {
        auto datatype = literal.getDatatype();
        if (datatype.has_value()) {
            // Typed literal - caller should handle rdf:datatype attribute
            return lexical;
        }
    }
    
    return lexical;
}

std::string RDFXMLSerializer::Builder::formatIndividual(const Individual& individual) const {
    if (std::holds_alternative<NamedIndividual>(individual)) {
        auto named = std::get<NamedIndividual>(individual);
        return escapeXML(named.getIRI().getFullIRI());
    } else {
        auto anon = std::get<AnonymousIndividual>(individual);
        return "_:" + anon.getNodeID();
    }
}

std::string RDFXMLSerializer::Builder::getBlankNodeID() {
    return "genid" + std::to_string(++blank_node_counter_);
}

void RDFXMLSerializer::Builder::writeAnnotations(const std::vector<Annotation>& annotations, const std::string& indent) {
    for (const auto& annotation : annotations) {
        auto prop = annotation.getProperty();
        auto value = annotation.getValue();
        
        std::string prop_qname = getQName(prop.getIRI());
        
        if (std::holds_alternative<IRI>(value)) {
            auto iri = std::get<IRI>(value);
            xml_ << indent << "<" << prop_qname << " rdf:resource=\"" << escapeXML(iri.getFullIRI()) << "\"/>\n";
        } else if (std::holds_alternative<Literal>(value)) {
            auto lit = std::get<Literal>(value);
            std::string lit_str = formatLiteral(lit);
            
            if (lit.hasLanguageTag()) {
                xml_ << indent << "<" << prop_qname << " xml:lang=\"" << lit.getLanguageTag().value() << "\">" << lit_str << "</" << prop_qname << ">\n";
            } else if (lit.isTyped() && lit.getDatatype().has_value()) {
                xml_ << indent << "<" << prop_qname << " rdf:datatype=\"" << escapeXML(lit.getDatatype().value().getFullIRI()) << "\">" << lit_str << "</" << prop_qname << ">\n";
            } else {
                xml_ << indent << "<" << prop_qname << ">" << lit_str << "</" << prop_qname << ">\n";
            }
        } else {
            auto anon = std::get<AnonymousIndividual>(value);
            xml_ << indent << "<" << prop_qname << " rdf:nodeID=\"" << anon.getNodeID() << "\"/>\n";
        }
    }
}

} // namespace owl2
} // namespace ista
