from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
                       url(r'^grappelli/', include('grappelli.urls')),
                       url(r'^$', 'fitcompetition.views.home', name='home'),

                       # url(r'^fitcompetition/', include('fitcompetition.foo.urls')),

                       url(r'^admin/', include(admin.site.urls)),
)
