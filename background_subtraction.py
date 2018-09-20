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
        if self.counter < 200:
            self.backGroundModel =  frame * self.alpha + self.backGroundModel * (1 - self.alpha)
        elif self.counter == 200:
            print('done')

        self.counter += 1

        diff = cv2.absdiff(self.backGroundModel.astype(np.uint8),frame)
        gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
        rgb_gray = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)

        return rgb_gray


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
    if ret is True:
        backSubtractor = BackSub(denoise(frame))
        run = True
    else:
        run = False

    # read image to put background over
    img = cv2.imread('backgrounds/paris-1-.png')
    print(img.shape)

    cv2.namedWindow('mask')
    cv2.namedWindow('input')
    cv2.setMouseCallback('mask', onmouse)
    cv2.setMouseCallback('input', onmouse)

    thresh = 45

    while(run):
        # Read a frame from the camera
        ret,frame = cam.read()

        # If the frame was properly read.
        if ret is True:
            # Show the filtered image
            cv2.imshow('input',denoise(frame))

            # get the foreground
            foreGround = backSubtractor.getForeground(denoise(frame))
            # foreGround = cv2.cvtColor(foreGround, cv2.COLOR_BGR2GRAY)

            # Apply thresholding on the background and display the resulting mask
            ret, mask = cv2.threshold(foreGround, thresh, 255, cv2.THRESH_BINARY)
            ret, mask_inv = cv2.threshold(foreGround, thresh, 255, cv2.THRESH_BINARY_INV)
            frame &= mask
            masked_img = img & mask_inv

            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            nogreen_mask = cv2.inRange(hsv, np.array((70., 20., 00.)), np.array((150., 255., 255.)))
            frame &= cv2.cvtColor(cv2.bitwise_not(nogreen_mask), cv2.COLOR_GRAY2BGR)

            frame = cv2.add(frame, masked_img)

            # Note: The mask is displayed as a RGB image, you can
            # display a grayscale image by converting 'foreGround' to
            # a grayscale before applying the threshold.
            cv2.imshow('mask', frame)

            key = cv2.waitKey(10) & 0xFF
        else:
            break

        if key == 27:
            break

    cam.release()
    cv2.destroyAllWindows()
