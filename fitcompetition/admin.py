from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.sites.models import Site
from djcelery.models import TaskState, WorkerState, IntervalSchedule, CrontabSchedule, PeriodicTask
from fitcompetition.models import Challenge, FitUser, Challenger, Transaction, Team, Account
from social.apps.django_app.default.models import Nonce, Association, UserSocialAuth


class TeamInline(admin.TabularInline):
    model = Team
    extra = 0

    def get_formset(self, request, obj=None, **kwargs):
        self.parent_obj = obj
        return super(TeamInline, self).get_formset(request, obj, **kwargs)

    def formfield_for_manytomany(self, db_field, request=None, **kwargs):
        if db_field.name == 'members' and self.parent_obj is not None:
            kwargs['queryset'] = self.parent_obj.challengers.all()

        return super(TeamInline, self).formfield_for_manytomany(db_field, request, **kwargs)


class ChallengerInline(admin.TabularInline):
    model = Challenger
    extra = 0


class TransactionInline(admin.TabularInline):
    model = Transaction
    extra = 0


class ChallengeAdmin(admin.ModelAdmin):
    list_display = ('name', 'distance', 'startdate', 'middate', 'enddate')
    exclude = ('middate',)
    ordering = ('-startdate', '-enddate',)
    inlines = (TeamInline, ChallengerInline,)


class FitUserAdmin(UserAdmin):
    list_display = ('fullname', 'email', 'phoneNumber', 'profile_url', 'lastExternalSyncDate', 'integrationName', 'date_joined')
    ordering = ('fullname', 'integrationName')


class AccountAdmin(admin.ModelAdmin):
    list_display = ('description', 'balance', 'user', 'challenge')
    inlines = (TransactionInline,)
    ordering = ('description',)

admin.site.register(Challenge, ChallengeAdmin)
admin.site.register(FitUser, FitUserAdmin)
admin.site.register(Account, AccountAdmin)

admin.site.unregister(Site)

#python-social-auth
admin.site.unregister(Nonce)
admin.site.unregister(Association)
admin.site.unregister(UserSocialAuth)

#djcelery
admin.site.unregister(TaskState)
admin.site.unregister(WorkerState)
admin.site.unregister(IntervalSchedule)
admin.site.unregister(CrontabSchedule)
admin.site.unregister(PeriodicTask)