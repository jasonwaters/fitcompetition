from datetime import datetime
from dateutil.relativedelta import relativedelta
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count, Sum
from django.http import HttpResponse
from django.shortcuts import render, redirect
from fitcompetition.models import Challenge, FitnessActivity, Challenger, FitUser, Transaction, Team
from fitcompetition.settings import TEAM_MEMBER_MAXIMUM
from fitcompetition.util.ListUtil import createListFromProperty, attr
import pytz


def challenges(request):
    currentChallenges = Challenge.objects.currentChallenges()
    upcomingChallenges = Challenge.objects.upcomingChallenges()
    pastChallenges = Challenge.objects.pastChallenges()

    challengeStats = Challenge.objects.filter(reconciled=True).aggregate(grandTotalDisbursed=Sum('totalDisbursed'), totalWinnerCount=Sum('numWinners'))

    return render(request, 'challenges.html', {
        'currentChallenges': currentChallenges,
        'upcomingChallenges': upcomingChallenges,
        'pastChallenges': pastChallenges,
        'totalPaid': attr(challengeStats, 'grandTotalDisbursed'),
        'averagePaid': attr(challengeStats, 'grandTotalDisbursed') / attr(challengeStats, 'totalWinnerCount')
    })


@login_required
def profile(request):
    return user(request, attr(request, 'user').id)


@login_required
def account(request):
    transactions = Transaction.objects.filter(account=request.user.account).order_by('-date')

    return render(request, 'account.html', {
        'transactions': transactions
    })


def user(request, id):
    try:
        user = FitUser.objects.get(id=id)
    except FitUser.DoesNotExist:
        user = None

    activeUserChallenges, upcomingUserChallenges, completedUserChallenges = Challenge.objects.userChallenges(id)

    thirtyDaysAgo = datetime.today() + relativedelta(days=-30)

    recentActivities = FitnessActivity.objects.filter(date__gte=thirtyDaysAgo, user=user).order_by('-date')

    return render(request, 'user.html', {
        'userprofile': user,
        'activeChallenges': activeUserChallenges,
        'upcomingUserChallenges': upcomingUserChallenges,
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
    now = datetime.now(tz=pytz.utc)

    try:
        challenge = Challenge.objects.get(id=id)
    except Challenge.DoesNotExist:
        return redirect('challenges')

    competitor = None

    if request.user.is_authenticated():
        try:
            competitor = challenge.challenger_set.get(fituser=request.user)
        except Challenger.DoesNotExist:
            competitor = None

    if competitor and challenge.startdate <= now <= challenge.enddate and request.user.healthGraphStale():
        request.user.syncRunkeeperData(syncProfile=False)

    approvedTypes = challenge.approvedActivities.all()

    params = {
        'show_social': 'social-callout-%s' % challenge.id not in request.COOKIES.get('hidden_callouts', ''),
        'disqus_identifier': 'fc_challenge_%s' % challenge.id,
        'challenge': challenge,
        'canJoin': not challenge.hasStarted and not competitor,
        'competitor': competitor,
        'userAchievedGoal': competitor and challenge.getAchievedGoal(request.user),
        'approvedActivities': createListFromProperty(approvedTypes, 'name'),
        'numPlayers': challenge.numPlayers,
        'canWithdraw': competitor and not competitor.user.delinquent and not challenge.hasStarted,
        'recentActivities': challenge.getRecentActivities(),
    }

    if challenge.isTypeIndividual:
        params['players'] = challenge.getChallengersWithActivities()
        params['teams'] = []
    elif challenge.isTypeTeam:
        params['open_teams'] = Team.objects.filter(challenge=challenge).annotate(num_members=Count('members')).filter(
            num_members__lt=TEAM_MEMBER_MAXIMUM)

        if request.user.is_authenticated():
            try:
                team = Team.objects.get(challenge=challenge, members__id__exact=request.user.id)
                params['open_teams'] = params['open_teams'].exclude(id=team.id)
            except Team.DoesNotExist:
                pass

        params['teams'] = challenge.rankedTeams
        params['canSwitchTeams'] = competitor and not competitor.user.delinquent and not challenge.hasStarted

    return render(request, 'challenge.html', params)


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