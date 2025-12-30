# Code conventions
- Always aim to implement complex functions in C++ with Python bindings
- Prefer native implementation of new features over using external libraries where reasonable
- All Python examples should use `ista.owl2` over `_libista_owl2`
- Prefer biomedical examples when possible, and when implementation decisions are encountered, prefer choices that are more suitable for biomedical data/knowledge
- Create good docstrings that will be compiled by sphinx (numpydoc for Python, doxygen for C++)

# Repository preferences
- Don't make a new markdown file every time you perform a new type of action - these just pollute the codebase and need to be removed down the road.

# Testing requirements
- Code coverage is a requirement, not just something that is good to have. Every line of executable code must be covered by tests.
