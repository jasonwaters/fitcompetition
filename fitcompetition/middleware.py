from django.shortcuts import render
from social.apps.django_app.middleware import SocialAuthExceptionMiddleware
from social import exceptions as social_exceptions
from django.conf import settings
from django.http import HttpResponsePermanentRedirect


class SocialAuthExceptionMiddleware(SocialAuthExceptionMiddleware):
    def process_exception(self, request, exception):
        if hasattr(social_exceptions, exception.__class__.__name__):
            return render(request, 'error.html', {
                'errorMessage': 'There was an authentication error.',
                'errorDetails': str(exception)
            })
        # else:
        #     raise exception


SSL = 'SSL'


class SSLRedirect:
    def process_view(self, request, view_func, view_args, view_kwargs):
        if SSL in view_kwargs:
            secure = view_kwargs[SSL]
            del view_kwargs[SSL]
        else:
            secure = False

        if getattr(settings, "SSL_ENABLED") and not secure == self._is_secure(request):
            return self._redirect(request, secure)
        else:
            return

    def _is_secure(self, request):
        if request.is_secure():
            return True

        #Handle the Webfaction case until this gets resolved in the request.is_secure()
        if 'HTTP_X_FORWARDED_SSL' in request.META:
            return request.META['HTTP_X_FORWARDED_SSL'] == 'on'

        return False

    def _redirect(self, request, secure):
        protocol = secure and "https" or "http"
        newurl = "%s://%s%s" % (protocol, request.get_host(), request.get_full_path())
        if settings.DEBUG and request.method == 'POST':
            raise RuntimeError("Django can't perform a SSL redirect while maintaining POST data.  Please structure your views so that redirects only occur during GETs.")


        return HttpResponsePermanentRedirect(newurl)