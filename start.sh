#!/bin/bash
set -e

cd project-registry
pip install -r requirements.txt
exec uvicorn backend.main:app --host 0.0.0.0 --port "${PORT:-8000}"
