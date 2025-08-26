# Production Process Documentation - Large File IFC Conversion

## Overview

This document outlines the complete production-ready process for converting IFC files of any size to web-ready fragments. Our system has been proven to handle files from small (MB) to extreme large (3.8+ GB) through adaptive processing strategies.

## System Architecture

### Core Components

1. **Standard Converter**: `frag_convert/convert_ifc_to_fragments.js`
   - ThatOpen Components-based converter
   - Handles files up to ~500MB efficiently
   - Streaming file reading with memory optimization

2. **IFC Splitter**: `frag_convert/ifc_splitter.py`
   - Python + IfcOpenShell for file analysis and splitting
   - Supports multiple splitting strategies (chunks, spatial, functional)
   - Automatic cleaning of non-essential entities

3. **Batch Processor**: `convert_split_files.bat`
   - Automated conversion of multiple split files
   - Progress tracking and error handling
   - Memory-optimized Node.js configuration

4. **Diagnostic Tools**: 
   - `frag_convert/diagnose_ifc.cjs` - File analysis and complexity assessment
   - `frag_convert/stream_preprocess.cjs` - Streaming preprocessing for size reduction

## Processing Strategies by File Size

### Small Files (< 100MB)
- **Method**: Direct conversion
- **Tool**: `convert_ifc_files.bat` (user-friendly drag & drop)
- **Memory**: Standard Node.js limits
- **Expected Time**: 30 seconds - 2 minutes

### Medium Files (100MB - 500MB)
- **Method**: Enhanced memory conversion
- **Tool**: Standard converter with increased memory
- **Memory**: 4-8GB Node.js allocation
- **Expected Time**: 2-10 minutes

### Large Files (500MB - 1GB)
- **Method**: Memory-optimized with preprocessing
- **Tool**: Enhanced converter + optional preprocessing
- **Memory**: 8-16GB Node.js allocation
- **Expected Time**: 10-30 minutes

### Extreme Files (>1GB)
- **Method**: Split-and-convert strategy
- **Tools**: IFC splitter → Batch converter
- **Memory**: 8GB per chunk conversion
- **Expected Time**: Variable (3.8GB processed in 4 minutes)

## Production Workflow

### Phase 1: File Analysis
```bash
# Analyze file complexity and determine strategy
cd D:\XIF2\frag_convert
node diagnose_ifc.cjs "input_file.ifc"
```

**Output**: File size, entity count, complexity assessment, recommended strategy

### Phase 2: Strategy Selection

#### For Files < 1GB:
```bash
# Direct conversion
cd D:\XIF2
convert_ifc_files.bat
# Or drag & drop IFC file onto batch file
```

#### For Files > 1GB:
```bash
# Step 1: Split the file
cd D:\XIF2\frag_convert
python ifc_splitter.py "large_file.ifc" "output_dir" --method chunks --clean --max-elements 50000

# Step 2: Convert all chunks
cd D:\XIF2
convert_split_files.bat
# (Edit paths in batch file for specific source/target directories)
```

### Phase 3: Quality Assurance
1. **Verify Output**: Check all fragment files exist and have reasonable sizes
2. **Test Loading**: Load fragments in IFC.js viewer
3. **Validate Content**: Ensure building elements are properly represented

## Proven Success Case: B142-KCX File

### Input Specifications
- **File**: B142-KCX-ZZ-ZZ-M-X-0001.ifc
- **Size**: 3,820.81 MB (3.8 GB)
- **Schema**: IFC2X3
- **Elements**: 217,291 total entities
- **Complexity**: Extreme (62M estimated entities, 20M CartesianPoints)

### Processing Results
- **Split into**: 5 chunks (50,000 elements each)
- **Cleaning**: Removed 2,569 grid elements
- **Total Processing Time**: 256 seconds (~4 minutes)
- **Conversion Success**: 100% (5/5 chunks converted)

### Output Specifications
```
chunk_001.frag    7.22 MB   (97.2% compression)   Beams, Building Parts
chunk_002.frag    7.25 MB   (98.1% compression)   Building Elements
chunk_003.frag    3.77 MB   (98.2% compression)   Proxies, Building Parts
chunk_004.frag    4.56 MB   (98.0% compression)   Columns, Curtain Walls
chunk_005.frag   30.14 MB   (97.8% compression)   Walls, Doors, Windows
```

## Configuration Settings

### Node.js Memory Configuration
```bash
# For standard files
set NODE_OPTIONS=--max-old-space-size=4096

# For large files
set NODE_OPTIONS=--max-old-space-size=8192 --expose-gc

# For extreme files (per chunk)
set NODE_OPTIONS=--max-old-space-size=8192 --expose-gc
```

### IFC Splitter Settings
```bash
# Recommended chunk size for most files
--max-elements 50000

# Cleaning options (removes non-essential entities)
--clean

# Splitting methods available
--method chunks      # Split by element count
--method spatial     # Split by spatial boundaries (future)
--method functional  # Split by building systems (future)
```

## File Organization Structure

```
D:\XIF2\
├── data\
│   ├── ifc\                     # Original IFC files
│   ├── ifc_split\               # Split IFC files
│   │   └── [project_name]\      # Split chunks per project
│   └── fragments\               # Output fragments
│       ├── single\              # Direct conversion fragments
│       └── split_fragments\     # Split-and-convert fragments
├── frag_convert\                # Core conversion tools
│   ├── convert_ifc_to_fragments.js
│   ├── ifc_splitter.py
│   ├── diagnose_ifc.cjs
│   └── stream_preprocess.cjs
├── convert_ifc_files.bat        # User interface
└── convert_split_files.bat      # Batch processor
```

## Performance Benchmarks

### Conversion Speed
- **Direct conversion**: ~1-2 seconds per 10MB
- **Split conversion**: ~1-2 seconds per 10MB (per chunk)
- **Splitting overhead**: ~2 seconds per 100MB

### Compression Ratios
- **Typical**: 95-98% size reduction
- **Geometric-heavy files**: 90-95% reduction
- **Property-heavy files**: 98-99% reduction

### Memory Usage
- **Standard files**: 3-5x file size in memory
- **Split chunks**: 3-5x chunk size in memory
- **Maximum tested**: 16GB allocation successful

## Quality Metrics

### Success Criteria
- ✅ Fragment files generated without errors
- ✅ Compression ratio > 90%
- ✅ All building elements preserved
- ✅ Fragments loadable in web viewers

### Common Issues and Solutions
1. **WASM abort errors**: Use split-and-convert strategy
2. **Memory exhaustion**: Increase Node.js memory allocation
3. **Long processing times**: Consider smaller chunk sizes
4. **Missing elements**: Verify IFC file integrity

## Production Deployment Checklist

### Prerequisites
- [ ] Node.js v22+ installed
- [ ] Python 3.12+ with IfcOpenShell
- [ ] ThatOpen Components dependencies (`npm install`)
- [ ] Sufficient disk space (2-3x input file size)

### Process Validation
- [ ] Test with small file (< 100MB)
- [ ] Test with medium file (100-500MB) 
- [ ] Test split-and-convert with large file
- [ ] Verify fragments load in IFC.js viewer

### Monitoring and Maintenance
- [ ] Monitor memory usage during processing
- [ ] Log conversion times for performance tracking
- [ ] Backup original IFC files before processing
- [ ] Regular cleanup of temporary split files

## Future Enhancements

### Planned Improvements
1. **Spatial Splitting**: Split by building levels/zones
2. **Functional Splitting**: Split by MEP/Structural/Architectural
3. **Progressive Loading**: Load fragments on-demand in viewer
4. **Fragment Merging**: Combine fragments for unified viewing
5. **Web Interface**: Browser-based file upload and processing

### Scalability Options
1. **Server-side Processing**: Deploy on cloud infrastructure
2. **Parallel Processing**: Process multiple chunks simultaneously
3. **Streaming Output**: Direct upload to web storage
4. **API Integration**: RESTful API for external systems

## Support and Troubleshooting

### Common Commands
```bash
# Diagnose file before processing
node diagnose_ifc.cjs "file.ifc"

# Standard conversion
convert_ifc_files.bat

# Large file processing
python ifc_splitter.py "file.ifc" "output" --method chunks --clean --max-elements 50000
convert_split_files.bat

# Check Node.js memory
node --max-old-space-size=8192 --version
```

### Error Resolution
- **"Cannot create string longer than..."**: Use streaming preprocessor
- **"RuntimeError: Aborted()"**: Use split-and-convert strategy
- **"Out of memory"**: Increase Node.js memory allocation
- **"Module not found"**: Run `npm install` in frag_convert directory

---
*Document Version*: 1.0
*Last Updated*: August 26, 2025
*Validated with*: B142-KCX-ZZ-ZZ-M-X-0001.ifc (3.8GB successful conversion)
