import cv2 as cv
import numpy as np
import sys

# local module
import video
from video import presets


class CamshiftTracker:
    def __init__(self):
        self.camera = get_new_video_source()

        self.point = None

        # Selection stuff
        # idk how this works
        self.user_selection_box = None
        self.drag_start = None
        self.track_window = None
        self.selection_completed = False

    def get_last_frame(self):
        return self.frame

    def ask_for_selection(self):
        cv.namedWindow("selection picker")
        cv.setMouseCallback("selection picker", self.selector)

        while not self.selection_completed:
            self.read_frame()
            cv.imshow("selection picker", self.frame)

            ch = cv.waitKey(5)
            if ch == 27:
                # if the user presses escape,
                # abort the selection process.
                break

        cv.destroyWindow("selection picker")

    def selector(self, event, x, y, flags, param):
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
                print("Got selection!")
                print(self.track_window)

                # compute histogram for selection
                hsv = cv.cvtColor(self.frame, cv.COLOR_BGR2HSV)
                # mask = cv.inRange(hsv, np.array((70., 100., 50.)), np.array((150., 255., 255.)))
                mask = cv.inRange(hsv, np.array((0., 0., 0.)), np.array((255., 255., 255.)))

                x0, y0, x1, y1 = self.user_selection_box
                hsv_roi = hsv[y0:y1, x0:x1]
                mask_roi = mask[y0:y1, x0:x1]
                hist = cv.calcHist( [hsv_roi], [0], mask_roi, [16], [0, 180] )
                cv.normalize(hist, hist, 0, 255, cv.NORM_MINMAX)
                self.hist = hist.reshape(-1)
                self.selection_completed = True

    def read_frame(self):
        self.frame = read_frame_from_camera(self.camera)

    def update(self):
        hsv = cv.cvtColor(self.frame, cv.COLOR_BGR2HSV)
        mask = cv.inRange(hsv, np.array((0., 00., 127.)), np.array((180., 255., 255.)))

        # TODO: figure out wtf this does
        if self.track_window and self.track_window[2] > 0 and self.track_window[3] > 0:
            prob = cv.calcBackProject([hsv], [0], self.hist, [0, 180], 1)
            prob &= mask
            term_crit = ( cv.TERM_CRITERIA_EPS | cv.TERM_CRITERIA_COUNT, 10, 1 )
            track_box, self.track_window = cv.CamShift(prob, self.track_window, term_crit)

            x = int(track_box[0][0])
            y = int(track_box[0][1])
            self.point = (x, y)
            self.track_box = track_box

    def update_all(self):
        self.read_frame()
        self.update()


def get_new_video_source():
    video_src = 0
    camera = video.create_capture(video_src, presets['cube'])

    return camera


def read_frame_from_camera(camera):
    # Reads frame from camera, and flips it.
    ret_value, frame = camera.read()
    frame = cv.flip(frame, 1)

    assert ret_value, "Something went horribly wrong, unable to read frame from camera!"

    return frame

if __name__ == "__main__":
    ct = CamshiftTracker()
    cv.namedWindow("main")

    # first wait for the user to press s,
    # then take a selection
    while True:
        ch = cv.waitKey(5)

        if ch == 27:
            # escape pressed
            sys.exit()
        elif ch == ord("s"):
            # create a selection
            ct.ask_for_selection()
            break

        ct.read_frame()
        cv.imshow("main", ct.get_last_frame())

    # now track that
    while True:
        ch = cv.waitKey(5)

        if ch == 27:
            # escape pressed
            break

        ct.update_all()
        frame = ct.get_last_frame()

        # cv.circle(frame, ct.point, 10, (0, 0, 255), -1)
        cv.ellipse(frame, ct.track_box, (0, 0, 255), 2)

        cv.imshow("main", frame)

        print(ct.point)

    # cleanup!
    cv.destroyAllWindows()
