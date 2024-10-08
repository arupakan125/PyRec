# Generated by Django 5.0.7 on 2024-08-05 19:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("guide", "0005_alter_audioinfo_component_type_and_more"),
    ]

    operations = [
        migrations.AddConstraint(
            model_name="relateditem",
            constraint=models.UniqueConstraint(
                fields=("item_type", "network_id", "service_id", "event_id"),
                name="unique_related_item",
            ),
        ),
    ]
