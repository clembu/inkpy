from enum import IntEnum
from inkpy._runtime.path import Path
from inkpy._runtime.inklist import InkList
from inkpy._runtime.object import Object


class ValueType(IntEnum):
    INT = 0
    FLOAT = 1
    LIST = 2
    STRING = 3
    DIVERT_TARGET = 4
    VAR_POINTER = 5


class Value(Object):
    def __init__(self, value, *, vtype):
        if not isinstance(vtype, type): raise TypeError
        self.__t = vtype
        self.__v = value

    @property
    def value_type(self):
        raise NotImplementedError

    def __bool__(self):
        raise NotImplementedError

    def cast(self, ntype):
        raise NotImplementedError

    @property
    def value(self):
        return self.__v

    @value.setter
    def value(self, v):
        if not isinstance(v, self.__t): raise TypeError
        self.__v = v

    @staticmethod
    def create(val):
        if isinstance(val, bool): val = 1 if val else 0
        if isinstance(val, int): return IntValue(val)
        if isinstance(val, float): return FloatValue(val)
        if isinstance(val, str): return StringValue(val)
        if isinstance(val, Path): return DivertTargetValue(val)
        if isinstance(val, InkList): return ListValue(val)
        return None

    def copy(self):
        return self.create(self.value)

    def __str__(self):
        return str(self.value)


class IntValue(Value):
    def __init__(self, i=0):
        super().__init__(i, vtype=int)

    @property
    def value_type(self):
        return ValueType.INT

    def __bool__(self):
        return self.value != 0

    def cast(self, ntype):
        if ntype == self.value_type: return self
        if ntype == ValueType.FLOAT: return FloatValue(float(self.value))
        if ntype == ValueType.STRING: return StringValue(str(self.value))
        raise ValueError("Unexpected type cast of Int Value to new ValueType")


class FloatValue(Value):
    def __init__(self, f=0.0):
        super().__init__(f, vtype=float)

    @property
    def value_type(self):
        return ValueType.FLOAT

    def __bool__(self):
        return self.value != 0.0

    def cast(self, ntype):
        if ntype == self.value_type: return self
        if ntype == ValueType.INT: return IntValue(int(self.value))
        if ntype == ValueType.STRING: return StringValue(str(self.value))
        raise ValueError(
            "Unexpected type cast of Float Value to new ValueType")


class StringValue(Value):
    def __init__(self, s=""):
        super().__init__(s, vtype=str)
        self.__nl = s == "\n"
        self.__iws = not any(c == ' ' or c == '\t' for c in s)

    @property
    def value_type(self):
        return ValueType.STRING

    def __bool__(self):
        return len(self.value) > 0

    @property
    def is_new_line(self):
        return self.__nl

    @property
    def is_inline_ws(self):
        return self.__iws

    @property
    def is_non_ws(self):
        return not self.__nl and not self.__iws

    def cast(self, ntype):
        if ntype == self.value_type: return self
        if ntype == ValueType.INT:
            try:
                return int(self.value)
            except ValueError:
                return None
        if ntype == ValueType.FLOAT:
            try:
                return float(self.value)
            except ValueError:
                return None
        raise ValueError(
            "Unexpected type cast of String Value to new ValueType")


class DivertTargetValue(Value):
    def __init__(self, p=None):
        super().__init__(p, vtype=Path)

    @property
    def value_type(self):
        return ValueType.DIVERT_TARGET

    def cast(self, ntype):
        if ntype == self.value_type: return self
        raise ValueError(
            "Unexpected type cast of Divert Target Value to new ValueType")

    def __str__(self):
        return "DivertTargetValue(%s)" % self.value


class VarPtrValue(Value):
    def __init__(self, vname=None, cidx=-1):
        super().__init__(vname, vtype=str)
        self.context_index = cidx

    @property
    def value_type(self):
        return ValueType.VAR_POINTER

    def cast(self, ntype):
        if ntype == self.value_type: return self
        raise ValueError(
            "Unexpected type cast of Variable Pointer Value to new ValueType")

    def __str__(self):
        return "VariablePointerValue(%s)" % self.value

    def copy(self):
        return VarPtrValue(self.value, self.context_index)


class ListValue(Value):
    def __init__(self, *args):
        if len(args) == 0:
            self.value = InkList()
            return
        if len(args) == 1:
            self.value = InkList(args[0])
            return
        if len(args) == 2:
            self.value = InkList.from_single(args)
            return
        raise NotImplementedError

    @property
    def value_type(self):
        return ValueType.LIST

    def __bool__(self):
        return any(v != 0 for v in self.value.values())

    def cast(self, ntype):
        if ntype == self.value_type: return self
        if ntype == ValueType.INT:
            m = self.value.max
            if m["item"].is_none: return 0
            return m["value"]
        if ntype == ValueType.FLOAT:
            m = self.value.max
            if m["item"].is_none: return 0.0
            return float(m["value"])
        if ntype == ValueType.STRING:
            m = self.value.max
            if m["item"].is_none: return ""
            return str(m["item"])
        raise ValueError(
            "Unexpected type cast of Ink List Value to new ValueType")

    @staticmethod
    def retain_list_origins(old, new):
        if not isinstance(old, ListValue) or not isinstance(new, ListValue):
            return
        if len(new.value) == 0:
            new.value.set_initial_orgnames(old.value.origin_names)
