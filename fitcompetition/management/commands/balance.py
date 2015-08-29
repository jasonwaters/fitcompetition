from django.core.management.base import BaseCommand
from fitcompetition.models import Transaction
from django.db.models import Sum
from decimal import Decimal


class Command(BaseCommand):
    def handle(self, *args, **options):

        result = Transaction.objects.all().aggregate(balance=Sum('amount'))

        self.stdout.write("Balance: %s" % result.get('balance', Decimal(0.0)))
