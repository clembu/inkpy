from ._runtime import Choice as RChoice


class Choice:

    # Constructor
    def __init__(self, *, c):
        if not isinstance(c, RChoice): raise TypeError
        self.__c = c

    # Properties

    @property
    def text(self):
        return self.__c.text

    @property
    def idx(self):
        return self.__c.idx

    # Methods
