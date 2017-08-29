# USAGE
# python object_movement.py

# import the necessary packages
from imutils.video import VideoStream
from collections import deque
import numpy as np
import argparse
import imutils
import time
import cv2


# ==========================================
#   Constants
# ==========================================
EMPTY_STRING = ""
# =================================
#   Classes
# =================================


def arg_parser():
    # construct the argument parse and parse the arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-v", "--video", help="path to the (optional) video file")
    ap.add_argument("-b", "--buffer", type=int, default=32, help="max buffer size")
    ap.add_argument("-r", "--picamera", type=int, default=1, help="whether or not the "
                                                                  "Raspberry Pi camera should be used")
    return vars(ap.parse_args())


class AutoPilot:
    # ========================================
    #   Constants
    # ========================================
    X = 0
    Y = 1

    def __init__(self, lower_color_bound, upper_color_bound):
        # initialize the list of tracked points, the frame counter, and the coordinate deltas
        self.pts = deque(maxlen=args["buffer"])
        self.counter = 0
        self.deltas = [0, 0]
        self.direction = ""
        self.LowerColorBound = lower_color_bound
        self.UpperColorBound = upper_color_bound
        self.target_radius = 0
        self.distance = EMPTY_STRING

    def get_color_mask(self, hsv):
        # construct a mask for the color "green", then perform
        # a series of dilation's and erosion's to remove any small
        # blobs left in the mask
        mask = cv2.inRange(hsv, self.LowerColorBound, self.UpperColorBound)
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)

        return mask

    def check_distance(self):
        if 30 <= self.target_radius <= 60:
            self.distance = "OK"
        elif self.target_radius > 60:
            self.distance = "Too Close!!!"
        else:
            self.distance = "Too Far!!!"

    def check_direction(self):
        (dir_x, dir_y) = ("", "")
        # ensure there is significant movement in the x-direction
        if np.abs(self.deltas[self.X]) > 20:
            dir_x = "left" if np.sign(self.deltas[self.X]) == 1 else "right"

        # ensure there is significant movement in the y-direction
        if np.abs(self.deltas[self.Y]) > 20:
            dir_y = "up" if np.sign(self.deltas[self.Y]) == 1 else "down"

        if dir_x != "" and dir_y != "":  # handle when both directions are non-empty
            self.direction = "{}-{}".format(dir_y, dir_x)
        else:                            # otherwise, only one direction is non-empty
            self.direction = dir_x if dir_x != "" else dir_y

    def auto_pilot_mode(self, frame_to_analyze):
        hsv = cv2.cvtColor(frame_to_analyze, cv2.COLOR_BGR2HSV)  # convert it to the HSV color space
        mask = self.get_color_mask(hsv)
        # find contours in the mask and initialize the current
        # (x, y) center of the ball
        cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
        center = None
        # only proceed if at least one contour was found
        if len(cnts) > 0:
            # find the largest contour in the mask, then use
            # it to compute the minimum enclosing circle and
            # centroid
            c = max(cnts, key=cv2.contourArea)
            ((x, y), radius) = cv2.minEnclosingCircle(c)
            m = cv2.moments(c)
            center = (int(m["m10"] / m["m00"]), int(m["m01"] / m["m00"]))
            self.target_radius = radius
            # only proceed if the radius meets a minimum size
            if radius > 10:
                # draw the circle and centroid on the frame,
                # then update the list of tracked points
                cv2.circle(frame_to_analyze, (int(x), int(y)), int(radius),
                           (0, 255, 255), 2)
                cv2.circle(frame_to_analyze, center, 5, (0, 0, 255), -1)
        self.pts.appendleft(center)

        # loop over the set of tracked points
        for i in np.arange(1, len(self.pts)):
            if self.pts[i - 1] is None or self.pts[i] is None:
                continue

            if self.counter >= 10 and i == 1 and self.pts[-10] is not None:
                self.deltas[self.X] = self.pts[-10][0] - self.pts[i][0]
                self.deltas[self.Y] = self.pts[-10][1] - self.pts[i][1]
                self.check_direction()
                self.check_distance()

            line_thickness = int(np.sqrt(args["buffer"] / float(i + 1)) * 2.5)
            cv2.line(frame_to_analyze, self.pts[i - 1], self.pts[i], (0, 0, 255), line_thickness)

        # show the movement deltas and the direction of movement on
        # the frame
        cv2.putText(frame_to_analyze, self.direction, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 0, 255), 1)
        cv2.putText(frame_to_analyze, "dx: {}, dy: {} distance: {} r: {}".format(self.deltas[self.X],
                    self.deltas[self.Y], self.distance, self.target_radius),
                    (10, frame_to_analyze.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX,
                    0.35, (0, 0, 255), 1)
        self.counter += 1


def get_color_to_follow_bounds():
    # TODO: get this function to do color analysis to a given point in the frame
    # define the lower and upper boundaries of the "green"
    # ball in the HSV color space
    greenLower = (29, 86, 6)
    greenUpper = (64, 255, 255)
    return greenLower, greenUpper


def turn_on_camera():
    # initialize the video stream and allow the cammera sensor to warmup
    camera_to_turn_on = VideoStream(usePiCamera=args["picamera"] > 0).start()
    time.sleep(2.0)
    return camera_to_turn_on


def turn_off_camera(camera_to_turn_off):
    # cleanup the camera and close any open windows
    camera.release(camera_to_turn_off)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    args = arg_parser()
    color_lower, color_upper = get_color_to_follow_bounds()  # TODO: get this function to its proper class
    camera = turn_on_camera()
    auto_pilot = AutoPilot(color_lower, color_upper)
    is_auto_pilot_on = True
    while True:
        frame = camera.read()                               # grab the current frame
        frame = imutils.resize(frame, width=600)            # resize the frame
        if is_auto_pilot_on:                                # TODO: find a place to update this boolean
            auto_pilot.auto_pilot_mode(frame)

        cv2.imshow("Frame", frame)  # show the frame to our screen and increment the frame counter
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):  # if the 'q' key is pressed, stop the loop
            break

    turn_off_camera(camera)
