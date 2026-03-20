from django.conf import settings
from django.core.management.base import BaseCommand

from common.services.outbox_publisher import publish_outbox_batch


class Command(BaseCommand):
    help = "Publish pending outbox events across configured databases."

    def add_arguments(self, parser):
        parser.add_argument(
            "--databases",
            default=",".join(getattr(settings, "OUTBOX_DATABASES", ["default"])),
            help="Comma separated DB aliases. ex) default,auth_db,events_db",
        )
        parser.add_argument("--limit", type=int, default=settings.OUTBOX_PUBLISH_BATCH_SIZE)
        parser.add_argument(
            "--aggregate-type",
            default=settings.OUTBOX_NOTIFICATION_AGGREGATE_TYPE,
        )
        parser.add_argument("--max-retries", type=int, default=settings.OUTBOX_MAX_RETRIES)
        parser.add_argument(
            "--retry-base-delay-seconds",
            type=int,
            default=settings.OUTBOX_RETRY_BASE_DELAY_SECONDS,
        )

    def handle(self, *args, **options):
        db_aliases = [d.strip() for d in options["databases"].split(",") if d.strip()]
        if not db_aliases:
            db_aliases = ["default"]

        total = {"picked": 0, "published": 0, "failed": 0}
        for alias in db_aliases:
            result = publish_outbox_batch(
                database=alias,
                aggregate_type=options["aggregate_type"],
                limit=options["limit"],
                max_retries=options["max_retries"],
                retry_base_delay_seconds=options["retry_base_delay_seconds"],
            )
            total["picked"] += result["picked"]
            total["published"] += result["published"]
            total["failed"] += result["failed"]
            self.stdout.write(
                self.style.SUCCESS(
                    "[{db}] picked={picked} published={published} failed={failed}".format(
                        db=alias, **result
                    )
                )
            )

        self.stdout.write(
            self.style.SUCCESS(
                "total picked={picked} published={published} failed={failed}".format(**total)
            )
        )
