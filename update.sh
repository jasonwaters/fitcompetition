source env/bin/activate
pip install -r requirements.pip
rm -rf static/*
python manage.py collectstatic --noinput
python manage.py syncdb
python manage.py migrate
