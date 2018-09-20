import cv2
import numpy as np

# local modules
import camshift as cs
import theremin
import background_subtraction as bsub

ct = cs.CamshiftTracker()
cv2.namedWindow("main")

# first wait for the user to press s,
# then take a selection
while True:
    ch = cv2.waitKey(5)

    if ch == 27:
        # escape pressed
        sys.exit()
    elif ch == ord("s"):
        # create a selection
        ct.ask_for_selection()
        break

    ct.read_frame()
    cv2.imshow("main", ct.get_last_frame())

# now track that
tm = theremin.Theremin()
tm.start()
bs = bsub.BackSub(ct.get_last_frame())
img = cv2.imread('backgrounds/paris-1-.png')
thresh = 45

while True:
    ch = cv2.waitKey(5)

    if ch == 27:
        # escape pressed
        break

    # update camshift, draw ellipse
    ct.update_all()
    frame = bsub.denoise(ct.get_last_frame())
    cv2.ellipse(frame, ct.track_box, (255, 255, 255), 2)

    # background substitution
    foreGround = bs.getForeground(frame)

    # Apply thresholding on the background and display the resulting mask
    ret, mask = cv2.threshold(foreGround, thresh, 255, cv2.THRESH_BINARY)
    ret, mask_inv = cv2.threshold(foreGround, thresh, 255, cv2.THRESH_BINARY_INV)
    frame &= mask
    masked_img = img & mask_inv

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    nogreen_mask = cv2.inRange(hsv, np.array((70., 20., 00.)), np.array((150., 255., 255.)))
    frame &= cv2.cvtColor(cv2.bitwise_not(nogreen_mask), cv2.COLOR_GRAY2BGR)

    frame = cv2.add(frame, masked_img)

    cv2.imshow("main", frame)

    # theremin shenanigans
    tone = (100 - ct.point[1] // 5)
    vol = ct.point[0] // 5
    tm.set_tone(tone)
    tm.set_volume(vol)

# cleanup!
tm.stop()
cv2.destroyAllWindows()
