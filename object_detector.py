"""Script for object detection."""
import time
import cv2
import numpy as np
import mediapipe as mp

MODEL_PATH = 'models/efficientdet_lite2.tflite'

MARGIN = 10
ROW_SIZE = 10
FONT_SIZE = 1
FONT_THICKNESS = 2
TEXT_COLOR = (255, 255, 255)  # white
LINE_COLOR = (255, 0, 0)  # red


class ObjectDetector:
    def __init__(self):
        self._detector = mp.tasks.vision.ObjectDetector
        self._result = mp.tasks.vision.ObjectDetectorResult
        self.__create_detector()

    @property
    def result(self):
        return self._result

    def __update_result(self, result: mp.tasks.vision.ObjectDetectorResult,
                        output_image: mp.Image, timestamp_ms: int):
        self._result = result

    def __create_detector(self):
        """Create a new detector using the chosen options."""
        options = mp.tasks.vision.ObjectDetectorOptions(
            base_options=mp.tasks.BaseOptions(model_asset_path=MODEL_PATH),
            running_mode=mp.tasks.vision.RunningMode.LIVE_STREAM,
            max_results=3, result_callback=self.__update_result)

        self._detector = self._detector.create_from_options(options)

    def detect(self, frame):
        """Convert the numpy array frame to a mediapipe image and detect
        images asynchronously."""
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
        self._detector.detect_async(image=mp_image,
                                    timestamp_ms=int(time.time() * 1000))

    def close(self):
        self._detector.close()

    @staticmethod
    def draw_objects(rgb_image,
                     detection_result: mp.tasks.vision.ObjectDetectorResult) \
            -> np.ndarray:
        """Draw boxes on the screen around detected objects."""
        for detection in detection_result.detections:
            # drawing box
            box = detection.bounding_box
            start_point = box.origin_x, box.origin_y
            end_point = box.origin_x + box.width, box.origin_y + box.height
            cv2.rectangle(rgb_image, start_point, end_point, LINE_COLOR, 2)

            category = detection.categories[0]
            category_name = category.category_name
            probability = round(category.score, 2)
            result_text = category_name + ' (' + str(probability) + ')'

            # draw filled rectangle for label and score
            (text_width, text_height), baseline = cv2.getTextSize(result_text,
                                                                  cv2.FONT_HERSHEY_PLAIN,
                                                                  FONT_SIZE,
                                                                  FONT_THICKNESS)
            baseline += MARGIN
            cv2.rectangle(rgb_image,
                          start_point,
                          (box.origin_x + text_width + baseline,
                           box.origin_y + text_height + baseline),
                          LINE_COLOR, -1)

            # draw label and score
            text_location = (MARGIN + box.origin_x, MARGIN + ROW_SIZE +
                             box.origin_y)
            cv2.putText(rgb_image,
                        result_text, text_location, cv2.FONT_HERSHEY_PLAIN,
                        FONT_SIZE, TEXT_COLOR, FONT_THICKNESS)

        return rgb_image
