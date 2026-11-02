@echo off
setlocal
cd /d "%~dp0.."
if exist ".venv\Scripts\python.exe" goto venv
py -3 --version >nul 2>&1
if not errorlevel 1 goto pylauncher
python --version >nul 2>&1
if not errorlevel 1 goto python
echo Python fehlt. Bitte Python 3 installieren und diese Datei danach erneut oeffnen.
pause
exit /b 1
:venv
".venv\Scripts\python.exe" -X utf8 "%~dp0start_local.py" %*
goto result
:pylauncher
py -3 -X utf8 "%~dp0start_local.py" %*
goto result
:python
python -X utf8 "%~dp0start_local.py" %*
:result
set "local_start_result=%errorlevel%"
if "%local_start_result%"=="0" exit /b 0
echo.
echo Der Start wurde abgebrochen. Bitte die Meldung oben beachten.
pause
exit /b %local_start_result%
