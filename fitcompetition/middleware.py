from django.shortcuts import render
from social.apps.django_app.middleware import SocialAuthExceptionMiddleware
from social import exceptions as social_exceptions


class SocialAuthExceptionMiddleware(SocialAuthExceptionMiddleware):
    def process_exception(self, request, exception):
        if hasattr(social_exceptions, exception.__class__.__name__):
            return render(request, 'error.html', {
                'errorMessage': 'There was an authentication error.',
                'errorDetails': str(exception)
            })
            # else:
            #     raise exception
