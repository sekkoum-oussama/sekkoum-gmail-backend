from django.db import models
from django.contrib.auth import get_user_model

from message.model_managers import UndeletedMessagesModelManager


User = get_user_model()

class Message(models.Model):
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.DO_NOTHING)
    receivers = models.TextField(blank=True, null=True)
    invisible_to = models.ManyToManyField(User, related_name='deleted_messages')
    object = models.CharField(blank=True, null=True, max_length=100)
    text = models.CharField(blank=True, null=True, max_length=500, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    sent = models.BooleanField(default=False)
    original = models.ForeignKey('self', related_name='replies', on_delete=models.CASCADE, default=None, null=True)
    starred = models.ManyToManyField(User, related_name='starred_massages')
    important = models.ManyToManyField(User, related_name='important_massages')
    spam = models.ManyToManyField(User, related_name='spam_massages')
    archive = models.ManyToManyField(User, related_name='archived_massages')
    trash = models.ManyToManyField(User, related_name='trash_massages')

    objects = models.Manager()
    undeleted_messages = UndeletedMessagesModelManager()

    def __str__(self) -> str:
        return f"{self.object} ({self.sender.email} To {self.receivers})"


class Attachment(models.Model):
    message = models.ForeignKey(Message, related_name='attachments', on_delete=models.CASCADE)
    file = models.FileField()