import numpy as np
import cv2


class BackGroundSubtractor:
    def __init__(self, firstFrame):
        # by default, uses only the first frame
        # to compute a background
        self.avg_frames = 1
        self.alpha = 1 / self.avg_frames
        self.backGroundModel = firstFrame
        self.updates = 0

    def getForeground(self, frame):
        if self.updates < self.avg_frames:
            # apply the background averaging formula:
            # NEW_BACKGROUND = CURRENT_FRAME * ALPHA + OLD_BACKGROUND * (1 - APLHA)
            self.backGroundModel =  frame * self.alpha + self.backGroundModel * (1 - self.alpha)

        self.updates += 1

        # after the previous operation, the dtype of
        # self.backGroundModel will be changed to a float type
        # therefore we do not pass it to cv2.absdiff directly,
        # instead we acquire a copy of it in the uint8 dtype
        # and pass that to absdiff.
        return cv2.absdiff(self.backGroundModel.astype(np.uint8),frame)

cam = cv2.VideoCapture(0)

# Just a simple function to perform
# some filtering before any further processing.
def denoise(frame):
    frame = cv2.medianBlur(frame,5)
    frame = cv2.GaussianBlur(frame,(5,5),0)
    
    return frame

ret, frame = cam.read()
if ret is True:
    backSubtractor = BackGroundSubtractor(denoise(frame))
    run = True
else:
    run = False

while(run):
    # Read a frame from the camera
    ret,frame = cam.read()

    # If the frame was properly read.
    if ret is True:
        # Show the filtered image
        cv2.imshow('input',denoise(frame))

        # get the foreground
        foreGround = backSubtractor.getForeground(denoise(frame))
        foreGround = cv2.cvtColor(foreGround, cv2.COLOR_BGR2GRAY)

        # Apply thresholding on the background and display the resulting mask
        mask = foreGround
        ret, mask = cv2.threshold(foreGround, 50, 255, cv2.THRESH_BINARY)
        mask = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
        frame &= mask

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
