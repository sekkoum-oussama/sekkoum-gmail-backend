from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver
import allauth

User = get_user_model()

@receiver(allauth.account.signals.user_signed_up)
def add_profile_picture(sender, user, **kwargs):
    user.photo = user.socialaccount_set.filter(provider='google')[0].extra_data['picture']
    user.save()