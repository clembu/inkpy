from io import IOBase


class Story:

    # Constructor
    def __init__(self, file_):
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
        raise NotImplementedError

    @property
    def text(self):
        raise NotImplementedError

    @property
    def tags(self):
        raise NotImplementedError

    @property
    def gtags(self):
        raise NotImplementedError

    @property
    def vars(self):
        raise NotImplementedError

    # Methods
    def continue_(self, max_=False):
        raise NotImplementedError

    def choose(self, idx):
        raise NotImplementedError

    def goto(self, path):
        raise NotImplementedError

    def tagsat(self, path):
        raise NotImplementedError

    def save(self, file_):
        raise NotImplementedError

    def load(self, file_):
        raise NotImplementedError

    def reset(self):
        raise NotImplementedError

    def force_end(self):
        raise NotImplementedError

    def visit_count(self, path):
        raise NotImplementedError

    def watch(self, var, f):
        raise NotImplementedError

    def unwatch(self, f):
        raise NotImplementedError

    def bindfun(self, fname, f):
        raise NotImplementedError

    def unbindfun(self, fname):
        raise NotImplementedError
