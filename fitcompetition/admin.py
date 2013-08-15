from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.sites.models import Site
from fitcompetition.models import Challenge, FitUser, Challenger


class ChallengerInline(admin.TabularInline):
    model = Challenger


class ChallengeAdmin(admin.ModelAdmin):
    list_display = ('name', 'distance', 'startdate', 'enddate')
    ordering = ('startdate', 'enddate',)
    inlines = (ChallengerInline,)


class FitUserAdmin(UserAdmin):
    list_display = ('fullname', 'email', 'phoneNumber', 'profile_url', 'lastHealthGraphUpdate', 'runkeeperToken', 'date_joined')
    ordering = ('date_joined',)

admin.site.register(Challenge, ChallengeAdmin)
admin.site.register(FitUser, FitUserAdmin)
admin.site.unregister(Site)