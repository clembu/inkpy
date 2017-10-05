class MetaItem(type):
    @property
    def NONE(cls):
        return cls(None, None)


class InkListItem(metaclass=MetaItem):
    def __init__(self, oname, iname=None):
        if iname is None and oname is not None:
            [oname, iname] = oname.split('.')
        self.__iname = iname
        self.__oname = oname

    @property
    def item_name(self):
        return self.__iname

    @property
    def origin_name(self):
        return self.__oname

    @property
    def is_null(self):
        return self.__iname is None and self.__oname is None

    @property
    def full_name(self):
        return "%s.%s" % (self.__oname or "?"), self.__iname

    __str__ = full_name

    def __eq__(self, other):
        return isinstance(
            other, InkListItem
        ) and self.__iname == other.__iname and self.__oname == other.__oname

    def __hash__(self):
        return hash(self.__oname or 0) + hash(self.__iname)


class InkList:
    def __init__(self):
        self.__dict = {}
        self.__orgnames = None
        self.__origins = None

    # Properties
    @property
    def origins(self):
        return self.__origins

    @property
    def origin_names(self):
        if len(self) > 0:
            if self.__orgnames is None:
                self.__orgnames = []
            else:
                del self.__orgnames[:]
            for k in self.__dict:
                self.__orgnames.append(k.origin_name)
        return self.__orgnames

    @property
    def origin_of_max(self):
        if self.origins is None: return None
        max_org_name = self.max["item"].origin_name
        for org in self.origins:
            if org.name == max_org_name:
                return org
        return None

    @property
    def min(self):
        k, v = min(self.__dict, key=lambda k: k[1])
        return {"item": k, "value": v}

    @property
    def max(self):
        k, v = max(self.__dict, key=lambda k: k[1])
        return {"item": k, "value": v}

    @property
    def max_list(self):
        if len(self) > 0:
            return InkList.from_single(self.max)
        else:
            return InkList()

    @property
    def min_list(self):
        if len(self) > 0:
            return InkList.from_single(self.min)
        else:
            return InkList()

    @property
    def all(self):
        l = InkList()
        l.__dict = {k: v for k, v in org.items for org in self.origins}
        return l

    # Methods
    def copy(self):
        l = InkList()
        l.__dict = self.__dict
        l.__orgnames = self.__orgnames

    def set_initial_orgnames(self, n):
        if n is None:
            self.__orgnames = None
            return
        if isinstance(n, list):
            self.__orgnames = n[:]
            return
        if isinstance(n, str):
            self.__orgnames = [n]
            return
        raise TypeError

    def items(self):
        return self.__dict.items()

    def values(self):
        return self.__dict.values()

    def keys(self):
        return self.__dict.keys()

    def _add(self, item, value):
        self.__dict[item] = value

    # Specials
    def __len__(self):
        return len(self.__dict)

    def __contains__(self, other):
        if isinstance(other, str):
            return any(k.item_name == other for k in self.__dict.keys())
        if isinstance(other, InkList):
            not any(k not in self.__dict for k in other.keys())
        raise TypeError

    def __hash__(self):
        return sum(hash(i) for i in self.__dict)

    def __str__(self):
        return ', '.join(sorted(self.__dict.items(), key=lambda i: i[1]))

    def __invert__(self):
        l = InkList()
        l.__dict = {
            k: v
            for k, v in org for org in self.origins if k not in self
        }
        return l

    # Comparisons
    def __lt__(self, other):
        if len(self) == 0: return True
        if len(other) == 0: return False
        return self.max["value"] < other.min["value"]

    def __le__(self, other):
        if len(self) == 0: return True
        if len(other) == 0: return False
        return (self.min["value"] <= other.min["value"]
                and self.max["value"] <= other.max["value"])

    def __eq__(self, other):
        if not isinstance(other, InkList): return False
        if len(self) != len(other): return False
        return all(k in other.__dict for k in self.__dict)

    def __ne__(self, other):
        return not self == other

    def __gt__(self, other):
        if len(self) == 0: return False
        if len(other) == 0: return True
        return self.min["value"] > other.max["value"]

    def __ge__(self, other):
        if len(self) == 0: return False
        if len(other) == 0: return True
        return (self.min["value"] >= other.min["value"]
                and self.max["value"] >= other.max["value"])

    # Alterations
    def __or__(self, other):
        l = self.copy()
        l.__dict.update(other.__dict)
        return l

    def __and__(self, other):
        l = InkList()
        l.__dict = {k: v for k, v in self.__dict.items() if k in other}
        return l

    def __sub__(self, other):
        l = self.copy()
        l.__dict = {k: v for k, v in self.__dict.items() if k not in other}
        return l

    def __ior__(self, other):
        if isinstance(other, InkListItem):
            if other.origin_name is None:
                self |= other.item_name
                return
            for org in self.__origins:
                if org.name == other.origin_name:
                    v = org.get_value(other)
                    if v:
                        self[other] = v
                        return
                    else:
                        raise KeyError(
                            "%s doesn't exist in the original list definition"
                            % other)
            raise ValueError(
                "Failed to add item to list because the item was from a new list definition "
                "that wasn't previously known to this list. "
                "Only items from previously known lists can be used, "
                "so that the number value can be found")
        elif isinstance(other, str):
            fldef = None
            for org in self.__origins:
                if other in org:
                    if fldef is not None:
                        raise KeyError(
                            "%s could come from either %s or %s" % other,
                            org.name, fldef.name)
                    else:
                        fldef = org
            if fldef is None:
                raise KeyError("Could not find origin of %s" % other)
            i = InkListItem(fldef.name, other)
            iv = fldef[i]
            self[i] = iv
            return
        elif isinstance(other, InkList):
            for i in other.__dict:
                self |= i
            return
        raise TypeError

    def __isub__(self, other):
        if isinstance(other, InkListItem):
            del self.__dict[other]
            return
        if isinstance(other, str):
            del self.__dict[InkListItem(other)]
            return
        if isinstance(other, InkList):
            self.__dict = {
                k: v
                for k, v in self.__dict.items() if k not in other
            }
        raise TypeError

    # Class Methods
    @classmethod
    def from_single(cls, i):
        if not isinstance(i, tuple): raise TypeError
        l = cls()
        l.__dict[i[0]] = i[1]

    @classmethod
    def from_story(cls, lname, s):
        l = cls()
        l.set_initial_orgnames(lname)
        ld = s.list_defs.get(lname)
        if ld is None:
            raise KeyError(
                "InkList origin could not be found in story when constructing new list: %s"
                % lname)
        else:
            l.__origins = [ld]
        return l
