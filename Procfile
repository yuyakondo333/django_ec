web: gunicorn config.wsgi --log-file -
release: /manage.py promotion_code_generate
&&./manage.py migrate --no-input
