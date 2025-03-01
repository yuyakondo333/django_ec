release: ./manage.py makemigrations order
&& ./manage.py migrate --no-input 
&& ./manage.py loaddata products/fixtures/products_data.json
&& ./manage.py promotion_code_generate
