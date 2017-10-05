from .value import ValueType, ListValue, IntValue, Value
from .object import Object
from .inklist import InkList, InkListItem
from enum import Enum


class Primitive(Object):
    class NAMES(Enum):
        ADD = "+"
        SUBTRACT = "-"
        DIVIDE = "/",
        MULTIPLY = "*",
        MOD = "%",
        NEGATE = "_",
        EQUAL = "==",
        GREATER = ">",
        LESS = "<",
        GREATERTHANOREQUALS = ">=",
        LESSTHANOREQUALS = "<=",
        NOTEQUALS = "!=",
        NOT = "!",
        AND = "&&",
        OR = "||",
        MIN = "MIN",
        MAX = "MAX",
        HAS = "?",
        HASNT = "!?",
        INTERSECT = "^",
        LISTMIN = "LIST_MIN",
        LISTMAX = "LIST_MAX",
        ALL = "LIST_ALL",
        COUNT = "LIST_COUNT",
        VALUEOFLIST = "LIST_VALUE",
        INVERT = "LIST_INVERT"

    _prims = None

    @classmethod
    def generate_prims(cls):
        if cls._prims is None:

            def iboolf(f):
                return lambda *args: 1 if f(*args) else 0

            cls._prims = {}
            # Int operations
            cls.add_int_binary_op(cls.NAMES.ADD, int.__add__)
            cls.add_int_binary_op(cls.NAMES.SUBTRACT, int.__sub__)
            cls.add_int_binary_op(cls.NAMES.MULTIPLY, int.__mul__)
            cls.add_int_binary_op(cls.NAMES.DIVIDE, int.__div__)
            cls.add_int_binary_op(cls.NAMES.MOD, int.__mod__)
            cls.add_int_unary_op(cls.NAMES.NEGATE, int.__neg__)

            cls.add_int_binary_op(cls.NAMES.EQUAL, iboolf(int.__eq__))
            cls.add_int_binary_op(cls.NAMES.GREATER, iboolf(int.__gt__))
            cls.add_int_binary_op(cls.NAMES.LESS, iboolf(int.__lt__))
            cls.add_int_binary_op(cls.NAMES.GREATERTHANOREQUALS,
                                  iboolf(int.__ge__))
            cls.add_int_binary_op(cls.NAMES.LESSTHANOREQUALS,
                                  iboolf(int.__le__))
            cls.add_int_binary_op(cls.NAMES.NOTEQUALS, iboolf(int.__ne__))
            cls.add_int_unary_op(cls.NAMES.NOT, iboolf(lambda x: x == 0))

            cls.add_int_binary_op(cls.NAMES.AND, iboolf(x != 0 and y != 0))
            cls.add_int_binary_op(cls.NAMES.OR,
                                  iboolf(lambda x, y: x != 0 or y != 0))

            cls.add_int_binary_op(cls.NAMES.MAX, max)
            cls.add_int_binary_op(cls.NAMES.MIN, min)

            # Float operations
            cls.add_float_binary_op(cls.NAMES.ADD, float.__add__)
            cls.add_float_binary_op(cls.NAMES.SUBTRACT, float.__sub__)
            cls.add_float_binary_op(cls.NAMES.MULTIPLY, float.__mul__)
            cls.add_float_binary_op(cls.NAMES.DIVIDE, float.__div__)
            cls.add_float_binary_op(cls.NAMES.MOD, float.__mod__)
            cls.add_float_unary_op(cls.NAMES.NEGATE, float.__neg__)

            cls.add_float_binary_op(cls.NAMES.EQUAL, iboolf(float.__eq__))
            cls.add_float_binary_op(cls.NAMES.GREATER, iboolf(float.__gt__))
            cls.add_float_binary_op(cls.NAMES.LESS, iboolf(float.__lt__))
            cls.add_float_binary_op(cls.NAMES.GREATERTHANOREQUALS,
                                    iboolf(float.__ge__))
            cls.add_float_binary_op(cls.NAMES.LESSTHANOREQUALS,
                                    iboolf(float.__le__))
            cls.add_float_binary_op(cls.NAMES.NOTEQUALS, iboolf(float.__ne__))
            cls.add_float_unary_op(cls.NAMES.NOT, iboolf(lambda x: x == 0.0))

            cls.add_float_binary_op(cls.NAMES.AND,
                                    iboolf(lambda x, y: x != 0.0 and y != 0.0))
            cls.add_float_binary_op(cls.NAMES.OR,
                                    iboolf(lambda x, y: x != 0.0 or y != 0.0))

            cls.add_float_binary_op(cls.NAMES.MAX, max)
            cls.add_float_binary_op(cls.NAMES.MIN, min)

            # String operations
            cls.add_string_binary_op(cls.NAMES.ADD, str.__add__)
            cls.add_string_binary_op(cls.NAMES.EQUAL, iboolf(str.__eq__))
            cls.add_string_binary_op(cls.NAMES.NOTEQUALS, iboolf(str.__ne__))
            cls.add_string_binary_op(cls.NAMES.HAS, iboolf(str.__contains__))

            # List operations
            cls.add_list_binary_op(cls.NAMES.ADD, InkList.__or__)
            cls.add_list_binary_op(cls.NAMES.SUBTRACT, InkList.__sub__)
            cls.add_list_binary_op(cls.NAMES.HAS, iboolf(InkList.__contains__))
            cls.add_list_binary_op(cls.NAMES.HASNT,
                                   lambda x, y: 1 if y not in x else 0)
            cls.add_list_binary_op(cls.NAMES.INTERSECT, InkList.__and__)

            cls.add_list_binary_op(cls.NAMES.EQUAL, iboolf(InkList.__eq__))
            cls.add_list_binary_op(cls.NAMES.GREATER, iboolf(InkList.__gt__))
            cls.add_list_binary_op(cls.NAMES.LESS, iboolf(InkList.__lt__))
            cls.add_list_binary_op(cls.NAMES.GREATERTHANOREQUALS,
                                   iboolf(InkList.__ge__))
            cls.add_list_binary_op(cls.NAMES.LESSTHANOREQUALS,
                                   iboolf(InkList.__le__))
            cls.add_list_binary_op(cls.NAMES.NOTEQUALS, iboolf(InkList.__ne__))

            cls.add_list_binary_op(
                cls.NAMES.AND, iboolf(lambda x, y: len(x) > 0 and len(y) > 0))
            cls.add_list_binary_op(
                cls.NAMES.OR, iboolf(lambda x, y: len(x) > 0 or len(y) > 0))

            cls.add_list_unary_op(cls.NAMES.NOT, iboolf(lambda x: len(x) == 0))

            # Placeholders to ensure that these special case functions can exist,
            # since these function is never actually run, and is special cased in Call
            cls.add_list_unary_op(cls.NAMES.INVERT, InkList.__invert__)
            cls.add_list_unary_op(cls.NAMES.ALL, lambda x: x.all)
            cls.add_list_unary_op(cls.NAMES.LISTMIN, lambda x: x.min_list)
            cls.add_list_unary_op(cls.NAMES.LISTMAX, lambda x: x.max_list)
            cls.add_list_unary_op(cls.NAMES.COUNT, InkList.__len__)
            cls.add_list_unary_op(cls.NAMES.VALUEOFLIST,
                                  lambda x: x.max["value"])
            cls.add_op_to_fun(cls.NAMES.EQUAL, 2, ValueType.DIVERT_TARGET,
                              iboolf(lambda d1, d2: d1 == d2))

    def __init__(self, name=None, *, nargs=-1):
        if nargs >= 0:
            self._is_proto = True
            self.nargs = nargs
        else:
            self.generate_prims()
        self.name = name

    @property
    def nargs(self):
        return self.__proto.nargs if self.__proto else self.__nargs

    @nargs.setter
    def nargs(self, v):
        self.__nargs = v

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, v):
        self.__name = v
        if not self._is_proto: self.__proto = self._prims[self.__name]

    def add_op_for_type(self, vtype, op):
        if self._opfuns is None:
            self._opfuns = {}
        self._opfuns[vtype] = op

    def coerce_values_to_single(self, params):
        vtype = ValueType.INT
        spcs_ls = None
        for p in params:
            if p.value_type.value > vtype.value:
                vtype = p.value_type
            if p.value_type == ValueType.LIST:
                spcs_ls = p
        params_out = []
        if vtype == ValueType.LIST:
            for p in params:
                if p.value_type == ValueType.LIST: params_out.append(p)
                elif p.value_type == ValueType.INT:
                    i = p.value
                    l = spcs_ls.value.origin_of_max
                    it = l.get_item(i)
                    if it is None:
                        raise ValueError(
                            "Could not find value %d in list %s" % i, l.name)
                    else:
                        params_out.append(ListValue(it, i))
                else:
                    raise TypeError("Cannot mix lists and %s in this operation"
                                    % p.value_type)
        else:
            params_out.extend(p.cast(vtype) for p in params)
        return params_out

    def call_list_inc_op(self, params):
        l = params[0]
        i = params[1]
        r = InkList()
        for li, lv in l.value.items():
            int_op = self._opfuns[ValueType.INT]
            target = int(int_op(lv, i.value))
            li_org = None
            for org in l.value.origins:
                if org.name == li.org_name:
                    li_org = org
                    break
            if li_org is not None:
                inc_i = li_org.get_item(target)
                if inc_i is not None:
                    r.add(inc_i, target)
        return ListValue(r)

    def call_binary_list_op(self, params):
        if self.name in (self.NAMES.ADD, self.NAMES.SUBTRACT) and isinstance(
                params[0], ListValue) and isinstance(params[1], IntValue):
            return self.call_list_inc_op(params)
        [v1, v2, *ignore] = params
        if self.name in (self.NAMES.AND,
                         self.NAMES.OR) and (v1.value_type != ValueType.LIST or
                                             v2.value_type != ValueType.LIST):
            op = self._opfuns[ValueType.INT]
            return IntValue(int(op(1 if v1 else 0, 1 if v2 else 0)))
        if v1.value_type == v2.value_type == ValueType.LIST:
            return self(params)
        raise TypeError("Can't do %s with %s and %s" % self.name,
                        v1.value_type, v2.value_type)

    def __call__(self, params):
        if len(params) < self.nargs: raise TypeError("Too few arguments")
        if len(params) > self.nargs: raise TypeError("Too many arguments")
        if self.__proto: return self.__proto(params)
        hasls = False
        for p in params:
            if isinstance(p, Void):  # TODO: Void
                raise ValueError("Can't perform an operation on void.")
            if isinstance(p, ListValue): hasls = True
        if self.nargs == 2 and hasls: return self.call_binary_list_op(params)
        coerced = self.coerce_values_to_single(params)
        ctype = coerced[0].value_type
        if ctype not in [
                ValueType.INT, ValueType.FLOAT, ValueType.STRING,
                ValueType.LIST, ValueType.DIVERT_TARGET
        ]:
            return None
        op = self._opfuns.get(ctype)
        if op is None:
            raise ValueError("Can't perform %s on %s" % self.name, ctype)
        if self.nargs == 2:
            v1, v2 = params
            return Value.create(op(v1.value, v2.value))
        if self.nargs == 1:
            v = params[0]
            return Value.create(op(v.value))
        return None

    @classmethod
    def exists(cls, name):
        cls.generate_prims()
        return name in cls._prims

    @classmethod
    def get(cls, name):
        return Primitive(name)

    @classmethod
    def add_op_to_fun(cls, name, args, vtype, op):
        nf = cls._prims.get(name)
        if nf is None:
            cls._prims[name] = Primitive(name, nargs=args)
        nf.add_op_for_type(vtype, op)

    @classmethod
    def add_int_binary_op(cls, name, op):
        cls.add_op_to_fun(name, 2, ValueType.INT, op)

    @classmethod
    def add_int_unary_op(cls, name, op):
        cls.add_op_to_fun(name, 1, ValueType.INT, op)

    @classmethod
    def add_float_binary_op(cls, name, op):
        cls.add_op_to_fun(name, 2, ValueType.FLOAT, op)

    @classmethod
    def add_float_unary_op(cls, name, op):
        cls.add_op_to_fun(name, 1, ValueType.FLOAT, op)

    @classmethod
    def add_str_binary_op(cls, name, op):
        cls.add_op_to_fun(name, 2, ValueType.STRING, op)

    @classmethod
    def add_list_binary_op(cls, name, op):
        cls.add_op_to_fun(name, 2, ValueType.LIST, op)

    @classmethod
    def add_list_unary_op(cls, name, op):
        cls.add_op_to_fun(name, 1, ValueType.LIST, op)
