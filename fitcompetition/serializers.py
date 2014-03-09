from fitcompetition.models import Challenge
from rest_framework import serializers


class ChallengeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Challenge
        fields = ('name',
                  'type',
                  'style',
                  'description',
                  'distance',
                  'startdate',
                  'enddate',
                  'ante')