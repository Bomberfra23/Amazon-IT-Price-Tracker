#!/bin/bash

echo
echo "Welcome! This is the installer script of Amazon IT Price Tracker for the Linux platform."
echo

read -p "Press ENTER to install all the dependencies"

echo
echo "Searching for Python 3..."
echo

# Attempt to find Python
PYTHON_CMD=$(command -v python3 || command -v python || command -v py)

if [ -z "$PYTHON_CMD" ]; then
    echo "Python 3 is not installed! Please try again."
    exit 1
fi

echo "Python 3 successfully found at: $PYTHON_CMD"
echo
echo "Checking Python 3 version..."

# Verify the Python version
PYTHON_VERSION=$($PYTHON_CMD --version 2>&1)
if [[ ! $PYTHON_VERSION =~ Python\ 3\.[0-9]+\.[0-9]* ]]; then
    echo "Python 3 is not correctly installed or is an incompatible version! Please try again."
    exit 1
fi

# Install the requirements
if [ ! -f "requirements.txt" ]; then
    echo "requirements.txt does not exist! Please try again."
    exit 1
fi

echo
echo "Upgrading pip and installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Starting main.py..."
# Start main.py
if [ -f "main.py" ]; then
    $PYTHON_CMD main.py
else
    echo "main.py does not exist! Please try again."
fi

echo "Setup completed!"