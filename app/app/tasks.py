from celery import shared_task

from .workers import StreamWorker

@shared_task
def process_stream(stream):
    result = StreamWorker(stream).run()
    return result

