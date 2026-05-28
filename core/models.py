import os
import uuid

from django.core.validators import FileExtensionValidator
from django.db import models

from core.utils import ALLOWED_AVATAR_EXTENSIONS, upload_to


def avatar_upload_to(instance, filename):
    return upload_to("avatars", filename)


class Profile(models.Model):
    user = models.OneToOneField(
        "auth.User",
        on_delete=models.CASCADE,
        related_name="profile",
        verbose_name="Пользователь",
    )

    avatar = models.ImageField(
        upload_to=avatar_upload_to,
        null=True,
        blank=True,
        verbose_name="Аватар",
        validators=[
            FileExtensionValidator(allowed_extensions=ALLOWED_AVATAR_EXTENSIONS)
        ],
    )

    class Meta:
        verbose_name = "Профиль"
        verbose_name_plural = "Профили"

    def __str__(self):
        return self.user.username
