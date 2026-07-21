@echo off
setlocal

cd /d "%~dp0"

where pythonw >nul 2>nul
if not errorlevel 1 (
  start "" pythonw .\run_loveca_app.py --window-mode app
  exit /b 0
)

where pyw >nul 2>nul
if not errorlevel 1 (
  start "" pyw -3 .\run_loveca_app.py --window-mode app
  exit /b 0
)

echo Starting Loveca Application...

python .\run_loveca_app.py --window-mode app
if not errorlevel 1 (
  exit /b 0
)

echo.
echo Python command failed. Trying Windows py launcher...
py -3 .\run_loveca_app.py --window-mode app
if not errorlevel 1 (
  exit /b 0
)

echo.
echo Failed to start Loveca Application.
echo Please install Python 3 and enable "Add python.exe to PATH".
echo https://www.python.org/downloads/
echo.
pause
exit /b 1
