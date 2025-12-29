#!/bin/bash

# Setup script for ISTA GUI dependencies
# This script downloads Dear ImGui and GLFW if they are not already present

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
EXTERNAL_DIR="$SCRIPT_DIR/../external"

mkdir -p "$EXTERNAL_DIR"
cd "$EXTERNAL_DIR"

echo "Setting up ISTA GUI dependencies..."

# Download Dear ImGui
if [ ! -d "imgui" ]; then
    echo "Downloading Dear ImGui..."
    git clone https://github.com/ocornut/imgui.git
    cd imgui
    # Use a stable release tag
    git checkout v1.90.4
    cd ..
    echo "Dear ImGui downloaded successfully"
else
    echo "Dear ImGui already exists, skipping download"
fi

# Download GLFW
if [ ! -d "glfw" ]; then
    echo "Downloading GLFW..."
    git clone https://github.com/glfw/glfw.git
    cd glfw
    # Use a stable release tag
    git checkout 3.4
    cd ..
    echo "GLFW downloaded successfully"
else
    echo "GLFW already exists, skipping download"
fi

# Download Native File Dialog
if [ ! -d "nfd" ]; then
    echo "Downloading Native File Dialog..."
    git clone https://github.com/btzy/nativefiledialog-extended.git nfd
    echo "Native File Dialog downloaded successfully"
else
    echo "Native File Dialog already exists, skipping download"
fi

echo ""
echo "Dependencies setup complete!"
echo ""
echo "To build the GUI application:"
echo "  mkdir -p build && cd build"
echo "  cmake .."
echo "  cmake --build ."
echo ""
echo "The executable will be: build/gui/ista_gui"
