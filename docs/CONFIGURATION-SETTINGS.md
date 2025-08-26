# Configuration & Settings Reference

## System Configuration

### Hardware Requirements
- **Minimum**: 8GB RAM, 4-core CPU, 50GB free disk space
- **Recommended**: 16GB+ RAM, 8+ core CPU, 100GB+ free disk space
- **Tested Successfully**: Intel Core Ultra 9 185H, 64GB RAM

### Software Prerequisites
```bash
# Node.js (Required)
Node.js v22.14.0 or higher
npm (comes with Node.js)

# Python (Required for large file splitting)
Python 3.12+ 
IfcOpenShell library: pip install ifcopenshell

# Dependencies (Auto-installed)
@thatopen/components ^2.4.11
@thatopen/fragments ^3.0.7
web-ifc 0.0.68
```

## Memory Configurations

### Node.js Memory Settings

#### Standard Files (< 500MB)
```bash
set NODE_OPTIONS=--max-old-space-size=4096
# 4GB allocation - sufficient for most files
```

#### Large Files (500MB - 1GB)
```bash
set NODE_OPTIONS=--max-old-space-size=8192 --expose-gc
# 8GB allocation with garbage collection
```

#### Extreme Files (>1GB, processed as chunks)
```bash
set NODE_OPTIONS=--max-old-space-size=8192 --expose-gc
# 8GB per chunk + GC for memory management
```

#### Maximum Configuration (if needed)
```bash
set NODE_OPTIONS=--max-old-space-size=16384 --expose-gc
# 16GB allocation - for exceptional cases
```

## IFC Splitter Configuration

### Basic Splitting Command
```bash
python ifc_splitter.py "input.ifc" "output_directory" [options]
```

### Splitting Options

#### Element Count Method (Recommended)
```bash
--method chunks
--max-elements 50000
# Splits into chunks of 50,000 elements each
# Proven successful with 3.8GB file
```

#### Cleaning Options
```bash
--clean
# Removes non-essential entities:
# - Grid axes (often numerous)
# - Annotations
# - Redundant elements
```

#### Alternative Chunk Sizes
```bash
--max-elements 25000   # Smaller chunks for very complex files
--max-elements 75000   # Larger chunks for simpler files
--max-elements 100000  # Maximum recommended size
```

## File Processing Strategies

### Decision Matrix

| File Size | Strategy | Tools | Memory | Expected Time |
|-----------|----------|-------|---------|---------------|
| < 100MB | Direct | convert_ifc_files.bat | 4GB | 30s - 2min |
| 100-500MB | Enhanced | Standard + memory | 8GB | 2-10min |
| 500MB-1GB | Optimized | Enhanced + preprocessing | 8-16GB | 10-30min |
| > 1GB | Split-Convert | ifc_splitter.py + batch | 8GB/chunk | Variable |

### Processing Parameters by Complexity

#### Low Complexity (Simple buildings)
```bash
# Direct conversion usually sufficient
# Standard memory allocation
# Minimal preprocessing needed
```

#### Medium Complexity (Detailed architecture)
```bash
# Enhanced memory conversion
# Optional preprocessing for size reduction
# Monitor memory usage during processing
```

#### High Complexity (MEP systems, detailed geometry)
```bash
# Preprocessing recommended
# Split if > 500MB
# Use cleaning options
```

#### Extreme Complexity (3.8GB B142-KCX level)
```bash
# Mandatory splitting
# Aggressive cleaning (--clean)
# 50,000 element chunks
# Monitor each chunk conversion
```

## Batch File Configurations

### convert_ifc_files.bat Settings
```batch
REM Memory for standard processing
set NODE_OPTIONS=--max-old-space-size=4096

REM File detection and processing
REM Supports drag & drop and directory processing
REM Automatic output file naming
```

### convert_split_files.bat Settings
```batch
REM Memory for chunk processing
set NODE_OPTIONS=--max-old-space-size=8192 --expose-gc

REM Source and target directories
set SOURCE_DIR=D:\XIF2\data\ifc_split\test_split
set TARGET_DIR=D:\XIF2\data\fragments\split_fragments

REM Processing all chunks in sequence
REM Progress tracking and error handling
```

## Output Configuration

### Fragment File Organization
```
D:\XIF2\data\fragments\
├── single\              # Direct conversion outputs
│   └── filename.frag
└── split_fragments\     # Split-and-convert outputs  
    ├── chunk_001.frag
    ├── chunk_002.frag
    ├── chunk_003.frag
    ├── chunk_004.frag
    └── chunk_005.frag
```

### Naming Conventions
- **Single files**: `{original_name}.frag`
- **Split files**: `chunk_{nnn}.frag` (001, 002, etc.)
- **Preprocessed**: `{original_name}_preprocessed.ifc`
- **Summary**: `splitting_summary.txt`

## Performance Tuning

### Optimization Settings

#### For Speed Priority
```bash
# Smaller chunks for parallel processing potential
--max-elements 25000

# Minimal cleaning for faster splitting
# Skip --clean if time is critical
```

#### For Quality Priority  
```bash
# Larger chunks for better cohesion
--max-elements 75000

# Comprehensive cleaning
--clean

# Additional preprocessing if needed
```

#### For Memory Efficiency
```bash
# Conservative chunk size
--max-elements 30000

# Aggressive memory management
set NODE_OPTIONS=--max-old-space-size=6144 --expose-gc

# Monitor memory usage during processing
```

## Validation Settings

### Quality Checks
```bash
# File size validation
# Input: Should be > 0 bytes
# Output: Should be 90-99% smaller than input

# Content validation  
# Fragments should load in IFC.js viewers
# Building elements should be preserved

# Performance validation
# Processing time should be reasonable
# Memory usage should stay within limits
```

### Success Metrics
- **Compression**: 90-99% size reduction expected
- **Completeness**: All input elements preserved in fragments
- **Performance**: < 5 seconds per 10MB of input
- **Reliability**: 100% success rate on properly formatted IFC files

## Troubleshooting Configuration

### Common Issues and Settings

#### "Cannot create string longer than..." Error
```bash
# Use streaming preprocessor instead of direct conversion
node stream_preprocess.cjs "large_file.ifc" "preprocessed.ifc"
```

#### "RuntimeError: Aborted()" Error
```bash
# Use split-and-convert strategy
# Reduce chunk size if still failing
--max-elements 25000
```

#### Memory Exhaustion
```bash
# Increase Node.js memory
set NODE_OPTIONS=--max-old-space-size=16384

# Or reduce chunk size
--max-elements 30000
```

#### Slow Processing
```bash
# Use smaller chunks for progress visibility
--max-elements 25000

# Enable garbage collection
set NODE_OPTIONS=--max-old-space-size=8192 --expose-gc
```

## Environment Variables

### Required Settings
```bash
# Node.js memory allocation
NODE_OPTIONS=--max-old-space-size=8192 --expose-gc

# Python path (if needed)
PYTHONPATH=D:\XIF2\frag_convert

# Working directory
CD=D:\XIF2\frag_convert
```

### Optional Settings
```bash
# Debug mode (if implemented)
DEBUG=1

# Verbose output
VERBOSE=1

# Custom temp directory
TEMP_DIR=D:\XIF2\temp
```

## Production Deployment Settings

### Server Configuration
```bash
# For server deployment
NODE_OPTIONS=--max-old-space-size=32768 --expose-gc
# Larger allocation for server environments

# Process monitoring
# Monitor memory usage
# Set up process restart on failure
# Log all operations for debugging
```

### Batch Processing Configuration
```bash
# For processing multiple files
# Set up queue management
# Parallel processing with resource limits
# Automatic cleanup of temporary files
```

---
*Configuration Guide Version*: 1.0  
*Last Updated*: August 26, 2025  
*Validated Configuration*: Successfully processed 3.8GB B142-KCX file
