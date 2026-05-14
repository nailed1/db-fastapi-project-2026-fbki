#!/bin/sh
set -e

echo "==> Running migrations..."
python -m app.db.migrate

echo "==> Setting up demo passwords..."
python -m app.db.setup_passwords

echo "==> Starting server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
