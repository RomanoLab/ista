# ISTA OWL2 Variant Types Reference

This document provides a quick reference for handling variant types in the ISTA OWL2 C++ library.

## Overview

The ISTA OWL2 library uses `std::variant` extensively to represent OWL2's flexible type system. When working with these types, you must check which alternative is active before accessing the value.

## Key Variant Types

### 1. Individual

```cpp
using Individual = std::variant<NamedIndividual, AnonymousIndividual>;
```

**Usage:**
```cpp
Individual ind = /* ... */;

if (std::holds_alternative<NamedIndividual>(ind)) {
    NamedIndividual named = std::get<NamedIndividual>(ind);
    std::string iri = named.getIRI().toString();
} else if (std::holds_alternative<AnonymousIndividual>(ind)) {
    AnonymousIndividual anon = std::get<AnonymousIndividual>(ind);
    std::string nodeId = anon.getNodeID();
}
```

**Example:** ObjectPropertyAssertion source and target
```cpp
auto assertion = /* ObjectPropertyAssertion */;
Individual source = assertion->getSource();
Individual target = assertion->getTarget();
```

### 2. ObjectPropertyExpression

```cpp
using ObjectPropertyExpression = std::variant<ObjectProperty, std::pair<ObjectProperty, bool>>;
```

The `bool` in the pair indicates whether it's an inverse property.

**Usage:**
```cpp
ObjectPropertyExpression prop_expr = /* ... */;

if (std::holds_alternative<ObjectProperty>(prop_expr)) {
    // Regular property
    ObjectProperty prop = std::get<ObjectProperty>(prop_expr);
    std::string iri = prop.getIRI().toString();
} else {
    // Inverse property
    auto pair = std::get<std::pair<ObjectProperty, bool>>(prop_expr);
    ObjectProperty prop = pair.first;
    bool isInverse = pair.second;
    std::string label = isInverse ? "inv(" + prop.getIRI().getAbbreviated() + ")" 
                                   : prop.getIRI().getAbbreviated();
}
```

**Example:** ObjectPropertyAssertion property
```cpp
auto assertion = /* ObjectPropertyAssertion */;
ObjectPropertyExpression prop_expr = assertion->getProperty();
```

### 3. ClassExpression

Class expressions in OWL2 can be complex nested structures. The base type is:

```cpp
using ClassExpressionPtr = std::shared_ptr<ClassExpression>;
```

Common subclasses:
- `NamedClass` - A simple class by IRI
- `ObjectIntersectionOf` - Intersection of classes
- `ObjectUnionOf` - Union of classes  
- `ObjectSomeValuesFrom` - Existential restriction
- `ObjectAllValuesFrom` - Universal restriction

**Usage:**
```cpp
ClassExpressionPtr expr = /* ... */;

// Use dynamic_pointer_cast to check type
if (auto named = std::dynamic_pointer_cast<NamedClass>(expr)) {
    Class cls = named->getClass();
    std::string iri = cls.getIRI().toString();
} else if (auto intersection = std::dynamic_pointer_cast<ObjectIntersectionOf>(expr)) {
    auto operands = intersection->getOperands();
    // Process operands...
}
```

### 4. AnnotationValue

```cpp
using AnnotationValue = std::variant<IRI, Literal, AnonymousIndividual>;
```

**Usage:**
```cpp
AnnotationValue value = /* ... */;

if (std::holds_alternative<IRI>(value)) {
    IRI iri = std::get<IRI>(value);
    std::string str = iri.toString();
} else if (std::holds_alternative<Literal>(value)) {
    Literal lit = std::get<Literal>(value);
    std::string lexical = lit.getLexicalForm();
} else if (std::holds_alternative<AnonymousIndividual>(value)) {
    AnonymousIndividual anon = std::get<AnonymousIndividual>(value);
    std::string nodeId = anon.getNodeID();
}
```

## Common Patterns

### Pattern 1: Extract Named Individuals Only

When you only care about named individuals (not anonymous):

```cpp
Individual ind = assertion->getSource();

if (std::holds_alternative<NamedIndividual>(ind)) {
    NamedIndividual named = std::get<NamedIndividual>(ind);
    // Process named individual
} else {
    // Skip anonymous individuals
    return;
}
```

### Pattern 2: Extract Simple Properties Only

When you only care about regular properties (not inverse):

```cpp
ObjectPropertyExpression prop_expr = assertion->getProperty();

if (std::holds_alternative<ObjectProperty>(prop_expr)) {
    ObjectProperty prop = std::get<ObjectProperty>(prop_expr);
    // Process regular property
} else {
    // Handle or skip inverse properties
    auto pair = std::get<std::pair<ObjectProperty, bool>>(prop_expr);
    // pair.first is the property, pair.second is true for inverse
}
```

### Pattern 3: Extract Named Classes from Class Expressions

When you only want simple named classes:

```cpp
ClassExpressionPtr expr = axiom->getSubClass();

if (auto named = std::dynamic_pointer_cast<NamedClass>(expr)) {
    Class cls = named->getClass();
    std::string iri = cls.getIRI().toString();
} else {
    // Skip complex class expressions
    return;
}
```

## Best Practices

### 1. Always Check Before Accessing

```cpp
// ❌ WRONG - will throw if wrong type
auto named = std::get<NamedIndividual>(ind);

// ✅ CORRECT - check first
if (std::holds_alternative<NamedIndividual>(ind)) {
    auto named = std::get<NamedIndividual>(ind);
}
```

### 2. Use Structured Bindings (C++17+)

```cpp
// For pairs in variants
if (!std::holds_alternative<ObjectProperty>(prop_expr)) {
    auto [prop, isInverse] = std::get<std::pair<ObjectProperty, bool>>(prop_expr);
    // Use prop and isInverse
}
```

### 3. Handle All Cases

```cpp
// Consider what to do with each variant alternative
if (std::holds_alternative<NamedIndividual>(ind)) {
    // Handle named
} else if (std::holds_alternative<AnonymousIndividual>(ind)) {
    // Handle anonymous  
} else {
    // This should never happen, but be defensive
    throw std::runtime_error("Unknown Individual type");
}
```

### 4. Use std::visit for Complex Logic

For more complex variant handling:

```cpp
std::visit([](auto&& arg) {
    using T = std::decay_t<decltype(arg)>;
    if constexpr (std::is_same_v<T, NamedIndividual>) {
        // Handle NamedIndividual
    } else if constexpr (std::is_same_v<T, AnonymousIndividual>) {
        // Handle AnonymousIndividual
    }
}, individual);
```

## Complete Example: Processing Object Property Assertions

```cpp
auto assertion_axioms = ontology->getAssertionAxioms();

for (const auto& axiom : assertion_axioms) {
    if (axiom->getAxiomType() == "ObjectPropertyAssertion") {
        auto obj_prop_axiom = std::dynamic_pointer_cast<ObjectPropertyAssertion>(axiom);
        if (!obj_prop_axiom) continue;
        
        // Get source and target (Individual variants)
        Individual source = obj_prop_axiom->getSource();
        Individual target = obj_prop_axiom->getTarget();
        
        // Only process named individuals
        if (!std::holds_alternative<NamedIndividual>(source) ||
            !std::holds_alternative<NamedIndividual>(target)) {
            continue; // Skip anonymous individuals
        }
        
        NamedIndividual source_ind = std::get<NamedIndividual>(source);
        NamedIndividual target_ind = std::get<NamedIndividual>(target);
        
        // Get property (ObjectPropertyExpression variant)
        ObjectPropertyExpression prop_expr = obj_prop_axiom->getProperty();
        std::string prop_label;
        
        if (std::holds_alternative<ObjectProperty>(prop_expr)) {
            // Regular property
            ObjectProperty prop = std::get<ObjectProperty>(prop_expr);
            prop_label = prop.getIRI().getAbbreviated();
        } else {
            // Inverse property
            auto [prop, isInverse] = std::get<std::pair<ObjectProperty, bool>>(prop_expr);
            prop_label = "inv(" + prop.getIRI().getAbbreviated() + ")";
        }
        
        // Now we have named individuals and property label
        std::cout << source_ind.getIRI().getAbbreviated() << " "
                  << prop_label << " "
                  << target_ind.getIRI().getAbbreviated() << std::endl;
    }
}
```

## Required Includes

```cpp
#include <variant>     // For std::variant, std::holds_alternative, std::get
#include <memory>      // For std::shared_ptr, std::dynamic_pointer_cast
#include <utility>     // For std::pair
```

## Debugging Tips

### Print Variant Index

```cpp
Individual ind = /* ... */;
std::cout << "Variant index: " << ind.index() << std::endl;
// 0 = NamedIndividual, 1 = AnonymousIndividual
```

### Check All Alternatives

```cpp
if (std::holds_alternative<NamedIndividual>(ind)) {
    std::cout << "It's a NamedIndividual" << std::endl;
} else if (std::holds_alternative<AnonymousIndividual>(ind)) {
    std::cout << "It's an AnonymousIndividual" << std::endl;
} else {
    std::cout << "Unknown type! Index: " << ind.index() << std::endl;
}
```

## Common Errors and Solutions

### Error: `std::bad_variant_access`

**Cause:** Trying to `std::get<T>` a variant that doesn't hold type `T`

**Solution:** Always use `std::holds_alternative<T>` before `std::get<T>`

### Error: `no member named 'getIRI'` on variant

**Cause:** Calling methods directly on a variant without extracting the value

**Solution:** Extract the value first:
```cpp
// ❌ WRONG
prop_expr.getIRI()  // prop_expr is a variant

// ✅ CORRECT  
if (std::holds_alternative<ObjectProperty>(prop_expr)) {
    auto prop = std::get<ObjectProperty>(prop_expr);
    prop.getIRI()  // Now we can call methods
}
```

### Error: Template argument deduction failed

**Cause:** Complex nested variant types confuse the compiler

**Solution:** Use explicit type names:
```cpp
std::pair<ObjectProperty, bool> pair = 
    std::get<std::pair<ObjectProperty, bool>>(prop_expr);
```

## Summary

When working with ISTA OWL2:
1. ✅ Always include `<variant>`
2. ✅ Check type with `std::holds_alternative<T>()` before accessing
3. ✅ Extract value with `std::get<T>()`
4. ✅ Handle all variant alternatives or explicitly skip unwanted ones
5. ✅ Use `std::dynamic_pointer_cast` for class expression hierarchies
6. ✅ Be defensive - check for null pointers and invalid variant states

This ensures type-safe, crash-free code when working with OWL2's flexible type system!
