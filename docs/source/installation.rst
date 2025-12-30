Installation
============

This guide covers installation of ista for different use cases.

Requirements
------------

Python Requirements
~~~~~~~~~~~~~~~~~~~

* Python 3.7 or higher
* pip (Python package manager)

C++ Requirements (for building from source)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* C++20 compatible compiler:

  * GCC 10+ (Linux)
  * Clang 12+ (macOS)
  * MSVC 2019+ (Windows)

* CMake 3.15 or higher
* Git (for submodules)

Installing from Source
----------------------

Basic Installation
~~~~~~~~~~~~~~~~~~

Install the Python package and build the C++ extension:

.. code-block:: bash

   git clone https://github.com/JDRomano2/ista.git
   cd ista
   pip install -e .

This will:

1. Initialize git submodules (pybind11, pugixml)
2. Build the C++ extension
3. Install the Python package in development mode

Custom Build Options
~~~~~~~~~~~~~~~~~~~~

Build with specific Python version:

.. code-block:: bash

   python3.9 -m pip install -e .

Build in Release mode (faster):

.. code-block:: bash

   CMAKE_BUILD_TYPE=Release pip install -e .

Force rebuild:

.. code-block:: bash

   pip install -e . --force-reinstall --no-cache-dir

Manual Build
~~~~~~~~~~~~

If you prefer to build manually:

.. code-block:: bash

   # Clone and initialize submodules
   git clone https://github.com/JDRomano2/ista.git
   cd ista
   git submodule update --init --recursive

   # Build C++ library and Python extension
   mkdir build && cd build
   cmake .. -DBUILD_PYTHON_BINDINGS=ON
   cmake --build . --config Release

   # Install Python package
   cd ..
   pip install -e .

Dependencies
------------

Python Dependencies
~~~~~~~~~~~~~~~~~~~

Core dependencies (automatically installed):

.. code-block:: text

   pandas         # Data manipulation
   openpyxl       # Excel file support
   tqdm           # Progress bars

Optional dependencies:

.. code-block:: bash

   # For graph analysis
   pip install networkx igraph

   # For Neo4j support
   pip install neo4j

Documentation Dependencies
~~~~~~~~~~~~~~~~~~~~~~~~~~

To build documentation:

.. code-block:: bash

   pip install sphinx furo numpydoc breathe sphinx-autodoc-typehints

C++ Dependencies
~~~~~~~~~~~~~~~~

The C++ library has minimal external dependencies:

* **pybind11** - Python bindings (included as submodule)
* **pugixml** - XML parsing (included as submodule)

Both are automatically fetched via git submodules.

Verifying Installation
-----------------------

Check Python Package
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import ista
   from ista import owl2

   # Check if C++ bindings are available
   if owl2.is_available():
       print("✓ C++ OWL2 library available")

       # Create a simple ontology
       ont = owl2.Ontology(owl2.IRI("http://test.org/test"))
       print(f"✓ Created ontology: {ont.get_ontology_iri().get_full_iri()}")
   else:
       print("✗ C++ library not available. Rebuild with: pip install -e .")

Run Tests
~~~~~~~~~

.. code-block:: bash

   # Run all tests
   python tests/test_simple_bindings.py
   python tests/test_parser.py
   python tests/test_subgraph.py

Troubleshooting
---------------

C++ Extension Not Building
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Error**: ``error: Microsoft Visual C++ 14.0 or greater is required``

**Solution (Windows)**: Install Visual Studio Build Tools from https://visualstudio.microsoft.com/downloads/

**Error**: ``fatal error: pybind11/pybind11.h: No such file or directory``

**Solution**: Initialize git submodules:

.. code-block:: bash

   git submodule update --init --recursive

C++ Extension Not Loading
~~~~~~~~~~~~~~~~~~~~~~~~~~

**Error**: ``ImportError: DLL load failed``

**Solution**: Ensure you have the correct Visual C++ Redistributable installed.

**Error**: ``owl2.is_available() returns False``

**Solution**: Rebuild the extension:

.. code-block:: bash

   pip install -e . --force-reinstall

Build Errors on Linux
~~~~~~~~~~~~~~~~~~~~~

**Error**: ``error: 'filesystem' is not a namespace-name``

**Solution**: Update GCC to version 10 or higher, or link against libstdc++fs:

.. code-block:: bash

   export LDFLAGS="-lstdc++fs"
   pip install -e .

Platform-Specific Notes
-----------------------

Windows
~~~~~~~

* Use PowerShell or Command Prompt (not Git Bash for building)
* Ensure Visual Studio Build Tools are in PATH
* Use ``python`` instead of ``python3``

macOS
~~~~~

* Install Xcode Command Line Tools: ``xcode-select --install``
* Use Homebrew for CMake: ``brew install cmake``

Linux
~~~~~

* Install build essentials: ``sudo apt install build-essential cmake``
* Install Python development headers: ``sudo apt install python3-dev``

Next Steps
----------

* :doc:`getting_started` - Quick start guide
* :doc:`user_guide/index` - Comprehensive user guide
* :doc:`examples` - Example programs
