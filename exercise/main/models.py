from django.db import models
from django.core.validators import MinValueValidator
from users.models import User
from django.db.models import Q
from django.core.exceptions import ValidationError


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
    quote = models.TextField("Цитата", unique=True)
    weight = models.IntegerField("Вес цитаты", default=1)
    likes = models.PositiveBigIntegerField(
        "Лайки", validators=[MinValueValidator(0)], default=0
    )
    dislikes = models.PositiveBigIntegerField(
        "Дизлайки", validators=[MinValueValidator(0)], default=0
    )
    views = models.PositiveBigIntegerField("Просмотры", default=0)
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    source = models.ForeignKey(
        Source,
        verbose_name="Источник",
        on_delete=models.CASCADE,
        related_name="post_set",
    )
    liked_by = models.ManyToManyField(
        User, related_name="liked_posts", blank=True
    )
    added_by = models.ForeignKey(
        User,
        verbose_name="Добавил",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="added_posts",
    )

    def __str__(self):
        return f"{self.quote[:50]}..." if len(self.quote) > 50 else self.quote

    class Meta:
        verbose_name = "Пост"
        verbose_name_plural = "Посты"
        ordering = ["likes"]
        constraints = [
            models.UniqueConstraint(fields=["quote"], name="unique_post"),
        ]

    def clean(self):
        if self.source_id and self.source.post_set.count() >= 3:
            if (
                not self.pk
                or self.source.post_set.filter(pk=self.pk).count() == 0
            ):
                raise ValidationError(
                    "У источника не может быть больше 3 цитат"
                )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def rating(self):
        """Рассчитывает рейтинг цитаты (лайки минус дизлайки)"""
        return self.likes - self.dislikes

    @property
    def popularity_score(self):
        """Рассчитывает общий балл популярности"""
        return (self.likes * 2) - self.dislikes + (self.views // 10)
