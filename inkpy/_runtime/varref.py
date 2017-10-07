from .object import Object
from .container import Container
from .path import Path


class VarRef(Object):
    def __init__(self, name=None):
        self.name = name
        self.path_for_count = None

    @property
    def container_for_count(self):
        c = self.resolve_path(self.path_for_count)
        if isinstance(c, Container):
            return c
        return None

    @property
    def path_str_for_count(self):
        if self.path_for_count is None: return None
        return self.compact_path_str(self.path_for_count)

    @path_str_for_count.setter
    def path_str_for_count(self, v):
        if v is None: self.path_for_count = None
        else: self.path_for_count = Path(v)

    def __str__(self):
        if self.name is None:
            return "read_count(%s)" % self.path_str_for_count
        return "var(%s)" % self.name
