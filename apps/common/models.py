from django.db import models


class OutboxEvent(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PUBLISHED = "published", "Published"
        FAILED = "failed", "Failed"

    outbox_id = models.BigAutoField(primary_key=True)
    aggregate_type = models.CharField(max_length=64)
    aggregate_id = models.CharField(max_length=64, null=True, blank=True)
    event_type = models.CharField(max_length=128)
    payload = models.JSONField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    attempts = models.PositiveIntegerField(default=0)
    available_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "outbox_events"
        ordering = ["outbox_id"]
        indexes = [
            models.Index(fields=["status", "available_at"]),
            models.Index(fields=["event_type", "created_at"]),
        ]
