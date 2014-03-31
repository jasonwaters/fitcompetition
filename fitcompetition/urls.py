from django.conf.urls import patterns, include, url
from django.contrib import admin
from fitcompetition import ajax
from fitcompetition.ajax import UserTransactionsList
from rest_framework import routers

admin.autodiscover()


router = routers.DefaultRouter()
router.register(r'activities', ajax.ActivityViewSet)
router.register(r'users', ajax.UserViewSet)
router.register(r'challenges', ajax.ChallengeViewSet)
router.register(r'transactions', ajax.TransactionViewSet)

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


                       #AJAX
                       url(r'^c/join/(?P<id>\d+)/$', 'fitcompetition.ajax.join_challenge', name="join_challenge"),
                       url(r'^c/join/(?P<challenge_id>\d+)/team/(?P<team_id>\d+)/$', 'fitcompetition.ajax.join_team', name="join_team"),
                       url(r'^c/join/(?P<challenge_id>\d+)/team-create/$', 'fitcompetition.ajax.create_team', name="create_team"),
                       url(r'^c/withdraw/(?P<id>\d+)/$', 'fitcompetition.ajax.withdraw_challenge', name="withdraw_challenge"),
                       url(r'^update-user-details/$', 'fitcompetition.ajax.user_details_update', name="user_details_update"),
                       url(r'^account-cash-out/$', 'fitcompetition.ajax.account_cash_out', {'SSL':True}, name="account_cash_out"),
                       url(r'^activity-photo-upload/(?P<activity_id>\d+)/$', 'fitcompetition.ajax.upload_activity_image', name="activity_upload_photo"),

                       #OTHER
                       url(r'^grappelli/', include('grappelli.urls')),
                       url(r'', include('social.apps.django_app.urls', namespace='social')),
                       url(r'^admin/', include(admin.site.urls)),


                       #Django REST Framework
                       url(r'^api/', include(router.urls)),
                       url(r'^api/users/(?P<pk>\d+)/transactions$', UserTransactionsList.as_view(), name='usertransactions-list'),
                       url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
)