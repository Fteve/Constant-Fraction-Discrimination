#!/bin/bash

# Stops the script if any command fails
# set -e

echo "Activating virtual environment...
"
source venv/bin/activate

cd ./Simulation

echo "Checking and installing required packages...
"
pip install numpy scipy plotly dash
echo "
Package checks complete!
"


echo "Running simulation web app...
"
python cfd_app.py

cd ..
read -p "Press enter to exit..."
