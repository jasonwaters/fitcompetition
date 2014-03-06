import base64
import json
from django.core.files.base import ContentFile
from fitcompetition.email import EmailFactory
import re
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from fitcompetition.models import Challenge, Team, FitnessActivity
from django.conf import settings
import mailchimp


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
def upload_activity_image(request, activity_id):
    activity = FitnessActivity.objects.get(pk=activity_id)

    if request.method == 'POST' and activity.user == request.user:
        if activity.photo:
            activity.photo.delete()

        dataUrlPattern = re.compile('data:image/(png|jpeg);base64,(.*)$')
        image_data = request.POST.get('base64image')
        image_data = dataUrlPattern.match(image_data).group(2)

        # If none or len 0, means illegal image data
        if image_data is None or len(image_data) == 0:
            return HttpResponse(json.dumps({'success': False}))

        # Decode the 64 bit string into 32 bit
        image_data = base64.b64decode(image_data)

        activity.photo.save(request.POST.get('filename'), ContentFile(image_data))
        activity.save()

        return HttpResponse(json.dumps({
            'success': True,
            'photoUrl': activity.photo.url
        }))
    return HttpResponse(json.dumps({'success': False}))


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


def subscribeToMailingList(user):
    api_key = getattr(settings, 'MAILCHIMP_API_KEY', None)
    list_id = getattr(settings, 'MAILCHIMP_LIST_ID', None)

    if api_key is not None and list_id is not None:
        m = mailchimp.Mailchimp(api_key)

        try:
            m.lists.subscribe(list_id, {
                'email': user.email
            }, {
                'FNAME': user.first_name,
                'LNAME': user.last_name
            }, double_optin=False, update_existing=True)
        except mailchimp.Error, e:
            pass

@login_required
def user_details_update(request):
    request.user.email = request.POST.get('emailAddress')
    request.user.save()

    subscribeToMailingList(request.user)

    return HttpResponse(json.dumps({'success': True}), content_type="application/json")


@login_required
def account_cash_out(request):
    paypalEmailAddress = request.POST.get('emailAddress')
    cashValue = float(request.POST.get('cashValue'))

    if request.user.email is None or len(request.user.email) == 0:
        request.user.email = paypalEmailAddress
        request.user.save()

    EmailFactory().cashWithdrawal(request.user, paypalEmailAddress, cashValue)

    return HttpResponse(json.dumps({'success': True}), content_type="application/json")
