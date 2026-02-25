#!/usr/bin/env bash
set -euo pipefail

# Resolve the directory containing this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Find a Python >= 3.11
find_python() {
    for candidate in python3 python; do
        if command -v "$candidate" &> /dev/null; then
            version_output=$("$candidate" --version 2>&1)
            version=$(echo "$version_output" | grep -oE '[0-9]+\.[0-9]+' | head -1)
            major=$(echo "$version" | cut -d. -f1)
            minor=$(echo "$version" | cut -d. -f2)
            if [ "$major" -ge 3 ] && [ "$minor" -ge 11 ]; then
                echo "$candidate"
                return 0
            fi
        fi
    done
    return 1
}

PYTHON=$(find_python) || {
    echo "ERROR: Python 3.11+ is required but not found."
    echo "Please install Python: https://www.python.org/downloads/"
    exit 1
}

exec "$PYTHON" "$SCRIPT_DIR/validate_setup.py" "$@"
