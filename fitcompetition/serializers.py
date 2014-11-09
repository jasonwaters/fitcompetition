from fitcompetition.models import Challenge, FitnessActivity, FitUser, Transaction, Account
from rest_framework import serializers


class AccountSerializer(serializers.ModelSerializer):
    balance = serializers.DecimalField(source='balance', read_only=True)
    isStripeCustomer = serializers.BooleanField(source='isStripeCustomer', read_only=True)

    class Meta:
        model = Account
        exclude = (
            'stripeCustomerID',
        )


class UserSerializer(serializers.ModelSerializer):
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
            'timezone',
        )


class ChallengeSerializer(serializers.ModelSerializer):
    approvedActivities = serializers.SlugRelatedField(many=True, read_only=True, slug_field="name")

    class Meta:
        model = Challenge

        exclude = (
            'account',
            'players'
        )


class ActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = FitnessActivity


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction