from apps.plots.models import DataRun
from django.core.management.base import BaseCommand
from django.utils import timezone


class Command(BaseCommand):
    help = "Delete expired runs and related plots"

    def handle(self, *args, **options):  # noqa: ARG002
        runs = DataRun.objects.all()
        expired_runs = 0
        for run in runs:
            if run.expiration_date < timezone.now():
                expired_runs += 1
                run.delete()
        self.stdout.write(self.style.SUCCESS(f"Deleted {expired_runs} expired runs"))
