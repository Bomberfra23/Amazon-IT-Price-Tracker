@echo off
setlocal


echo.
echo Welcome! this is the installer script of Amazon IT Price Tracker for Windows platform.
echo.
set "input="
set /p "input=Press ENTER to install all the dependencies"

if "%input%"=="" (
    echo.
    echo finding Python 3 ...
    echo.
    :: Tentare di trovare Python
set PYTHON_CMD=
for %%P in (python python3 py) do (
    for /f "delims=" %%I in ('where %%P 2^>nul') do (
        set PYTHON_CMD=%%I
        goto :found_python
    )
)

:found_python
if "%PYTHON_CMD%"=="" (
    echo Python 3 not installed! try again.
    exit /b 1
)

echo Python 3 successfully finded in: %PYTHON_CMD%
echo.
echo checking Python 3 version...

:: Verificare la versione di Python
%PYTHON_CMD% --version
%PYTHON_CMD% --version 2>nul | findstr /r "Python 3\.[0-9]+\.[0-9]*" >nul
if %ERRORLEVEL% NEQ 0 (
    echo Python 3 is not correctly installed or is an incompatible version! try again.
    exit /b 1
)

:: Installare i requisiti
if not exist "requirements.txt" (
    echo requirements.txt does not exists! try again.
    exit /b 1
)
echo.
echo upgrading pip and installing dependencies...
pip install --upgrade pip
pip install -r requirements.txt
echo starting main.py...
:: Avviare main.py
if exist "main.py" (
    %PYTHON_CMD% main.py
) else (
    echo main.py does not exists! try again.
)

echo Setup completed!
) else (
    set "input="
    echo.
    exit /b 1
)

