from django.core.management.base import BaseCommand
from django.utils import timezone

from ...models import DataRun


class Command(BaseCommand):
    help = "Delete expired runs and related plots"

    def handle(self, *args, **options):  # noqa: ARG002
        for item in DataRun.objects.all():
            if item.expiration_date < timezone.now():
                item.delete()
