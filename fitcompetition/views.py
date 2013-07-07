from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
from fitcompetition.models import Challenge


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

    # records = pruneDeadAndPopulateGoal(RunkeeperRecord.objects.all(), goal)

    return render(request, 'challenge.html', {
        # 'records': multikeysort(records, ['-totalMiles'], getter=operator.attrgetter),
        'challenge': challenge
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