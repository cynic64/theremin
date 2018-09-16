import cv2 as cv
import sys
import os

# local modules
import camshift as cs
import timing

class Theremin:
    def __init__(self):
        self.path = 'tones/pure/'
        self.current_tone = 0
        self.rep_timer = None
        self.interval = 0.1
        self.volume = 100

    def start(self):
        if not self.rep_timer:
            self.rep_timer = timing.RepeatedTimer(self.interval, self.update)

        else:
            self.rep_timer.start()

    def stop(self):
        assert self.rep_timer, "You called stop on theremin without creating a rep timer."

        self.rep_timer.stop()

    def update(self):
        path = '{}{:02d}.wav'.format(self.path, self.current_tone)
        print(path)
        command = 'mplayer {} -volume {} &'.format(path, self.volume)
        os.system(command)

    def set_tone(self, tone):
        self.current_tone = tone

    def set_volume(self, volume):
        self.volume = volume


ct = cs.CamshiftTracker()
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

tm = Theremin()
tm.start()
# now track that
while True:
    ch = cv.waitKey(5)

    if ch == 27:
        # escape pressed
        break

    ct.update_all()
    frame = ct.get_last_frame()

    cv.ellipse(frame, ct.track_box, (0, 0, 255), 2)

    cv.imshow("main", frame)

    print(ct.point)
    tone = (100 - ct.point[1] // 5)
    vol = ct.point[0] // 5
    tm.set_tone(tone)
    tm.set_volume(vol)

# cleanup!
tm.stop()
cv.destroyAllWindows()
