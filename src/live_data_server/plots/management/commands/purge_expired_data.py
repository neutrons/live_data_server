from django.core.management.base import BaseCommand

from ...view_util import purge_expired_runs


class Command(BaseCommand):
    help = "Delete expired runs and related plots"

    def handle(self, *args, **options):  # noqa: ARG002
        purge_expired_runs()
