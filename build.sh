#!/usr/bin/env bash

# --- build.sh pour Render ou Railway ---

echo "📦 Application des migrations..."
python manage.py makemigrations
python manage.py migrate

echo "🧱 Collecte des fichiers statiques..."
python manage.py collectstatic --noinput
