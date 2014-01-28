from datetime import datetime
from fitcompetition.celery import app
from fitcompetition.email import Email
import pytz


@app.task(ignore_result=True)
def emailme():
    email = Email(to='jason@myheck.net', subject="This is a periodic test")

    now = datetime.now(tz=pytz.utc)

    ctxt = {
        'first_name': 'Jason',
        'now': now
    }

    email.text("email/test.txt", ctxt)
    email.html("email/test.html", ctxt)
    email.send("FitCrown<contact@fitcrown.com>")
