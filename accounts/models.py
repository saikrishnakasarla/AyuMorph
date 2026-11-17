"""
Models for the Accounts application.
"""

from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    institution = models.CharField(
        max_length=200,
        blank=True,
        default="",
        help_text="Academic institution, department, or research organization."
    )
    bio = models.TextField(
        blank=True,
        default="",
        help_text="Brief researcher biography or interest in botanical classification."
    )
    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True,
        help_text="Profile portrait image."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} Profile"
