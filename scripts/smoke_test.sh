#!/bin/bash
# Smoke test for MSDS PoC

set -e

echo "Running MSDS PoC smoke tests..."
echo "================================"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python3 is required but not installed"
    exit 1
fi

echo "✓ Python3 is available"

# Install dependencies
echo "Installing dependencies..."
pip install -q -e .

echo "✓ Dependencies installed"

# Run basic tests
echo "Running basic PoC execution..."
python3 -c "
from msds_poc import run_poc
result = run_poc()
print(f'PoC Result: {result}')
assert result['status'] == 'success', 'PoC execution failed'
"

echo "✓ Basic PoC execution passed"

# Check directory structure
echo "Verifying directory structure..."
for dir in input output assets; do
    if [ ! -d "$dir" ]; then
        echo "ERROR: Missing directory: $dir"
        exit 1
    fi
    echo "✓ Directory exists: $dir"
done

echo ""
echo "================================"
echo "All smoke tests passed! ✓"
echo "================================"
