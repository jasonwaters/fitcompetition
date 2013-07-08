import json
from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.db.models import Sum, Q, Max
from django.http import HttpResponse
from django.shortcuts import render
from fitcompetition.models import Challenge, FitnessActivity
from fitcompetition.util.ListUtil import createListFromProperty

@login_required
def home(request):
    challenges = Challenge.objects.order_by('-startdate')

    return render(request, 'home.html', {
        'challenges': challenges
    })

@login_required
def challenge(request, id):
    try:
        challenge = Challenge.objects.get(id=id)
    except Challenge.DoesNotExist:
        challenge = None

    players = challenge.players.all()
    canJoin = request.user not in players

    approvedTypes = challenge.approvedActivities.all()

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


def json_useractivities(request):
    challengeID = request.GET.get('challengeID')
    userID = request.GET.get('userID')
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

    return HttpResponse(serializers.serialize('json', activities, fields=('duration', 'date', 'calories', 'distance')), mimetype="application/json")


def login_error(request):
    return HttpResponse("login error")


def login(request):
    return render(request, 'login.html', {})