from .object import Object

class Tag(Object):
    def __init__(self, txt):
        self.__txt = txt

    @property
    def txt(self): return self.__txt

    def __str__(self):
        return "# %s" % self.txt
