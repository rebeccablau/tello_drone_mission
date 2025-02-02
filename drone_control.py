"""Script that manages drone commands."""
from djitellopy import Tello
from threading import Thread
import queue


class DroneController:
    def __init__(self):
        self.flying = False
        self.tello = Tello()
        self.tello.connect()
        print("Battery: %", self.tello.get_battery())
        self.command_queue = queue.Queue()
        self.process_cmd_thread = Thread(target=self.process_command, args=())
        self.process_cmd_thread.daemon = True

    def start(self):
        self.tello.streamon()
        self.process_cmd_thread.start()
        self.flying = True

    def get_frame(self):
        return self.tello.get_frame_read().frame

    def get_frame_dimensions(self):
        return self.tello.get_frame_read().frame.shape

    def is_flying(self):
        return self.flying

    def send_command(self, key):
        print("send_command ", key)
        self.command_queue.put(key)

    def process_command(self):
        while True:
            try:
                key = self.command_queue.get(timeout=7)
                print("command_queue.get ", key)
                if key == 27:  # ESC
                    self.tello.land()
                    self.flying = False
                elif key == ord("t"):
                    self.tello.takeoff()
                elif key == ord("f"):
                    self.tello.move_forward(30)
                elif key == ord("b"):
                    self.tello.move_back(30)
                elif key == ord("l"):
                    self.tello.move_left(30)
                elif key == ord("r"):
                    self.tello.move_right(30)
                elif key == ord("u"):
                    self.tello.move_up(30)
                elif key == ord("d"):
                    self.tello.move_down(30)
                elif key == ord("c"):
                    self.tello.rotate_clockwise(20)
                elif key == ord("q"):
                    self.tello.rotate_counter_clockwise(20)
            except queue.Empty:
                self.tello.send_control_command("command")  # keep drone alive
