from io import IOBase
from ._runtime import Story as RStory, InkList as RInkList
from .choice import Choice


class Story:

    # Constructor
    def __init__(self, file_):
        self.__s = RStory(None, None)
        if isinstance(file_, str):
            pass
            # create from file path
        elif isinstance(file_, IOBase):
            pass
            # create from readable stream
        raise NotImplementedError

    # Properties
    @property
    def can_continue(self):
        return self.__s.state.can_continue

    @property
    def choices(self):
        return [Choice(c=c) for c in self.__s.choices]

    @property
    def text(self):
        return self.__s.state.text

    @property
    def tags(self):
        return self.__s.state.tags

    @property
    def gtags(self):
        return self.__s.gtags

    @property
    def vars(self):
        raise NotImplementedError

    @property
    def has_errors(self):
        return self.__s.state.has_errors

    @property
    def errors(self):
        return self.__s.state.current_errors

    # Methods
    def continue_(self, max_=False):
        return self.__s.continue_(max_)

    def choose(self, idx):
        self.__s.choose(idx)

    def goto(self, path):
        self.__s.goto(path)

    def tagsat(self, path):
        return self.__s.tagsat(path)

    def save(self, file_):
        raise NotImplementedError

    def load(self, file_):
        raise NotImplementedError

    def reset(self):
        self.__s.reset()

    def force_end(self):
        self.__s.state.force_end()

    def watch(self, var, f):
        self.__s.watch(var, f)

    def unwatch(self, f):
        self.__s.unwatch(f)

    def bindfun(self, fname, f):
        self.__s.bindfun(fname, f)

    def unbindfun(self, fname):
        self.__s.unbindfun(fname)

    def inklist(self, lname):
        return RInkList.from_story(self.__s)
