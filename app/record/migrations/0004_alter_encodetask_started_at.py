# Generated by Django 5.0.7 on 2024-08-08 14:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("record", "0003_encodetask"),
    ]

    operations = [
        migrations.AlterField(
            model_name="encodetask",
            name="started_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
