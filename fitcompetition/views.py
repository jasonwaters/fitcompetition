from datetime import datetime
import json
from dateutil.relativedelta import relativedelta
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Q, Max
from django.http import HttpResponse
from django.shortcuts import render
from fitcompetition.models import Challenge, FitnessActivity, Challenger, FitUser, Transaction
from fitcompetition.settings import TIME_ZONE
from fitcompetition.util import ListUtil
from fitcompetition.util.ListUtil import createListFromProperty, attr
import pytz


def challenges(request):
    allUserChallenges, activeUserChallenges, completedUserChallenges = Challenge.objects.userChallenges(request.user.id)
    openChallenges = Challenge.objects.openChallenges(request.user.id)
    pastChallenges = Challenge.objects.pastChallenges()

    return render(request, 'challenges.html', {
        'myChallenges': activeUserChallenges,
        'openChallenges': openChallenges,
        'pastChallenges': pastChallenges
    })


@login_required
def profile(request):
    return user(request, attr(request, 'user').id)

@login_required
def account(request):
    transactions = Transaction.objects.filter(user=request.user).order_by('-date')

    return render(request, 'account.html', {
        'transactions': transactions
    })


def user(request, id):
    try:
        user = FitUser.objects.get(id=id)
    except FitUser.DoesNotExist:
        user = None

    allUserChallenges, activeUserChallenges, completedUserChallenges = Challenge.objects.userChallenges(id)

    thirtyDaysAgo = datetime.today() + relativedelta(days=-30)

    recentActivities = FitnessActivity.objects.filter(date__gte=thirtyDaysAgo, user=user).order_by('-date')

    return render(request, 'user.html', {
        'userprofile': user,
        'activeChallenges': activeUserChallenges,
        'completedChallenges': completedUserChallenges,
        'recentActivities': recentActivities
    })


def faq(request):
    return render(request, 'faq.html', {})


def challenge(request, id):
    now = datetime.utcnow().replace(tzinfo=pytz.utc)

    try:
        challenge = Challenge.objects.get(id=id)
    except Challenge.DoesNotExist:
        challenge = None

    competitor = None

    if request.user.is_authenticated():
        try:
            competitor = challenge.challenger_set.get(fituser=request.user)
        except Challenger.DoesNotExist:
            competitor = None

    allPlayers = challenge.challengers
    canJoin = not challenge.hasEnded and not competitor

    approvedTypes = challenge.approvedActivities.all()

    playersWithActivities = challenge.getChallengersWithActivities()
    playersWithActivitiesMap = ListUtil.mappify(playersWithActivities, 'id')

    if competitor and challenge.startdate <= now <= challenge.enddate:
        request.user.syncRunkeeperData()

    playersWithoutActivities = []

    for player in allPlayers:
        if playersWithActivitiesMap.get(player.id) is None:
            playersWithoutActivities.append(player)

    return render(request, 'challenge.html', {
        'disqus_identifier': 'fc_challenge_%s' % challenge.id,
        'challenge': challenge,
        'allPlayers': allPlayers,
        'playersWithActivities': playersWithActivities,
        'playersWithoutActivities': playersWithoutActivities,
        'canJoin': canJoin,
        'competitor': competitor,
        'numPlayers': len(allPlayers),
        'userAchievedGoal': challenge.getAchievedGoal(request.user),
        'approvedActivities': createListFromProperty(approvedTypes, 'name')
    })


@login_required
def join_challenge(request, id):
    try:
        challenge = Challenge.objects.get(id=id)
    except Challenge.DoesNotExist:
        challenge = None

    try:
        challenge.challenger_set.get(fituser=request.user)
    except Challenger.DoesNotExist:
        now = datetime.now(tz=pytz.timezone(TIME_ZONE))
        Challenger.objects.create(challenge=challenge,
                                  fituser=request.user,
                                  date_joined=now)

        Transaction.objects.create(date=now,
                                   user=request.user,
                                   description="Joined '%s' competition." % challenge.name,
                                   amount=challenge.ante * -1,
                                   challenge=challenge)

    return HttpResponse(json.dumps({'success': True}), content_type="application/json")


@login_required
def withdraw_challenge(request, id):
    try:
        challenge = Challenge.objects.get(id=id)
    except Challenge.DoesNotExist:
        challenge = None

    try:
        challenger = Challenger.objects.get(challenge=challenge, fituser=request.user)
        if not challenge.hasEnded:
            challenger.delete()
            now = datetime.now(tz=pytz.timezone(TIME_ZONE))

            Transaction.objects.create(date=now,
                                       user=request.user,
                                       description="Withdrew from '%s' competition." % challenge.name,
                                       amount=challenge.ante,
                                       challenge=challenge)
            success = True

    except Challenger.DoesNotExist:
        success = False

    return HttpResponse(json.dumps({'success': success}), content_type="application/json")


@login_required
def user_details_update(request):
    request.user.email = request.POST.get('emailAddress')
    request.user.phoneNumber = request.POST.get('phoneNumber')
    request.user.save()

    return HttpResponse(json.dumps({'success': True}), content_type="application/json")


@login_required
def refresh_user_activities(request):
    request.user.syncRunkeeperData()
    return HttpResponse(json.dumps({'success': True}), content_type="application/json")


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