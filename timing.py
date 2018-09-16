from threading import Timer


class RepeatedTimer(object):
    def __init__(self, interval, function, *args, **kwargs):
        self._timer     = None
        self.interval   = interval
        self.function   = function
        self.args       = args
        self.kwargs     = kwargs
        self.is_running = False
        self.start()

    def _run(self):
        self.is_running = False
        self.start()
        self.function(*self.args, **self.kwargs)

    def start(self):
        if not self.is_running:
            self._timer = Timer(self.interval, self._run)
            self._timer.start()
            self.is_running = True

    def stop(self):
        self._timer.cancel()
        self.is_running = False


class Ticker:
    def __init__(self, name, duration):
        self.name     = name
        self.duration = duration * 60

    def display(self):
        print("{} - {}:{:02d}".format(self.name, minutes(self.duration), seconds(self.duration)))

    def tick(self):
        self.duration -= 1


if __name__ == "__main__":
    def say_hello():
        print("hello!")

    rt = RepeatedTimer(1, say_hello)
