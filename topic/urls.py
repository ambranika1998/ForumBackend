from django.urls import path

from topic.model_views.topic_section import TopicSectionViewSet
from topic.model_views.topics import TopicListCreateAPIView, TopicRetrieveUpdateAPIView

FORUM_SECTIONS = 'forum-sections'
FORUM_TOPIC = 'forum-topic'

urlpatterns = [
    path('topic-sections/', TopicSectionViewSet.as_view({'post': 'list'}), name=FORUM_SECTIONS),
    path('topics/<int:section_id>/', TopicListCreateAPIView.as_view(), name=FORUM_TOPIC),
    path('topics/<int:pk>/', TopicRetrieveUpdateAPIView.as_view(), name=FORUM_TOPIC)
    ]
