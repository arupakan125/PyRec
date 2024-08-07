from django.db import models

# Create your models here.


class RecordRule(models.Model):
    keyword = models.CharField(max_length=255, null=True, blank=True)
    service_id = models.IntegerField(null=True, blank=True)
    is_enable = models.BooleanField(default=True)


class Recorded(models.Model):
    program = models.ForeignKey('guide.Program', on_delete=models.PROTECT)
    file = models.FileField(upload_to='recorded/')
    started_at = models.DateTimeField()
    last_updated_at = models.DateTimeField()
    ended_at = models.DateTimeField(null=True, blank=True)
    is_recording = models.BooleanField(default=False)
