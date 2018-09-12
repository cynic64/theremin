#!/usr/bin/env python

'''
Camshift tracker
================
This is a demo that shows mean-shift based tracking
You select a color objects such as your face and it tracks it.
This reads from video camera (0 by default, or the camera number the user enters)
http://www.robinhewitt.com/research/track/camshift.html
Usage:
------
    camshift.py [<video source>]
    To initialize tracking, select the object with mouse
Keys:
-----
    ESC   - exit
    b     - toggle back-projected probability visualization
'''

import sys
import math
import numpy as np
import cv2 as cv

# local module
import video
from video import presets


def get_video_source():
    video_src = 0
    camera = video.create_capture(video_src, presets['cube'])

    return camera


def read_frame_from_camera(camera):
    # Reads frame from camera, and flips it.
    ret_value, frame = camera.read()
    frame = cv.flip(frame, 1)

    assert ret_value, "Something went horribly wrong, unable to read frame from camera!"

    return frame


class Segments:
    def __init__(self):
        self.segments = []

    def new_segment(self):
        self.segments.append([])

    def add_to_last_segment(self, point):
        self.segments[-1].append(point)

    def draw(self, destination):
        for segment in self.segments:
            if len(segment) >= 2:
                for i in range(len(segment) - 1):
                    start_point_x = int(segment[i][0])
                    start_point_y = int(segment[i][1])

                    end_point_x = int(segment[i + 1][0])
                    end_point_y = int(segment[i + 1][1])

                    cv.line(destination, (start_point_x, start_point_y), (end_point_x, end_point_y), (0, 255, 0), 2)


class App:
    def __init__(self):
        # Create a video capture source
        self.cam = get_video_source()
        self.frame = read_frame_from_camera(self.cam)

        # Create a window and mouse callback
        cv.namedWindow('camshift')
        cv.setMouseCallback('camshift', self.onmouse)

        # Selection stuff. It's complicated, ok
        self.user_selection_box = None
        self.drag_start = None
        self.track_window = None
        self.paint_active = False
        self.selection_completed = False

        self.show_backproj = False

        # list of points drawn by user
        self.segments = Segments()
        self.segments.new_segment()

    def onmouse(self, event, x, y, flags, param):
        # if no selection has been made, treat the event as creating the selection
        if not self.selection_completed:
            if event == cv.EVENT_LBUTTONDOWN:
                self.drag_start = (x, y)
                self.track_window = None
            if self.drag_start:
                xmin = min(x, self.drag_start[0])
                ymin = min(y, self.drag_start[1])
                xmax = max(x, self.drag_start[0])
                ymax = max(y, self.drag_start[1])
                self.user_selection_box = (xmin, ymin, xmax, ymax)
            if event == cv.EVENT_LBUTTONUP:
                self.drag_start = None
                self.track_window = (xmin, ymin, xmax - xmin, ymax - ymin)
                self.selection_completed = True

        # otherwise, treat it as a painting toggle
        else:
            if event == cv.EVENT_LBUTTONDOWN:
                self.paint_active = not self.paint_active
                became_active = self.paint_active

                if became_active:
                    self.segments.new_segment()

    def run(self):
        while True:
            self.update()

            ch = cv.waitKey(5)
            if ch == 27:
                return
            if ch == ord('b'):
                self.show_backproj = not self.show_backproj

        cv.destroyAllWindows()

    def update(self):
        self.frame = read_frame_from_camera(self.cam)
        final_img = self.frame.copy()
        hsv = cv.cvtColor(self.frame, cv.COLOR_BGR2HSV)
        mask = cv.inRange(hsv, np.array((70., 100., 50.)), np.array((150., 255., 255.)))

        if self.user_selection_box:
            x0, y0, x1, y1 = self.user_selection_box
            hsv_roi = hsv[y0:y1, x0:x1]
            mask_roi = mask[y0:y1, x0:x1]
            hist = cv.calcHist( [hsv_roi], [0], mask_roi, [16], [0, 180] )
            cv.normalize(hist, hist, 0, 255, cv.NORM_MINMAX)
            self.hist = hist.reshape(-1)

            vis_roi = final_img[y0:y1, x0:x1]
            cv.bitwise_not(vis_roi, vis_roi)
            final_img[mask == 0] = 0

        if self.track_window and self.track_window[2] > 0 and self.track_window[3] > 0:
            self.user_selection_box = None
            prob = cv.calcBackProject([hsv], [0], self.hist, [0, 180], 1)
            prob &= mask
            term_crit = ( cv.TERM_CRITERIA_EPS | cv.TERM_CRITERIA_COUNT, 10, 1 )
            track_box, self.track_window = cv.CamShift(prob, self.track_window, term_crit)

            if self.show_backproj:
                final_img[:] = prob[...,np.newaxis]

            cv.ellipse(final_img, track_box, (0, 0, 255), 2)

            if self.paint_active:
                x = track_box[0][0]
                y = track_box[0][1]
                point = (x, y)
                self.segments.add_to_last_segment(point)

            self.segments.draw(final_img)

        cv.imshow('camshift', final_img)

    def add_to_history(self, track_box):
        max_jump = 30000

        point_is_reasonable = None

        x = track_box[0][0]
        y = track_box[0][1]

        if len(self.history) >= 2:
            last_x = self.history[-1][0]
            last_y = self.history[-1][1]

            distance = math.hypot(last_x - x, last_y - y)

            if distance < max_jump:
                point_is_reasonable = True
        else:
            point_is_reasonable = True

        if point_is_reasonable:
            self.history.append((x, y))


if __name__ == '__main__':
    print(__doc__)
    App().run()
