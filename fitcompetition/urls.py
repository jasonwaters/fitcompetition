from django.conf.urls import patterns, include, url
from django.contrib import admin
from fitcompetition.api import TransactionViewSet, ChallengeViewSet, UserViewSet, ActivityViewSet, AccountViewSet
from rest_framework import routers
from django.conf import settings

admin.autodiscover()


router = routers.DefaultRouter()
router.register(r'account', AccountViewSet)
router.register(r'activities', ActivityViewSet)
router.register(r'users', UserViewSet)
router.register(r'challenges', ChallengeViewSet)
router.register(r'transactions', TransactionViewSet)

urlpatterns = patterns('',
                       #VIEWS
                       url(r'^$', 'fitcompetition.views.challenges', name='home'),
                       url(r'^$', 'fitcompetition.views.challenges', name='challenges'),
                       url(r'^challenge/(?P<id>\d+)/$', 'fitcompetition.views.challenge', name="challenge_details"),
                       url(r'^c/(?P<id>\d+)/$', 'fitcompetition.views.challenge', name="challenge_details2"),
                       url(r'^faq/$', 'fitcompetition.views.faq', name="faq"),
                       url(r'^profile/$', 'fitcompetition.views.profile', name="user_profile"),
                       url(r'^account/$', 'fitcompetition.views.account', {'SSL':True}, name="account"),
                       url(r'^user/(?P<id>\d+)/$', 'fitcompetition.views.user', name="user_details"),
                       url(r'^team/(?P<id>\d+)/$', 'fitcompetition.views.team', name="team_details"),
                       url(r'^login/$', 'fitcompetition.views.login', name="login"),
                       url(r'^logout/$', 'django.contrib.auth.views.logout', {'next_page': '/', }, name='logout'),
                       url(r'^login-error/$', 'fitcompetition.views.login_error'),
                       url(r'^useractivities/(?P<userID>\d+)/(?P<challengeID>\d+)/$', 'fitcompetition.views.user_activities', name="useractivities"),
                       url(r'^diagnostics/$', 'fitcompetition.views.diagnostics', name='diagnostics'),

                       #AJAX
                       url(r'^c/join/(?P<id>\d+)/$', 'fitcompetition.api.join_challenge', name="join_challenge"),
                       url(r'^c/join/(?P<challenge_id>\d+)/team/(?P<team_id>\d+)/$', 'fitcompetition.api.join_team', name="join_team"),
                       url(r'^c/join/(?P<challenge_id>\d+)/team-create/$', 'fitcompetition.api.create_team', name="create_team"),
                       url(r'^c/withdraw/(?P<id>\d+)/$', 'fitcompetition.api.withdraw_challenge', name="withdraw_challenge"),
                       url(r'^update-user-details/$', 'fitcompetition.api.user_details_update', name="user_details_update"),
                       url(r'^api/account-cash-out$', 'fitcompetition.api.account_cash_out', {'SSL':True}, name="account_cash_out"),
                       url(r'^activity-photo-upload/(?P<activity_id>\d+)/$', 'fitcompetition.api.upload_activity_image', name="activity_upload_photo"),

                       #OTHER
                       url(r'^grappelli/', include('grappelli.urls')),
                       url(r'', include('social.apps.django_app.urls', namespace='social')),
                       url(r'^admin/', include(admin.site.urls)),


                       #Django REST Framework
                       url(r'^api/', include(router.urls)),
                       url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
                       )

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += patterns('',
                            url(r'^__debug__/', include(debug_toolbar.urls)),
                            )