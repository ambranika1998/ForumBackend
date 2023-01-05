from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from topic.models import Topic


class BasicTopicSerializer(ModelSerializer):
    class Meta:
        model = Topic
        fields = ['id', 'name']
        extra_kwargs = {'id': {'read_only': True}}


class TopicSerializer(ModelSerializer):
    class Meta:
        model = Topic
        fields = ['id', 'topic_section_id', 'name', 'text', 'user_id']
        extra_kwargs = {'id': {'read_only': True}}