@echo off
echo ========================================
echo   XIF2 Repository Cleanup for GitHub
echo ========================================
echo.
echo This will remove large files while preserving:
echo - Core conversion tools and scripts
echo - Small demo/test IFC files
echo - Generated fragment files (optimized outputs)
echo - Documentation
echo.
echo FILES TO BE REMOVED:
echo.
echo Large IFC files (over 100MB):
echo - COPY_IFC_FILE_TEST.ifc (4.0 GB test file)
echo - B142-KCX-ZZ-ZZ-M-X-0001.ifc (4.0 GB)
echo - B142-KCX_preprocessed.ifc (3.9 GB)
echo - 230221-WDHB-MCWH-AR-KLE-MDL-Architecture-RVT21.ifc (1.2 GB)
echo - Mason Clinic files (660 MB)
echo - Village files (463 MB)
echo.
echo Split files:
echo - All files in frag_convert\splits\ (6.6 GB)
echo - All files in data\ifc_split\ (2.5 GB)
echo.
echo FILES TO BE KEPT:
echo - Small test file: 3-0000-112-SBD-30-MD-0001_GDA2020.ifc (3.5 MB)
echo - Fragment files: data\fragments\*.frag (130 MB total)
echo - All core tools and documentation
echo.
pause
echo.
echo Starting cleanup...

REM Remove large IFC files (keep small test file)
echo Removing large IFC files...
del "data\ifc\COPY_IFC_FILE_TEST.ifc" 2>nul
del "data\ifc\B142-KCX-ZZ-ZZ-M-X-0001.ifc" 2>nul
del "data\ifc\B142-KCX_preprocessed.ifc" 2>nul
del "data\ifc\230221-WDHB-MCWH-AR-KLE-MDL-Architecture-RVT21.ifc" 2>nul
del "data\ifc\Mason Clinic E Tu Wairua Hinengaro - Structural Model.ifc" 2>nul
del "data\ifc\Mason_Clinic - SBC.ifc" 2>nul
del "data\ifc\Village_ARCH_Building C_R22-1_detached.ifc" 2>nul
del "data\ifc\Village_STR_Building C_R22-2023.01.27.ifc" 2>nul

REM Remove split files
echo Removing split files...
rmdir /s /q "data\ifc_split" 2>nul
rmdir /s /q "frag_convert\splits" 2>nul

REM Remove large fragment files but keep small ones as examples
echo Removing large fragment files (keeping small examples)...
del "data\fragments\chunk_001.frag" 2>nul
del "data\fragments\chunk_002.frag" 2>nul
del "data\fragments\chunk_003.frag" 2>nul

echo.
echo ========================================
echo   CLEANUP COMPLETE
echo ========================================
echo.
echo Repository is now GitHub-ready with:
echo - Core conversion tools preserved
echo - Small demo file preserved (3.5 MB)
echo - Example fragment files preserved (~75 MB)
echo - All documentation preserved
echo.
echo Ready for: git add . && git commit && git push
echo.
pause
