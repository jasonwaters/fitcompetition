from datetime import datetime
from fitcompetition.celery import app
from fitcompetition.email import Email
import pytz


@app.task(ignore_result=True)
def hourly():
    email = Email(to='jason@myheck.net', subject="This is an hourly test")

    now = datetime.now(tz=pytz.utc)

    ctxt = {
        'first_name': 'Jason',
        'now': now
    }

    email.html("email/test.html", ctxt)
    email.send("FitCrown<contact@fitcrown.com>")

@app.task(ignore_result=True)
def daily():
    email = Email(to='jason@myheck.net', subject="This is a daily test")

    now = datetime.now(tz=pytz.utc)

    ctxt = {
        'first_name': 'Jason',
        'now': now
    }

    email.html("email/test.html", ctxt)
    email.send("FitCrown<contact@fitcrown.com>")
