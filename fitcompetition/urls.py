from django.conf.urls import patterns, include, url
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from django.views.generic import RedirectView

admin.autodiscover()

urlpatterns = patterns('',
                       url(r'^grappelli/', include('grappelli.urls')),
                       url(r'', include('social_auth.urls')),

                       url(r'^$', 'fitcompetition.views.home', name='home'),
                       url(r'^c/(?P<id>\d+)/$', 'fitcompetition.views.challenge', name="challenge_details"),
                       url(r'^c/join/(?P<id>\d+)/$', 'fitcompetition.views.join_challenge', name="join_challenge"),
                       url(r'^c/refresh-user-activities/$', 'fitcompetition.views.refresh_user_activities', name="refresh_user_activities"),

                       url(r'^login/$', 'fitcompetition.views.login', name="login"),
                       url(r'^logout/$', 'django.contrib.auth.views.logout', {'next_page': '/', }, name='logout'),
                       url(r'^login-error/$', 'fitcompetition.views.login_error'),

                       url(r'^useractivities/(?P<userID>\d+)/(?P<challengeID>\d+)/$', 'fitcompetition.views.user_activities', name="useractivities"),
                       url(r'^admin/', include(admin.site.urls)),
)
