from django.db.models.signals import post_save, pre_delete, m2m_changed, post_delete
from django.dispatch import receiver
from django.db.models.loading import get_model
from datetime import datetime

from fitcompetition.settings import TIME_ZONE
import pytz


#this is to avoid cyclical dependencies, since this file is imported in models.py
def getModel(name):
    return get_model('fitcompetition', name)


@receiver(post_save, sender=getModel('Challenger'))
def save_new_challenger(sender, **kwargs):
    if kwargs.get('created') and isinstance(kwargs['instance'], getModel('Challenger')):
        user = kwargs['instance'].fituser
        challenge = kwargs['instance'].challenge

        now = datetime.now(tz=pytz.timezone(TIME_ZONE))
        getModel('Transaction').objects.create(date=now,
                                               user=user,
                                               description="Joined '%s' competition." % challenge.name,
                                               amount=challenge.ante * -1,
                                               challenge=challenge)


@receiver(post_delete, sender=getModel('Challenger'))
def delete_existing_challenger(sender, **kwargs):
    if isinstance(kwargs['instance'], getModel('Challenger')):
        user = kwargs['instance'].fituser
        challenge = kwargs['instance'].challenge

        now = datetime.now(tz=pytz.timezone(TIME_ZONE))
        getModel('Transaction').objects.create(date=now,
                                               user=user,
                                               description="Withdrew from '%s' competition." % challenge.name,
                                               amount=challenge.ante,
                                               challenge=challenge)

        #remove membership on any teams too
        getModel('Team').objects.withdrawAll(challenge.id, user)