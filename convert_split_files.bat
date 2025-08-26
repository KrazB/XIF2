@echo off
echo ========================================
echo Converting Split IFC Files to Fragments
echo ========================================
echo.

REM Set enhanced Node.js memory options
set NODE_OPTIONS=--max-old-space-size=8192 --expose-gc

echo [MEMORY] Configured Node.js with 8GB memory limit
echo [GC] Garbage collection enabled for memory management
echo.

REM Source and target directories
set SOURCE_DIR=D:\XIF2\data\ifc_split\test_split
set TARGET_DIR=D:\XIF2\data\fragments\split_fragments

echo [SOURCE] %SOURCE_DIR%
echo [TARGET] %TARGET_DIR%
echo.

REM Create target directory if needed
if not exist "%TARGET_DIR%" (
    mkdir "%TARGET_DIR%"
    echo [SETUP] Created fragments directory: %TARGET_DIR%
)

echo [START] Converting split IFC files to fragments...
echo.

REM Change to converter directory
cd /d "D:\XIF2\frag_convert"

REM Convert each chunk file
echo ========================================
echo Converting chunk_001.ifc (255.39 MB)
echo ========================================
node convert_ifc_to_fragments.js "%SOURCE_DIR%\chunk_001.ifc" "%TARGET_DIR%\chunk_001.frag"

if %ERRORLEVEL% EQU 0 (
    echo ✅ chunk_001.ifc converted successfully
) else (
    echo ❌ chunk_001.ifc conversion failed
)
echo.

echo ========================================
echo Converting chunk_002.ifc (391.08 MB)
echo ========================================
node convert_ifc_to_fragments.js "%SOURCE_DIR%\chunk_002.ifc" "%TARGET_DIR%\chunk_002.frag"

if %ERRORLEVEL% EQU 0 (
    echo ✅ chunk_002.ifc converted successfully
) else (
    echo ❌ chunk_002.ifc conversion failed
)
echo.

echo ========================================
echo Converting chunk_003.ifc (206.49 MB)
echo ========================================
node convert_ifc_to_fragments.js "%SOURCE_DIR%\chunk_003.ifc" "%TARGET_DIR%\chunk_003.frag"

if %ERRORLEVEL% EQU 0 (
    echo ✅ chunk_003.ifc converted successfully
) else (
    echo ❌ chunk_003.ifc conversion failed
)
echo.

echo ========================================
echo Converting chunk_004.ifc (231.60 MB)
echo ========================================
node convert_ifc_to_fragments.js "%SOURCE_DIR%\chunk_004.ifc" "%TARGET_DIR%\chunk_004.frag"

if %ERRORLEVEL% EQU 0 (
    echo ✅ chunk_004.ifc converted successfully
) else (
    echo ❌ chunk_004.ifc conversion failed
)
echo.

echo ========================================
echo Converting chunk_005.ifc (1357.59 MB) - LARGEST CHUNK
echo ========================================
echo [WARNING] This is the largest chunk - may take longer...
node convert_ifc_to_fragments.js "%SOURCE_DIR%\chunk_005.ifc" "%TARGET_DIR%\chunk_005.frag"

if %ERRORLEVEL% EQU 0 (
    echo ✅ chunk_005.ifc converted successfully
) else (
    echo ❌ chunk_005.ifc conversion failed
    echo [NOTE] If this chunk fails, try splitting it further or use preprocessing
)
echo.

echo ========================================
echo CONVERSION SUMMARY
echo ========================================
echo.

REM Check results and display summary
set CONVERTED_COUNT=0
set TOTAL_SIZE=0

if exist "%TARGET_DIR%\chunk_001.frag" (
    set /a CONVERTED_COUNT+=1
    for %%I in ("%TARGET_DIR%\chunk_001.frag") do echo chunk_001.frag: %%~zI bytes
)

if exist "%TARGET_DIR%\chunk_002.frag" (
    set /a CONVERTED_COUNT+=1
    for %%I in ("%TARGET_DIR%\chunk_002.frag") do echo chunk_002.frag: %%~zI bytes
)

if exist "%TARGET_DIR%\chunk_003.frag" (
    set /a CONVERTED_COUNT+=1
    for %%I in ("%TARGET_DIR%\chunk_003.frag") do echo chunk_003.frag: %%~zI bytes
)

if exist "%TARGET_DIR%\chunk_004.frag" (
    set /a CONVERTED_COUNT+=1
    for %%I in ("%TARGET_DIR%\chunk_004.frag") do echo chunk_004.frag: %%~zI bytes
)

if exist "%TARGET_DIR%\chunk_005.frag" (
    set /a CONVERTED_COUNT+=1
    for %%I in ("%TARGET_DIR%\chunk_005.frag") do echo chunk_005.frag: %%~zI bytes
)

echo.
echo Converted files: %CONVERTED_COUNT% out of 5
echo Location: %TARGET_DIR%
echo.

if %CONVERTED_COUNT% EQU 5 (
    echo ========================================
    echo 🎉 ALL CONVERSIONS COMPLETED SUCCESSFULLY!
    echo ========================================
    echo.
    echo You now have 5 fragment files that can be loaded in IFC.js viewers.
    echo The original 3.8GB B142-KCX file has been successfully processed!
    echo.
    echo Next steps:
    echo 1. Test individual fragments in viewer
    echo 2. Combine fragments if needed for unified viewing
    echo 3. Deploy for web-based viewing
) else (
    echo ========================================
    echo ⚠️  PARTIAL CONVERSION COMPLETED
    echo ========================================
    echo.
    echo Some files may have failed conversion.
    echo Check the error messages above for details.
    echo Successfully converted files can still be used.
)

echo.
echo Press any key to exit...
pause >nul
