from AutoPilot import AutoPilot
import imutils
from imutils.video import VideoStream
import cv2
import argparse
import time

DEFAULT_DEBUG = False


class SkyPi:
    def __init__(self):
        self.camera = self.turn_on_camera()
        self.color_to_follow_bounds = self.get_color_bounds()
        self.auto_pilot = AutoPilot(self.color_to_follow_bounds[0], self.color_to_follow_bounds[1])
        self.flight_controller = FlightControllet()

    @staticmethod
    def get_color_bounds():
        green_lower = (29, 86, 6)
        green_upper = (64, 255, 255)
        return green_lower, green_upper

    @staticmethod
    def turn_on_camera():
        camera_to_turn_on = VideoStream(usePiCamera=args["picamera"] > 0).start()
        time.sleep(2.0)

        return camera_to_turn_on

    def turn_off_camera(self):
        self.camera.stop()
        cv2.destroyAllWindows()

    def run(self):
        is_auto_pilot_on = False
        flight_command = {}

        while True:
            frame = self.camera.read()  # grab the current frame
            frame = imutils.resize(frame, width=600)
            if is_auto_pilot_on:
                # TODO: add current pitch, roll, throttle and yaw to this function to simulate a smooth transfer
                flight_command = self.auto_pilot.auto_pilot_mode(frame)
            else:
                flight_command = self.get_flight_command_from_client()

            cv2.imshow("Frame", frame)  # show the frame to our screen and increment the frame counter
            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):  # if the 'q' key is pressed, stop the loop
                break
            if key == ord("p"):
                is_auto_pilot_on = True
            else:
                is_auto_pilot_on = False

        self.turn_off_camera()


def arg_parser():
    # construct the argument parse and parse the arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-v", "--video", help="path to the (optional) video file")
    ap.add_argument("-b", "--buffer", type=int, default=32, help="max buffer size")
    ap.add_argument("-r", "--picamera", type=int, default=1, help="whether or not the "
                                                                  "Raspberry Pi camera should be used")
    ap.add_argument("-d", "--debug", type=bool, default=DEFAULT_DEBUG, help="1 to show debug outputs")

    return vars(ap.parse_args())


if __name__ == "__main__":
    args = arg_parser()
    skypi = SkyPi()
    skypi.run()
