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

from __future__ import print_function
import sys
import math
import numpy as np
import cv2 as cv

# local module
import video
from video import presets


class App(object):
    def __init__(self, video_src):
        self.cam = video.create_capture(video_src, presets['cube'])
        _ret, self.frame = self.cam.read()
        cv.namedWindow('camshift')
        cv.setMouseCallback('camshift', self.onmouse)

        self.selection = None
        self.drag_start = None
        self.show_backproj = False
        self.track_window = None
        self.history = []
        self.paint_active = False
        self.selection_completed = False

    def onmouse(self, event, x, y, flags, param):
        if not self.selection_completed:
            if event == cv.EVENT_LBUTTONDOWN:
                self.drag_start = (x, y)
                self.track_window = None
            if self.drag_start:
                xmin = min(x, self.drag_start[0])
                ymin = min(y, self.drag_start[1])
                xmax = max(x, self.drag_start[0])
                ymax = max(y, self.drag_start[1])
                self.selection = (xmin, ymin, xmax, ymax)
            if event == cv.EVENT_LBUTTONUP:
                self.drag_start = None
                self.track_window = (xmin, ymin, xmax - xmin, ymax - ymin)
                self.selection_completed = True

        else:
            if event == cv.EVENT_LBUTTONDOWN:
                self.paint_active = not self.paint_active

    def run(self):
        while True:
            _ret, self.frame = self.cam.read()
            self.frame = cv.flip(self.frame, 1)
            vis = self.frame.copy()
            hsv = cv.cvtColor(self.frame, cv.COLOR_BGR2HSV)
            mask = cv.inRange(hsv, np.array((70., 100., 0.)), np.array((150., 255., 255.)))

            if self.selection:
                x0, y0, x1, y1 = self.selection
                hsv_roi = hsv[y0:y1, x0:x1]
                mask_roi = mask[y0:y1, x0:x1]
                hist = cv.calcHist( [hsv_roi], [0], mask_roi, [16], [0, 180] )
                cv.normalize(hist, hist, 0, 255, cv.NORM_MINMAX)
                self.hist = hist.reshape(-1)

                vis_roi = vis[y0:y1, x0:x1]
                cv.bitwise_not(vis_roi, vis_roi)
                vis[mask == 0] = 0

            if self.track_window and self.track_window[2] > 0 and self.track_window[3] > 0:
                self.selection = None
                prob = cv.calcBackProject([hsv], [0], self.hist, [0, 180], 1)
                prob &= mask
                term_crit = ( cv.TERM_CRITERIA_EPS | cv.TERM_CRITERIA_COUNT, 10, 1 )
                track_box, self.track_window = cv.CamShift(prob, self.track_window, term_crit)

                if self.show_backproj:
                    vis[:] = prob[...,np.newaxis]

                cv.ellipse(vis, track_box, (0, 0, 255), 2)

                if self.paint_active:
                    self.add_to_history(track_box)

                if self.history:
                    for i in range(0, len(self.history) - 1):
                        start_point_x = int(self.history[i][0])
                        start_point_y = int(self.history[i][1])

                        end_point_x = int(self.history[i + 1][0])
                        end_point_y = int(self.history[i + 1][1])

                        cv.line(vis, (start_point_x, start_point_y), (end_point_x, end_point_y), (0, 255, 0), 2)

            cv.imshow('camshift', vis)

            ch = cv.waitKey(5)
            if ch == 27:
                break
            if ch == ord('b'):
                self.show_backproj = not self.show_backproj
        cv.destroyAllWindows()

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
    import sys
    try:
        video_src = sys.argv[1]
    except:
        video_src = 0
    print(__doc__)
    App(video_src).run()
