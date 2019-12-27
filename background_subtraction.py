import numpy as np
import cv2


class BackSub:
    def __init__(self, firstFrame):
        # by default, uses only the first 200 frames
        # to compute a background
        self.avg_frames = 1
        self.alpha = 1 / self.avg_frames
        self.backGroundModel = firstFrame
        self.counter = 0

    def getForeground(self, frame):
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        green = cv2.inRange(hsv, np.array((50., 10., 0.)), np.array((200., 255, 170.0)))
        not_green = cv2.bitwise_not(green)
        not_green = cv2.cvtColor(not_green, cv2.COLOR_GRAY2BGR)

        return not_green


def denoise(frame):
    frame = cv2.medianBlur(frame, 5)
    frame = cv2.GaussianBlur(frame, (5, 5), 0)

    return frame


if __name__ == "__main__":
    # Just a simple function to perform
    # some filtering before any further processing.
    def onmouse(event, x, y, flags, param):
        # increases or decreases threshold.
        global thresh
        if event == cv2.EVENT_LBUTTONDOWN:
            if thresh < 255:
                print('up!')
                thresh += 1
        elif event == cv2.EVENT_RBUTTONDOWN:
            if thresh > 0:
                print('down!')
                thresh -= 1

    cam = cv2.VideoCapture(0)
    ret, frame = cam.read()
    cam_height, cam_width, _channels = frame.shape

    if ret:
        backSubtractor = BackSub(denoise(frame))
        run = True
    else:
        run = False

    # read image to put background over
    img = cv2.imread('backgrounds/paris-1-.png')
    img = cv2.resize(img, (cam_width, cam_height))

    cv2.namedWindow('mask')
    cv2.setMouseCallback('mask', onmouse)

    thresh = 45

    while(run):
        # Read a frame from the camera
        ret, frame = cam.read()

        # If the frame was properly read.
        if ret is True:
            # Show the filtered image

            # get the foreground
            fgmask = backSubtractor.getForeground(denoise(frame))
            # foreGround = cv2.cvtColor(foreGround, cv2.COLOR_BGR2GRAY)
            frame &= fgmask

            mask_inv = cv2.bitwise_not(fgmask)
            masked_img = img & mask_inv

            final = cv2.add(frame, masked_img)

            # Apply thresholding on the background and display the resulting mask

            # Note: The mask is displayed as a RGB image, you can
            # display a grayscale image by converting 'foreGround' to
            # a grayscale before applying the threshold.
            cv2.imshow('mask', final)

            key = cv2.waitKey(10) & 0xFF
        else:
            break

        if key == 27:
            break

    cam.release()
    cv2.destroyAllWindows()
