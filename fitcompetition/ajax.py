import json

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from fitcompetition.models import Challenge, Team
from fitcompetition.templatetags.apptags import toMiles


def addChallenger(challenge_id, user):
    try:
        challenge = Challenge.objects.get(id=challenge_id)
        if challenge.hasStarted:
            raise Exception('Challenge Already Started')
        challenge.addChallenger(user)
        return True, challenge
    except Challenge.DoesNotExist:
        return False, None
    except Exception:
        return False, None


@login_required
def fetch_latest_activities(request, challenge_id):
    request.user.syncRunkeeperData()

    try:
        challenge = Challenge.objects.get(id=challenge_id)
        distance = request.user.getDistance(challenge)
        return HttpResponse(json.dumps({'success': True, 'distance': toMiles(distance)}), content_type="application/json")
    except Challenge.DoesNotExist:
        return HttpResponse(json.dumps({'success': False}), content_type="application/json")


@login_required
def join_challenge(request, id):
    added_challenger, challenge = addChallenger(id, request.user)
    return HttpResponse(json.dumps({'success': added_challenger}), content_type="application/json")


@login_required
def join_team(request, challenge_id, team_id):
    added_challenger, challenge = addChallenger(challenge_id, request.user)

    if added_challenger:
        try:
            team = Team.objects.get(id=team_id)
            team.addChallenger(request.user)
        except Team.DoesNotExist:
            return HttpResponse(json.dumps({'success': False}), content_type="application/json")

    return HttpResponse(json.dumps({'success': True}), content_type="application/json")


@login_required
def create_team(request, challenge_id):
    added_challenger, challenge = addChallenger(challenge_id, request.user)

    if added_challenger:
        Team.objects.startTeam(challenge, request.user)

    return HttpResponse(json.dumps({'success': True}), content_type="application/json")


@login_required
def withdraw_challenge(request, id):
    try:
        challenge = Challenge.objects.get(id=id)
        challenge.removeChallenger(request.user)
        Team.objects.withdrawAll(challenge, request.user)
    except Challenge.DoesNotExist:
        return HttpResponse(json.dumps({'success': False}), content_type="application/json")

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