from inkpy._runtime.path import Component, Path
from inkpy._runtime.container import Container


class Object:

    # Constructor
    def __init__(self):
        self.parent = None
        self._path = None

    # Properties
    @property
    def rootContainer(self):
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
                while cnt:
                    try:
                        if child.has_valid_name:
                            cmp.append(Component(child.name))
                            pass
                    except AttributeError:
                        cmp.append(Path.Comp(cnt.content.index(child)))
                        pass
                self._path = Path.from_comps(cmp)
        return self._path

    # Methods

    def resolve_path(self, path):
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
            return nrContainer[path]
        else:
            return self.rootContainer[path]

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

    # Special Methods
