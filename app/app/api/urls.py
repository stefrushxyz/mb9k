from django.urls import path

from .views import (
    ListStreamsAPI,
    SingleStreamAPI,
    stream_start,
    stream_stop,
    stream_by_key,
    ListDetectionsAPI,
    SingleDetectionAPI,
)

urlpatterns = [
    path('streams/', ListStreamsAPI),
    path('streams/<int:pk>/', SingleStreamAPI),
    path('streams/start/', stream_start),
    path('streams/stop/', stream_stop),
    path('streams/by_key/<slug:key>/', stream_by_key),
    path('detections/', ListDetectionsAPI),
    path('detections/<int:pk>/', SingleDetectionAPI),
]

