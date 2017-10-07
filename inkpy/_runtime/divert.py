from .object import Object
from .path import Path
from .callstack import StackType


class Divert(Object):
    def __init__(self, stack_type=None):
        if stack_type is None:
            self.pushes_to_stack = False
        else:
            self.pushes_to_stack = True
            self.stack_type = stack_type
        self.is_external = False
        self.is_conditional = False
        self.ext_args = 0
        self.variable_divert_name = None
        self.__target_ctnt = None
        self.__target_path = None
        raise NotImplementedError

    @property
    def has_variable_target(self):
        return self.variable_divert_name is not None

    @property
    def target_content(self):
        if self.__target_ctnt is None:
            self.__target_path = self.resolve_path(self.__target_path)
        return self.__target_ctnt

    @property
    def target_path(self):
        if self.__target_path is not None and self.__target_path.is_relative:
            o = self.target_content
            if o is not None: self.__target_path = o.path
        return self.__target_path

    @target_path.setter
    def target_path(self, v):
        self.__target_path = v
        self.__target_ctnt = None

    @property
    def target_path_str(self):
        if targetPath is None:
            return None
        return self.compact_path_str(targetPath)

    @target_path_str.setter
    def target_path_str(self, v):
        if v is None: self.target_path = None
        else: self.target_path = Path(v)

    def __eq__(self, other):
        if not isinstance(other, Divert): return False
        if self.has_variable_target == other.has_variable_target:
            if self.has_variable_target:
                return self.variable_divert_name == other.variable_divert_name
            else:
                return self.target_path == other.target_path
        return False

    def __hash__(self):
        if self.has_variable_target:
            return hash(self.variable_divert_name) + 12345
        else:
            return hash(self.target_path) + 54321

    def __str__(self):
        from io import StringIO
        if self.has_variable_target:
            return "Divert (variable: %s)" % self.variable_divert_name
        elif self.target_path is None:
            return "Divert (None)"
        else:
            s = StringIO()
            target_s = str(self.target_path)
            target_ln = self.debug_line_number_of_path(self.target_path)
            if target_ln:
                target_s = "line %d" % target_ln
            s.write("Divert")
            if self.pushes_to_stack:
                if self.stack_type == StackType.FUNCTION:
                    s.write(" function")
                else:
                    s.write(" tunnel")
            s.write(" (%s)" % target_s)
            return s.getvalue()
