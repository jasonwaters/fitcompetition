# from django.conf import settings
from django.contrib.auth.models import User, Group
# from django_openid_auth.exceptions import IdentityAlreadyClaimed
# from openid.consumer.consumer import SUCCESS


class RunkeeperBackend(object):
    def authenticate(self, openid_response, **kwargs):
        # if openid_response is None:
        #     return None
        # if openid_response.status != SUCCESS:
        #     return None
        #
        # google_email = openid_response.getSigned('http://openid.net/srv/ax/1.0',  'value.email')
        # google_firstname = openid_response.getSigned('http://openid.net/srv/ax/1.0', 'value.firstname')
        # google_lastname = openid_response.getSigned('http://openid.net/srv/ax/1.0', 'value.lastname')
        #
        # acceptable_account = False
        #
        # if not acceptable_account:
        #     for account in settings.GOOGLE_OPENID_WHITELIST_ACCOUNTS:
        #         if google_email == account:
        #             acceptable_account = True
        #
        # if not acceptable_account:
        #     for domain in settings.GOOGLE_OPENID_WHITELIST_DOMAINS:
        #         if google_email.endswith(domain):
        #             acceptable_account = True
        #
        # if not acceptable_account:
        #     raise IdentityAlreadyClaimed('Please log in with your %s email address to authenticate.' % ENTITY_NAME)
        #
        # try:
        #     #user = User.objects.get(username=google_email)
        #     # Make sure that the e-mail is unique.
        #     user = User.objects.get(email=google_email)
        # except User.DoesNotExist:
        #     user = User.objects.create_user(google_email, google_email, 'password')
        #     user.first_name = google_firstname
        #     user.last_name = google_lastname
        #     user.is_staff = True
        #     salesGroup, created = Group.objects.get_or_create(name="Sales")
        #     user.groups.add(salesGroup)
        #     user.save()
        #     user = User.objects.get(username=google_email)
        #     return user
        #
        return None

    # def get_user(self, user_id):
    #     try:
    #         return User.objects.get(pk=user_id)
    #     except User.DoesNotExist:
    #         return None