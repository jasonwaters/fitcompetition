import operator
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from fitcompetition.models import RunkeeperRecord, Goal
from fitcompetition.util.ListUtil import multikeysort
import healthgraph


def pruneDeadAndPopulateGoal(records, goal):
    pruned = []

    for record in records:
        if record.isDead:
            record.delete()
        else:
            record.populateGoal(goal)
            pruned.append(record)

    return pruned

@login_required
def home(request):
    try:
        goal = Goal.objects.get(isActive=True)
    except Goal.DoesNotExist:
        goal = None

    # records = pruneDeadAndPopulateGoal(RunkeeperRecord.objects.all(), goal)

    return render(request, 'home.html', {
        # 'records': multikeysort(records, ['-totalMiles'], getter=operator.attrgetter),
        'goal': goal
    })


def login_error(request):
    return HttpResponse("login error")


def login(request):
    # auth = healthgraph.AuthManager(getattr(settings, 'RUNKEEPER_CLIENT_ID', ''),
    #                                getattr(settings, 'RUNKEEPER_CLIENT_SECRET', ''),
    #                                'http://%s/login' % request.get_host())
    #
    # code = request.GET.get('code')
    # access_token = auth.get_access_token(code) if code is not None else ""
    #
    # if code is not None:
    #     user = healthgraph.User(session=healthgraph.Session(access_token))
    #     profile = user.get_profile()
    #
    #     userID = user.get('userID')
    #     name = profile.get('name')
    #
    #     record, created = RunkeeperRecord.objects.get_or_create(userID=userID)
    #     record.name = name
    #     record.code = code
    #     record.token = access_token
    #     record.save()
    #
    #     return HttpResponseRedirect('/')
    # else:
        return render(request, 'login.html', {})