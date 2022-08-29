from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from rest_framework_bulk import ListBulkCreateUpdateDestroyAPIView as ListAPI
from rest_framework.generics import RetrieveUpdateDestroyAPIView as SingleAPI

from ..tasks import process_stream
from ..models import Stream, Detection
from .serializers import StreamSerializer, DetectionSerializer

@require_POST
@csrf_exempt
def stream_start(request):
    key = request.POST['name']
    stream = get_object_or_404(Stream, key=key, active=True)

    stream.live = True
    stream.live_at = timezone.now()
    stream.save()

    process_stream.delay(StreamSerializer(stream).data)

    return HttpResponse(status=201)

@require_POST
@csrf_exempt
def stream_stop(request):
    key = request.POST['name']
    stream = get_object_or_404(Stream, key=key)

    stream.live = False
    stream.not_live_at = timezone.now()
    stream.save()

    return HttpResponse(status=201)

@require_GET
@csrf_exempt
def stream_by_key(request, key=None):
    stream = get_object_or_404(Stream, key=key)
    res = StreamSerializer(stream).data
    return JsonResponse(res, safe=False)

StreamQuery = Stream.objects.all().order_by('-created_at')
ListStreamsAPI = ListAPI.as_view(queryset=StreamQuery, serializer_class=StreamSerializer)
SingleStreamAPI = SingleAPI.as_view(queryset=StreamQuery, serializer_class=StreamSerializer)

DetectionQuery = Detection.objects.all().order_by('-created_at')
ListDetectionsAPI = ListAPI.as_view(queryset=DetectionQuery, serializer_class=DetectionSerializer)
SingleDetectionAPI = SingleAPI.as_view(queryset=DetectionQuery, serializer_class=DetectionSerializer)

