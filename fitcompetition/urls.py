from django.conf.urls import patterns, include, url
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
                       url(r'^grappelli/', include('grappelli.urls')),
                       url(r'', include('social_auth.urls')),

                       url(r'^$', 'fitcompetition.views.home', name='home'),
                       url(r'^c/(?P<id>\d+)/$', 'fitcompetition.views.challenge', name="challenge_details"),
                       url(r'^profile/$', 'fitcompetition.views.profile', name="user_profile"),
                       url(r'^user/(?P<id>\d+)/$', 'fitcompetition.views.user', name="user_details"),
                       url(r'^update-user-details/$', 'fitcompetition.views.user_details_update', name="user_details_update"),
                       url(r'^c/join/(?P<id>\d+)/$', 'fitcompetition.views.join_challenge', name="join_challenge"),
                       url(r'^c/withdraw/(?P<id>\d+)/$', 'fitcompetition.views.withdraw_challenge', name="withdraw_challenge"),
                       url(r'^c/refresh-user-activities/$', 'fitcompetition.views.refresh_user_activities', name="refresh_user_activities"),

                       url(r'^login/$', 'fitcompetition.views.login', name="login"),
                       url(r'^logout/$', 'django.contrib.auth.views.logout', {'next_page': '/', }, name='logout'),
                       url(r'^login-error/$', 'fitcompetition.views.login_error'),

                       url(r'^useractivities/(?P<userID>\d+)/(?P<challengeID>\d+)/$', 'fitcompetition.views.user_activities', name="useractivities"),
                       url(r'^admin/', include(admin.site.urls)),
)
