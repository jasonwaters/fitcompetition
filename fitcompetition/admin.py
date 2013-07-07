from django.contrib import admin
from django.contrib.sites.models import Site
from fitcompetition.models import Challenge


class ChallengeAdmin(admin.ModelAdmin):
    list_display = ('name', 'distance', 'startdate', 'enddate')
    ordering = ('startdate', 'enddate',)

admin.site.register(Challenge, ChallengeAdmin)
admin.site.unregister(Site)