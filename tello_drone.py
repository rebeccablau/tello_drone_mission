"""Manages the mission (user interface/drone camera, sending commands)."""
import cv2
import datetime
from object_detector import ObjectDetector
from drone_control import DroneController


class TelloDrone:
    def __init__(self):
        self.object_detector = ObjectDetector()

        self.drone_controller = DroneController()
        self.drone_controller.start()

        self.video_file_writer = None

    def start(self):
        """Record video & identify objects on screen while drone is flying."""

        # a frame counter is used to defer sending the first two frames because
        # the incorrect dimensions are returned until the third frame
        frame_counter = 1
        while self.drone_controller.is_flying():
            # process video frame
            frame = self.drone_controller.get_frame()
            if frame is not None:
                if frame_counter == 3:
                    height, width, _ = (
                        self.drone_controller.get_frame_dimensions())
                    fourcc = cv2.VideoWriter_fourcc(*"avc1")
                    video_file_name = "./videos/mission_{0}.mp4".format(
                        datetime.datetime.now())
                    self.video_file_writer = cv2.VideoWriter(
                        video_file_name, fourcc, 20, (width, height))

                frame_counter = frame_counter + 1
                self.object_detector.detect(frame)

                # draw rectangles on frame if objects are detected
                if hasattr(self.object_detector.result, "detections"):
                    frame = (self.object_detector.draw_objects
                             (frame, self.object_detector.result))

                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                cv2.imshow("Drone Video", frame)
                
                # write frame
                if self.video_file_writer is not None:
                    self.video_file_writer.write(frame)

            # listen and process keyboard commands
            key = cv2.waitKey(1)
            if key != -1:
                self.drone_controller.send_command(key)

        self.video_file_writer.release()
