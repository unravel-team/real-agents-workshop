@echo off
setlocal enabledelayedexpansion

REM Try python3 first, then python
set PYTHON=
where python3 >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON=python3
    goto :check_version
)

where python >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON=python
    goto :check_version
)

echo ERROR: Python is not installed or not in PATH.
echo Please install Python 3.11+: https://www.python.org/downloads/
exit /b 1

:check_version
for /f "tokens=2 delims= " %%v in ('!PYTHON! --version 2^>^&1') do set PYVER=%%v
for /f "tokens=1,2 delims=." %%a in ("!PYVER!") do (
    if %%a LSS 3 goto :version_error
    if %%a EQU 3 if %%b LSS 11 goto :version_error
)

!PYTHON! "%~dp0validate_setup.py" %*
exit /b %errorlevel%

:version_error
echo ERROR: Python 3.11+ is required. Found: %PYVER%
echo Please install Python: https://www.python.org/downloads/
exit /b 1
