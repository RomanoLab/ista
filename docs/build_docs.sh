#!/bin/bash
# Build documentation for ista project
# This script builds both C++ (Doxygen) and Python (Sphinx) documentation

set -e  # Exit on error

echo "Building ista documentation..."

# Navigate to docs directory
cd "$(dirname "$0")"

# Step 1: Generate C++ documentation with Doxygen
echo "Step 1/2: Generating C++ API documentation with Doxygen..."
if command -v doxygen &> /dev/null; then
    doxygen Doxyfile
    echo "Doxygen documentation generated successfully."
else
    echo "Warning: Doxygen not found. Skipping C++ documentation generation."
    echo "Install Doxygen to generate C++ API documentation."
fi

# Step 2: Build Sphinx documentation
echo "Step 2/2: Building Sphinx documentation..."
if command -v sphinx-build &> /dev/null; then
    sphinx-build -b html source build/html
    echo "Sphinx documentation built successfully."
    echo "Documentation available at: build/html/index.html"
else
    echo "Error: sphinx-build not found. Please install Sphinx:"
    echo "  pip install -r ../requirements.txt"
    exit 1
fi

echo ""
echo "Documentation build complete!"
echo "Open build/html/index.html in your browser to view the documentation."
