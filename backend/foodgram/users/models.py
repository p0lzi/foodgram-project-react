from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """ Модель пользователя. """

    email = models.EmailField('Электронная почта', max_length=254, unique=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name')

    class Meta:

        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Subscribe(models.Model):
    user = models.ForeignKey(
        User,
        related_name="following",
        on_delete=models.CASCADE,
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        related_name="follower",
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
