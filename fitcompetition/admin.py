from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.sites.models import Site
from djcelery.models import TaskState, WorkerState, IntervalSchedule, CrontabSchedule, PeriodicTask
from fitcompetition.models import Challenge, FitUser, Challenger, Transaction, Team, Account, FitnessActivity
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
    list_display = ('name', 'accountingType', 'distance', 'calories', 'duration', 'startdate', 'middate', 'enddate')
    exclude = ('middate',)
    ordering = ('-startdate', '-enddate',)
    inlines = (TeamInline, ChallengerInline,)


class FitnessActivityAdmin(admin.ModelAdmin):
    list_display = ('date', 'user', 'type', 'distance', 'calories', 'hasProof', 'cancelled')
    ordering = ('-date',)
    list_filter = ('user', 'type')


class FitUserAdmin(UserAdmin):
    list_display = ('fullname', 'email', 'phoneNumber', 'profile_url', 'lastExternalSyncDate', 'integrationName', 'date_joined')
    ordering = ('date_joined',)
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('account',)}),
    )


class AccountAdmin(admin.ModelAdmin):

    def users(self):
        def getAdminUrl(user):
            return "/admin/fitcompetition/fituser/%s/" % user.id

        html = "<ul>"

        for user in FitUser.objects.filter(account__id__exact=self.id):
            html += '<li><a href="%s">%s ( %s )</a></li>' % (getAdminUrl(user), user.fullname, user.integrationName)

        html += "</ul>"

        return html

    def challenges(self):
        def getAdminUrl(challenge):
            return "/admin/fitcompetition/challenge/%s/" % challenge.id

        html = "<ul>"

        for challenge in Challenge.objects.filter(account__id__exact=self.id):
            html += '<li><a href="%s">%s</a></li>' % (getAdminUrl(challenge), challenge.name)

        html += "</ul>"

        return html

    users.allow_tags = True
    challenges.allow_tags = True

    list_display = ('description', 'balance', users, challenges)
    inlines = (TransactionInline,)
    ordering = ('description',)

admin.site.register(Challenge, ChallengeAdmin)
admin.site.register(FitUser, FitUserAdmin)
admin.site.register(FitnessActivity, FitnessActivityAdmin)
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