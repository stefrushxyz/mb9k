from redistimeseries.client import Client

class TimeSeriesClient:
    def __init__(self):
        self.redis = Client('redis')

    def add_stream(self, stream):
        self.redis.create(self.key(stream), labels=self.label(stream))

    def add_detection(self, detection):
        self.redis.add(self.key(detection), '*', int(detection.mask_on), \
                       labels=self.label(detection))

    def key(self, model):
        return 'detections:{}'.format(self.stream_id(model))

    def label(self, model):
        return { 'stream': self.stream_id(model) }

    def stream_id(self, model):
        if not hasattr(model, 'stream'):
            return model.id
        return model.stream.id

