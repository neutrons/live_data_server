# Generated by Django 5.1 on 2024-08-08 18:55

import datetime

from django.conf import settings
from django.db import migrations, models


def set_expiration_date(apps, schema_editor):
    DataRun = apps.get_model("plots", "DataRun")
    for run in DataRun.objects.all():
        if run.run_number == 0:
            run.expiration_date = run.created_on + datetime.timedelta(days=365*100)
        else:
            run.expiration_date = run.created_on + datetime.timedelta(days=settings.LIVE_PLOT_EXPIRATION_TIME)
        run.save()


class Migration(migrations.Migration):
    dependencies = [
        ("plots", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="datarun",
            name="expiration_date",
            field=models.DateTimeField(
                default=None,
                verbose_name="Expires",
            ),
        ),
        migrations.RunPython(set_expiration_date),
    ]
