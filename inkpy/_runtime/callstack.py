from enum import Enum
from .container import Container
from .path import Path
from .value import ListValue


class StackType(Enum):
    FUNCTION = 0
    TUNNEL = 1


class Element:
    def __init__(self, stack_type, container, content_idx, in_expr_eval=False):
        self.container = container
        self.content_idx = content_idx
        self.in_expr_eval = in_expr_eval
        self.tmp_var = {}
        self.stack_type = stack_type

    @property
    def obj(self):
        try:
            return self.container.content[self.content_idx]
        except (IndexError, NameError, AttributeError):
            return None

    @obj.setter
    def obj(self, v):
        if v is None:
            self.container = None
            self.content_idx = 0
            return
        self.container = v.parent
        if self.container is not None:
            self.content_idx = self.container.content.index(v)

        if self.content_idx == -1 or self.container is None:
            self.container = v
            self.content_idx = 0

    def copy(self):
        e = Element(self.stack_type, self.container, self.content_idx,
                    self.in_expr_eval)
        e.tmp_var = self.tmp_var.copy()
        return e


class Thread:
    def __init__(self, *args):
        if len(args) == 1 or len(args) > 2:
            raise TypeError("Can't initialize thread with these arguments")
        self.idx = 0
        self.callstack = []
        self.prev_ct_obj = None
        if len(args) == 2:
            jobj = args[0]
            story = args[1]
            self.idx = jobj["threadIndex"]
            jstack = jobj["callstack"]
            for tok in jstack:
                stype = StackType(tok["type"])
                container = None
                ct_idx = 0
                container_path_str = None
                container_path_str_tok = tok.get("cPath")
                if container_path_str_tok is not None:
                    container_path_str = str(container_path_str_tok)
                    container = story.content_at(Path(container_path_str))
                    ct_idx = tok["idx"]
                in_expr_eval = tok["exp"]
                e = Element(stype, container, ct_idx, in_expr_eval)
                e.tmp_var = tok["temp"]
                self.callstack.append(e)
            prev_ct_path = jobj.get("previousContentObject")
            if prev_ct_path is not None:
                self.prev_ct_obj = story.content_at(Path(prev_ct_path))

    def copy(self):
        t = Thread()
        t.idx = self.idx
        t.callstack.extend(e.copy() for e in self.callstack)
        t.prev_ct_obj = self.prev_ct_obj
        return t

    # TODO: json token
    @property
    def json_token(self):
        raise NotImplementedError


class CallStack:
    def __init__(self, root):
        self.__thread_cnt = 0
        self.__threads = [Thread()]
        self.__threads[0].callstack.append(Element(StackType.TUNNEL, root, 0))

    def copy(self):
        l = CallStack(None)
        l.__threads = [t.copy() for t in self.__threads]

    @property
    def current_thread(self):
        return self.__threads[-1]

    @current_thread.setter
    def current_thread(self, v):
        if len(self.__threads) != 1:
            raise ValueError(
                "Don't set the current thread when we have a stack of them.")
        del self.__threads[:]
        self.__threads.append(v)

    @property
    def callstack(self):
        return self.current_thread.callstack

    @property
    def depth(self):
        return len(self.callstack)

    @property
    def current_element(self):
        return self.callstack[-1]

    @property
    def current_element_idx(self):
        return len(self.callstack) - 1

    @property
    def can_pop(self):
        return len(self.callstack) > 1

    @property
    def can_pop_thread(self):
        return len(self.__threads) > 1

    @property
    def json_token(self):
        return {
            "threads": [t.json_token for t in self.__threads],
            "threadCounter": self.__thread_cnt
        }

    def set_json(self, o, story):
        del self.__threads[:]
        jthr = o["threads"]
        self.__threads.extend(Thread(tok, story) for tok in jthr)
        self.__thread_cnt = o["threadCounter"]

    def index(self, idx):
        return next(t for t in self.__threads if t.idx == idx, None)

    def push_thread(self):
        nthr = self.current_thread.copy()
        self.__thread_cnt += 1
        nthr.idx = self.__thread_cnt
        self.__threads.append(nthr)

    def pop_thread(self):
        if self.can_pop_thread:
            self.__threads.pop()
        else:
            raise IndexError("Can't pop thread")

    def push(self, t):
        self.callstack.append(
            Element(t, self.current_element.container,
                    self.current_element.content_idx, False))

    def can_pop_t(self, t):
        if not self.can_pop: return False
        if t is None: return True
        return self.current_element.stack_type == t

    def pop(self, t):
        if self.can_pop_t(t):
            self.callstack.pop()
        else:
            raise ValueError("Mismatched push/pop in callstack")

    def get_var(self, name, ctx_idx=None):
        if ctx_idx is None: ctx_idx = self.current_element_idx + 1
        ctx_el = self.callstack[ctx_idx - 1]
        return ctx_el.tmp_var.get(name)

    def set_var(self, name, v, new, ctx_idx=None):
        if ctx_idx is None: ctx_idx = self.current_element_idx + 1
        ctx_el = self.callstack[ctx_idx - 1]
        if not new and name not in self.current_element.tmp_var:
            raise ValueError("Can't find variable: %s" % name)
        old = self.current_element.tmp_var.get(name)
        if old is not None:
            ListValue.retain_list_origins(old, v)
        ctx_el.tmp_var[name] = v

    def context(self, name):
        if name in self.current_element.tmp_var:
            return self.current_element_idx + 1
        return 0
