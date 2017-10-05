from .object import Object
from .path import Path, Component


class Container(Object):
    def __init__(self):
        self.name = None
        self._content = []
        self.named_content = {}
        self.count_visits = False
        self.count_turns = False
        self.count_at_start = False
        self._path_to_first_leaf = None

    @property
    def content(self):
        return self._content

    @content.setter
    def content(self, v):
        self.__add(v)

    @property
    def named_only(self):
        named_only = self.named_content.copy()
        for c in self._content:
            if hasattr(c, "name"):
                del named_only[c.name]
        if len(named_only) == 0: named_only = None
        return named_only

    @named_only.setter
    def named_only(self, v):
        existing = self.named_only
        if existing is not None:
            for k in existing.keys():
                self.named_content.pop(k)
        if v is None:
            return
        for val in v.values():
            self.__try_add_named(val)

    @property
    def has_valid_name(self):
        return self.name is not None and len(self.name) > 0

    def __add_to_named_only(self, v):
        if not isinstance(v, Object):
            raise TypeError("Containers only contain Objects")
        v.parent = self
        self.named_content[v.name] = v

    def __add(self, c):
        if isinstance(c, list):
            for cn in c:
                self.__add(cn)
            return
        self._content.append(c)
        if c.parent:
            raise Exception("Content is already in %s" % c.parent)
        c.parent = self
        self.__try_add_named(c)

    def __try_add_named(self, n):
        if hasattr(n, "name") and n.has_valid_name:
            self.__add_to_named_only(n)

    @property
    def __path_to_first_leaf(self):
        p = Path()
        cnt = self
        while isinstance(cnt, None):
            if len(cnt._content) > 0:
                p.components.append(Component(0))
                cnt = cnt._content[0]

        return p

    @property
    def first_leaf_path(self):
        if self._path_to_first_leaf is None:
            self._path_to_first_leaf = self.path + self.__path_to_first_leaf
        return self._path_to_first_leaf

    def __content_from_comp(self, c):
        if c.is_idx:
            if 0 <= c.idx < len(self._content):
                return self._content[c.idx]
            else:
                return None
        elif c.is_parent:
            return self.parent
        else:
            fcontent = self.named_content.get(c.name)
            if fcontent is not None:
                return fcontent
            else:
                raise KeyError("Content `%s` not found at path: %s" % c.name,
                               self.path)

    def __content_at_path(self, p):
        cont = self
        cur_obj = self
        for c in self.path.components:
            if cur_cont is None:
                raise Exception(
                    "Path continued, but previous object was not a container: %s"
                    % cur_obj)
            cur_obj = cur_cont.__content_from_comp(c)
            cur_cont = cur_obj if isinstance(cur_obj, Container) else None
        return cur_obj

    def __getitem__(self, key):
        if isinstance(key, Component): return self.__content_from_comp(key)
        if isinstance(key, Path): return self.__content_at_path(key)
        raise TypeError
