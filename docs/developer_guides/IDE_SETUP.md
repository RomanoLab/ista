# IDE Setup Guide for ISTA

This guide helps you configure your IDE to properly recognize headers (especially pybind11) and eliminate linting errors.

## Quick Fix Summary

The linting errors occur because your IDE doesn't know where to find:
- `pybind11/pybind11.h` (located in `external/pybind11/include/`)
- Python headers (e.g., `Python.h`)
- Project headers (`owl2/*.hpp`)

**Solution**: Configure your IDE's include paths.

---

## VS Code Setup (Recommended)

### Option 1: Using C/C++ Extension (Microsoft)

1. **Install Extension**:
   - Install "C/C++" extension by Microsoft

2. **Configuration Files** (Already Created):
   - `.vscode/c_cpp_properties.json` - IntelliSense configuration
   - `.vscode/settings.json` - VS Code settings

3. **Adjust Python Path** (if needed):
   Edit `.vscode/c_cpp_properties.json` and update the Python include path:
   ```json
   "C:/Users/YOUR_USERNAME/miniconda3/include"
   ```
   Or find it with:
   ```bash
   python -c "import sysconfig; print(sysconfig.get_path('include'))"
   ```

4. **Reload Window**:
   - Press `Ctrl+Shift+P`
   - Type "Reload Window"
   - Select "Developer: Reload Window"

5. **Verify**:
   - Open `lib/python/bindings_simple.cpp`
   - Hover over `#include <pybind11/pybind11.h>`
   - Should show no errors

### Option 2: Using clangd Extension (Alternative)

1. **Install Extension**:
   - Install "clangd" extension
   - Disable or uninstall "C/C++" extension (they conflict)

2. **Configuration File** (Already Created):
   - `.clangd` - Clangd configuration in project root

3. **Install clangd**:
   ```bash
   # Windows (via LLVM)
   # Download from: https://github.com/clangd/clangd/releases
   
   # Linux
   sudo apt-get install clangd-12
   
   # macOS
   brew install llvm
   ```

4. **Adjust Python Path** (if needed):
   Edit `.clangd` and update:
   ```yaml
   - "-IC:/Users/YOUR_USERNAME/miniconda3/include"
   ```

5. **Reload Window**:
   - Press `Ctrl+Shift+P`
   - Type "Reload Window"

---

## CLion / JetBrains IDEs

### Automatic Configuration (via CMake)

1. **Open Project**:
   - File → Open → Select `D:\projects\ista`

2. **CMake Configuration**:
   - CLion will automatically detect `CMakeLists.txt`
   - It will parse include directories from CMake

3. **Reload CMake** (if needed):
   - Tools → CMake → Reload CMake Project

4. **Verify**:
   - Errors should disappear automatically
   - CLion uses CMake's include paths

### Manual Configuration (if needed)

1. **Open Settings**:
   - File → Settings → Build, Execution, Deployment → CMake

2. **CMake Options**:
   Add to "CMake options":
   ```
   -DCMAKE_EXPORT_COMPILE_COMMANDS=ON
   ```

3. **Include Directories**:
   - Settings → Languages & Frameworks → C/C++ → Project Include Paths
   - Add:
     - `D:\projects\ista\lib`
     - `D:\projects\ista\external\pybind11\include`
     - `D:\projects\ista\external\pugixml\src`
     - Your Python include path

---

## Visual Studio (MSVC)

### Using CMake Integration

1. **Open Folder**:
   - File → Open → Folder
   - Select `D:\projects\ista`

2. **CMake Settings**:
   - Project → CMake Settings for ista
   - Visual Studio should auto-detect include paths from CMakeLists.txt

3. **Regenerate Cache**:
   - Project → Delete Cache and Reconfigure

### Manual Configuration

1. **Project Properties**:
   - Right-click project → Properties
   - Configuration Properties → C/C++ → General → Additional Include Directories

2. **Add Include Paths**:
   ```
   D:\projects\ista\lib;
   D:\projects\ista\external\pybind11\include;
   D:\projects\ista\external\pugixml\src;
   C:\Users\YOUR_USERNAME\miniconda3\include;
   %(AdditionalIncludeDirectories)
   ```

---

## Sublime Text

1. **Install LSP Package**:
   - Install Package Control
   - Install "LSP" and "LSP-clangd"

2. **Configure LSP-clangd**:
   - Preferences → Package Settings → LSP → Settings
   - Add:
   ```json
   {
     "clients": {
       "clangd": {
         "enabled": true,
         "command": ["clangd", "--background-index"],
         "initializationOptions": {
           "clangd.path": "clangd"
         }
       }
     }
   }
   ```

3. **Use .clangd file**:
   - The `.clangd` file in project root will be auto-detected

---

## Vim / Neovim

### Using coc.nvim + clangd

1. **Install coc.nvim**:
   ```vim
   Plug 'neoclide/coc.nvim', {'branch': 'release'}
   ```

2. **Install clangd language server**:
   ```vim
   :CocInstall coc-clangd
   ```

3. **Configure**:
   - The `.clangd` file in project root will be auto-detected
   - No additional configuration needed

### Using ALE

1. **Install ALE**:
   ```vim
   Plug 'dense-analysis/ale'
   ```

2. **Configure for C++**:
   ```vim
   let g:ale_linters = {
   \   'cpp': ['clangd'],
   \}
   let g:ale_cpp_clangd_options = '--background-index'
   ```

---

## Emacs

### Using lsp-mode

1. **Install lsp-mode**:
   ```elisp
   (use-package lsp-mode
     :commands lsp
     :hook ((c++-mode . lsp)))
   ```

2. **Install clangd**:
   ```elisp
   (setq lsp-clients-clangd-args
         '("--background-index"
           "--clang-tidy"
           "--completion-style=detailed"))
   ```

3. **Use .clangd file**:
   - The `.clangd` file will be auto-detected

---

## Troubleshooting

### Issue: Headers Still Not Found

**Check Python Path**:
```bash
# Find your Python include directory
python -c "import sysconfig; print(sysconfig.get_path('include'))"

# Example output:
# C:/Users/jdr2160/miniconda3/include
# /usr/include/python3.9
```

Update this path in your IDE configuration files.

**Check pybind11 Location**:
```bash
cd /d/projects/ista
ls external/pybind11/include/pybind11/pybind11.h
```

If missing, the submodule wasn't initialized:
```bash
git submodule update --init --recursive
```

### Issue: Errors Only in bindings_simple.cpp

**This is normal if**:
- The file compiles successfully with CMake
- Only the IDE shows errors

**Solution**: Use one of the configurations above

**Quick Workaround**:
Add this at the top of `bindings_simple.cpp`:
```cpp
// IDE configuration hint
#ifndef __INTELLISENSE__
// Include guards for IDE
#endif
```

### Issue: Too Many Warnings

**Suppress External Warnings**:

In `.clangd`:
```yaml
Diagnostics:
  Suppress:
    - "pp_file_not_found"
    - "unused-parameter"
  ClangTidy:
    Remove: ['modernize-*', 'readability-*']
```

In VS Code `c_cpp_properties.json`:
```json
"compilerArgs": [
  "-Wno-unused-parameter",
  "-isystem", "${workspaceFolder}/external/pybind11/include"
]
```

### Issue: Slow IntelliSense

**For VS Code C/C++ Extension**:
```json
"C_Cpp.intelliSenseCacheSize": 2048,
"C_Cpp.default.browse.limitSymbolsToIncludedHeaders": true
```

**For clangd**:
```yaml
Index:
  Background: Skip
```

---

## Testing Your Configuration

### Test 1: Check Include Path

Open `lib/python/bindings_simple.cpp` and add:
```cpp
#include <pybind11/pybind11.h>  // Should have no squiggles
```

Hover over it - should show the file path.

### Test 2: Autocomplete

Type `py::` and you should see autocomplete suggestions for pybind11 classes.

### Test 3: Go to Definition

Ctrl+Click (or Cmd+Click) on `pybind11.h` - should jump to the header file.

---

## Recommended Setup by IDE

| IDE | Recommended Extension | Config File |
|-----|----------------------|-------------|
| **VS Code** | clangd | `.clangd` |
| **CLion** | Built-in CMake | Automatic |
| **Visual Studio** | Built-in | CMake |
| **Sublime Text** | LSP-clangd | `.clangd` |
| **Vim/Neovim** | coc-clangd | `.clangd` |
| **Emacs** | lsp-mode + clangd | `.clangd` |

---

## Alternative: Disable Linting for One File

If you don't want to configure your IDE globally, you can disable linting for `bindings_simple.cpp`:

### VS Code
Add to `settings.json`:
```json
"C_Cpp.errorSquiggles": "EnabledIfIncludesResolve",
"files.exclude": {
  "**/bindings_simple.cpp": false
}
```

### CLion
Right-click `bindings_simple.cpp` → Mark as → Plain Text

---

## Files Created for You

✅ `.clangd` - Universal clangd configuration  
✅ `.vscode/c_cpp_properties.json` - VS Code IntelliSense  
✅ `.vscode/settings.json` - VS Code settings  
✅ `IDE_SETUP.md` - This guide  

## What to Modify

**You need to update the Python include path**:

1. Find your Python include directory:
   ```bash
   python -c "import sysconfig; print(sysconfig.get_path('include'))"
   ```

2. Update in:
   - `.clangd` (line with `-IC:/Users/...`)
   - `.vscode/c_cpp_properties.json` (all Python paths)

That's it! Your IDE should now properly recognize all headers.

---

## Additional Resources

- [clangd Documentation](https://clangd.llvm.org/)
- [VS Code C++ Documentation](https://code.visualstudio.com/docs/cpp/config-msvc)
- [pybind11 Documentation](https://pybind11.readthedocs.io/)
- [CMake compile_commands.json](https://cmake.org/cmake/help/latest/variable/CMAKE_EXPORT_COMPILE_COMMANDS.html)

## Getting Help

If you still have issues:
1. Check that CMake build succeeds: `cmake --build build/`
2. Verify header exists: `ls external/pybind11/include/pybind11/pybind11.h`
3. Check your IDE's output/log for specific errors
4. Try the simpler `.clangd` configuration first
