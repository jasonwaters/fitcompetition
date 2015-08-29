from django.core.management.base import BaseCommand
from fitcompetition.models import Transaction
from django.db.models import Sum


class Command(BaseCommand):
    def handle(self, *args, **options):

        result = Transaction.objects.all().aggregate(balance=Sum('amount'))

        return getattr(result, 'balance')
