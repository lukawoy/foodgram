from django.contrib.auth.models import AbstractUser
from django.core import validators
from django.db import models


class User(AbstractUser):
    username = models.CharField(
        "Имя пользователя",
        unique=True,
        db_index=True,
        max_length=150,
        validators=[validators.RegexValidator(r"^[\w.@+-]+\Z")],
    )
    email = models.EmailField(
        "Адрес электронной почты", unique=True, max_length=254
    )
    first_name = models.CharField("Имя", max_length=150)
    last_name = models.CharField("Фамилия", max_length=150)
    avatar = models.ImageField(
        "Аватар", upload_to="users/", null=True, default=None, blank=True
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    class Meta:
        verbose_name = "пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ["username"]

    def __str__(self):
        return self.username


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Кто подписан",
        related_name="followings_user",
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="followings",
        verbose_name="На кого подписан",
    )

    class Meta:
        verbose_name = "подписка"
        verbose_name_plural = "Подписки"
        # order_with_respect_to = "user"

    def __str__(self):
        return f"Подписка {self.user.username} на {self.following.username}"
