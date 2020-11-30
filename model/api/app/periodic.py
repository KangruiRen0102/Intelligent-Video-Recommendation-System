from threading import Event, Thread


class Periodic(object):
    """Periodically run a function with arguments asynchronously in the background
    Period is a float of seconds.
    Don't expect exact precision with timing.
    Threading is used instead of Multiprocessing because we need shared memory
    otherwise changes made by the function to arguments won't be reflected in
    the rest of the script.
    """

    def __init__(self, func, period, args=[], kwargs={}):
        self.period = period
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.seppuku = Event()

    def start(self):
        self.seppuku.clear()
        self.proc = Thread(target=self._doit)
        self.proc.start()

    def stop(self):
        """Nearly immediately kills the Periodic function"""
        self.seppuku.set()
        self.proc.join()

    def _doit(self):
        while True:
            self.seppuku.wait(self.period)
            if self.seppuku.is_set():
                break
            self.func(*self.args, **self.kwargs)

def test(recommendations):
    print(recommendations)
    recommendations.clear()
