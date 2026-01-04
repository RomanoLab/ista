#!/bin/bash
# Complete clean build script for ISTA GUI

set -e  # Exit on error

PROJECT_DIR="/Users/jdr2160/projects/ista"
cd "$PROJECT_DIR"

echo "========================================="
echo "ISTA GUI - Complete Clean Build Script"
echo "========================================="
echo ""

echo "=== Step 1: Downloading dependencies ==="
echo ""

# Download pugixml
if [ ! -f "external/pugixml/src/pugixml.cpp" ]; then
    echo "Downloading pugixml..."
    cd external/pugixml
    git clone https://github.com/zeux/pugixml.git .
    cd ../..
    echo "✓ pugixml downloaded"
else
    echo "✓ pugixml already exists"
fi

# Download ImGui
if [ ! -f "external/imgui/imgui.cpp" ]; then
    echo "Downloading Dear ImGui..."
    cd external
    git clone https://github.com/ocornut/imgui.git
    cd imgui
    git checkout v1.90.4
    cd ../..
    echo "✓ Dear ImGui downloaded"
else
    echo "✓ Dear ImGui already exists"
fi

# Download GLFW
if [ ! -f "external/glfw/CMakeLists.txt" ]; then
    echo "Downloading GLFW..."
    cd external
    git clone https://github.com/glfw/glfw.git
    cd glfw
    git checkout 3.4
    cd ../..
    echo "✓ GLFW downloaded"
else
    echo "✓ GLFW already exists"
fi

# Download Native File Dialog
if [ ! -f "external/nfd/src/include/nfd.h" ]; then
    echo "Downloading Native File Dialog..."
    cd external
    git clone https://github.com/btzy/nativefiledialog-extended.git nfd
    cd ..
    echo "✓ Native File Dialog downloaded"
else
    echo "✓ Native File Dialog already exists"
fi

echo ""
echo "=== Step 2: Cleaning previous build ==="
rm -rf build
mkdir build
echo "✓ Build directory cleaned"

echo ""
echo "=== Step 3: Configuring with CMake ==="
cd build
cmake .. -DBUILD_PYTHON_BINDINGS=OFF -DBUILD_GUI=ON
echo "✓ CMake configuration complete"

echo ""
echo "=== Step 4: Building ==="
cmake --build . 2>&1 | tee build.log
BUILD_STATUS=$?

echo ""
echo "========================================="
if [ $BUILD_STATUS -eq 0 ]; then
    echo "✓ BUILD SUCCESSFUL!"
    echo "========================================="
    echo ""
    echo "Executable location: $PROJECT_DIR/build/gui/ista_gui"
    ls -lh gui/ista_gui
    echo ""
    echo "To run the GUI:"
    echo "  ./build/gui/ista_gui"
    echo ""
else
    echo "✗ BUILD FAILED"
    echo "========================================="
    echo ""
    echo "Check build.log for errors:"
    echo "  tail -50 build/build.log"
    echo ""
    exit 1
fi
