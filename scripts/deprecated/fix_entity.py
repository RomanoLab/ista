#!/usr/bin/env python3
import re

# Read the corrupted file
with open('lib/owl2/core/entity.hpp', 'r') as f:
    content = f.read()

# Find the namespace std section and extract everything before it
main_part = content.split('// Hash functions for entities')[0]
main_part += '''// Hash functions for entities
namespace std {
    template<>
    struct hash<ista::owl2::Class> {
        size_t operator()(const ista::owl2::Class& c) const {
            return hash<ista::owl2::IRI>()(c.getIRI());
        }
    };
    
    template<>
    struct hash<ista::owl2::Datatype> {
        size_t operator()(const ista::owl2::Datatype& dt) const {
            return hash<ista::owl2::IRI>()(dt.getIRI());
        }
    };
    
    template<>
    struct hash<ista::owl2::ObjectProperty> {
        size_t operator()(const ista::owl2::ObjectProperty& op) const {
            return hash<ista::owl2::IRI>()(op.getIRI());
        }
    };
    
    template<>
    struct hash<ista::owl2::DataProperty> {
        size_t operator()(const ista::owl2::DataProperty& dp) const {
            return hash<ista::owl2::IRI>()(dp.getIRI());
        }
    };
    
    template<>
    struct hash<ista::owl2::AnnotationProperty> {
        size_t operator()(const ista::owl2::AnnotationProperty& ap) const {
            return hash<ista::owl2::IRI>()(ap.getIRI());
        }
    };
    
    template<>
    struct hash<ista::owl2::NamedIndividual> {
        size_t operator()(const ista::owl2::NamedIndividual& ni) const {
            return hash<ista::owl2::IRI>()(ni.getIRI());
        }
    };
    
    template<>
    struct hash<ista::owl2::AnonymousIndividual> {
        size_t operator()(const ista::owl2::AnonymousIndividual& ai) const {
            return hash<string>()(ai.getNodeID());
        }
    };
}

#endif // ISTA_OWL2_ENTITY_HPP
'''

with open('lib/owl2/core/entity.hpp', 'w') as f:
    f.write(main_part)

print("Fixed entity.hpp")
