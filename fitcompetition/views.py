from datetime import datetime
import json
from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.db.models import Sum, Q, Max
from django.http import HttpResponse
from django.shortcuts import render
from fitcompetition.models import Challenge, FitnessActivity, ActivityType
from fitcompetition.settings import TIME_ZONE
from fitcompetition.util import ListUtil
from fitcompetition.util.ListUtil import createListFromProperty
import pytz


@login_required
def home(request):
    myChallenges = Challenge.objects.filter(players__id=request.user.id).order_by('-enddate')
    otherChallenges = Challenge.objects.exclude(players__id=request.user.id).order_by('-enddate')

    return render(request, 'home.html', {
        'myChallenges': myChallenges,
        'otherChallenges': otherChallenges
    })

@login_required
def challenge(request, id):
    now = datetime.now(tz=pytz.timezone(TIME_ZONE))

    try:
        challenge = Challenge.objects.get(id=id)
    except Challenge.DoesNotExist:
        challenge = None

    refresh = request.GET.get('refresh', False) or request.user.healthGraphStale()
    if refresh:
        request.user.refreshFitnessActivities()

    joinNow = request.GET.get('join', False)

    players = challenge.players.all().order_by('fullname')
    canJoin = request.user not in players

    if joinNow and canJoin:
        challenge.players.add(request.user)
        canJoin = False

    approvedTypes = challenge.approvedActivities.all()

    if challenge.startdate <= now:
        dateFilter = Q(fitnessactivity__date__gte=challenge.startdate) & Q(fitnessactivity__date__lte=challenge.enddate)
        typeFilter = Q()

        for type in approvedTypes:
            typeFilter |= Q(fitnessactivity__type=type)

        activitiesFilter = dateFilter & typeFilter

        players = players.filter(activitiesFilter).annotate(total_distance=Sum('fitnessactivity__distance'), latest_activity_date=Max('fitnessactivity__date')).order_by('-total_distance')

    return render(request, 'challenge.html', {
        'challenge': challenge,
        'players': players,
        'canJoin': canJoin,
        'approvedActivities': createListFromProperty(approvedTypes, 'name')
    })


def user_activities(request, userID, challengeID):
    activities = []

    if challengeID is not None and userID is not None:
        challenge = Challenge.objects.get(id=challengeID)
        approvedTypes = challenge.approvedActivities.all()

        dateFilter = Q(date__gte=challenge.startdate) & Q(date__lte=challenge.enddate) & Q(user_id=userID)
        typeFilter = Q()

        for type in approvedTypes:
            typeFilter |= Q(type=type)

        activitiesFilter = dateFilter & typeFilter
        activities = FitnessActivity.objects.filter(activitiesFilter).order_by('-date')

    return render(request, 'user_activities.html', {
        'activities': activities
    })


def login_error(request):
    return HttpResponse("login error")


def login(request):
    return render(request, 'login.html', {})