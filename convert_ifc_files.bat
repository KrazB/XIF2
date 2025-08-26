@echo off
setlocal enabledelayedexpansion

echo.
echo ========================================
echo   IFC to Fragments Converter
echo ========================================
echo.

REM Check if argument provided
if "%~1"=="" (
    echo Usage: Drag and drop IFC files or folders onto this batch file
    echo Or run: convert_ifc_files.bat "path\to\ifc\files"
    echo.
    echo Examples:
    echo   - Drag a folder containing IFC files onto this file
    echo   - Drag individual IFC files onto this file
    echo   - Run: convert_ifc_files.bat "C:\MyProject\IFC_Files"
    echo.
    pause
    exit /b 1
)

REM Check if input exists
if not exist "%~1" (
    echo ERROR: Path not found: %~1
    echo.
    pause
    exit /b 1
)

echo Converting: %~1
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    echo.
    pause
    exit /b 1
)

REM Check if Node.js is installed  
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js is not installed or not in PATH
    echo Please install Node.js 18+ from https://nodejs.org
    echo.
    pause
    exit /b 1
)

REM Get the directory where this batch file is located
set "SCRIPT_DIR=%~dp0"
set "CONVERTER_PATH=%SCRIPT_DIR%frag_convert\ifc_fragments_converter.py"

REM Check if converter exists
if not exist "%CONVERTER_PATH%" (
    echo ERROR: IFC converter not found at: %CONVERTER_PATH%
    echo Please ensure the frag_convert folder is in the same directory as this batch file.
    echo.
    pause
    exit /b 1
)

echo Starting conversion...
echo Input: %~1
echo.

REM Check if it's a single IFC file
if /i "%~x1"==".ifc" (
    REM Single file - extract directory and filename
    set "INPUT_DIR=%~dp1"
    set "FILENAME=%~nx1"
    echo Converting single file: !FILENAME!
    echo From directory: !INPUT_DIR!
    echo.
    
    REM Remove trailing slash from directory path
    if "!INPUT_DIR:~-1!"=="\" set "INPUT_DIR=!INPUT_DIR:~0,-1!"
    
    REM Run converter for single file
    python "%CONVERTER_PATH%" "!INPUT_DIR!" --single "!FILENAME!" --auto
) else (
    REM Directory - convert all IFC files
    echo Converting all IFC files in directory: %~1
    echo.
    
    REM Run converter for directory
    python "%CONVERTER_PATH%" "%~1" --auto
)

REM Check conversion result
if errorlevel 1 (
    echo.
    echo ❌ Conversion failed! Check the output above for error details.
    echo.
) else (
    echo.
    echo ✅ Conversion completed successfully!
    echo Fragment files (.frag) have been created.
    echo.
    if exist "%~1\*.frag" (
        echo Fragment files created in: %~1
    ) else (
        echo Check the converter output above for file locations.
    )
    echo.
)

echo Press any key to close this window...
pause >nul
