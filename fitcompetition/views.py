import operator
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
from fitcompetition.models import Challenge, RunkeeperRecord
from fitcompetition.util.ListUtil import multikeysort


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

    # records = pruneDeadAndPopulateGoal(RunkeeperRecord.objects.all(), challenge)
    players = challenge.players.all()
    canJoin = request.user not in players

    return render(request, 'challenge.html', {
        # 'records': multikeysort(records, ['-totalMiles'], getter=operator.attrgetter),
        'challenge': challenge,
        'players': players,
        'canJoin': canJoin
    })


def login_error(request):
    return HttpResponse("login error")


def login(request):
    return render(request, 'login.html', {})