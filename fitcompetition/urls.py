from django.conf.urls import patterns, include, url
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from django.views.generic import RedirectView

admin.autodiscover()

urlpatterns = patterns('',
                       url(r'^grappelli/', include('grappelli.urls')),
                       url(r'', include('social_auth.urls')),

                       url(r'^$', 'fitcompetition.views.home', name='home'),
                       url(r'c/(?P<id>\d+)/$', 'fitcompetition.views.challenge', name="challenge_details"),
                       url(r'login/$', 'fitcompetition.views.login', name="login"),
                       url(r'^logout/$', 'django.contrib.auth.views.logout', {'next_page': '/', }, name='logout'),
                       # url(r'login/$', RedirectView.as_view(url='/login/runkeeper'), name='login-runkeeper'),
                       url(r'login-error/$', 'fitcompetition.views.login_error'),

                       url(r'^admin/', include(admin.site.urls)),
)
