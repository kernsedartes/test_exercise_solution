from django.db import models
from django.core.validators import MinValueValidator
from users.models import User
from django.db.models import Q


class Source(models.Model):
    name = models.CharField("Имя источника", max_length=128)

    class Meta:
        verbose_name = "Источник"
        verbose_name_plural = "Источники"
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(fields=["name"], name="unique_source"),
        ]


class Post(models.Model):
    quote = models.TextField("Цитата")
    weight = models.IntegerField("Вес цитаты")
    likes = models.PositiveBigIntegerField(
        "Лайки", validators=[MinValueValidator(0)]
    )
    dislikes = models.IntegerField(
        "Дизлайки", validators=[MinValueValidator(0)]
    )
    source = models.ForeignKey(
        Source,
        verbose_name="Источник",
        on_delete=models.CASCADE,
        related_name="posts",
    )

    class Meta:
        verbose_name = "Пост"
        verbose_name_plural = "Посты"
        ordering = ["likes"]
        constraints = [
            models.UniqueConstraint(fields=["quote"], name="unique_post"),
            models.CheckConstraint(condition=Q(posts__count__lte=3)),
        ]
