from django.http import HttpResponseRedirect
from social_auth.db.django_models import UserSocialAuth


def first_name(request, *args, **kwargs):
    if 'saved_first_name' in request.session:
        user = kwargs['user']
        user.first_name = request.session.get('saved_first_name')
        user.save()


def get_username(details, user=None,
                 user_exists=UserSocialAuth.simple_user_exists,
                 *args, **kwargs):
    """Return an username for new user. Return current user username
    if user was given.
    """
    if user:
        return {'username': UserSocialAuth.user_username(user)}


    return {'username': unicode(details['username'])}