#!/usr/bin/env bash
#
# Build script for Render (and most Linux PaaS hosts).
# Run from the Django project root (tWeb/).
#
set -euo pipefail

echo "==> 1. Installing Python dependencies from requirements.txt"
pip install --upgrade pip
pip install -r requirements.txt

echo "==> 2. Installing TA-Lib C library + Python wrapper"
# TA-Lib's C library isn't on PyPI, so we compile it from source.
# This is the canonical, reliable way on Debian/Ubuntu-based build images.
if ! python -c "import talib" 2>/dev/null; then
    curl -sSL https://github.com/TA-Lib/ta-lib/releases/download/v0.4.0/ta-lib-0.4.0-src.tar.gz -o /tmp/talib.tar.gz
    tar -xzf /tmp/talib.tar.gz -C /tmp
    cd /tmp/ta-lib-0.4.0
    ./configure --prefix=/usr
    make -j"$(nproc)"
    make install
    cd -
    pip install TA-Lib==0.4.32
fi
python -c "import talib; print('TA-Lib OK', talib.__ta_version__)"

echo "==> 3. Collecting static files"
python manage.py collectstatic --noinput

echo "==> 4. Applying database migrations"
python manage.py migrate --noinput

echo "==> BUILD COMPLETE"