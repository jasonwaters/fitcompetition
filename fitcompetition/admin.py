from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.sites.models import Site
from fitcompetition.models import Challenge, FitUser, Challenger, Transaction, Team


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
    list_display = ('name', 'distance', 'startdate', 'enddate')
    ordering = ('-startdate', '-enddate',)
    inlines = (TeamInline, ChallengerInline,)


class FitUserAdmin(UserAdmin):
    list_display = ('fullname', 'balance', 'email', 'phoneNumber', 'profile_url', 'lastHealthGraphUpdate', 'runkeeperToken', 'date_joined')
    inlines = (TransactionInline,)
    ordering = ('fullname',)


class TransactionAdmin(admin.ModelAdmin):
    list_display = ('date', 'user', 'description', 'amount', 'challenge')
    ordering = ('date',)


admin.site.register(Challenge, ChallengeAdmin)
admin.site.register(FitUser, FitUserAdmin)
admin.site.register(Transaction, TransactionAdmin)


admin.site.unregister(Site)