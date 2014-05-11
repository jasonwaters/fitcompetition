import base64
from datetime import datetime
import json
from django.core.files.base import ContentFile
from fitcompetition.email import EmailFactory
from fitcompetition.serializers import UserSerializer, ChallengeSerializer, TransactionSerializer, AccountSerializer
import pytz
import re
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from fitcompetition.models import Challenge, Team, FitnessActivity, FitUser, Transaction, Account, ActivityType
from django.conf import settings
import mailchimp
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
import stripe


def addChallenger(challenge_id, user):
    try:
        challenge = Challenge.objects.get(id=challenge_id)
        if not challenge.canJoin:
            raise Exception('Challenge Cannot be Joined')
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
    paypalEmailAddress = request.GET.get('email')
    cashValue = float(request.GET.get('amount'))

    if request.user.email is None or len(request.user.email) == 0:
        request.user.email = paypalEmailAddress
        request.user.save()

    EmailFactory().cashWithdrawal(request.user, paypalEmailAddress, cashValue)

    return HttpResponse(json.dumps({'success': True}), content_type="application/json")


@login_required
def charge_card(request):
    token = request.GET.get('token')
    netAmount = float(request.GET.get('netAmount'))
    chargeAmount = float(request.GET.get('chargeAmount'))

    stripe.api_key = getattr(settings, "STRIPE_SECRET_KEY")

    # Create the charge on Stripe's servers - this will charge the user's card
    try:
        charge = stripe.Charge.create(
            amount=int(chargeAmount * 100),  # amount in cents
            currency="usd",
            card=token,
            description="Deposit: %s" % request.user.fullname
        )

        Transaction.objects.deposit(request.user.account, netAmount, token)

        return HttpResponse(json.dumps({'success': True}), content_type="application/json")

    except stripe.StripeError, e:
        # The card has been declined
        return HttpResponse(json.dumps({'success': False, 'message': e.message}), content_type="application/json")


#################################
##  Django REST Framework
#################################

class IsAdminOrOwner(IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        can_edit = False
        if super(IsAdminOrOwner, self).has_object_permission(request, view, obj):
            if obj is None:
                # Either a list or a create, so no author
                can_edit = True
            else:
                can_edit = request.user.account == obj.account

        return can_edit


class ActivityTypeViewSet(viewsets.ReadOnlyModelViewSet):
    model = ActivityType


class AccountViewSet(viewsets.ReadOnlyModelViewSet):
    model = Account
    permission_classes = (IsAuthenticated,)
    serializer_class = AccountSerializer


class ActivityViewSet(viewsets.ReadOnlyModelViewSet):
    model = FitnessActivity


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    model = FitUser
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer


class ChallengeViewSet(viewsets.ReadOnlyModelViewSet):
    model = Challenge
    serializer_class = ChallengeSerializer


class TransactionViewSet(viewsets.ReadOnlyModelViewSet):
    model = Transaction
    serializer_class = TransactionSerializer
    permission_classes = (IsAdminOrOwner,)
    paginate_by_param = 'page_size'

    def get_queryset(self):
        queryset = super(TransactionViewSet, self).get_queryset()
        return queryset.filter(account=self.request.user.account).order_by('-date')