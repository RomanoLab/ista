@echo off
REM Build documentation for ista project
REM This script builds both C++ (Doxygen) and Python (Sphinx) documentation

echo Building ista documentation...

REM Navigate to docs directory
cd /d "%~dp0"

REM Step 1: Generate C++ documentation with Doxygen
echo Step 1/2: Generating C++ API documentation with Doxygen...
where doxygen >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    doxygen Doxyfile
    echo Doxygen documentation generated successfully.
) else (
    echo Warning: Doxygen not found. Skipping C++ documentation generation.
    echo Install Doxygen to generate C++ API documentation.
)

REM Step 2: Build Sphinx documentation
echo Step 2/2: Building Sphinx documentation...
where sphinx-build >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Error: sphinx-build not found. Please install Sphinx:
    echo   pip install -r ..\requirements.txt
    exit /b 1
)

sphinx-build -b html source build\html
if %ERRORLEVEL% NEQ 0 (
    echo Error: Sphinx build failed.
    exit /b 1
)

echo Sphinx documentation built successfully.
echo Documentation available at: build\html\index.html

echo.
echo Documentation build complete!
echo Open build\html\index.html in your browser to view the documentation.
