from .object import Object


class Tag(Object):
    def __init__(self, txt):
        super().__init__()
        self.__txt = txt

    @property
    def txt(self):
        return self.__txt

    def __str__(self):
        return "# %s" % self.txt
