Contributing to ista
====================

Thank you for your interest in contributing to ista! This guide will help you get started
with contributing code, documentation, bug reports, and feature requests.

Code of Conduct
---------------

Please be respectful and constructive in all interactions. We aim to maintain a welcoming
and inclusive community.

Ways to Contribute
------------------

There are many ways to contribute to ista:

- **Report bugs** and suggest features
- **Improve documentation** (fix typos, add examples, clarify instructions)
- **Write code** (fix bugs, implement features, add tests)
- **Review pull requests**
- **Share your use cases** and examples
- **Help other users** in discussions and issues

Getting Started
---------------

Development Environment Setup
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. **Fork and clone the repository**:

   .. code-block:: bash

       git clone https://github.com/YOUR_USERNAME/ista.git
       cd ista

2. **Create a virtual environment**:

   .. code-block:: bash

       python -m venv venv
       source venv/bin/activate  # On Windows: venv\Scripts\activate

3. **Install development dependencies**:

   .. code-block:: bash

       pip install -e .
       pip install -r requirements.txt
       pip install pytest pytest-cov black flake8 mypy

4. **Build C++ components** (if modifying C++ code):

   .. code-block:: bash

       mkdir build
       cd build
       cmake ..
       cmake --build .

5. **Run tests** to verify setup:

   .. code-block:: bash

       pytest tests/

Development Workflow
--------------------

1. **Create a new branch** for your work:

   .. code-block:: bash

       git checkout -b feature/my-new-feature
       # or
       git checkout -b fix/issue-123

2. **Make your changes** following the coding standards (see below)

3. **Write or update tests** for your changes

4. **Run tests** to ensure nothing breaks:

   .. code-block:: bash

       pytest tests/

5. **Format your code**:

   .. code-block:: bash

       black ista/ tests/
       flake8 ista/ tests/

6. **Commit your changes** with clear, descriptive messages:

   .. code-block:: bash

       git add .
       git commit -m "Add feature: describe what you added"

7. **Push to your fork** and **create a pull request**:

   .. code-block:: bash

       git push origin feature/my-new-feature

Coding Standards
----------------

Python Code Style
~~~~~~~~~~~~~~~~~

- Follow **PEP 8** style guidelines
- Use **Black** for automatic code formatting (line length: 88)
- Use **type hints** for function signatures
- Write **docstrings** for all public functions, classes, and modules
- Use **numpydoc** style for docstrings

Example:

.. code-block:: python

    def extract_neighborhood(
        self,
        seed_iri: IRI,
        depth: int = 2,
        include_superclasses: bool = True,
        include_subclasses: bool = True
    ) -> FilterResult:
        """Extract neighborhood around a seed IRI.

        Parameters
        ----------
        seed_iri : IRI
            The starting point for extraction
        depth : int, optional
            Maximum distance from seed (default: 2)
        include_superclasses : bool, optional
            Whether to include superclasses (default: True)
        include_subclasses : bool, optional
            Whether to include subclasses (default: True)

        Returns
        -------
        FilterResult
            The extraction result containing the subgraph

        Examples
        --------
        >>> filter_obj = OntologyFilter(ontology)
        >>> result = filter_obj.extract_neighborhood(disease_iri, depth=2)
        >>> subgraph = result.get_ontology()
        """
        # Implementation here
        pass

C++ Code Style
~~~~~~~~~~~~~~

- Follow **modern C++20** idioms
- Use **CamelCase** for class names
- Use **camelCase** for function and variable names
- Use **SCREAMING_SNAKE_CASE** for constants
- Use **smart pointers** (std::shared_ptr, std::unique_ptr) for memory management
- Include **doxygen comments** for all public APIs

Example:

.. code-block:: cpp

    /**
     * @brief Extract a neighborhood around a seed IRI
     *
     * @param seedIri The starting point for extraction
     * @param depth Maximum distance from seed
     * @param includeSuperclasses Whether to include superclasses
     * @return FilterResult The extraction result
     */
    FilterResult extractNeighborhood(
        const IRI& seedIri,
        int depth = 2,
        bool includeSuperclasses = true
    ) {
        // Implementation here
    }

Documentation
~~~~~~~~~~~~~

- Update documentation when adding or changing features
- Add examples to user guides when appropriate
- Keep docstrings synchronized with code
- Run documentation build to check for errors:

  .. code-block:: bash

      cd docs
      make clean
      make html

Testing Guidelines
------------------

Writing Tests
~~~~~~~~~~~~~

- Write tests for all new features
- Add regression tests for bug fixes
- Aim for high code coverage (>80%)
- Use descriptive test names
- Test both success and failure cases
- Test edge cases and boundary conditions

Test Structure:

.. code-block:: python

    import pytest
    from ista import owl2

    class TestOntologyFilter:
        """Tests for OntologyFilter class."""

        def setup_method(self):
            """Set up test fixtures."""
            self.ont = owl2.Ontology(owl2.IRI("http://test.org/ont"))
            # Add test data

        def test_extract_neighborhood_basic(self):
            """Test basic neighborhood extraction."""
            filter_obj = owl2.OntologyFilter(self.ont)
            result = filter_obj.extract_neighborhood(seed_iri, depth=1)

            assert result is not None
            assert isinstance(result, owl2.FilterResult)
            assert result.get_ontology().get_axiom_count() > 0

        def test_extract_neighborhood_depth_zero(self):
            """Test neighborhood extraction with depth=0."""
            filter_obj = owl2.OntologyFilter(self.ont)
            result = filter_obj.extract_neighborhood(seed_iri, depth=0)

            # Should only include the seed itself
            assert len(result.get_included_iris()) == 1

        def test_extract_neighborhood_invalid_iri(self):
            """Test extraction with non-existent IRI."""
            filter_obj = owl2.OntologyFilter(self.ont)
            invalid_iri = owl2.IRI("http://test.org/NonExistent")

            with pytest.raises(ValueError):
                filter_obj.extract_neighborhood(invalid_iri)

Running Tests
~~~~~~~~~~~~~

.. code-block:: bash

    # Run all tests
    pytest

    # Run specific test file
    pytest tests/test_ontology_filter.py

    # Run specific test
    pytest tests/test_ontology_filter.py::TestOntologyFilter::test_extract_neighborhood

    # Run with coverage
    pytest --cov=ista --cov-report=html

    # Run verbose
    pytest -v

C++ Testing
~~~~~~~~~~~

C++ tests use the same framework (pybind11 allows testing from Python):

.. code-block:: bash

    # C++ unit tests (if implemented)
    cd build
    ctest

Pull Request Guidelines
------------------------

Before Submitting
~~~~~~~~~~~~~~~~~

- Ensure all tests pass
- Update documentation if needed
- Add yourself to CONTRIBUTORS.md (if not already there)
- Check that code follows style guidelines
- Rebase on latest main branch if needed

Pull Request Description
~~~~~~~~~~~~~~~~~~~~~~~~~

Include in your PR description:

- **What** does this PR do?
- **Why** is this change needed?
- **How** does it work?
- **Testing**: How was this tested?
- **Related issues**: Link to related issues (Fixes #123)

Example PR template:

.. code-block:: markdown

    ## Description
    Adds neighborhood extraction with configurable depth to OntologyFilter.

    ## Motivation
    Users need to extract subgraphs around specific entities for focused analysis.

    ## Changes
    - Add `extract_neighborhood()` method to OntologyFilter
    - Add `depth` parameter to control extraction depth
    - Add directional parameters (superclasses, subclasses, properties)
    - Add tests for new functionality
    - Update user guide with examples

    ## Testing
    - Added unit tests in `tests/test_ontology_filter.py`
    - Tested with real-world ontology (Gene Ontology)
    - All existing tests still pass

    ## Fixes
    Fixes #42

Review Process
~~~~~~~~~~~~~~

1. **Automated checks** will run (tests, linting, coverage)
2. **Maintainer review**: One or more maintainers will review your code
3. **Address feedback**: Make requested changes if any
4. **Approval**: Once approved, a maintainer will merge your PR

Reporting Bugs
--------------

Before Reporting
~~~~~~~~~~~~~~~~

- Check if the bug has already been reported
- Try to reproduce with latest version
- Collect relevant information (OS, Python version, ista version)

Bug Report Template
~~~~~~~~~~~~~~~~~~~

When reporting a bug, include:

.. code-block:: markdown

    **Describe the bug**
    A clear description of what the bug is.

    **To Reproduce**
    Steps to reproduce:
    1. Load ontology '...'
    2. Call method '...'
    3. See error

    **Expected behavior**
    What you expected to happen.

    **Actual behavior**
    What actually happened.

    **Error messages**
    ```
    Full error message and traceback
    ```

    **Environment**
    - OS: [e.g., Ubuntu 22.04]
    - Python version: [e.g., 3.10.5]
    - ista version: [e.g., 0.1.0]
    - Installation method: [pip, source]

    **Additional context**
    Any other relevant information.

Requesting Features
-------------------

Feature Request Template
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: markdown

    **Feature description**
    Clear description of the proposed feature.

    **Use case**
    Why is this feature needed? What problem does it solve?

    **Proposed solution**
    How should this feature work?

    **Alternatives considered**
    Other approaches you've considered.

    **Additional context**
    Examples, mockups, or references.

Community Guidelines
--------------------

Communication Channels
~~~~~~~~~~~~~~~~~~~~~~

- **GitHub Issues**: Bug reports, feature requests
- **GitHub Discussions**: Questions, ideas, general discussion
- **Pull Requests**: Code contributions

Best Practices
~~~~~~~~~~~~~~

- Be respectful and constructive
- Search before posting to avoid duplicates
- Provide clear, detailed information
- Stay on topic
- Help others when you can

Recognition
-----------

Contributors are recognized in:

- CONTRIBUTORS.md file
- Release notes
- Documentation credits

Project Structure
-----------------

Understanding the codebase:

.. code-block:: text

    ista/
    ├── lib/                  # C++ library
    │   └── owl2/             # OWL2 implementation
    │       ├── iri.hpp
    │       ├── literal.hpp
    │       ├── ontology.hpp
    │       └── ...
    ├── ista/                 # Python package
    │   ├── __init__.py
    │   ├── owl2.py           # Python bindings
    │   ├── converters.py     # Graph converters
    │   ├── database_parser.py
    │   └── graph.py
    ├── src/                  # Executables
    │   └── ista.cpp          # Main C++ program
    ├── tests/                # Test suite
    │   ├── test_owl2.py
    │   ├── test_converters.py
    │   └── ...
    ├── docs/                 # Documentation
    │   ├── source/           # Sphinx source
    │   └── Doxyfile          # Doxygen config
    ├── examples/             # Example projects
    │   └── projects/
    └── requirements.txt

Key Files to Know
~~~~~~~~~~~~~~~~~

- **lib/owl2/**: Core C++ OWL2 implementation
- **ista/owl2.py**: Python bindings and interface
- **tests/**: Test suite
- **docs/source/**: Documentation source
- **setup.py**: Python package configuration
- **CMakeLists.txt**: C++ build configuration

Getting Help
------------

If you need help:

1. Check the **documentation** (this site)
2. Search **existing issues** on GitHub
3. Ask in **GitHub Discussions**
4. Create a **new issue** if needed

Resources
---------

- **OWL2 Specification**: https://www.w3.org/TR/owl2-overview/
- **Python Packaging**: https://packaging.python.org/
- **CMake Documentation**: https://cmake.org/documentation/
- **pybind11**: https://pybind11.readthedocs.io/

Thank You!
----------

Your contributions make ista better for everyone. Thank you for being part of the community!
