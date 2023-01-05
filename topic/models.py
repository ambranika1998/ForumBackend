from django.contrib.auth.models import User
from django.db import models


# Create your models here.

class TopicSection(models.Model):
    class Meta:
        db_table = 'topic_section'
        verbose_name = 'Topic Section'
        verbose_name_plural = 'Topic Sections'

    name = models.CharField(verbose_name='name', max_length=50, unique=True)
    description = models.CharField(verbose_name='description', max_length=200, null=True, blank=True)

    def __str__(self):
        return self.name


class Topic(models.Model):
    class Meta:
        db_table = 'topic'
        verbose_name = 'Topic'
        verbose_name_plural = 'Topics'

    topic_section = models.ForeignKey(TopicSection, related_name='topics', on_delete=models.CASCADE)
    text = models.CharField(verbose_name='text', max_length=2000, blank=True, null=True)
    # photo = models.ImageField(null=True, blank=True)
    user = models.ForeignKey(User, related_name='topics', on_delete=models.CASCADE)
    created_on = models.DateField(auto_now_add=True)


class Comment(models.Model):
    class Meta:
        db_table = 'comment'
        verbose_name = 'Comment'
        verbose_name_plural = 'Comments'

    topic = models.ForeignKey(Topic, related_name='comments', on_delete=models.CASCADE)
    text = models.CharField(verbose_name='text', max_length=2000, blank=True, null=True)
    # photo = models.ImageField(null=True, blank=True)
    user = models.ForeignKey(User, related_name='comments', on_delete=models.CASCADE)
    created_on = models.DateField(auto_now_add=True)
    parent = models.ForeignKey('self', related_name='comments', on_delete=models.CASCADE, null=True)
