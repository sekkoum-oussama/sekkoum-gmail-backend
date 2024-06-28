from django.contrib import admin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ("email", "username", "is_staff", "date_joined")
    list_editable = ("username", "is_staff")
    list_filter = ("email",)