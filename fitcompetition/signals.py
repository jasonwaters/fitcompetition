from django.db.models.signals import post_save, pre_delete, m2m_changed, post_delete
from django.dispatch import receiver
from django.db.models.loading import get_model
from datetime import datetime

from fitcompetition.settings import TIME_ZONE
import pytz


#this is to avoid cyclical dependencies, since this file is imported in models.py
def getModel(name):
    return get_model('fitcompetition', name)


@receiver(post_save, sender=getModel('Challenge'))
def save_new_challenge(sender, **kwargs):
    if kwargs.get('created') and isinstance(kwargs['instance'], getModel('Challenge')):
        challenge = kwargs['instance']
        account, created = getModel('Account').objects.get_or_create(challenge=challenge)
        if created:
            account.description = "Challenge Account: %s" % challenge.name
            account.save()


@receiver(post_save, sender=getModel('FitUser'))
def save_new_user(sender, **kwargs):
    if kwargs.get('created') and isinstance(kwargs['instance'], getModel('FitUser')):
        user = kwargs['instance']
        account, created = getModel('Account').objects.get_or_create(user=user)

        if created:
            account.description = "User Account: %s" % user.fullname
            account.save()


@receiver(post_save, sender=getModel('Challenger'))
def save_new_challenger(sender, **kwargs):
    if kwargs.get('created') and isinstance(kwargs['instance'], getModel('Challenger')):
        user = kwargs['instance'].fituser
        challenge = kwargs['instance'].challenge

        now = datetime.now(tz=pytz.timezone(TIME_ZONE))

        getModel('Transaction').objects.create(date=now,
                                               account=user.account,
                                               description="Joined '%s' competition." % challenge.name,
                                               amount=challenge.ante * -1)

        getModel('Transaction').objects.create(date=now,
                                               account=challenge.account,
                                               description="%s Joined" % user.fullname,
                                               amount=challenge.ante)


@receiver(post_delete, sender=getModel('Challenger'))
def delete_existing_challenger(sender, **kwargs):
    if isinstance(kwargs['instance'], getModel('Challenger')):
        user = kwargs['instance'].fituser
        challenge = kwargs['instance'].challenge

        now = datetime.now(tz=pytz.timezone(TIME_ZONE))
        getModel('Transaction').objects.create(date=now,
                                               account=user.account,
                                               description="Withdrew from '%s' competition." % challenge.name,
                                               amount=challenge.ante)

        getModel('Transaction').objects.create(date=now,
                                               account=challenge.account,
                                               description="%s Withdrew" % user.fullname,
                                               amount=challenge.ante*-1)

        #remove membership on any teams too
        getModel('Team').objects.withdrawAll(challenge.id, user)