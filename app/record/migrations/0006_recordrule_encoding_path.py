# Generated by Django 5.0.7 on 2024-08-08 14:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("record", "0005_recordrule_encoder_path_alter_encodetask_file"),
    ]

    operations = [
        migrations.AddField(
            model_name="recordrule",
            name="encoding_path",
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
