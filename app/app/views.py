from django.http import HttpResponse
from django.template.loader import get_template

from mb9k.settings import VERSION
from .models import Detection, Stream

app_name = 'mb9k'
version = VERSION

class Todo:
    def __init__(self, desc, lengthy=0):
        self.desc = desc
        self.lengthy = lengthy

class Link:
    def __init__(self, url, title):
        self.url = url
        self.title = title

class Source(Link):
    pass

def index(request):
    detection_count = Detection.objects.all().count()
    mask_on_count = Detection.objects.filter(mask_on=True).count()
    mask_on_rate = round(mask_on_count / detection_count * 100, 1) if detection_count else '-'
    mask_off_count = Detection.objects.filter(mask_on=False).count()
    mask_off_rate = round(mask_off_count / detection_count * 100, 1) if detection_count else '-'
    stream_count = Stream.objects.all().count()
    live_stream_count = Stream.objects.filter(live=True).count()
    latest_detection_image = Detection.objects.last().image_url() if detection_count else None

    return HttpResponse(get_template('app/index.html').render({
        'app_name': app_name,
        'version': version,
        'detection_count': detection_count,
        'mask_on_count': mask_on_count,
        'mask_on_rate': mask_on_rate,
        'mask_off_count': mask_off_count,
        'mask_off_rate': mask_off_rate,
        'stream_count': stream_count,
        'live_stream_count': live_stream_count,
        'latest_detection_image': latest_detection_image,
        'todos': [
            # Add or remove as needed
            Todo('Move detection images to more obscure url; urls can be guessed currently'),
            Todo('Add signal to delete detection image automatically when a detection is deleted; app/app/signals.py'),
            Todo('Find best way to add/upgrade dependencies on staging/production server'),
            Todo('Add time series compaction rule creation to current redis client; app/app/clients.py'),
            Todo('Add detection querying to current redis client; app/app/clients.py'),
            Todo('Build public API at /data for redis database to serve detection data as JSON'),
            Todo('Build public single-page frontend at / for public API; could be a graph with time filters: live, daily, weekly, and monthly; Javascript with WebSockets could be useful here; app/app/views.py; app/templates/app/index.html', 1),
            Todo('Configure nginx reverse-proxy for app to use HTTPS; proxy/nginx.conf'),
            Todo('Find best way to scale StreamWorker in production', 1),
            Todo('Deploy to Google Cloud Platform'),
        ],
        'links': [
            Link('/admin', 'Admin'),
            Link('https://github.com/CSCI-3308-CU-Boulder/F20-Team-Won/blob/dev/mb9k', 'Source'),
            Link('https://github.com/CSCI-3308-CU-Boulder/F20-Team-Won/blob/dev/mb9k/README.md', 'Docs'),
            Link('http://mb9k.site', 'Staging App Server'),
            Link('rtmp://mb9k.site/live/CHANGEME', 'Staging RTMP Server'),
            Link('http://localhost:8000', 'Development App Server'),
            Link('rtmp://localhost/live/ABCDE01234', 'Development RTMP Server'),
        ],
        'sources': [
            Source('https://testdriven.io/blog/dockerizing-django-with-postgres-gunicorn-and-nginx/', 'docker; docker-compose'),
            Source('https://benwilber.github.io/streamboat.tv/nginx/rtmp/streaming/2016/10/22/implementing-stream-keys-with-nginx-rtmp-and-django.html', 'nginx; rtmp'),
            Source('https://docs.opencv.org/3.4/db/d28/tutorial_cascade_classifier.html', 'opencv'),
            Source('https://www.pyimagesearch.com/2020/05/04/covid-19-face-mask-detector-with-opencv-keras-tensorflow-and-deep-learning/', 'opencv; keras'),
            Source('https://github.com/django/django', 'django'),
            Source('https://gist.github.com/thegitfather/9c9f1a927cd57df14a59c268f118ce86', 'javascript'),
            Source('https://gist.github.com/npearce/6f3c7826c7499587f00957fee62f8ee9', 'staging server'),
            Source('https://nvie.com/posts/a-successful-git-branching-model/', 'git'),
            Source('https://favicon.io/', 'favicons'),
            Source('https://github.com/miki725/django-rest-framework-bulk#example', 'django-rest-framework'),
            Source('https://github.com/eugenp/tutorials/tree/master/linux-bash/command-line-arguments/src/main/bash', 'bash'),
        ],
    }, request))

