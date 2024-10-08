# Generated by Django 5.0.7 on 2024-08-08 14:00

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("record", "0002_recordrule_recording_path"),
    ]

    operations = [
        migrations.CreateModel(
            name="EncodeTask",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("file", models.FileField(upload_to="recorded/")),
                ("encoder_path", models.CharField(max_length=255)),
                ("is_executed", models.BooleanField(default=False)),
                ("error_message", models.TextField(blank=True, null=True)),
                ("started_at", models.DateTimeField()),
                ("ended_at", models.DateTimeField(blank=True, null=True)),
                (
                    "recorded",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="record.recorded",
                    ),
                ),
            ],
        ),
    ]
