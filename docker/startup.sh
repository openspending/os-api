#!/bin/sh
set -e

cd /app
echo OS-API DB: $OS_API_ENGINE

gunicorn -t 120 -w 4 os_api.app:app -b 0.0.0.0:8000
