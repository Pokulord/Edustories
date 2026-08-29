import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _

# Create your models here.


class Roadmap(models.Model):
    """Модель для дорожной карты"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(_("Название"), max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Дорожная карта"
        verbose_name_plural = "Дорожные карты"

    def __str__(self):
        return f"{self.title}"


class Node(models.Model):
    """Модель для узла дорожной карты"""

    class NodeStatuses(models.TextChoices):
        PUBLISHED = "published", _("Опубликован")
        DRAFT = "draft", _("Черновик")
        ARCHIEVED = "archieved", _("Архивный")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    roadmap = models.ForeignKey(
        Roadmap,
        on_delete=models.CASCADE,
        related_name="nodes",
        verbose_name=_("Дорожная карта"),
    )
    order = models.PositiveIntegerField(default=1)
    status = models.CharField(
        max_length=20, choices=NodeStatuses.choices, default=NodeStatuses.DRAFT
    )
    available_from = models.DateTimeField(null=True, blank=True)
    current_revision = models.OneToOneField(
        "NodeRevision",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="current_revision",
        verbose_name=_("Текущая ревизия"),
    )

    class Meta:
        ordering = ("order",)
        unique_together = ("roadmap", "order")
        verbose_name = "Узел карты"
        verbose_name_plural = "Узлы карты"

    def __str__(self):
        title = self.current_revision.title if self.current_revision else "-"
        return f"{self.order}. {title}"


class NodeRevision(models.Model):
    """Модель для ревизий узлов"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    node = models.ForeignKey(
        Node,
        on_delete=models.CASCADE,
        related_name="revisions",
        verbose_name=_("Ревизия"),
    )
    title = models.CharField(max_length=255)
    question_order = models.JSONField(
        default=list, help_text="Список UUID вопросов в порядке на момент ревизии"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)
        verbose_name = "Ревизия узла"
        verbose_name_plural = "Ревизии узлов"


class Question(models.Model):
    """Модель для вопросов к узлам"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    node = models.ForeignKey(
        Node,
        on_delete=models.CASCADE,
        related_name="questions",
        verbose_name="Вопрос к узлу",
    )
    order = models.PositiveIntegerField(default=1)
    current_revision = models.OneToOneField(
        "QuestionRevision",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="current_revision_for_question",
    )

    class Meta:
        ordering = ("order",)
        unique_together = ("node", "order")
        verbose_name = "Вопрос"
        verbose_name_plural = "Вопросы"

    def __str__(self):
        text = self.current_revision.text[:50] if self.current_revision else "—"
        return f"{self.order}: {text}"


class QuestionRevision(models.Model):
    """Ревизия контента вопроса. Никогда не обновляется."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="revisions",
    )
    text = models.TextField()
    correct_answer = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)
        verbose_name = "Ревизия вопроса"
        verbose_name_plural = "Ревизии вопросов"

    def __str__(self):
        return f"{self.text[:40]}... ({self.created_at:%d.%m.%Y})"
