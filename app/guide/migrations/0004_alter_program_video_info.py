# Generated by Django 5.0.7 on 2024-08-04 13:21

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("guide", "0003_alter_relateditem_event_id_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="program",
            name="video_info",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="guide.videoinfo",
            ),
        ),
    ]
