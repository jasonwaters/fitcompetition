from datetime import datetime
import json
import operator
from dateutil.relativedelta import relativedelta
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Q, Max, Count
from django.http import HttpResponse
from django.shortcuts import render
from fitcompetition.models import Challenge, FitnessActivity, Challenger, FitUser, Transaction, Team
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


def team(request, id):
    try:
        team = Team.objects.get(id=id)
    except Team.DoesNotExist:
        team = None

    members = team.members.all()

    return render(request, 'team.html', {
        'team': team,
        'teamMembers': members
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

    if competitor and challenge.startdate <= now <= challenge.enddate:
        request.user.syncRunkeeperData()

    canJoin = not challenge.hasEnded and not competitor

    approvedTypes = challenge.approvedActivities.all()

    params = {
        'show_social': 'social-callout-%s' % challenge.id not in request.COOKIES.get('hidden_callouts', ''),
        'disqus_identifier': 'fc_challenge_%s' % challenge.id,
        'challenge': challenge,
        'canJoin': canJoin,
        'competitor': competitor,
        'userAchievedGoal': competitor and challenge.getAchievedGoal(request.user),
        'approvedActivities': createListFromProperty(approvedTypes, 'name'),
        'numPlayers': challenge.numPlayers,
    }

    if challenge.isTypeSimple:
        params['players'] = challenge.getChallengersWithActivities()
    elif challenge.isTypeTeam:
        params['open_teams'] = Team.objects.filter(challenge=challenge).annotate(num_members=Count('members')).filter(num_members__lt=5)

        if request.user.is_authenticated():
            try:
                team = Team.objects.get(challenge=challenge, members__id__exact=request.user.id)
                params['open_teams'] = params['open_teams'].exclude(id=team.id)
            except Team.DoesNotExist:
                pass

        params['teams'] = ListUtil.multikeysort(challenge.teams, ['-distance'], getter=operator.attrgetter)
        params['canSwitchTeams'] = competitor and not challenge.hasStarted

    return render(request, 'challenge.html', params)


@login_required
def join_challenge(request, id):
    try:
        challenge = Challenge.objects.get(id=id)
    except Challenge.DoesNotExist:
        return HttpResponse(json.dumps({'success': False}), content_type="application/json")

    challenge.addChallenger(request.user)

    return HttpResponse(json.dumps({'success': True}), content_type="application/json")

@login_required
def join_team(request, challenge_id, team_id):
    try:
        challenge = Challenge.objects.get(id=challenge_id)
        challenge.addChallenger(request.user)
    except Challenge.DoesNotExist:
        return HttpResponse(json.dumps({'success': False}), content_type="application/json")

    try:
        team = Team.objects.get(id=team_id)
        withdraw_all_teams(request.user, except_for=team)
    except Team.DoesNotExist:
        return HttpResponse(json.dumps({'success': False}), content_type="application/json")

    return HttpResponse(json.dumps({'success': True}), content_type="application/json")

@login_required
def create_team(request, challenge_id):
    try:
        challenge = Challenge.objects.get(id=challenge_id)
        challenge.addChallenger(request.user)
    except Challenge.DoesNotExist:
        return HttpResponse(json.dumps({'success': False}), content_type="application/json")

    withdraw_all_teams(request.user)

    team, created = Team.objects.get_or_create(challenge=challenge, captain=request.user)
    team.name = "%s's Team" % request.user.first_name
    team.members.add(request.user)
    team.save()

    return HttpResponse(json.dumps({'success': True}), content_type="application/json")


def withdraw_all_teams(user, except_for=None):
    teams = Team.objects.exclude(id=except_for.id) if except_for is not None else Team.objects.all()
    for team in teams:
            team.members.remove(user)

    if except_for is not None:
        except_for.members.add(user)

    Team.objects.filter(captain=user).annotate(num_members=Count('members')).filter(num_members=0).delete()


@login_required
def withdraw_challenge(request, id):
    try:
        challenge = Challenge.objects.get(id=id)
        challenge.removeChallenger(request.user)
    except Challenge.DoesNotExist:
        return HttpResponse(json.dumps({'success': False}), content_type="application/json")

    withdraw_all_teams(request.user)
    return HttpResponse(json.dumps({'success': True}), content_type="application/json")

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