import cv2
import numpy as np

# local modules
import camshift as cs
import theremin
import background_subtraction as bsub


def onmouse(event, x, y, flags, param):
    global img_idx, tm

    if event == cv2.EVENT_LBUTTONDOWN:
        img_idx = (img_idx + 1) % len(imgs)
    elif event == cv2.EVENT_MBUTTONDOWN:
        tm.toggle()


ct = cs.CamshiftTracker()
cv2.namedWindow("main")
cv2.setMouseCallback('main', onmouse)

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
thresh = 45

imgs = []
img_idx = 0

for name in ('space.png', 'paris-1-.png', 'alley.png', 'lab.png', 'sharks.png'):
    img = cv2.imread('backgrounds/{}'.format(name))
    imgs.append(img)

height, width, channels = ct.get_last_frame().shape

point_hist = []
MAX_POINTS = 20

while True:
    print("tick")

    img = imgs[img_idx]
    img = cv2.resize(img, (width, height))
    ch = cv2.waitKey(5)

    if ch == 27:
        # escape pressed
        break

    # update camshift, draw ellipse
    ct.update_all()
    frame = bsub.denoise(ct.get_last_frame())
    tb = ct.track_box
    print(tb)
    if tb[1][0] > 0 and tb[1][1] > 0:
        cv2.ellipse(frame, tb, (255, 255, 255), 2)

    # background substitution
    fgmask = bs.getForeground(frame)

    # Apply thresholding on the background and display the resulting mask
    frame &= fgmask

    mask_inv = cv2.bitwise_not(fgmask)
    masked_img = img & mask_inv

    final = cv2.add(frame, masked_img)

    # theremin shenanigans
    if len(point_hist) < MAX_POINTS:
        point_hist.append(ct.point)
    else:
        # this is a really stupid way to do it
        point_hist = point_hist[1:]
        point_hist.append(ct.point)

    for i in range(len(point_hist) - 1):
        start = point_hist[i]
        end = point_hist[i + 1]
        cv2.line(final, start, end, (0, 255, 0), 2)
    cv2.imshow('main', final)

    tone = int(ct.point[0] / width * 100)
    vol = int((1 - (ct.point[1] / height)) ** 2 * 100)
    tm.set_tone(tone)
    tm.set_volume(vol)

# cleanup!
tm.stop()
cv2.destroyAllWindows()
