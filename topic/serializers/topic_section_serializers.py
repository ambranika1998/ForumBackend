from abc import ABC

from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from topic.models import TopicSection
from topic.serializers.topic_serializers import BasicTopicSerializer


class TopicSectionSerializer(ModelSerializer):
    topics = serializers.SerializerMethodField()

    class Meta:
        model = TopicSection
        fields = ['id', 'name', 'description', 'topics']
        extra_kwargs = {'id': {'read_only': True}}

    def get_topics(self, obj):
        return BasicTopicSerializer(obj.topics.all(), many=True).data


class TopicAndSectionFilterSerializer(serializers.Serializer):
    topic_search = serializers.CharField(max_length=255, required=False, allow_blank=True, allow_null=True)
