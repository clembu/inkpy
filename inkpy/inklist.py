class InkList:

    # Constructor
    def __init__(self):
        raise NotImplementedError

    # Properties
    @property
    def min(self):
        raise NotImplementedError

    @property
    def max(self):
        raise NotImplementedError

    @property
    def all(self):
        raise NotImplementedError

    # Methods
    def copy(self):
        raise NotImplementedError

    # Specials
    def __contains__(self, other):
        raise NotImplementedError

    def __hash__(self):
        raise NotImplementedError

    def __str__(self):
        raise NotImplementedError

    def __bool__(self):
        raise NotImplementedError

    def __invert__(self):
        raise NotImplementedError

    # Comparisons
    def __lt__(self, other):
        raise NotImplementedError

    def __le__(self, other):
        raise NotImplementedError

    def __eq__(self, other):
        raise NotImplementedError

    def __ne__(self, other):
        raise NotImplementedError

    def __gt__(self, other):
        raise NotImplementedError

    def __ge__(self, other):
        raise NotImplementedError

    # Alterations
    def __or__(self, other):
        raise NotImplementedError

    def __and__(self, other):
        raise NotImplementedError

    def __sub__(self, other):
        raise NotImplementedError

    def __ior__(self, other):
        raise NotImplementedError

    def __isub__(self, other):
        raise NotImplementedError
