from fitcompetition.models import Challenge, FitnessActivity, FitUser, Transaction, Account
from rest_framework import serializers


class AccountSerializer(serializers.ModelSerializer):
    balance = serializers.DecimalField(source='balance', read_only=True)

    class Meta:
        model = Account
        fields = (
            'id',
            'description',
            'balance'
        )


class UserSerializer(serializers.ModelSerializer):
    account = AccountSerializer(required=False)

    transactions = serializers.HyperlinkedIdentityField('transactions', view_name='usertransactions-list')

    class Meta:
        model = FitUser
        fields = (
            'id',
            'first_name',
            'last_name',
            'fullname',
            'medium_picture',
            'normal_picture',
            'integrationName',
            'gender',
            'account',
        )


class ChallengeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Challenge
        #account
        #teams
        #players
        fields = ('id',
                  'name',
                  'type',
                  'style',
                  'description',
                  'distance',
                  'startdate',
                  'enddate',
                  'ante'
        )


class ActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = FitnessActivity
        fields = ('id',
                  'user',
                  'duration',
                  'date',
                  'calories',
                  'distance',
                  'photo',
                  'hasEvidence'
        )


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ('id',
                  'date',
                  'description',
                  'amount',
                  'isCashflow',
        )