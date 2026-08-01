#!/usr/bin/env sh
set -eu

case "${1:-serve}" in
  migrate)
    exec python manage.py migrate --noinput
    ;;
  serve)
    exec gunicorn advanced_hello_world.wsgi:application \
      --bind 0.0.0.0:8000 \
      --workers "${GUNICORN_WORKERS:-2}" \
      --access-logfile -
    ;;
  *)
    exec "$@"
    ;;
esac

