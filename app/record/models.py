from django.db import models

# Create your models here.


class RecordRule(models.Model):
    keyword = models.CharField(max_length=255, null=True, blank=True)
    service_id = models.IntegerField(null=True, blank=True)
    is_enable = models.BooleanField(default=True)
    recording_path = models.CharField(max_length=255, blank=True)
    encoding_path = models.CharField(max_length=255, blank=True)
    encoder_path = models.CharField(max_length=255, null=True, blank=True)


class Recorded(models.Model):
    program = models.ForeignKey("guide.Program", on_delete=models.PROTECT)
    file = models.FileField(upload_to="recorded/")
    started_at = models.DateTimeField()
    last_updated_at = models.DateTimeField()
    ended_at = models.DateTimeField(null=True, blank=True)
    is_recording = models.BooleanField(default=False)


class EncodeTask(models.Model):
    recorded = models.ForeignKey(Recorded, on_delete=models.CASCADE)
    file = models.FileField(null=True, blank=True)
    encoder_path = models.CharField(max_length=255)
    encoding_path = models.CharField(max_length=255, blank=True)
    is_executed = models.BooleanField(default=False)
    error_message = models.TextField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)
