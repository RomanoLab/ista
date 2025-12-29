# ISTA GUI - Complete Build Instructions

Step-by-step instructions to build the ISTA GUI application from scratch.

## Prerequisites

### Required Software
- **CMake 3.15+**: `brew install cmake` or download from https://cmake.org
- **C++20 Compiler**: Xcode Command Line Tools or full Xcode
  ```bash
  xcode-select --install
  ```
- **Git**: Usually comes with Xcode Command Line Tools

### Check Your Setup
```bash
cmake --version        # Should be 3.15 or higher
c++ --version         # Should support C++20
git --version
```

## Step 1: Download Dependencies

The GUI requires two external libraries that are not included in the repo:

### 1.1 Download pugixml (XML parser)
```bash
cd /Users/jdr2160/projects/ista/external/pugixml
git clone https://github.com/zeux/pugixml.git .
```

Verify:
```bash
ls /Users/jdr2160/projects/ista/external/pugixml/src/
# Should show: pugiconfig.hpp  pugixml.cpp  pugixml.hpp
```

### 1.2 Download Dear ImGui and GLFW (GUI libraries)

Run the setup script:
```bash
cd /Users/jdr2160/projects/ista/gui
./setup_dependencies.sh
```

Or manually:
```bash
cd /Users/jdr2160/projects/ista/external

# Download Dear ImGui
git clone https://github.com/ocornut/imgui.git
cd imgui
git checkout v1.90.4
cd ..

# Download GLFW
git clone https://github.com/glfw/glfw.git
cd glfw
git checkout 3.4
cd ..
```

Verify:
```bash
ls /Users/jdr2160/projects/ista/external/imgui/
# Should show: imgui.cpp  imgui.h  backends/  etc.

ls /Users/jdr2160/projects/ista/external/glfw/
# Should show: CMakeLists.txt  include/  src/  etc.
```

### 1.3 Install System GLFW (Recommended Alternative)

If you have SDK/linker issues, use system GLFW instead:
```bash
brew install glfw
```

## Step 2: Clean Previous Builds

Start fresh to avoid any cached configuration issues:

```bash
cd /Users/jdr2160/projects/ista
rm -rf build
mkdir build
```

## Step 3: Configure with CMake

```bash
cd build
cmake .. -DBUILD_PYTHON_BINDINGS=OFF -DBUILD_GUI=ON
```

**Expected output:**
```
-- Library sources: ...
-- Added pugixml from: /Users/jdr2160/projects/ista/lib/../external/pugixml
-- Executable sources: ...
-- ISTA GUI will be built
-- Configuring done
-- Generating done
```

**Common configuration errors and fixes:**

### Error: "pugixml not found"
```bash
# Download pugixml (see Step 1.1)
cd /Users/jdr2160/projects/ista/external/pugixml
git clone https://github.com/zeux/pugixml.git .
```

### Error: "Dear ImGui not found"
```bash
# Download ImGui (see Step 1.2)
cd /Users/jdr2160/projects/ista/external
git clone https://github.com/ocornut/imgui.git
cd imgui
git checkout v1.90.4
```

### Error: "Could NOT find OpenGL"
This is a macOS-specific issue. The CMakeLists.txt should handle it, but if not:
```bash
# Install GLFW via Homebrew
brew install glfw
```

### Error: "pybind11 not found"
This is normal if you disabled Python bindings. Ignore or install pybind11:
```bash
pip install pybind11
```

## Step 4: Build

```bash
cd /Users/jdr2160/projects/ista/build
cmake --build .
```

**Build process:**
```
[  3%] Building CXX object lib/CMakeFiles/libista.dir/...
...
[ 50%] Linking CXX static library libista.a
[ 50%] Built target libista
...
[ 70%] Building CXX object gui/CMakeFiles/ista_gui.dir/...
...
[100%] Linking CXX executable ista_gui
[100%] Built target ista_gui
```

**Common build errors and fixes:**

### Error: "ld: library 'libista' not found"

**Cause:** CMake cache issue or incorrect build order.

**Fix:**
```bash
# Clean everything and rebuild
cd /Users/jdr2160/projects/ista
rm -rf build
mkdir build
cd build

# Reconfigure
cmake .. -DBUILD_PYTHON_BINDINGS=OFF -DBUILD_GUI=ON

# Build
cmake --build .
```

### Error: "fatal error: 'pugixml.hpp' file not found"

**Cause:** pugixml not downloaded or CMake didn't detect it.

**Fix:**
```bash
# Ensure pugixml is downloaded
ls /Users/jdr2160/projects/ista/external/pugixml/src/pugixml.cpp

# If missing, download it
cd /Users/jdr2160/projects/ista/external/pugixml
git clone https://github.com/zeux/pugixml.git .

# Reconfigure CMake
cd /Users/jdr2160/projects/ista/build
rm CMakeCache.txt
cmake .. -DBUILD_PYTHON_BINDINGS=OFF -DBUILD_GUI=ON
cmake --build .
```

### Error: "ld: library 'System' not found"

**Cause:** macOS SDK issue (system-level problem).

**Fix:** Use system GLFW instead of bundled:
```bash
brew install glfw

# Clean and rebuild
cd /Users/jdr2160/projects/ista
rm -rf build
mkdir build
cd build
cmake .. -DBUILD_PYTHON_BINDINGS=OFF -DBUILD_GUI=ON
cmake --build .
```

### Error: "ImGuiConfigFlags_DockingEnable" not found

**Cause:** This should already be fixed in the code. If you still see it:

**Fix:** Make sure you have the latest version of kg_editor.cpp:
```bash
cd /Users/jdr2160/projects/ista/gui/src
grep "ImGuiConfigFlags_DockingEnable" kg_editor.cpp

# Should be commented out:
# // io.ConfigFlags |= ImGuiConfigFlags_DockingEnable;
```

## Step 5: Verify Build

Check that the executable was created:

```bash
ls -lh /Users/jdr2160/projects/ista/build/gui/ista_gui
```

Expected output:
```
-rwxr-xr-x  1 user  staff   3.8M Dec 26 12:59 /Users/jdr2160/projects/ista/build/gui/ista_gui
```

## Step 6: Test Run

```bash
# Run the GUI (no arguments)
/Users/jdr2160/projects/ista/build/gui/ista_gui
```

You should see a window titled "ISTA Knowledge Graph Editor" with:
- Menu bar (File, View, Data, Help)
- Empty graph view (gray background with grid)
- Properties panel
- Data Sources panel

## Complete Clean Build Script

If you want to automate the entire process:

```bash
#!/bin/bash
# Complete clean build script

set -e  # Exit on error

PROJECT_DIR="/Users/jdr2160/projects/ista"
cd "$PROJECT_DIR"

echo "=== Step 1: Downloading dependencies ==="

# Download pugixml
if [ ! -f "external/pugixml/src/pugixml.cpp" ]; then
    echo "Downloading pugixml..."
    cd external/pugixml
    git clone https://github.com/zeux/pugixml.git .
    cd ../..
else
    echo "pugixml already exists"
fi

# Download ImGui
if [ ! -f "external/imgui/imgui.cpp" ]; then
    echo "Downloading Dear ImGui..."
    cd external
    git clone https://github.com/ocornut/imgui.git
    cd imgui
    git checkout v1.90.4
    cd ../..
else
    echo "Dear ImGui already exists"
fi

# Download GLFW
if [ ! -f "external/glfw/CMakeLists.txt" ]; then
    echo "Downloading GLFW..."
    cd external
    git clone https://github.com/glfw/glfw.git
    cd glfw
    git checkout 3.4
    cd ../..
else
    echo "GLFW already exists"
fi

echo "=== Step 2: Cleaning previous build ==="
rm -rf build
mkdir build

echo "=== Step 3: Configuring with CMake ==="
cd build
cmake .. -DBUILD_PYTHON_BINDINGS=OFF -DBUILD_GUI=ON

echo "=== Step 4: Building ==="
cmake --build .

echo "=== Build complete! ==="
echo "Executable location: $PROJECT_DIR/build/gui/ista_gui"
ls -lh gui/ista_gui

echo ""
echo "To run the GUI:"
echo "  ./build/gui/ista_gui"
```

Save this as `build_gui.sh` and run:
```bash
chmod +x build_gui.sh
./build_gui.sh
```

## Troubleshooting

### Nothing works!

Nuclear option - completely clean start:

```bash
cd /Users/jdr2160/projects/ista

# Remove all build artifacts
rm -rf build
rm -rf external/pugixml/*
rm -rf external/imgui
rm -rf external/glfw

# Download everything fresh
cd external/pugixml
git clone https://github.com/zeux/pugixml.git .
cd ..

git clone https://github.com/ocornut/imgui.git
cd imgui
git checkout v1.90.4
cd ..

git clone https://github.com/glfw/glfw.git
cd glfw
git checkout 3.4
cd ../..

# Use system GLFW if available
brew install glfw

# Build
mkdir build
cd build
cmake .. -DBUILD_PYTHON_BINDINGS=OFF -DBUILD_GUI=ON
cmake --build . 2>&1 | tee build.log

# Check for errors
tail -50 build.log
```

### Still getting "library 'libista' not found"?

This means the linker can't find the static library. Check:

```bash
# Is libista being built?
ls build/lib/libista.a

# If it exists, the issue is linking
# If it doesn't exist, libista didn't build
```

If `libista.a` doesn't exist:
```bash
# Build just the library
cd build
cmake --build . --target libista

# Check output
ls lib/libista.a
```

If it still fails, check CMake configuration:
```bash
cd build
cat CMakeCache.txt | grep -i "ista"
```

## Platform-Specific Notes

### macOS
- OpenGL is deprecated but still works (warnings are silenced)
- May need to link against system frameworks (already handled in CMakeLists.txt)
- If SDK issues persist, use `brew install glfw`

### Linux
Requires additional system packages:
```bash
sudo apt-get install libx11-dev libxrandr-dev libxinerama-dev \
                     libxcursor-dev libxi-dev libgl1-mesa-dev
```

### Windows
- Use Visual Studio 2019 or later
- CMake will generate `.sln` files
- Build from Visual Studio or command line with `cmake --build .`

## Success!

If everything worked, you should have:
- ✅ Executable at `build/gui/ista_gui`
- ✅ Size around 3-4 MB
- ✅ Runs without errors
- ✅ Shows GUI window

Next: See [QUICKSTART.md](QUICKSTART.md) for how to use the GUI!
