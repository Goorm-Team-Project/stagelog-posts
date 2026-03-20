import json
from datetime import timedelta
import logging

import boto3
from django.conf import settings
from django.db import DatabaseError, transaction
from django.utils import timezone

from common.models import OutboxEvent

logger = logging.getLogger(__name__)


def _eventbridge_client():
    return boto3.client("events", region_name=settings.AWS_REGION)


def _build_entries(events, event_bus_name: str):
    entries = []
    for event in events:
        payload = event.payload or {}
        entries.append(
            {
                "EventBusName": event_bus_name,
                "Source": payload.get("source", "stagelog.core"),
                "DetailType": event.event_type,
                "Detail": json.dumps(payload, ensure_ascii=False),
            }
        )
    return entries


def publish_outbox_batch(
    *,
    database: str = "default",
    aggregate_type: str = "notification",
    limit: int = 50,
    max_retries: int = 5,
    retry_base_delay_seconds: int = 30,
):
    now = timezone.now()
    logger.info(
        "outbox_publisher batch_start database=%s aggregate_type=%s limit=%s",
        database,
        aggregate_type,
        limit,
    )
    manager = OutboxEvent.objects.using(database)
    qs = manager.filter(status=OutboxEvent.Status.PENDING, available_at__lte=now)
    if aggregate_type:
        qs = qs.filter(aggregate_type=aggregate_type)

    with transaction.atomic(using=database):
        try:
            events = list(qs.select_for_update(skip_locked=True).order_by("outbox_id")[:limit])
        except DatabaseError:
            events = list(qs.select_for_update().order_by("outbox_id")[:limit])

        if not events:
            logger.info(
                "outbox_publisher batch_end database=%s picked=0 published=0 failed=0",
                database,
            )
            return {"picked": 0, "published": 0, "failed": 0}

        entries = _build_entries(events, settings.NOTIFICATION_EVENT_BUS_NAME)

        try:
            response = _eventbridge_client().put_events(Entries=entries)
            result_entries = response.get("Entries", [])
        except Exception:
            logger.exception("outbox_publisher put_events_failed database=%s", database)
            result_entries = [{} for _ in events]

        published = 0
        failed = 0
        for idx, event in enumerate(events):
            result = result_entries[idx] if idx < len(result_entries) else {}
            if result.get("EventId") and not result.get("ErrorCode"):
                event.status = OutboxEvent.Status.PUBLISHED
                event.published_at = now
                event.save(using=database, update_fields=["status", "published_at"])
                logger.info(
                    "outbox_publisher published database=%s outbox_id=%s event_type=%s event_id=%s",
                    database,
                    event.outbox_id,
                    event.event_type,
                    result.get("EventId"),
                )
                published += 1
                continue

            failed += 1
            event.attempts += 1
            logger.warning(
                "outbox_publisher publish_failed database=%s outbox_id=%s event_type=%s error_code=%s error_message=%s attempts=%s",
                database,
                event.outbox_id,
                event.event_type,
                result.get("ErrorCode"),
                result.get("ErrorMessage"),
                event.attempts,
            )
            if event.attempts >= max_retries:
                event.status = OutboxEvent.Status.FAILED
                event.save(using=database, update_fields=["status", "attempts"])
                continue

            event.status = OutboxEvent.Status.PENDING
            event.available_at = now + timedelta(seconds=retry_base_delay_seconds * event.attempts)
            event.save(using=database, update_fields=["status", "attempts", "available_at"])

        logger.info(
            "outbox_publisher batch_end database=%s picked=%s published=%s failed=%s",
            database,
            len(events),
            published,
            failed,
        )
        return {"picked": len(events), "published": published, "failed": failed}
