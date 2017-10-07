from .state import State
from .object import Object
from .listdeforg import ListDefOrigin


class Story(Object):

    # Constructor
    def __init__(self, root_container, lists):
        self.__state = None
        self.__list_defs = None if lists is None else ListDefOrigin(lists)

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

    @property
    def list_defs(self):
        return self.__list_defs

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

    def content_at(self, path):
        raise NotImplementedError
