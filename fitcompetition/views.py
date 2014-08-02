from datetime import datetime
from dateutil.relativedelta import relativedelta
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count, Sum
from django.http import HttpResponse
from django.shortcuts import render, redirect
from fitcompetition import tasks
from fitcompetition.models import Challenge, FitnessActivity, FitUser, Team, Transaction, Challenger
from fitcompetition.settings import TEAM_MEMBER_MAXIMUM, TIME_ZONE
from fitcompetition.util.ListUtil import createListFromProperty, attr
import pytz


def challenges(request):
    now = datetime.now(tz=pytz.timezone(TIME_ZONE))
    currentChallenges = Challenge.objects.currentChallenges()
    upcomingChallenges = Challenge.objects.upcomingChallenges()
    pastChallenges = Challenge.objects.pastChallenges(daysAgo=60)

    challengeStats = Challenge.objects.filter(reconciled=True).aggregate(grandTotalDisbursed=Sum('totalDisbursed'), totalWinnerCount=Sum('numWinners'))

    accountFilter = Q()

    unReconciledChallenges = Challenge.objects.filter(reconciled=False)

    for challenge in unReconciledChallenges:
        accountFilter |= Q(account=challenge.account)

    transactionResult = Transaction.objects.filter(accountFilter).aggregate(upForGrabs=Sum('amount'))

    return render(request, 'challenges.html', {
        'currentChallenges': currentChallenges,
        'upcomingChallenges': upcomingChallenges,
        'pastChallenges': pastChallenges,
        'totalPaid': attr(challengeStats, 'grandTotalDisbursed', defaultValue=0),
        'upForGrabs': transactionResult.get('upForGrabs'),
        'playingNow': Challenger.objects.filter(challenge__reconciled=False).count(),
        'totalAllTimePlayers': Challenger.objects.all().count(),
        'unReconciledChallenges': unReconciledChallenges.count(),
        'totalCompletedChallenges': Challenge.objects.filter(reconciled=True).count()
    })


@login_required
def profile(request):
    return user(request, attr(request, 'user').id)


@login_required
def account(request):
    return render(request, 'account.html')


def user(request, id):
    try:
        user = FitUser.objects.get(id=id)
    except FitUser.DoesNotExist:
        user = None

    activeUserChallenges, upcomingUserChallenges, completedUserChallenges = Challenge.objects.userChallenges(id)

    thirtyDaysAgo = datetime.today() + relativedelta(days=-30)

    recentActivities = FitnessActivity.objects.select_related('type').filter(user=user).order_by('-date')[:20]

    return render(request, 'user.html', {
        'userprofile': user,
        'activeChallenges': activeUserChallenges,
        'upcomingUserChallenges': upcomingUserChallenges,
        'completedChallenges': completedUserChallenges,
        'recentActivities': recentActivities
    })


def team(request, id):
    try:
        team = Team.objects.prefetch_related('members').get(id=id)
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
        challenge = Challenge.objects.prefetch_related('approvedActivities', 'players', 'teams').get(id=id)
    except Challenge.DoesNotExist:
        return redirect('challenges')

    isCompetitor = False

    if request.user.is_authenticated():
        isCompetitor = request.user in challenge.players.all()

    if isCompetitor and challenge.startdate <= now <= challenge.enddate:
        if request.user.healthGraphStale():
            request.user.syncExternalActivities()
        else:
            tasks.syncExternalActivities.delay(request.user.id)

    approvedTypes = challenge.approvedActivities.all()

    footFilter = Q(name__contains="Running")
    footFilter |= Q(name__contains="Walking")
    footFilter |= Q(name__contains="Hiking")

    isFootRace = len(challenge.approvedActivities.filter(footFilter)) > 0

    params = {
        'show_social': 'social-callout-%s' % challenge.id not in request.COOKIES.get('hidden_callouts', ''),
        'disqus_identifier': 'fc_challenge_%s' % challenge.id,
        'challenge': challenge,
        'canJoin': challenge.canJoin and not isCompetitor,
        'isCompetitor': isCompetitor,
        'approvedActivities': createListFromProperty(approvedTypes, 'name'),
        'numPlayers': challenge.numPlayers,
        'canWithdraw': isCompetitor and not challenge.hasStarted,
        'recentActivities': challenge.getRecentActivities()[:15],
        'isFootRace': isFootRace
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
        params['canSwitchTeams'] = isCompetitor and not challenge.hasStarted

    return render(request, 'challenge.html', params)


def user_activities(request, userID, challengeID):
    activities = []

    if challengeID is not None and userID is not None:
        challenge = Challenge.objects.get(id=challengeID)

        activitiesFilter = challenge.getActivitiesFilter(generic=True)

        activitiesFilter = Q(user_id=userID) & activitiesFilter
        activities = FitnessActivity.objects.filter(activitiesFilter).order_by('-date')

    return render(request, 'user_activities.html', {
        'activities': activities
    })

@login_required
def diagnostics(request):

    if request.GET.get('syncActivities') is not None:
        tasks.syncExternalActivities(request.user.id)
    elif request.GET.get('pruneActivities') is not None:
        tasks.pruneExternalActivities(request.user.id)
    elif request.GET.get('syncProfile') is not None:
        tasks.syncExternalProfile(request.user.id)
    elif request.GET.get('resetSyncDate') is not None:
        user = FitUser.objects.get(id=request.user.id)
        user.lastExternalSyncDate = None
        user.save()

    return render(request, 'diagnostics.html', {})


def login_error(request):
    return HttpResponse("login error")


def login(request):
    return render(request, 'login.html', {})