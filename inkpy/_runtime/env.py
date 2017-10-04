from inkpy.util.event import Event
from inkpy._runtime.value import ListValue


class LexEnv:
    def __init__(self, callstack, ldefsorg):
        self.__callstack = callstack
        self.__varchanged = Event()
        self.__batchObserving = False
        self.__changedVars = None
        self.__globals = {}

    @property
    def variableChanged(self):
        return self.__varchanged

    @property
    def batchObserving(self):
        return self.__batchObserving

    @batchObserving.setter
    def batchObserving(self, v):
        self.__batchObserving = v
        if v:
            self.__changedVars = set()
        else:
            if self.__changedVars is not None:
                for var in self.__changedVars:
                    self.variableChanged(var, self.__globals[var])
            self.__changedVars = None

    def __setglobal(self, var, val):
        oldval = self[var]
        ListValue.retain_list_origins(oldval, val)
        self.__globals[var] = val
        if len(self.variableChanged) > 0 and val != oldval:
            if self.batchObserving:
                self.__changedVars.add(var)
            else:
                self.variableChanged(var, val)

    def __getitem__(self, key):
        return self.__globals.get(key)

    def __setitem__(self, key, value):
        if value is None:
            raise TypeError("Variable value cannot be None")
        if key not in self.__globals:
            raise KeyError("%s is not a global variable" % key)
        val = None  # TODO: create value
        if val is None:
            raise ValueError("Invalid value passed to variable: %s" % value)
        self.__setglobal(key, val)
