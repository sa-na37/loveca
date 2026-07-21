@echo off
setlocal

cd /d "%~dp0"

set "PYTHON_BIN=python"
where "%PYTHON_BIN%" >nul 2>nul
if errorlevel 1 (
  set "PYTHON_BIN=py -3"
)

echo Loveca Application を起動しています...
%PYTHON_BIN% .\run_loveca_app.py --window-mode app

if errorlevel 1 (
  echo.
  echo 起動に失敗しました。
  echo Python 3 がインストールされているか確認してください。
  echo https://www.python.org/downloads/
  echo.
  pause
)
