parentstr = "^"


class Component:
    def __init__(self, s):
        self.__value = None
        if isinstance(s, str):
            if len(s) < 1:
                raise ValueError("Can't create component from empty string")
            self.__value = s
        elif isinstance(s, int):
            if s < 0:
                raise ValueError("Component index must be positive")
            self.__value = s
        else:
            raise TypeError

    @property
    def isIdx(self):
        return isinstance(self.__value, int)

    @property
    def isParent(self):
        return self.__value == parentstr

    @property
    def idx(self):
        return int(self.__value) if self.isIdx else None

    @property
    def name(self):
        return str(self.__value)

    @classmethod
    def to_parent(cls):
        return cls(parentstr)

    __str__ = name

    def __eq__(self, other):
        return isinstance(other, Component) and self.__value == other.__value

    def __hash__(self):
        if self.isIdx: return self.__value
        else: return hash(self.__value)


class MetaPath(type):
    @property
    def here(cls):
        p = cls()
        p._isRelative = True
        return p

    def join(cls, hd, tl):
        p = cls()
        p.components.append(hd)
        p.components.extend(tl)
        return p

    def from_string(cls, s):
        p = cls()
        p.comp_str = s
        return p

    def from_comps(cls, cmps, isRel=False):
        p = cls()
        p.components.extend(cmps)
        p._isRelative = isRel
        return p


class Path(metaclass=MetaPath):
    def __init__(self):
        self.__cmps = []
        self._isRelative = False

    @property
    def components(self):
        return self.__cmps

    @property
    def is_relative(self):
        return self._isRelative

    @property
    def head(self):
        if len(self.__cmps > 0):
            return self.__cmps[0]
        else:
            return None

    @property
    def tail(self):
        if len(self.__cmps > 1):
            return Path.from_comps(self.__cmps[1:])
        else:
            return self.here

    @property
    def last(self):
        if len(self.__cmps > 0):
            return self.__cmps[-1]
        else:
            return None

    @property
    def contains_names(self):
        return any([not c.isIdx in self.__cmps])

    @property
    def comp_str(self):
        return ("." if self.is_relative else "") + ".".join(self.__cmps)

    @comp_str.setter
    def comp_str(self, value):
        del self.__cmps[:]
        if value is None or value == "":
            return
        if value[0] == ".":
            self._isRelative = True
            value = value[1:]
        else:
            self._isRelative = False
        for cs in value.split('.'):
            try:
                self.components.append(Component(int(cs)))
            except ValueError:
                self.components.append(Component(cs))

    def __add__(self, other):
        p = Path()
        upMoves = 0
        for c in other.__cmps:
            if c.is_parent:
                upMoves += 1
            else:
                break
        p.components.extend(self.components[:-upMoves])
        p.components.extend(other.components[upMoves:])
        return p

    def __len__(self):
        return len(self.__cmps)

    def __eq__(self, other):
        if other is None: return False
        if len(self) != len(other.components): return False
        if self.is_relative != other.is_relative: return False
        return self.components == other.components

    __str__ = comp_str

    def __hash__(self):
        return hash(str(self))
