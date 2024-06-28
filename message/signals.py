from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Message


@receiver(post_save, sender=Message)
def add_original_if_not_set(sender, instance, created, **kwargs):
    if created:
        if instance.original == None:
            instance.original = instance
            instance.save()