from .object import Object
from .container import Container
from .path import Path


class ChoicePoint(Object):
    def __init__(self, once=True):
        super().__init__()
        self.__path_on_choice = None
        self.once_only = once
        self.has_condition = False
        self.has_start_content = False
        self.has_choice_only_content = False
        self.is_invisible_default = False

    @property
    def choice_target(self):
        o = self.resolve_path(self.__path_on_choice)
        return o if isinstance(o, Container) else None

    @property
    def path_on_choice(self):
        if self.__path_on_choice is not None and self.__path_on_choice.is_relative:
            o = self.choice_target
            if o is not None: self.__path_on_choice = o.path
        return self.__path_on_choice

    @path_on_choice.setter
    def path_on_choice(self, value):
        if not isinstance(value, Path): raise TypeError
        self.__path_on_choice = value

    @property
    def path_str(self):
        return self.compact_path_str(self.path_on_choice)

    @path_str.setter
    def path_str(self, value):
        self.path_on_choice = Path.from_string(value)

    @property
    def flags(self):
        flags = 0
        if self.has_condition: flags |= 1
        if self.has_start_content: flags |= 2
        if self.has_choice_only_content: flags |= 4
        if self.is_invisible_default: flags |= 8
        if self.once_only: flags |= 16
        return flags

    @flags.setter
    def flags(self, value):
        value = value.value
        self.has_condition = (value & 1) > 0
        self.has_start_content = (value & 2) > 0
        self.has_choice_only_content = (value & 4) > 0
        self.is_invisible_default = (value & 8) > 0
        self.once_only = (value & 16) > 0

    def __str__(self):
        target_l = self.debug_line_number_of_path(self.path_on_choice)
        target_s = str(self.path_on_choice)
        if target_l is not None:
            target_s = " line %d" % target_l
        return "Choice: -> %s" % target_s
