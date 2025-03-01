web: gunicorn config.wsgi --log-file -
release: ./manage.py promotion_code_generate
&& ./manage.py migrate --no-input 
&& ./manage.py loaddata products/fixtures/products_data.json
