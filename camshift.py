import cv2 as cv
import numpy

# local module
import video
from video import presets


class CamshiftTracker:
    def __init__(self):
        self.camera = get_new_video_source()

    def get_value(self):
        frame = read_frame_from_camera(self.camera)
        return frame


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

    while True:
        cv.imshow("main", ct.get_value())
        ch = cv.waitKey(5)
        if ch == 27:
            # escape pressed
            break

    cv.destroyAllWindows()
