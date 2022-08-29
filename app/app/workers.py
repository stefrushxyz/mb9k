import os
import cv2
import argparse
import imutils
import time
import numpy as np
from requests import post, ConnectionError
from datetime import datetime
from random import choice
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras.models import load_model

class StreamWorker:
    def __init__(self, stream, **kwargs):
        self.stream_id = stream.get('id')
        self.stream_key = stream.get('key')
        self.headless = kwargs.get('headless', True)
        self.cap_host = kwargs.get('cap_host', 'rtmp')
        self.api_host = kwargs.get('api_host', 'app:8000')
        self.get_interval = kwargs.get('get_interval', 1)
        self.submit_interval = kwargs.get('submit_interval', 2)
        self.confidence_threshold = kwargs.get('confidence_threshold', 0.5)

        self.cap_url = f'rtmp://{self.cap_host}/live/{self.stream_key}'
        self.api_url = f'http://{self.api_host}/api/'

        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.image_dir = os.path.join(self.base_dir, f'mediafiles/detections/{self.stream_id}')
        os.makedirs(self.image_dir, exist_ok=True)

        self.haar_dir = cv2.data.haarcascades
        self.face_xml = os.path.join(self.haar_dir, 'haarcascade_frontalface_default.xml')
        self.face_haar = cv2.CascadeClassifier(self.face_xml)
        self.box_color = (200, 174, 121)

        self.cap = None
        self.get_at = None
        self.submit_at = None
        self.detections_submitted = 0
        self.errors = []

        self.ml_dir = os.path.join(self.base_dir, 'app/ml')
        self.proto_path = os.path.join(self.ml_dir, 'deploy.prototxt')
        self.weights_path = os.path.join(self.ml_dir, 'res10_300x300_ssd_iter_140000.caffemodel')
        self.model_path = os.path.join(self.ml_dir, 'mask_detector.model')

        self.face_net = cv2.dnn.readNet(self.proto_path, self.weights_path)
        self.mask_net = load_model(self.model_path)

        if not self.headless:
            os.environ['OPENCV_FFMPEG_CAPTURE_OPTIONS'] = 'rtsp_transport;udp'

    def run(self):
        self.cap = cv2.VideoCapture(self.cap_url, cv2.CAP_FFMPEG)

        while self.cap.isOpened():
            ret, frame = self.cap.read()

            if not ret:
                break

            if self.interval_passed(self.get_interval, self.get_at):
                (locations, predictions) = self.get_detection_boxes(frame)

                can_submit = self.interval_passed(self.submit_interval, \
                                                  self.submit_at)
                self.process_detections(locations, predictions, frame, can_submit)

                if not self.headless and self.show_frame(frame):
                    break

        self.cap.release()
        if not self.headless:
            cv2.destroyAllWindows()

        return {
            'stream_id': self.stream_id,
            'detections_submitted': self.detections_submitted,
            'errors': len(self.errors),
        }

    def interval_passed(self, interval, event_at):
        if not event_at or not interval:
            return True
        seconds_since_event = (datetime.now() - event_at).seconds
        return seconds_since_event >= interval

    def get_detection_boxes(self, frame):
        self.get_at = datetime.now()

        (org_h, org_w) = frame.shape[:2]

        frame = imutils.resize(frame, width=400)

        (h, w) = frame.shape[:2]
        blob = cv2.dnn.blobFromImage(frame, 1.0, (300, 300), (104.0, 177.0, 123.0))

        self.face_net.setInput(blob)
        detections = self.face_net.forward()

        faces = []
        locs = []
        preds = []

        for i in range(0, detections.shape[2]):
            confidence = detections[0, 0, i, 2]

            if confidence <= self.confidence_threshold:
                continue

            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            (start_x, start_y, end_x, end_y) = box.astype("int")

            (start_x, start_y) = (max(0, start_x), max(0, start_y))
            (end_x, end_y) = (min(w - 1, end_x), min(h - 1, end_y))

            face = frame[start_y:end_y, start_x:end_x]
            try:
                face = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)
            except Exception as e:
                self.errors.append(e)
            face = cv2.resize(face, (224, 224))
            face = img_to_array(face)
            face = preprocess_input(face)

            (start_x, start_y) = (int(start_x * (org_w / w)), int(start_y * (org_h / h)))
            (end_x, end_y) = (int(end_x * (org_w / w)), int(end_y  * (org_h / h)))

            faces.append(face)
            locs.append((start_x, start_y, end_x, end_y))

        if len(faces) > 0:
            faces = np.array(faces, dtype="float32")
            preds = self.mask_net.predict(faces, batch_size=32)

        return (locs, preds)

    def process_detections(self, locations, predictions, frame, can_submit=False):
        detections_json = []

        for (box, pred) in zip(locations, predictions):
            (start_x, start_y, end_x, end_y) = box
            (mask_on, mask_off) = pred

            mask = bool(mask_on > mask_off)
            label = 'Mask On' if mask else 'Mask Off'
            label = "{}: {:.2f}%".format(label, max(mask_on, mask_off) * 100)
            color = (0, 255, 0) if mask else (0, 0, 255)

            cv2.putText(frame, label, (start_x, start_y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 2)
            cv2.rectangle(frame, (start_x, start_y), (end_x, end_y), color, 2)

            detections_json.append({
                'mask_on': mask,
                'stream': self.stream_id,
            })

        if can_submit:
            self.submit_detections(detections_json, frame)

    def submit_detections(self, detections_json, image):
        try:
            detections = post(f'{self.api_url}detections/', \
                              json=detections_json).json()
        except ConnectionError as e:
            self.errors.append(e)
            detections = None

        if type(detections) is list and len(detections) > 0:
            self.submit_at = datetime.now()
            self.detections_submitted += len(detections)
            for detection in detections:
                cv2.imwrite(self.image_path(detection.get('id')), image)

    def image_path(self, detection_id):
        return os.path.join(self.image_dir, f'{detection_id}.jpg')

    def show_frame(self, frame):
        cv2.imshow('mb9k StreamWorker', frame)
        return (cv2.waitKey(1) & 0xFF) == ord('q')