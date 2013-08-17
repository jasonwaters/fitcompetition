from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.sites.models import Site
from fitcompetition.models import Challenge, FitUser, Challenger, Transaction


class ChallengerInline(admin.TabularInline):
    model = Challenger


class TransactionInline(admin.TabularInline):
    model = Transaction


class ChallengeAdmin(admin.ModelAdmin):
    list_display = ('name', 'distance', 'startdate', 'enddate')
    ordering = ('startdate', 'enddate',)
    inlines = (ChallengerInline,)


class FitUserAdmin(UserAdmin):
    list_display = ('fullname', 'balance', 'email', 'phoneNumber', 'profile_url', 'lastHealthGraphUpdate', 'runkeeperToken', 'date_joined')
    ordering = ('date_joined',)
    inlines = (TransactionInline,)


class TransactionAdmin(admin.ModelAdmin):
    list_display = ('date', 'user', 'description', 'amount', 'challenge')
    ordering = ('date',)


admin.site.register(Challenge, ChallengeAdmin)
admin.site.register(FitUser, FitUserAdmin)
admin.site.register(Transaction, TransactionAdmin)


admin.site.unregister(Site)