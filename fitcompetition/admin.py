from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.sites.models import Site
from fitcompetition.models import Challenge, FitUser


class ChallengeAdmin(admin.ModelAdmin):
    list_display = ('name', 'distance', 'startdate', 'enddate')
    ordering = ('startdate', 'enddate',)


class FitUserAdmin(UserAdmin):
    pass

admin.site.register(Challenge, ChallengeAdmin)
admin.site.register(FitUser)
admin.site.unregister(Site)