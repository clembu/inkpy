class Object:

    # Constructor
    def __init__(self):
        self.parent = None
        self._path = None
        self.__dm = None

    # Properties
    @property
    def debug_metadata(self):
        if self.__dm is None and self.parent:
            return self.parent.debug_metadata
        return self.__dm

    @debug_metadata.setter
    def debug_metadata(self, value):
        if not isinstance(value, DebugMetadata): raise TypeError
        self.__dm = value

    @property
    def root(self):
        ancestor = self
        while ancestor.parent:
            ancestor = ancestor.parent
        return ancestor

    @property
    def path(self):
        if self._path is None:
            if self.parent is None:
                self._path = Path()
            else:
                cmp = []
                child = self
                cnt = self.parent
                while isinstance(cnt, Container):
                    try:
                        if child.has_valid_name:
                            cmp.append(Component(child.name))
                    except AttributeError:
                        cmp.append(Component(cnt.content.index(child)))
                    child = cnt
                    cnt = cnt.parent
                self._path = Path.from_comps(cmp)
        return self._path

    # Methods

    def resolve_path(self, path):
        print("Resolving path: {0}".format(path))
        if path.is_relative:
            nrContainer = self
            if not isinstance(nrContainer, Container):
                if self.parent is None:
                    raise Exception
                nrContainer = self.parent
                if not isinstance(nrContainer, Container):
                    raise Exception
                if not path.components[0].is_parent:
                    raise Exception
                path = path.tail
                print("Resolved path: {0}".format(path))
            return nrContainer[path]
        else:
            return self.root[path]

    def make_path_relative(self, other_path):
        min_plen = min(len(self.path), len(other_path))
        last_shared_idx = -1
        for i in range(0, min_plen):
            own = self.path.components[i]
            other = other.path.components[i]
            if own == other:
                last_shared_idx = i
            else:
                break
        if last_shared_idx == -1: return other_path

        num_up_moves = (len(self.path.components) - 1) - last_shared_idx

        new_cmp = []
        for up in range(0, num_up_moves):
            new_cmp.append(Component.to_parent)
        for down in range(last_shared_idx + 1, len(other_path.components)):
            new_cmp.append(other_path.components[down])
        return Path.from_comps(new_cmp, True)

    def compact_path_str(self, other_path):
        glob_str = None
        rel_str = None
        if other_path.is_relative:
            rel_str = other_path.components_string
            glob_str = (self.path + other_path).components_string
        else:
            rel_str = self.make_path_relative(other_path).components_string
            glob_str = other_path.components_string

        if len(rel_str) < len(glob_str): return rel_str
        else: return glob_str

    def debug_line_number_of_path(self, path):
        if self.path is None: return None

        root = self.root
        if root:
            target = None
            try:
                target = root[path]
            except:
                pass
            if target:
                dm = target.debug_metadata
                if dm: return dm.start_line_number
        return None

    # Special Methods


class Void(Object):
    def __init__(self):
        super().__init__()


from .path import Component, Path
from .container import Container
from ..debug import DebugMetadata
