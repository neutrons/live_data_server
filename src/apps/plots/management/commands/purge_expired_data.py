from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.plots.models import DataRun


class Command(BaseCommand):
    help = "Delete expired runs and related plots"

    def handle(self, *args, **options):  # noqa: ARG002
        runs = DataRun.objects.all()
        for run in runs:
            if run.expiration_date < timezone.now():
                run.delete()
