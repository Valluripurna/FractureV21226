@echo off
setlocal

REM Prepare LaTeX for Pandoc (simplify image macros and normalize math)
python "%~dp0export_to_word.py" || goto :error

REM Convert to Word .docx using Pandoc
REM Requires: Pandoc installed (https://pandoc.org/installing.html)
REM Optional: Use CSL for IEEE citations via online style
set PANDOC_STYLE=https://www.zotero.org/styles/ieee

REM Resolve pandoc exe (PATH or local user install)
set PANDOC_EXE=pandoc
where pandoc >nul 2>&1
if errorlevel 1 if exist "%LOCALAPPDATA%\Pandoc\pandoc.exe" set PANDOC_EXE="%LOCALAPPDATA%\Pandoc\pandoc.exe"

REM Use reference.docx if present to preserve Word styles
set REF_DOC="%~dp0reference.docx"
if not exist %REF_DOC% set REF_DOC=

if defined REF_DOC (
	%PANDOC_EXE% "%~dp0fracturedetect_ai_paper_word.tex" -s --citeproc --bibliography="%~dp0references.bib" --csl=%PANDOC_STYLE% --resource-path=%~dp0;%~dp0figures --reference-doc=%REF_DOC% -o "%~dp0fracturedetect_ai_paper.docx" || goto :error
) else (
	%PANDOC_EXE% "%~dp0fracturedetect_ai_paper_word.tex" -s --citeproc --bibliography="%~dp0references.bib" --csl=%PANDOC_STYLE% --resource-path=%~dp0;%~dp0figures -o "%~dp0fracturedetect_ai_paper.docx" || goto :error
)

REM Post-process DOCX to split sections and format references
python "%~dp0postprocess_docx.py" || goto :error

echo.
echo Export complete: %~dp0fracturedetect_ai_paper.docx
exit /b 0

:error
echo.
echo Export failed. Ensure Python and Pandoc are installed and on PATH.
exit /b 1
