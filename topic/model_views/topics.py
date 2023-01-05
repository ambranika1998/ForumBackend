from rest_framework.generics import ListCreateAPIView

from topic.models import Topic
from topic.serializers.topic_serializers import TopicSerializer


class TopicListCreateAPIView(ListCreateAPIView):
    """
    get:
    Return a list of Topic instances.

    post:
    Create a Topic instance.
    """
    queryset = Topic.objects.all()
    serializer_class = TopicSerializer

    def get_queryset(self):
        return self.queryset.filter(topic_section_id=self.kwargs['section_id'])


class TopicRetrieveUpdateAPIView(ListCreateAPIView):
    """
    get:
    Return a list of Topic instances.

    post:
    Create a Topic instance.
    """
    queryset = Topic.objects.all()
    serializer_class = TopicSerializer
