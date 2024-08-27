@echo off
setlocal

echo.
echo Welcome! This is the installer script of Amazon IT Price Tracker for the Windows platform.
echo.
set "input="
set /p "input=Press ENTER to install all the dependencies"

if "%input%"=="" (
    echo.
    echo Searching for Python 3...
    echo.
    :: Attempt to find Python
    set PYTHON_CMD=
    for %%P in (python python3 py) do (
        for /f "delims=" %%I in ('where %%P 2^>nul') do (
            set PYTHON_CMD=%%I
            goto :found_python
        )
    )

:found_python
if "%PYTHON_CMD%"=="" (
    echo Python 3 is not installed! Please try again.
    exit /b 1
)

echo Python 3 successfully found at: %PYTHON_CMD%
echo.
echo Checking Python 3 version...

:: Verify the Python version
%PYTHON_CMD% --version
%PYTHON_CMD% --version 2>nul | findstr /r "Python 3\.[0-9]+\.[0-9]*" >nul
if %ERRORLEVEL% NEQ 0 (
    echo Python 3 is not correctly installed or is an incompatible version! Please try again.
    exit /b 1
)

:: Install the requirements
if not exist "requirements.txt" (
    echo requirements.txt does not exist! Please try again.
    exit /b 1
)
echo.
echo Upgrading pip and installing dependencies...
pip install --upgrade pip
pip install -r requirements.txt
echo Starting main.py...
:: Start main.py
if exist "main.py" (
    %PYTHON_CMD% main.py
) else (
    echo main.py does not exist! Please try again.
)

echo Setup completed!
) else (
    set "input="
    echo.
    exit /b 1
)
