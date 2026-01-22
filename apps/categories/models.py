import uuid
from django.db import models
from django.conf import settings


class Category(models.Model):
    TYPE_CHOICES = [
        ('expense', 'Expense'),
        ('income', 'Income'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='categories'
    )
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=10)
    color = models.CharField(max_length=7)  # Hex color like #f97316
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'categories'
        ordering = ['name']
        unique_together = ['user', 'name', 'type']

    def __str__(self):
        return f"{self.icon} {self.name}"
