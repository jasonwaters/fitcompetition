from fitcompetition.models import Challenge, FitnessActivity, FitUser, Transaction, Account
from rest_framework import serializers


class AccountSerializer(serializers.ModelSerializer):
    balance = serializers.DecimalField(source='balance', read_only=True)

    class Meta:
        model = Account


class UserSerializer(serializers.ModelSerializer):
    account = AccountSerializer(required=False)

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


class ActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = FitnessActivity


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction