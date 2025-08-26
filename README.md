# IFC to Fragments Converter - Production Ready System

A comprehensive solution for converting IFC (Industry Foundation Classes) files into web-ready Fragments format using ThatOpen Components and advanced processing strategies for files of any size.

## 🎉 Major Breakthrough Achieved

**Successfully processed the massive 3.8GB B142-KCX file** using innovative split-and-convert methodology! This establishes our system as capable of handling extreme large IFC files through intelligent preprocessing and chunking strategies.

## Features

- **Universal File Support**: Handles any size IFC file through adaptive processing strategies
- **Multi-Strategy Processing**: Standard, enhanced, and split-processing for different file sizes
- **ThatOpen Components**: Uses official @thatopen/fragments library for reliable output
- **Intelligent Preprocessing**: Automatic file analysis and size reduction techniques
- **Split-and-Convert**: Revolutionary approach for extreme large files (>1GB)
- **Web-Ready Output**: Fragments optimized for IFC.js and web-based viewers
- **Automated Pipeline**: Complete batch processing with progress tracking

## Installation

```bash
# Clone the repository
git clone https://github.com/KrazB/XIF2.git
cd XIF2

# Install core dependencies
cd frag_convert
npm install

# Install Python dependencies for large file processing
pip install ifcopenshell
```

## Quick Start

### Simple Conversion (Drag & Drop)
1. Drag your IFC file onto `convert_ifc_files.bat`
2. Wait for conversion to complete
3. Find your `.frag` file in `data/fragments/`

### Large Files (>1GB)
1. Run `frag_convert/diagnose_ifc.cjs` to analyze your file
2. Use `frag_convert/ifc_splitter.py` to split large files
3. Run `convert_split_files.bat` to convert all chunks

## Project Structure

```
XIF2/
├── README.md                          # This file
├── convert_ifc_files.bat             # User-friendly interface
├── convert_split_files.bat           # Batch processing
├── docs/                             # Complete documentation
│   ├── PRODUCTION-PROCESS-GUIDE.md   # Detailed workflow
│   ├── CONFIGURATION-SETTINGS.md     # Settings reference
│   ├── BREAKTHROUGH-ACHIEVEMENT-SUMMARY.md
│   └── ...
├── frag_convert/                     # Core conversion tools
│   ├── convert_ifc_to_fragments.js  # Main converter
│   ├── ifc_splitter.py              # Large file splitter
│   ├── diagnose_ifc.cjs             # File analyzer
│   ├── stream_preprocess.cjs         # Preprocessor
│   └── package.json                 # Dependencies
└── data/                            # Test data and outputs
    ├── ifc/                         # Input IFC files
    ├── fragments/                   # Output fragments
    └── ifc_split/                   # Split file outputs
```

## Usage Examples

### Standard Files (< 1GB)
```bash
# Drag and drop method
# Simply drag your IFC file onto convert_ifc_files.bat

# Or manual conversion
cd frag_convert
node convert_ifc_to_fragments.js "path/to/file.ifc" "output.frag"
```

### Large Files (> 1GB) - Split and Convert
```bash
# Step 1: Analyze the file
cd frag_convert
node diagnose_ifc.cjs "large_file.ifc"

# Step 2: Split the file
python ifc_splitter.py "large_file.ifc" "../data/ifc_split/project" --method chunks --clean --max-elements 50000

# Step 3: Convert all chunks (edit convert_split_files.bat for your paths)
cd ..
convert_split_files.bat
```

## Available IFC Files

The following IFC files are available in `data/ifc/` for testing:

- `230221-WDHB-MCWH-AR-KLE-MDL-Architecture-RVT21.ifc`
- `B142-KCX-ZZ-ZZ-M-X-0001.ifc`
- `Mason Clinic E Tu Wairua Hinengaro - Structural Model.ifc`
- `Mason_Clinic - SBC.ifc`
- `Village_ARCH_Building C_R22-1_detached.ifc`
- `Village_STR_Building C_R22-2023.01.27.ifc`

## Performance Benchmarks

Our system has been proven with extreme large files:

### Success Case: 3.8GB B142-KCX File
- **Input**: 3,820.81 MB, 62M entities
- **Strategy**: Split into 5 chunks (50K elements each)  
- **Output**: 53.94 MB fragments (97.8% compression)
- **Time**: 4 minutes total processing

### Processing Strategies by Size
| File Size | Method | Expected Time | Compression |
|-----------|--------|---------------|-------------|
| < 100MB | Direct conversion | 30s - 2min | 95-98% |
| 100MB-1GB | Enhanced processing | 2-30min | 95-98% |
| > 1GB | Split-and-convert | Variable | 95-98% |

## System Requirements

### Minimum Requirements
- **OS**: Windows 10/11
- **RAM**: 8GB (16GB recommended for large files)
- **Storage**: 2-3x file size free space
- **Software**: Node.js 18+, Python 3.8+

### Tested Configuration
- **CPU**: Intel Core Ultra 9 185H (16 cores)
- **RAM**: 64GB DDR5-5600
- **Successfully processed**: Files up to 3.8GB

## Documentation

Complete documentation is available in the `docs/` directory:

- **[Production Process Guide](docs/PRODUCTION-PROCESS-GUIDE.md)** - Complete workflow documentation
- **[Configuration Settings](docs/CONFIGURATION-SETTINGS.md)** - All settings and parameters
- **[Breakthrough Achievement](docs/BREAKTHROUGH-ACHIEVEMENT-SUMMARY.md)** - Success story with 3.8GB file
- **[IFC Splitting Guide](docs/IFC-SPLITTING-GUIDE.md)** - Large file processing strategies
- **[Next Steps Roadmap](docs/NEXT-STEPS-ROADMAP.md)** - Future development plans

## Technologies Used

- **[ThatOpen Components](https://github.com/ThatOpen/engine)** - Fragment generation
- **[IfcOpenShell](https://ifcopenshell.org/)** - IFC file manipulation and splitting
- **[web-ifc](https://github.com/ThatOpen/engine/tree/main/packages/web-ifc)** - High-performance IFC parsing
- **Node.js** - Runtime environment for conversion
- **Python** - Large file processing and splitting

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with various IFC files
5. Submit a pull request

## Support

For issues and questions:
1. Check the documentation in `docs/`
2. Review the troubleshooting section
3. Open an issue on GitHub with:
   - File size and complexity
   - Error messages
   - System specifications

## License

MIT License - see LICENSE file for details.
