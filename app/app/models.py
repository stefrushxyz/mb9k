from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.timezone import localtime
from django.utils.html import format_html, escape
from random import choice

from mb9k.settings import HOSTNAME

def time_since_str(from_time, full=False):
    delta = timezone.now() - from_time

    time_since = {}
    time_since['d'] = delta.days
    time_since['h'], rem_s = divmod(delta.seconds, 60 * 60)
    time_since['m'], time_since['s'] = divmod(rem_s, 60)

    show_s = show_m = True
    if not full:
        show_s = not (time_since['h'] > 0 or time_since['d'] > 0)
        show_m = not (time_since['d'] > 0)

    time_str = (
        f'{time_since["d"]} d' if time_since['d'] > 0 else '',
        f'{time_since["h"]} h' if time_since['h'] > 0 else '',
        f'{time_since["m"]} m' if time_since['m'] > 0 and show_m else '',
        f'{time_since["s"]} s' if show_s else '',
    )

    return ' '.join(filter(None, time_str))

class Stream(models.Model):
    name = models.CharField(max_length=255)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    identifier = models.CharField(max_length=255, unique=True, blank=True)
    key = models.CharField(max_length=10, unique=True, blank=True)
    active = models.BooleanField(default=True)
    live = models.BooleanField(default=False)
    live_at = models.DateTimeField(blank=True, null=True)
    not_live_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True)
    created_at = models.DateTimeField(blank=True)

    def __str__(self):
        s = [self.identifier]
        if self.live:
            s.append('<LIVE>')
        return ' '.join(s)

    def save(self, *args, **kwargs):
        if not self.id:
            self.created_at = timezone.now()
        self.updated_at = timezone.now()

        if not self.key:
            self.key = self.generate_key(self.__class__.key.field.max_length)

        self.identifier = f'{self.owner.username}:{self.name}'

        return super().save(*args, **kwargs)

    def url(self):
        return f'rtmp://{HOSTNAME}/live/{self.key}'

    def link(self):
        return format_html('<a href="{}">{}</a>', *((escape(self.url()),) * 2))

    def uptime(self):
        return '-' if not self.live else time_since_str(self.live_at)

    def generate_key(self, key_len):
        gen_key = []
        alpha_offset = ord('A') - ord('9') - 1

        for _ in range(key_len):
            r = choice(range(36))
            c = ord('0') + r + (alpha_offset if r >= 10 else 0)
            gen_key.append(chr(c))

        return ''.join(gen_key)

class Detection(models.Model):
    mask_on = models.BooleanField()
    detected_at = models.DateTimeField(blank=True)
    stream = models.ForeignKey(Stream, on_delete=models.CASCADE)
    created_at = models.DateTimeField(blank=True)
    updated_at = models.DateTimeField(blank=True)

    def image_url(self):
        return '/media/detections/{}/{}.jpg'.format(self.stream.id, self.id)

    def image(self):
        return format_html('<img src="{}" alt="{}">', \
                           escape(self.image_url()), 'Detection Image')

    def __str__(self):
        s = [
            localtime(self.detected_at).strftime('%Y/%m/%d %H:%M:%S %Z'),
            self.stream.identifier,
            '<MASK',
            'ON>' if self.mask_on else 'OFF>',
        ]
        return ' '.join(s)

    def save(self, *args, **kwargs):
        if not self.id:
            self.created_at = timezone.now()
        self.updated_at = timezone.now()

        if not self.detected_at:
            self.detected_at = timezone.now()

        return super().save(*args, **kwargs)

