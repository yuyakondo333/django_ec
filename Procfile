web: gunicorn config.wsgi --log-file -
release: ./manage.py migrate --no-input 
&& ./manage.py loaddata products/fixtures/products_data.json
&& ./manage.py promotion_code_generate
