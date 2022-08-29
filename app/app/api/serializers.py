from rest_framework.serializers import ModelSerializer
from rest_framework_bulk import BulkSerializerMixin, BulkListSerializer

from ..models import Stream, Detection

class StreamSerializer(BulkSerializerMixin, ModelSerializer):
    class Meta:
        model = Stream
        exclude = ('created_at', 'updated_at')
        list_serializer_class = BulkListSerializer

class DetectionSerializer(BulkSerializerMixin, ModelSerializer):
    class Meta:
        model = Detection
        exclude = ('created_at', 'updated_at')
        list_serializer_class = BulkListSerializer

