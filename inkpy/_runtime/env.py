from inkpy.util.event import Event


class LexEnv:
    def __init__(self, callstack, ldefsorg):
        self.__varchanged = Event()

    @property
    def variableChanged(self):
        return self.__varchanged

    def __getitem__(self, key):
        raise NotImplementedError

    def __setitem__(self, key):
        raise NotImplementedError
