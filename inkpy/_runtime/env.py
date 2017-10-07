from ..util.event import Event
from .value import Value, ListValue, VarPtrValue


class LexEnv:
    def __init__(self, callstack, ldefsorg):
        self.__callstack = callstack
        self.__varchanged = Event()
        self.__batchObserving = False
        self.__changedVars = None
        self.__globals = {}
        self.__ldef_org = None

    @property
    def variableChanged(self):
        return self.__varchanged

    @property
    def batchObserving(self):
        return self.__batchObserving

    @batchObserving.setter
    def batchObserving(self, v):
        self.__batchObserving = v
        if v:
            self.__changedVars = set()
        else:
            if self.__changedVars is not None:
                for var in self.__changedVars:
                    self.variableChanged(var, self.__globals[var])
            self.__changedVars = None

    @property
    def json_token(self):
        raise NotImplementedError

    @json_token.setter
    def json_token(self, v):
        raise NotImplementedError

    @property
    def callstack(self):
        return self.__callstack

    @callstack.setter
    def callstack(self, v):
        self.__callstack = v

    def copy_from(self, other):
        self.__globals = other.__globals.copy()
        self.variableChanged = other.variableChanged
        if self.batchObserving != other.batchObserving:
            if other.batchObserving:
                self.__batchObserving = True
                self.__varchanged = set(other.__varchanged)
            else:
                self.__batchObserving = False
                self.__varchanged = None

    def __get_raw_var(self, name, idx):
        v = None
        if idx <= 0:
            v = self.__globals.get(name)
            if v is not None: return v
            v = self.__ldef_org.find(name)
            if v is not None: return v
        v = self.__callstack.get_var(name)
        if v is None:
            raise ValueError(
                "RUNTIME ERROR: Variable '%s' could not be found in context '%d'."
                "This shouldn't be possible so is a bug in the ink(py) engine."
                "Please try to construct a minimal story that reproduces"
                "the problem and report to facelesspanda, thank you!" % name,
                idx)
        return v

    def __index(self, name):
        if name in self.__globals: return 0
        return self.__callstack.current_element_idx

    def __resolve_ptr(self, ptr):
        ctx_idx = ptr.context_idx
        if ctx_idx == -1:
            ctx_idx = self.__index(ptr.value)
        v = self.__get_raw_var(ptr.value, ctx_idx)
        if isinstance(v, VarPtrValue): return v
        else:
            return VarPtrValue(ptr.value, ctx_idx)

    def __retain_list_orgs(self, old, new):
        if not isinstance(old, ListValue): return
        if not isinstance(new, ListValue): return
        if len(new.value) == 0:
            new.value.set_initial_orgnames(old.value.origin_names)

    def assign(self, var_ass, val):
        name = var_ass.name
        ctx_idx = -1
        set_global = var_ass.is_global if var_ass.is_new else (
            name in self.__globals)
        if var_ass.is_new:
            if isinstance(val, VarPtrValue):
                val = self.__resolve_ptr(val)
        else:
            ptr = None
            while True:
                ptr = self.__get_raw_var(name, ctx_idx)
                if isinstance(ptr, VarPtrValue):
                    name = ptr.value
                    ctx_idx = ptr.context_index
                    set_global = ctx_idx == 0
                else:
                    break
        if set_global:
            self.__setglobal(name, val)
        else:
            self.__callstack.set_var(name, val, var_ass.is_new, ctx_idx)

    def ptr_val(self, v):
        return self.get_var(v.value, v.context_index)

    def get_var(self, name, idx=-1):
        v = self.__get_raw_var(name, idx)
        if isinstance(v, VarPtrValue):
            v = self.ptr_val(v)
        return v

    def __setglobal(self, var, val):
        oldval = self[var]
        ListValue.retain_list_origins(oldval, val)
        self.__globals[var] = val
        if len(self.variableChanged) > 0 and val != oldval:
            if self.batchObserving:
                self.__changedVars.add(var)
            else:
                self.variableChanged(var, val)

    def __getitem__(self, key):
        return self.__globals.get(key)

    def __setitem__(self, key, value):
        if value is None:
            raise TypeError("Variable value cannot be None")
        if key not in self.__globals:
            raise KeyError("%s is not a global variable" % key)
        val = Value.create(value)
        if val is None:
            raise ValueError("Invalid value passed to variable: %s" % value)
        self.__setglobal(key, val)

    def __iter__(self):
        return self.__globals.keys().__iter__()
