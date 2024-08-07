# Generated by Django 5.0.7 on 2024-08-05 07:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("guide", "0004_alter_program_video_info"),
    ]

    operations = [
        migrations.AlterField(
            model_name="audioinfo",
            name="component_type",
            field=models.IntegerField(
                choices=[
                    (0, "将来使用のためリザーブ"),
                    (1, "1/0モード（シングルモノ）"),
                    (2, "1/0+1/0モード（デュアルモノ）"),
                    (3, "2/0モード（ステレオ）"),
                    (4, "2/1モード"),
                    (5, "3/0モード"),
                    (6, "2/2モード"),
                    (7, "3/1モード"),
                    (8, "3/2モード"),
                    (9, "3/2＋LFEモード（3/2.1モード）"),
                    (10, "3/3.1モード"),
                    (11, "2/0/0-2/0/2-0.1モード"),
                    (12, "5/2.1モード"),
                    (13, "3/2/2.1モード"),
                    (14, "2/0/0-3/0/2-0.1モード"),
                    (15, "0/2/0-3/0/2-0.1モード"),
                    (16, "2/0/0-3/2/3-0.2モード"),
                    (17, "3/3/5-2/3-3/0/0.2モード"),
                    (18, "将来使用のためリザーブ"),
                    (31, "将来使用のためリザーブ"),
                ]
            ),
        ),
        migrations.AlterField(
            model_name="program",
            name="audio_infos",
            field=models.ManyToManyField(blank=True, to="guide.audioinfo"),
        ),
        migrations.AlterField(
            model_name="program",
            name="genres",
            field=models.ManyToManyField(blank=True, to="guide.genre"),
        ),
        migrations.AlterField(
            model_name="program",
            name="related_items",
            field=models.ManyToManyField(blank=True, to="guide.relateditem"),
        ),
    ]
