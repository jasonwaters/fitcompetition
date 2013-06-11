from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
                       url(r'^grappelli/', include('grappelli.urls')),
                       url(r'^$', 'fitcompetition.views.home', name='home'),

                       # url(r'^fitcompetition/', include('fitcompetition.foo.urls')),

                       url(r'^admin/', include(admin.site.urls)),

                       url(r'^runkeeper/login/$', 'django_openid_auth.views.login_begin',
                           kwargs={'render_failure': 'sales.views.error'}, name='openid-login'),

                       url(r'^runkeeper/login-complete/$', 'django_openid_auth.views.login_complete',
                           name='openid-complete'),

                       url(r'^login/$', 'fitcompetition.views.login', name='login'),
                       url(r'^logout/$', 'django.contrib.auth.views.logout', {'next_page': '/', }, name='logout'),
)
