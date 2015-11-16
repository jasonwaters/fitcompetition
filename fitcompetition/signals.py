from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from fitcompetition.email import EmailFactory

from django.apps import apps
get_model = apps.get_model


#this is to avoid cyclical dependencies, since this file is imported in models.py
def getModel(name):
    return get_model('fitcompetition', name)


@receiver(post_save, sender=getModel('Transaction'))
def save_new_transaction(sender, **kwargs):
    if kwargs.get('created') and isinstance(kwargs['instance'], getModel('Transaction')):
        transaction = kwargs['instance']
        account = transaction.account

        try:
            user = account.fituser_set.all().order_by('-last_login')[0]

            if user and transaction.isCashflow and transaction.amount > 0:
                EmailFactory().cashDeposit(transaction, account, user)
        except IndexError:
            pass



@receiver(post_save, sender=getModel('Challenge'))
def save_new_challenge(sender, **kwargs):
    if kwargs.get('created') and isinstance(kwargs['instance'], getModel('Challenge')):
        challenge = kwargs['instance']
        if challenge.account is None:
            account = getModel('Account').objects.create(description="Challenge Account: %s" % challenge.name)

            challenge.account = account
            challenge.save()


@receiver(post_save, sender=getModel('FitUser'))
def save_new_user(sender, **kwargs):
    if kwargs.get('created') and isinstance(kwargs['instance'], getModel('FitUser')):
        user = kwargs['instance']

        if user.account is None:
            account = getModel('Account').objects.create(description = "User Account: %s" % user.fullname)

            user.account = account
            user.save()


@receiver(post_save, sender=getModel('Challenger'))
def save_new_challenger(sender, **kwargs):
    if kwargs.get('created') and isinstance(kwargs['instance'], getModel('Challenger')):
        user = kwargs['instance'].fituser
        challenge = kwargs['instance'].challenge

        getModel('Transaction').objects.transact(user.account,
                                                 challenge.account,
                                                 challenge.ante,
                                                 "Joined '%s' competition." % challenge.name,
                                                 "%s Joined" % user.fullname)

        EmailFactory().challengeJoin(user, challenge)

@receiver(post_delete, sender=getModel('Challenger'))
def delete_existing_challenger(sender, **kwargs):
    if isinstance(kwargs['instance'], getModel('Challenger')):
        user = kwargs['instance'].fituser
        challenge = kwargs['instance'].challenge

        getModel('Transaction').objects.transact(challenge.account,
                                                 user.account,
                                                 challenge.ante,
                                                 "%s Withdrew" % user.fullname,
                                                 "Withdrew from '%s' competition." % challenge.name)

        #remove membership on any teams too
        getModel('Team').objects.withdrawAll(challenge.id, user)