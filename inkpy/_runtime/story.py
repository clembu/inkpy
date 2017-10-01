from inkpy._runtime.state import State


class Story:

    # Constructor
    def __init__(self, root_container, lists):
        self.__state = None

        self.reset()

    # Properties
    @property
    def choices(self):
        raise NotImplementedError

    @property
    def gtags(self):
        raise NotImplementedError

    @property
    def state(self):
        return self.__state

# Methods

    def continue_(self, max_=False):
        raise NotImplementedError

    def choose(self, idx):
        raise NotImplementedError

    def goto(self, path):
        raise NotImplementedError

    def tagsat(self, path):
        raise NotImplementedError

    def reset(self):
        self.__state = State(self)
        raise NotImplementedError

    def force_end(self):
        raise NotImplementedError

    def watch(self, var, f):
        raise NotImplementedError

    def unwatch(self, f):
        raise NotImplementedError

    def bindfun(self, fname, f):
        raise NotImplementedError

    def unbindfun(self, fname):
        raise NotImplementedError
