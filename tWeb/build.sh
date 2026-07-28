#!/usr/bin/env bash
#
# Build script for cloud hosts (Render, PythonAnywhere, Heroku, etc.).
# Run from the Django project root (tWeb/).
#
# Note: TA-Lib is NOT needed — the views use pure pandas for indicators.
#
set -euo pipefail

echo "==> 1. Installing Python dependencies from requirements.txt"
pip install --upgrade pip
pip install -r requirements.txt

echo "==> 2. Collecting static files"
python manage.py collectstatic --noinput

echo "==> 3. Applying database migrations"
python manage.py migrate --noinput

echo "==> BUILD COMPLETE"