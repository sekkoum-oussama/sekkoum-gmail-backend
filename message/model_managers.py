from email.message import Message
from django.db import models


class UndeletedMessagesModelManager(models.Manager):
    def get_queryset(self) -> Message:
        return super().get_queryset()