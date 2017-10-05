from ._runtime import InkList as RInkList


class InkList:

    # Constructor
    def __init__(self, *, l=RInkList()):
        if not isinstance(l, RInkList): raise TypeError
        self._l = l

    # Properties
    @property
    def min(self):
        return self._l.min

    @property
    def max(self):
        return self._l.max

    @property
    def all(self):
        return self._l.all

    # Methods
    def copy(self):
        l = InkList()
        l._l = self._l.copy()
        return l

    # Specials
    def __contains__(self, other):
        return other in self._l

    def __hash__(self):
        return hash(self._l)

    def __str__(self):
        return str(self._l)

    def __len__(self):
        return len(self._l)

    def __invert__(self):
        return ~self._l

    # Comparisons
    def __lt__(self, other):
        return self._l < other._l

    def __le__(self, other):
        return self._l <= other._l

    def __eq__(self, other):
        return self._l == other._l

    def __ne__(self, other):
        return self._l != other._l

    def __gt__(self, other):
        return self._l > other._l

    def __ge__(self, other):
        return self._l >= other._l

    # Alterations
    def __or__(self, other):
        return self._l | other._l

    def __and__(self, other):
        return self._l & other._l

    def __sub__(self, other):
        return self._l - other._l

    def __ior__(self, other):
        if isinstance(other, InkList): other = other._l
        self._l |= other._l

    def __isub__(self, other):
        if isinstance(other, InkList): other = other._l
        self._l -= other
