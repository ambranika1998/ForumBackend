from rest_framework import viewsets, permissions

from common.api_views import ForumListCreateAPIView
from topic.models import TopicSection
from topic.serializers.topic_section_serializers import TopicSectionSerializer, TopicAndSectionFilterSerializer


class TopicSectionListCreateAPIView(ForumListCreateAPIView):
    """
    get:
    Return a list of TopicSection instances.

    post:
    Create a TopicSection instance.
    """
    queryset = TopicSection.objects.all()
    read_serializer_class = TopicSectionSerializer
    write_serializer_class = TopicSectionSerializer
    filter_serializer_class = TopicAndSectionFilterSerializer


class TopicSectionViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = TopicSection.objects.all()
    serializer_class = TopicSectionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.data['filter']:
            return self.queryset.filter(topics__text__icontains=self.request.data['filter']).distinct()
        else:
            return self.queryset
