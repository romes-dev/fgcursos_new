#!/bin/sh
set -e

echo "==> Aguardando o banco de dados..."
until python -c "
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fgcursos.settings')
django.setup()
from django.db import connection
connection.ensure_connection()
print('Banco disponível.')
" 2>/dev/null; do
  echo "   banco ainda não disponível, aguardando 2s..."
  sleep 2
done

echo "==> Aplicando migrations..."
python manage.py migrate --noinput

echo "==> Coletando arquivos estáticos..."
python manage.py collectstatic --noinput

echo "==> Iniciando Gunicorn..."
exec gunicorn fgcursos.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers ${GUNICORN_WORKERS:-3} \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
