from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """ Модель пользователя. """

    email = models.EmailField(
        'Электронная почта', unique=True,
        max_length=settings.MAX_LENGTH_FOR_EMAIL_OF_MODELS)
    first_name = models.CharField(
        "Имя",
        max_length=settings.MAX_LENGTH_FOR_NAME_OF_MODELS)
    last_name = models.CharField(
        "Фамилия",
        max_length=settings.MAX_LENGTH_FOR_NAME_OF_MODELS)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name')

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('email',)

    def __str__(self):
        return self.username


class Subscribe(models.Model):
    user = models.ForeignKey(
        User,
        related_name="followings",
        on_delete=models.CASCADE,
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        related_name="followers",
        on_delete=models.CASCADE,
        verbose_name='Подписка'
    )

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'author'),
                name='unique_user_author'
            )
        ]

    def __str__(self):
        return self.author.username
