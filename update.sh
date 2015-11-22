source env/bin/activate
pip install -r requirements.pip
python manage.py collectstatic --noinput
python manage.py migrate --fake-initial --noinput
