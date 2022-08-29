from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth.models import User

from .models import Stream, Detection
from .clients import TimeSeriesClient

rts_client = TimeSeriesClient()

@receiver(post_save, sender=Stream)
def add_stream(sender, instance, created, **kwargs):
    if created:
        rts_client.add_stream(instance)

@receiver(post_save, sender=Detection)
def add_detection(sender, instance, created, **kwargs):
    if created:
        rts_client.add_detection(instance)

@receiver(post_save, sender=User)
def update_user_streams(sender, instance, **kwargs):
    user_streams = Stream.objects.filter(owner=instance)
    for stream in user_streams:
        stream.save()

