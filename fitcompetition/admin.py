from django.contrib import admin
from django.contrib.sites.models import Site
from fitcompetition.models import Goal


class GoalAdmin(admin.ModelAdmin):
    list_display = ('name', 'distance', 'startdate', 'enddate', 'isActive')
    ordering = ('startdate', 'enddate',)

admin.site.register(Goal, GoalAdmin)
admin.site.unregister(Site)