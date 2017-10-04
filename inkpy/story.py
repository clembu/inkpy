from io import IOBase
import inkpy._runtime as runtime
from inkpy.choice import Choice


class Story:

    # Constructor
    def __init__(self, file_):
        self.__s = runtime.Story(None, None)
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
        raise NotImplementedError

    @property
    def choices(self):
        return [Choice(c=c) for c in self.__s.choices]

    @property
    def text(self):
        raise NotImplementedError

    @property
    def tags(self):
        raise NotImplementedError

    @property
    def gtags(self):
        return self.__s.gtags

    @property
    def vars(self):
        raise NotImplementedError

    @property
    def has_errors(self):
        raise NotImplementedError

    @property
    def errors(self):
        raise NotImplementedError

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
        self.__s.force_end()

    def visit_count(self, path):
        raise NotImplementedError

    def watch(self, var, f):
        self.__s.watch(var, f)

    def unwatch(self, f):
        self.__s.unwatch(f)

    def bindfun(self, fname, f):
        self.__s.bindfun(fname, f)

    def unbindfun(self, fname):
        self.__s.unbindfun(fname)

    def inklist(self, lname):
        return runtime.InkList.from_story(self.__s)
