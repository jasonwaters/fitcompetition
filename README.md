Fit Crown
=========

A django based web application used to track exercise challenges and display a leaderboard based on workout activities entered in [Runkeeper](http://runkeeper.com), [MapMyFitness](http://www.mapmyfitness.com) or [Strava](http://strava.com).

Project Setup
---------------  
1. Clone the repository
2. Create the virtual environment

  ```bash
  virtualenv --no-site-packages env
  ```
  or
  ```bash
  virtualenv env -p /usr/local/bin/python --no-site-packages
  ```  
3. Install node and lessc dependency for compiling .less files

  ```bash
  source env/bin/activate
  pip install nodeenv
  nodeenv --python-virtualenv
  npm install -g less
  ```

3. Install dependencies
  ```bash
  pip install -r requirements.pip
  ```  

4. Copy the local_settings.py.template file to local_settings.py and modify it accordingly.

5. Server side, install nginx or apache and configure a proxy to uwsgi or gunicorn.

6. For development just run the management script for a test server
  ```bash
  ./manage.py runserver 0.0.0.0:8000 --insecure
  ```  

7. Set up celery and celerybeat to work with RabbitMQ.
  ```bash
  celery -A fitcompetition worker --loglevel=INFO
  ```  


Testing
-------
There is a test suite with unit and integration tests.  The suite can be run by:
```bash
./manage.py test fitcompetition/tests
```



Dependencies
------------

[Django](https://www.djangoproject.com) is the web framework that makes rapid and clean development of this application possible.

[RabbitMQ](http://www.rabbitmq.com) is a message broker that makes it possible to add tasks to a queue.

[Celery](http://celery.readthedocs.org/en/latest/index.html) is a simple, flexible and reliable distributed task queue.  It does the heavy lifting to add tasks to the queue and prioritize the execution of them.  Relies on RabbitMQ.

see requirements.pip
