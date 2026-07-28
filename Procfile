web: gunicorn tWeb.wsgi:application --chdir tWeb
release: bash -c "cd tWeb && python manage.py migrate --noinput && python manage.py collectstatic --noinput"