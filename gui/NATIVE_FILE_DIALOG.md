# Native File Dialog Integration

The ISTA GUI now uses native, platform-specific file dialogs for a better user experience.

## What Changed

### Before
- Text input box where users had to type the full file path
- Error-prone (typos, wrong paths)
- No file browsing capability

### After
- Native macOS/Windows/Linux file picker dialog
- Browse files visually
- File type filtering (shows only .owl, .rdf files by default)
- Standard OS file dialog experience

## Implementation

### Library Used
**nativefiledialog-extended (NFD)** - https://github.com/btzy/nativefiledialog-extended

- Lightweight C library
- Cross-platform (macOS, Windows, Linux)
- MIT licensed
- No additional runtime dependencies

### Features Added

1. **Load Ontology Dialog** (File > Load Ontology or Ctrl+O)
   - Filters: OWL/RDF files (*.owl, *.rdf) and All Files
   - Opens native file picker
   - Returns selected file path
   
2. **Save As Dialog** (File > Save As...)
   - Filters: OWL/RDF files only
   - Default filename: "ontology.owl"
   - Native save dialog with overwrite confirmation

3. **Add Data Source Dialog** (Data > Add Data Source)
   - Filters: CSV and Excel files (*.csv, *.xlsx)
   - Multiple locations (menu and data source panel)

## Code Changes

### Files Modified

1. **`gui/CMakeLists.txt`**
   - Added NFD source files (platform-specific)
   - Added NFD include directory
   - Added required macOS frameworks (UniformTypeIdentifiers, AppKit)
   - Set Objective-C language for macOS NFD implementation

2. **`CMakeLists.txt` (root)**
   - Enabled Objective-C compiler for macOS builds
   - Required for NFD's Cocoa implementation

3. **`gui/src/kg_editor.cpp`**
   - Added `#include "nfd.h"`
   - Added `NFD_Init()` in `initialize()`
   - Added `NFD_Quit()` in `shutdown()`
   - Replaced text input dialog with `NFD_OpenDialog()` for loading
   - Added `NFD_SaveDialog()` for Save As functionality
   - Added file dialogs for data source selection
   - Removed `filepath_buffer_` (no longer needed)

4. **`gui/include/kg_editor.hpp`**
   - Removed `char filepath_buffer_[512]` member variable

5. **`build_gui.sh`**
   - Added NFD download step

6. **`gui/setup_dependencies.sh`**
   - Added NFD download step

### Platform-Specific Implementation

#### macOS (Cocoa)
- Uses `NSSavePanel` and `NSOpenPanel`
- Requires: Cocoa, AppKit, UniformTypeIdentifiers frameworks
- File: `external/nfd/src/nfd_cocoa.m`

#### Windows
- Uses `IFileDialog` COM API
- Requires: Shell32, Ole32 libraries (standard Windows)
- File: `external/nfd/src/nfd_win.cpp`

#### Linux
- Uses GTK3 file chooser
- Requires: GTK3 development libraries
- File: `external/nfd/src/nfd_gtk.cpp`
- Alternative: Portal API for Flatpak/Snap

## Usage Example

### Loading an Ontology

```cpp
// User clicks File > Load Ontology
if (show_ontology_loader_) {
    show_ontology_loader_ = false;
    
    nfdchar_t *outPath;
    nfdfilteritem_t filterItem[2] = { 
        { "OWL/RDF Files", "owl,rdf" }, 
        { "All Files", "*" } 
    };
    nfdresult_t result = NFD_OpenDialog(&outPath, filterItem, 2, nullptr);
    
    if (result == NFD_OKAY) {
        std::string filepath(outPath);
        load_ontology(filepath);
        NFD_FreePath(outPath);  // Important: free the path
    } else if (result == NFD_ERROR) {
        std::cerr << "Error: " << NFD_GetError() << std::endl;
    }
    // NFD_CANCEL - user cancelled
}
```

### Saving an Ontology

```cpp
nfdchar_t *savePath;
nfdfilteritem_t filterItem[1] = { { "OWL/RDF Files", "owl,rdf" } };
nfdresult_t result = NFD_SaveDialog(&savePath, filterItem, 1, nullptr, "ontology.owl");

if (result == NFD_OKAY) {
    std::string filepath(savePath);
    save_ontology(filepath);
    NFD_FreePath(savePath);
}
```

## Building

### Dependencies Download

The build script automatically downloads NFD:

```bash
./build_gui.sh
```

Or manually:
```bash
cd external
git clone https://github.com/btzy/nativefiledialog-extended.git nfd
```

### Platform Requirements

#### macOS
- macOS 10.13+ (for UniformTypeIdentifiers framework)
- Xcode Command Line Tools
- Frameworks: Cocoa, AppKit, UniformTypeIdentifiers (auto-linked)

#### Windows
- Visual Studio 2019+
- Windows SDK (for IFileDialog)
- Links against: Shell32.lib, Ole32.lib

#### Linux
- GTK3 development libraries:
  ```bash
  sudo apt-get install libgtk-3-dev
  ```

## Benefits

✅ **Better UX** - Visual file browsing instead of typing paths
✅ **Fewer errors** - No typos in file paths
✅ **Native feel** - Uses OS-standard file dialogs
✅ **File filtering** - Shows only relevant files by extension
✅ **Cross-platform** - Same API, native dialogs on each OS
✅ **Lightweight** - Adds only ~50KB to executable
✅ **No dependencies** - Uses OS-provided APIs

## Future Enhancements

Potential future improvements:
- Remember last opened directory
- Multi-file selection for batch operations
- Custom file preview in dialog
- Bookmark/favorites support
- Recent files list

## Troubleshooting

### Build Error: "UniformTypeIdentifiers framework not found"

**macOS only** - Update to macOS 10.13+ or use older NFD version

### Build Error: "GTK3 not found"

**Linux only** - Install GTK3 development libraries:
```bash
sudo apt-get install libgtk-3-dev
```

### Dialog doesn't appear

Check console for NFD errors:
```cpp
if (result == NFD_ERROR) {
    std::cerr << "NFD Error: " << NFD_GetError() << std::endl;
}
```

### Memory leak warnings

Always call `NFD_FreePath()` after successful dialogs:
```cpp
if (result == NFD_OKAY) {
    // Use outPath...
    NFD_FreePath(outPath);  // Don't forget!
}
```

## References

- [nativefiledialog-extended GitHub](https://github.com/btzy/nativefiledialog-extended)
- [NFD API Documentation](https://github.com/btzy/nativefiledialog-extended/blob/master/docs/api.md)
- [Original nativefiledialog](https://github.com/mlabbe/nativefiledialog) (NFD-extended is a maintained fork)
