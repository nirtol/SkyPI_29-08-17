from collections import deque
import numpy as np
import cv2

# ==========================================
#   Constants
# ==========================================
EMPTY_STRING = ""
DEBUG = True

# =================================
#   Classes
# =================================


class AutoPilot:
    # ========================================
    #   Constants
    # ========================================
    X = 0
    Y = 1
    RADIUS_SMALL = 30
    RADIUS_BIG = 60
    STEP = 10
    YAW_RATE = 3
    CENTER_VALUE = 1500
    CENTER_THROTTLE_VALUE = 1300
    PITCH_CLOSE_STR = "Too Close!!!"
    PITCH_CLOSE = -1
    PITCH_FAR_STR = "Too Far!!!"
    PITCH_FAR = 1
    PITCH_OK_STR = "OK"
    PITCH_OK = 0
    ROLL_LEFT = -1
    ROLL_LEFT_STR = "left"
    ROLL_RIGHT = 1
    ROLL_RIGHT_STR = "right"
    ROLL_CENTER = 0
    THROTTLE_CENTER = 0
    THROTTLE_UP = 1
    THROTTLE_UP_STR = "up"
    THROTTLE_DOWN = -1
    THROTTLE_DOWN_STR = "down"
    YAW_LEFT = -1
    YAW_CENTER = 0
    YAW_RIGHT = 1
    YAW_STR = "Searching for target..."

    def __init__(self, lower_color_bound, upper_color_bound):
        # initialize the list of tracked points, the frame counter, and the coordinate deltas
        self.pts = deque(maxlen=32)
        self.counter = 0
        self.deltas = [0, 0]
        self.direction = ""
        self.LowerColorBound = lower_color_bound
        self.UpperColorBound = upper_color_bound
        self.target_radius = 0
        self.distance = EMPTY_STRING
        self.pitch = self.CENTER_VALUE
        self.yaw = self.CENTER_VALUE
        self.roll = self.CENTER_VALUE
        self.throttle = self.CENTER_THROTTLE_VALUE
        self.last_known_direction = self.YAW_CENTER
        self.debug = DEBUG

    def get_color_mask(self, frame_to_get_hsv):
        hsv = cv2.cvtColor(frame_to_get_hsv, cv2.COLOR_BGR2HSV)  # convert it to the HSV color space
        # construct a mask for the color "green", then perform
        # a series of dilation's and erosion's to remove any small
        # blobs left in the mask
        mask = cv2.inRange(hsv, self.LowerColorBound, self.UpperColorBound)
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)

        return mask

    def check_distance(self):
        if self.RADIUS_SMALL <= self.target_radius <= self.RADIUS_BIG:
            self.distance = self.PITCH_OK_STR
        elif self.target_radius > self.RADIUS_BIG:
            self.distance = self.PITCH_CLOSE_STR
        else:
            self.distance = self.PITCH_FAR_STR
        self.set_pitch_value()

    def set_roll_value(self, x_val):
        if x_val == self.ROLL_LEFT:
            if self.roll >= self.CENTER_VALUE:
                self.roll = self.CENTER_VALUE
            self.roll -= self.STEP
        elif x_val == self.ROLL_RIGHT:
            if self.roll <= self.CENTER_VALUE:
                self.roll = self.CENTER_VALUE
            self.roll += self.STEP
        else:
            self.roll = self.CENTER_VALUE

    def set_throttle_value(self, y_val):
        if y_val == self.THROTTLE_UP:
            if self.throttle >= self.CENTER_THROTTLE_VALUE:
                self.throttle = self.CENTER_THROTTLE_VALUE
            self.throttle -= self.STEP
        elif y_val == self.THROTTLE_DOWN:
            if self.throttle <= self.CENTER_THROTTLE_VALUE:
                self.throttle = self.CENTER_THROTTLE_VALUE
            self.throttle += self.STEP
        else:
            self.throttle = self.CENTER_THROTTLE_VALUE

    def set_pitch_value(self):
        if self.distance == self.PITCH_FAR:
            if self.pitch >= self.CENTER_VALUE:
                self.pitch = self.CENTER_VALUE
            self.pitch -= self.STEP
        elif self.distance == self.PITCH_CLOSE:
            if self.pitch <= self.CENTER_VALUE:
                self.pitch = self.CENTER_VALUE
            self.pitch += self.STEP
        else:
            self.pitch = self.CENTER_VALUE

    def search_for_target(self):
        yaw_direction = self.get_yaw_direction()
        self.yaw += yaw_direction * self.YAW_RATE * self.STEP

    def get_yaw_direction(self):
        yaw = self.YAW_LEFT
        if self.last_known_direction == self.YAW_RIGHT:
            yaw = self.YAW_RIGHT

        return yaw

    def set_last_known_direction(self, roll_direction):
        if roll_direction == self.ROLL_RIGHT:
            self.last_known_direction = self.YAW_RIGHT
        elif roll_direction == self.ROLL_LEFT:
            self.last_known_direction = self.YAW_LEFT

    def check_direction(self):
        (dir_x, dir_y) = (self.ROLL_CENTER, self.THROTTLE_CENTER)
        # ensure there is significant movement in the x-direction
        if np.abs(self.deltas[self.X]) > 20 and self.target_radius > 10:
            dir_x = self.ROLL_LEFT if np.sign(self.deltas[self.X]) == 1 else self.ROLL_RIGHT
            self.set_roll_value(dir_x)
            self.set_last_known_direction(dir_x)

        # ensure there is significant movement in the y-direction
        if np.abs(self.deltas[self.Y]) > 20 and self.target_radius > 10:
            dir_y = self.THROTTLE_UP if np.sign(self.deltas[self.Y]) == 1 else self.THROTTLE_DOWN
            self.set_throttle_value(dir_y)
            self.set_last_known_direction(dir_x)

        if dir_x == self.ROLL_CENTER and dir_y == self.THROTTLE_CENTER and self.target_radius <= 10:
            self.search_for_target()
        else:
            self.yaw = self.CENTER_VALUE

        if self.debug:
            dir_x_str, dir_y_str = self.get_direction_str(dir_x, dir_y)
            if dir_x != self.ROLL_CENTER and dir_y != self.THROTTLE_CENTER:  # handle when both directions are non-empty
                self.direction = "{}-{}".format(dir_y_str, dir_x_str)
            else:  # otherwise, only one direction is non-empty
                self.direction = dir_x_str if dir_x != self.ROLL_CENTER else dir_y_str

    def get_direction_str(self, x, y):
        x_str = EMPTY_STRING
        y_str = EMPTY_STRING

        if x == self.ROLL_LEFT:
            x_str = self.ROLL_LEFT_STR
        elif x == self.ROLL_RIGHT:
            x_str = self.ROLL_RIGHT_STR

        if y == self.THROTTLE_DOWN:
            y_str = self.THROTTLE_DOWN_STR
        elif y == self.THROTTLE_UP:
            y_str = self.THROTTLE_UP_STR

        return x_str, y_str

    def calculate_movement(self, frame_to_produce_movements):
        if self.debug:
            self.debug_prints(frame_to_produce_movements)
        flight_command = {
            'throttle': self.throttle,
            'pitch': self.pitch,
            'yaw': self.yaw,
            'roll': self.roll
        }

        return flight_command

    def auto_pilot_mode(self, frame_to_analyze):
        mask = self.get_color_mask(frame_to_analyze)
        # find contours in the mask and initialize the current (x, y) center of the target
        cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
        center = None
        # only proceed if at least one contour was found
        if len(cnts) > 0:
            # find the largest contour in the mask, then use
            # it to compute the minimum enclosing circle and centroid
            c = max(cnts, key=cv2.contourArea)
            ((x, y), radius) = cv2.minEnclosingCircle(c)
            m = cv2.moments(c)
            center = (int(m["m10"] / m["m00"]), int(m["m01"] / m["m00"]))
            self.target_radius = radius
            if radius > 10:  # only proceed if the radius meets a minimum size
                # draw the circle and centroid on the frame, then update the list of tracked points
                cv2.circle(frame_to_analyze, (int(x), int(y)), int(radius),
                           (0, 255, 255), 2)
                cv2.circle(frame_to_analyze, center, 5, (0, 0, 255), -1)
        self.pts.appendleft(center)

        for i in np.arange(1, len(self.pts)):
            if self.pts[i - 1] is None or self.pts[i] is None:
                continue
            if self.counter >= 10 and i == 1 and self.pts[-10] is not None:
                self.deltas[self.X] = self.pts[-10][0] - self.pts[i][0]
                self.deltas[self.Y] = self.pts[-10][1] - self.pts[i][1]
                self.check_direction()
                self.check_distance()
            line_thickness = int(np.sqrt(32 / float(i + 1)) * 2.5)
            cv2.line(frame_to_analyze, self.pts[i - 1], self.pts[i], (0, 0, 255), line_thickness)

        self.calculate_movement(frame_to_analyze)
        self.counter += 1

    def debug_prints(self, frame_to_print_debug):
        # show the movement deltas and the direction of movement on the frame
        cv2.putText(frame_to_print_debug, self.direction, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 0, 255), 1)
        cv2.putText(frame_to_print_debug, "dx: {}, dy: {} distance: {} r: {}".format(self.deltas[self.X],
                                                                                     self.deltas[self.Y], self.distance,
                                                                                     self.target_radius),
                    (10, frame_to_print_debug.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)
        if not self.yaw == self.CENTER_VALUE:
            cv2.putText(frame_to_print_debug, self.YAW_STR, (150, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 0, 0), 1)
