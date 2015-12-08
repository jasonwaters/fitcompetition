from django.conf.urls import patterns, include, url
from django.contrib import admin
from fitcompetition.api import TransactionViewSet, ChallengeViewSet, UserViewSet, ActivityViewSet, AccountViewSet, ActivityTypeViewSet
from rest_framework import routers
from django.conf import settings

admin.autodiscover()

router = routers.DefaultRouter()
router.register(r'accounts', AccountViewSet)
router.register(r'activities', ActivityViewSet)
router.register(r'users', UserViewSet)
router.register(r'challenges', ChallengeViewSet)
router.register(r'transactions', TransactionViewSet)
router.register(r'activitytypes', ActivityTypeViewSet)

urlpatterns = patterns('',
                       #VIEWS
                       url(r'^$', 'fitcompetition.views.challenges', name='home'),
                       url(r'^challenges/$', 'fitcompetition.views.challenges', name='challenges'),
                       url(r'^challenge/(?P<id>\d+)/$', 'fitcompetition.views.challenge_id', name="challenge_details_id"),
                       url(r'^challenge/(?P<slug>[-\w\d]+)/$', 'fitcompetition.views.challenge_slug', name="challenge_details"),

                       url(r'^faq/$', 'fitcompetition.views.faq', name="faq"),
                       url(r'^profile/$', 'fitcompetition.views.profile', name="user_profile"),
                       url(r'^account/$', 'fitcompetition.views.account', name="account"),
                       url(r'^user/(?P<id>\d+)/$', 'fitcompetition.views.user', name="user_details"),
                       url(r'^team/(?P<id>\d+)/$', 'fitcompetition.views.team', name="team_details"),
                       url(r'^login/$', 'fitcompetition.views.login', name="login"),
                       url(r'^logout/$', 'django.contrib.auth.views.logout', {'next_page': '/', }, name='logout'),
                       url(r'^login-error/$', 'fitcompetition.views.login_error'),
                       url(r'^useractivities/(?P<userID>\d+)/(?P<challengeID>\d+)/$', 'fitcompetition.views.user_activities', name="useractivities"),
                       url(r'^diagnostics/$', 'fitcompetition.views.diagnostics', name='diagnostics'),
                       url(r'^weight/$', 'fitcompetition.views.weight', name='weight'),

                       #AJAX
                       url(r'^api/join-challenge$', 'fitcompetition.api.join_challenge', name="join_challenge"),
                       url(r'^api/join-team$', 'fitcompetition.api.join_team', name="join_team"),
                       url(r'^api/create-team$', 'fitcompetition.api.create_team', name="create_team"),
                       url(r'^api/withdraw-challenge$', 'fitcompetition.api.withdraw_challenge', name="withdraw_challenge"),
                       url(r'^api/update-user-details$', 'fitcompetition.api.user_details_update', name="user_details_update"),
                       url(r'^api/update-user-timezone', 'fitcompetition.api.user_timezone_update', name="user_timezone_update"),
                       url(r'^api/account-cash-out$', 'fitcompetition.api.account_cash_out', name="account_cash_out"),
                       url(r'^api/charge-card$', 'fitcompetition.api.charge_card', name="charge_card"),
                       url(r'^api/stripe-customer$', 'fitcompetition.api.get_stripe_customer', name="get_stripe_customer"),
                       url(r'^api/del-stripe-card', 'fitcompetition.api.delete_stripe_card', name="delete_stripe_card"),
                       url(r'^api/activity-photo-upload/(?P<activity_id>\d+)/$', 'fitcompetition.api.upload_activity_image', name="activity_upload_photo"),

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