from .inklist import InkListItem
from .value import ListValue


class ListDefOrigin:
    def __init__(self, lists):
        self.__lists = {l.name: l for l in lists}

    def get(self, name):
        return self.__lists.get(name)

    def find(self, name):
        item = InkListItem.NONE
        ldef = None

        nparts = name.split('.')
        if len(nparts) == 2:
            item = InkListItem(nparts[0], nparts[1])
            ldef = self.get(item.origin_name)
        else:
            for n, v in self.__lists.items():
                item = InkListItem(n, name)
                if item in v:
                    ldef = v
                    break

        if ldef is not None:
            item_v = ldef.value(item)
            return ListValue(item, item_v)
        return None
