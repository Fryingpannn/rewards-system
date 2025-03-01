#!/bin/bash
set -e

if [ "$1" = "test" ]; then
    python -m unittest discover tests/
else
    # Use PORT environment variable in the Flask application
    python -c "from main import app; app.run(host='0.0.0.0', port=int('$PORT'))"
fi
