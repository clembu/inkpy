import inkpy._runtime as runtime


class Choice:

    # Constructor
    def __init__(self, *, c):
        if not isinstance(c, runtime.Choice): raise TypeError
        self.__c = c

    # Properties

    @property
    def text(self):
        return self.__c.text

    @property
    def idx(self):
        return self.__c.idx

    # Methods
