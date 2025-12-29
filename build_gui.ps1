# Complete clean build script for ISTA GUI
# PowerShell version

# Exit on error
$ErrorActionPreference = "Stop"

$PROJECT_DIR = $PSScriptRoot
$ORIGINAL_DIR = Get-Location
Set-Location $PROJECT_DIR

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "ISTA GUI - Complete Clean Build Script" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "=== Step 1: Downloading dependencies ===" -ForegroundColor Yellow
Write-Host ""

# Download pugixml
if (-not (Test-Path "external/pugixml/src/pugixml.cpp")) {
    Write-Host "Downloading pugixml..."
    Set-Location external/pugixml
    git clone https://github.com/zeux/pugixml.git .
    Set-Location ../..
    Write-Host "✓ pugixml downloaded" -ForegroundColor Green
} else {
    Write-Host "✓ pugixml already exists" -ForegroundColor Green
}

# Download ImGui
if (-not (Test-Path "external/imgui/imgui.cpp")) {
    Write-Host "Downloading Dear ImGui..."
    Set-Location external
    git clone https://github.com/ocornut/imgui.git
    Set-Location imgui
    git checkout v1.90.4
    Set-Location ../..
    Write-Host "✓ Dear ImGui downloaded" -ForegroundColor Green
} else {
    Write-Host "✓ Dear ImGui already exists" -ForegroundColor Green
}

# Download GLFW
if (-not (Test-Path "external/glfw/CMakeLists.txt")) {
    Write-Host "Downloading GLFW..."
    Set-Location external
    git clone https://github.com/glfw/glfw.git
    Set-Location glfw
    git checkout 3.4
    Set-Location ../..
    Write-Host "✓ GLFW downloaded" -ForegroundColor Green
} else {
    Write-Host "✓ GLFW already exists" -ForegroundColor Green
}

# Download Native File Dialog
if (-not (Test-Path "external/nfd/src/include/nfd.h")) {
    Write-Host "Downloading Native File Dialog..."
    Set-Location external
    git clone https://github.com/btzy/nativefiledialog-extended.git nfd
    Set-Location ..
    Write-Host "✓ Native File Dialog downloaded" -ForegroundColor Green
} else {
    Write-Host "✓ Native File Dialog already exists" -ForegroundColor Green
}

Write-Host ""
Write-Host "=== Step 2: Cleaning previous build ===" -ForegroundColor Yellow
if (Test-Path "build") {
    Remove-Item -Recurse -Force build
}
New-Item -ItemType Directory -Path build | Out-Null
Write-Host "✓ Build directory cleaned" -ForegroundColor Green

Write-Host ""
Write-Host "=== Step 3: Configuring with CMake ===" -ForegroundColor Yellow
Set-Location build
cmake .. -DBUILD_PYTHON_BINDINGS=OFF -DBUILD_GUI=ON
Write-Host "✓ CMake configuration complete" -ForegroundColor Green

Write-Host ""
Write-Host "=== Step 4: Building ===" -ForegroundColor Yellow
cmake --build . 2>&1 | Tee-Object -FilePath build.log
$BUILD_STATUS = $LASTEXITCODE

Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
if ($BUILD_STATUS -eq 0) {
    Write-Host "✓ BUILD SUCCESSFUL!" -ForegroundColor Green
    Write-Host "=========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Executable location: $PROJECT_DIR\build\gui\Debug\ista_gui.exe (or Release)"
    if (Test-Path "gui/Debug/ista_gui.exe") {
        Get-ChildItem gui/Debug/ista_gui.exe | Format-Table Name, Length, LastWriteTime
    } elseif (Test-Path "gui/Release/ista_gui.exe") {
        Get-ChildItem gui/Release/ista_gui.exe | Format-Table Name, Length, LastWriteTime
    }
    Write-Host ""
    Write-Host "To run the GUI:"
    Write-Host "  .\build\gui\Debug\ista_gui.exe"
    Write-Host "  or"
    Write-Host "  .\build\gui\Release\ista_gui.exe"
    Write-Host ""
} else {
    Write-Host "✗ BUILD FAILED" -ForegroundColor Red
    Write-Host "=========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Check build.log for errors:"
    Write-Host "  Get-Content build\build.log -Tail 50"
    Write-Host ""
    Set-Location $ORIGINAL_DIR
    exit 1
}

# Return to original directory
Set-Location $ORIGINAL_DIR
