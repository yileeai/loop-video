@echo off
setlocal
rem Usage: install.bat            -> %USERPROFILE%\.claude\skills (all folders)
rem        install.bat "D:\vault" -> that folder only
if "%~1"=="" (
  set "DEST=%USERPROFILE%\.claude\skills"
) else (
  set "DEST=%~1\.claude\skills"
)
if not exist "%DEST%" mkdir "%DEST%"
robocopy "%~dp0skills" "%DEST%" /E /NFL /NDL /NJH /NJS >nul
if not "%~1"=="" if exist "%~1\_claude-skills" robocopy "%~dp0skills" "%~1\_claude-skills" /E /NFL /NDL /NJH /NJS >nul
echo.
echo Done: video skills installed to %DEST%
echo Needs Python 3, Pillow 10+, FFmpeg. Restart Claude Code, then try /speech-motion-edit
endlocal
exit /b 0
