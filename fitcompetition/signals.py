from django import dispatch
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models.loading import get_model

# new_challenger = dispatch.Signal(providing_args=["toppings", "size"])


#this is to avoid cyclical dependencies, since this file is imported in models.py
from fitcompetition.email import Email
from fitcompetition.util.ListUtil import createListFromProperty


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

        getModel('Transaction').objects.transact(user.account,
                                                 challenge.account,
                                                 challenge.ante,
                                                 "Joined '%s' competition." % challenge.name,
                                                 "%s Joined" % user.fullname)

        if user.email and len(user.email) > 0:
            email = Email(to=user.email, subject='You joined "%s"' % challenge.name)

            approvedTypes = challenge.approvedActivities.all()

            ctxt = {
                'challenge': challenge,
                'user': user,
                'approvedActivities': createListFromProperty(approvedTypes, 'name'),
            }

            # email.text("email/test.txt", ctxt)
            email.html("email/joined_challenge.html", ctxt)
            email.send("FitCrown<contact@fitcrown.com>")


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