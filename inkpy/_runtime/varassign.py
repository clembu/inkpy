from .object import Object


class VarAssign(Object):
    def __init__(self, name=None, new=False):
        self.__varname = name
        self.__new = new
        self.is_global = False

    @property
    def var_name(self):
        return self.__varname

    @property
    def is_new(self):
        return self.__new

    def __str__(self):
        return "VarAssign to %s" % self.var_name
