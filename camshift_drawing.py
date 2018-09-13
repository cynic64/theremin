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

# colors (in BGR, idk why)
RED = (0, 0, 255)
GREEN = (0, 255, 0)
BLUE = (255, 0, 0)


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


class Canvas:
    def __init__(self, existing_image):
        # existing_image determines size of paint image
        self.image = existing_image.copy()
        self.image[:] = (0, 0, 0)

        self.last_point = None
        self.next_point_disconnected = False
        self.color = GREEN

    def add_point(self, point):
        if not self.next_point_disconnected:
            if self.last_point:
                cv.line(self.image, self.last_point, point, self.color, 2)
        else:
            self.next_point_disconnected = False

        self.last_point = point

    def add_gap(self):
        self.next_point_disconnected = True

    def change_color(self):
        if self.color == GREEN:
            self.color = BLUE
        else:
            self.color = GREEN


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
        self.selection_completed = False

        self.show_backproj = False

        # image we paint on
        self.canvas = Canvas(self.frame)
        self.paint_active = False


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
                    self.canvas.add_gap()

            elif event == cv.EVENT_RBUTTONDOWN:
                self.canvas.change_color()

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
            final_img[:] = (0, 0, 0)
            self.user_selection_box = None
            prob = cv.calcBackProject([hsv], [0], self.hist, [0, 180], 1)
            prob &= mask
            term_crit = ( cv.TERM_CRITERIA_EPS | cv.TERM_CRITERIA_COUNT, 10, 1 )
            track_box, self.track_window = cv.CamShift(prob, self.track_window, term_crit)

            if self.show_backproj:
                final_img[:] = prob[...,np.newaxis]

            if self.paint_active:
                x = int(track_box[0][0])
                y = int(track_box[0][1])
                point = (x, y)
                self.canvas.add_point(point)

            final_img = cv.add(final_img, self.canvas.image)
            cv.ellipse(final_img, track_box, (0, 0, 255), 2)

        cv.imshow('camshift', final_img)


if __name__ == '__main__':
    print(__doc__)
    App().run()
