from datetime import datetime
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
import pytz


class Email(object):
    def __init__(self, to, subject):
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
