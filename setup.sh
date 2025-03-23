#!/bin/bash
cd src

# Check if Poetry is installed
if ! command -v poetry &> /dev/null
then
    echo "Poetry is not installed. Please install Poetry first."
    exit
fi

# Activate the Poetry environment
echo "Activating Poetry virtual environment..."

# This command activates the environment and opens a new shell within it
poetry shell

# You can run additional commands here if needed, for example:
# poetry run <command>