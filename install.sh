#!/bin/bash

# Install system dependencies
sudo apt-get update
sudo apt-get install -y python3-gi python3-gi-cairo gir1.2-gtk-3.0

# Create a virtual environment with access to system site packages
python3 -m venv venv --system-site-packages

# Activate the virtual environment and install python packages
source venv/bin/activate
pip install -r requirements.txt

# Create a .env file from the example
cp .env.example .env

echo "Installation complete. Please edit the .env file to add your API key."
