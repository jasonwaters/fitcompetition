from datetime import datetime
import logging
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template import Context
from django.template.loader import render_to_string
from fitcompetition.util.ListUtil import createListFromProperty
import pytz


class EmailFactory(object):
    def __init__(self):
        self.FROM = "FitCrown<contact@fitcrown.com>"

    def _emailable(self, user):
        return user.email and len(user.email) > 0

    def cashWithdrawal(self, user, paypalEmailAddress, value):
        if self._emailable(user):
            playerEmail = Email(to=user.email, subject="Your cash is on it's way!")
            systemEmail = Email(to=getattr(settings, "PAYPAL_ACCOUNT_EMAIL"), subject="%s is cashing out" % user.first_name)

            context = Context({
                'user': user,
                'email': paypalEmailAddress,
                'value': value
            })

            playerEmail.html('email/cashWithdrawal_player.html', context)
            systemEmail.html('email/cashWithdrawal_system.html', context)

            playerEmail.send(self.FROM)
            systemEmail.send()

    def challengeJoin(self, user, challenge):
        if self._emailable(user):
            email = Email(to=user.email, subject='You joined "%s"' % challenge.name)

            approvedTypes = challenge.approvedActivities.all()

            context = Context({
                'challenge': challenge,
                'user': user,
                'approvedActivities': createListFromProperty(approvedTypes, 'name'),
            })

            email.html("email/challenge_joined.html", context)
            email.send(self.FROM)

    def challengeStart(self, user, challenge):
        email = Email(to=user.email, subject="The challenge has begun!")

        approvedTypes = challenge.approvedActivities.all()

        context = Context({
            'challenge': challenge,
            'user': user,
            'approvedActivities': createListFromProperty(approvedTypes, 'name'),
        })

        email.html("email/challenge_start.html", context)
        email.send(self.FROM)

    def challengeHalf(self, user, challenge):
        email = Email(to=user.email, subject="The challenge is half over!")

        context = Context({
            'challenge': challenge,
            'user': user,
            'achievedGoal': challenge.getAchievedGoal(user)
        })

        email.html("email/challenge_half.html", context)
        email.send(self.FROM)

    def challengeEnd(self, user, challenge, upcomingChallenges, isWinner):
        email = Email(to=user.email, subject="The challenge is over!")

        context = Context({
            'challenge': challenge,
            'user': user,
            'achievedGoal': challenge.getAchievedGoal(user),
            'isWinner': isWinner,
            'upcomingChallenges': upcomingChallenges
        })

        email.html("email/challenge_end.html", context)
        email.send(self.FROM)

    def cashDeposit(self, transaction, account, user):
        email = Email(to=user.email, subject="Your payment was received")

        context = Context({
            'transaction': transaction,
            'user': user,
            'account': account
        })

        email.html("email/cashDeposit.html", context)
        email.send(self.FROM)


class Email(object):
    def __init__(self, to, subject):
        self.logger = logging.getLogger(__name__)
        self.to = to
        self.subject = subject
        self._html = None
        self._text = None

    def _render(self, template, context):
        context['now'] = datetime.now(tz=pytz.utc)
        context['message_title'] = self.subject

        try:
            output = render_to_string(template, context)
        except Exception, e:
            self.logger.error(e)
            output = ""

        return output

    def html(self, template, context):
        self._html = self._render(template, context)

    def text(self, template, context):
        self._text = self._render(template, context)

    def send(self, from_addr=None, fail_silently=False):
        if isinstance(self.to, basestring):
            self.to = [self.to]

        if not from_addr:
            from_addr = getattr(settings, "SERVER_EMAIL")

        msg = EmailMultiAlternatives(
            self.subject,
            self._text,
            from_addr,
            self.to
        )

        if self._html:
            msg.attach_alternative(self._html, 'text/html')

        msg.send(fail_silently)
