from inkpy._runtime.inklist import InkList, InkListItem
from inkpy._runtime.value import ListValue


class ListDef:
    def __init__(self, name, items):
        self.__name = name
        self.__itemnames = items
        self.__items = None

    @property
    def name(self):
        return self.__name

    @property
    def items(self):
        if self.__items is None:
            self.__items = {
                InkListItem(self.name, k): v
                for k, v in self.__itemnames
            }
        return self.__items.items()

    def __getitem__(self, k):
        return self.__itemnames.get(k.item_name, 0)

    def __contains__(self, i):
        if isinstance(i, InkListItem):
            if i.origin_name != self.name: return False
            return i.item_name in self.__itemnames
        return i in self.__itemnames

    def get_item(self, v):
        for n, i in self.__itemnames:
            if i == v: return InkListItem(self.name, n)
        return InkListItem.NONE

    def get_value(self, i):
        return self.__itemnames.get(i.item_name)

    def range(self, mn, mx):
        rawl = InkList()
        for n, v in self.__itemnames:
            if mn <= v <= mx:
                rawl[InkListItem(name, n)] = v
        return ListValue(rawl)
