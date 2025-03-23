#!/bin/bash

# Navigate to src directory
cd ../src

# Check if we are in the correct directory
echo "Current directory: $(pwd)"

# Find all Python files in the current directory and all subdirectories, and run autoflake to remove unused imports
autoflake --in-place --remove-unused-variables --remove-all-unused-imports --recursive .

# Find all Python files in the current directory and all subdirectories, and run autopep8 on them
autopep8 --in-place --aggressive --recursive .

# Print a message indicating completion
echo "autopep8 ran successfully on all Python files."