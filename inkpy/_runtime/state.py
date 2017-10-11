from .object import Void
from .env import LexEnv
from io import StringIO
from .value import StringValue, ListValue, Value, ValueType
from .callstack import CallStack, StackType
from .glue import Glue
from .cmd import Cmd, CmdType
import random


class State:
    # Constructor
    def __init__(self, story):
        # Public fields
        self.story = story
        self.callstack = CallStack(story.root)
        self.divert_target_obj = None
        self.story_seed = random.randrange(100)
        self.prev_rnd = 0
        self.did_safe_exit = 0
        # Private fields
        self.__is_ext_fun_eval = False
        self.__org_callstack = None
        self.__org_eval_stack_height = 0
        self.__output_stream = []
        self.__output_txt_dirty = False
        self.__output_tags_dirty = False
        self.__dirty()
        self.__current_choices = []
        self.__lexenv = LexEnv(self.callstack, story.list_defs)
        self.__current_errors = None
        self.__eval_stack = []
        self.__visit_counts = {}
        self.__turn_indices = {}
        self.__current_turn_idx = -1
        self.__txt = None
        self.__tags = None
        # Init
        self.go_to_start()

    # Properties

    @property
    def generated_choices(self):
        return self.__current_choices

    @property
    def current_choices(self):
        if self.can_continue: return []
        return self.__current_choices

    @property
    def current_errors(self):
        return self.__current_errors

    @property
    def lexenv(self):
        return self.__lexenv

    @property
    def eval_stack(self):
        return self.__eval_stack

    @property
    def visit_counts(self):
        return self.__visit_counts

    @property
    def turn_indices(self):
        return self.__turn_indices

    @property
    def current_turn_index(self):
        return self.__current_turn_idx

    @property
    def callstack_depth(self):
        return self.__callstack.depth

    @property
    def output_stream(self):
        return self.__output_stream

    @property
    def current_path(self):
        if self.current_content is None: return None
        return self.current_content.path

    @current_path.setter
    def current_path(self, v):
        if v is None:
            self.current_content = None
        else:
            self.current_content = story.content_at(v)

    @property
    def current_content(self):
        return self.callstack.current_element.obj

    @current_content.setter
    def current_content(self, v):
        self.callstack.current_element.obj = v

    @property
    def current_container(self):
        return self.callstack.current_element.container

    @property
    def prev_ct_obj(self):
        return self.callstack.current_thread.prev_ct_obj

    @prev_ct_obj.setter
    def prev_ct_obj(self, v):
        self.callstack.current_thread.prev_ct_obj = v

    @property
    def has_errors(self):
        return self.current_errors is not None and len(self.current_errors) > 0

    @property
    def can_continue(self):
        print("content: {0} ({1} errors)".format(self.current_content,
                                                 len(self.current_errors)
                                                 if self.has_errors else 0))
        input()
        return self.current_content is not None and not self.has_errors

    @property
    def text(self):
        if self.__output_txt_dirty:
            s = StringIO()
            for o in self.__output_stream:
                if isinstance(o, StringValue):
                    s.write(o.value)
            self.__txt = s.getvalue()
            self.__output_txt_dirty = False
        return self.__txt

    @property
    def tags(self):
        if self.__output_tags_dirty:
            self.__tags = []
            for o in self.__output_stream:
                if isinstance(o, Tag):
                    self.__tags.append(o)
            self.__output_tags_dirty = False
        return self.__tags

    @property
    def in_expr_eval(self):
        return self.callstack.current_element.in_expr_eval

    @in_expr_eval.setter
    def in_expr_eval(self, v):
        self.callstack.current_element.in_expr_eval = v

    @property
    def json_token(self):
        raise NotImplementedError

    @json_token.setter
    def json_token(self, v):
        raise NotImplementedError

    @property
    def glue_index(self):
        for i, c in reversed(list(enumerate(self.__output_stream))):
            if isinstance(c, Glue):
                return i
            elif isinstance(c, Cmd):
                break
        return -1

    @property
    def output_ends_in_nl(self):
        if len(self.__output_stream) > 0:
            for i, c in self.__output_stream:
                if isinstance(c, Cmd): break
                if isinstance(c, StringValue):
                    if c.is_new_line: return True
                    elif c.is_non_ws: break
        return False

    @property
    def output_contains_content(self):
        for c in self.__output_stream:
            if isinstance(c, StringValue): return True
        return False

    @property
    def in_str_eval(self):
        for i, c in self.__output_stream:
            if isinstance(c, Cmd):
                if c.cmd_type == CmdType.BEGIN_STR: return True
        return False

    # Private methods

    def __dirty(self):
        self.__output_txt_dirty = True
        self.__output_tags_dirty = True

    def __try_splitting_head_tail_ws(self, sv):
        s = sv.value
        hfirst_nlidx = -1
        hlast_nlidx = -1
        for i, c in enumerate(s):
            if c == '\n':
                if hfirst_nlidx == -1:
                    hfirst_nlidx = i
                hlast_nlidx = i
            elif c in [' ', '\t']:
                continue
            else:
                break
        tfirst_nlidx = -1
        tlast_nlidx = -1
        for i, c in enumerate(s):
            if c == '\n':
                if hfirst_nlidx == -1:
                    hfirst_nlidx = i
                hlast_nlidx = i
            elif c in [' ', '\t']:
                continue
            else:
                break
        if hfirst_nlidx == -1 and tlast_nlidx == -1:
            return None
        list_texts = []
        inner_str_start = 0
        inner_str_end = len(s)
        if hfirst_nlidx != -1:
            if hfirst_nlidx > 0:
                list_texts.append(StringValue(s[:hfirst_nlidx]))
            list_texts.append(StringValue("\n"))
            inner_str_start = hlast_nlidx + 1
        if tlast_nlidx != -1:
            inner_str_end = tfirst_nlidx
        if inner_str_end > inner_str_start:
            list_texts.append(StringValue(s[inner_str_start:inner_str_end]))
        if tlast_nlidx != -1 and tfirst_nlidx > hlast_nlidx:
            list_texts.append(StringValue("\n"))
            if tlast_nlidx < len(s) - 1:
                num_spaces = len(s) - tlast_nlidx - 1
                list_texts.append(StringValue(s[tlast_nlidx + 1, num_spaces]))
        return list_texts

    def __push_to_output_individual(self, o):
        include = True
        if isinstance(o, Glue):
            match_right_glue = None
            if o.is_left:
                match_right_glue = self.__match_right_glue(o)
            if o.is_left or o.is_bi:
                self.__trim_new_lines(match_right_glue)
            include = o.is_bi or o.is_right
        elif isinstance(o, StringValue):
            if self.current_glue_index != -1:
                if o.is_new_line:
                    self.__trim_from_glue()
                    include = False
                elif o.is_non_ws:
                    self.__remove_glue()
            elif o.is_new_line:
                if self.output_ends_in_nl or not self.output_contains_content:
                    include = False
        if include:
            self.__output_stream.append(o)
        self.__dirty()

    def __trim_new_lines(self, glue):
        remove_from = -1
        right_glue = -1
        found_non_ws = False
        for i, o in reversed(list(enumerate(self.__output_stream))):
            is_cmd = isinstance(o, Cmd)
            is_txt = isinstance(o, StringValue)
            is_glue = isinstance(o, Glue)
            if is_cmd or (is_txt and o.is_non_ws):
                found_non_ws = True
                if glue is None: break
            elif glue and o == glue:
                right_glue = i
                break
            elif is_txt and o.is_new_line and not found_non_ws:
                remove_from = i
            if remove_from >= 0:
                i = remove_from
                while i < len(self.__output_stream):
                    if isinstance(self.__output_stream[i], StringValue):
                        del self.__output_stream[i]
                    else:
                        i += 1
            if glue and right_glue >= 0:
                i = right_glue
                while i < len(self.__output_stream):
                    if isinstance(self.__output_stream[i],
                                  Glue) and self.__output_stream[i].is_right:
                        del self.__output_stream[i]
                    else:
                        i += 1
            self.__dirty()

    def __match_right_glue(self, glue):
        if not glue.is_left: return None
        for i, c in reversed(list(enumerate(self.__output_stream))):
            if isinstance(c, Glue) and c.is_right and c.parent == glue.parent:
                return c
            elif isinstance(c, Cmd):
                break
        return None

    def __trim_from_glue(self):
        i = self.glue_index
        while i < len(self.__output_stream):
            c = self.__output_stream[i]
            if isinstance(c, StringValue) and not c.is_non_ws:
                del self.__output_stream[i]
            else:
                i += 1
        self.__dirty()

    def __remove_glue(self):
        for i, c in reversed(list(enumerate(self.__output_stream))):
            if isinstance(c, Glue):
                del self.__output_stream[i]
            elif isinstance(c, Cmd):
                break
        return self.__dirty()

    # Public methods

    def go_to_start(self):
        self.callstack.current_element.container = self.story.main
        self.callstack.current_element.content_idx = 0

    def copy(self):
        copy = State(self.story)
        copy.output_stream.extend(self.__output_stream)
        self.__dirty()
        copy.__current_choices.extend(self.__current_choices)
        if self.has_errors:
            copy.__current_errors = self.current_errors[:]
        copy.callstack = self.callstack.copy()
        if self.__org_callstack is not None:
            copy.__org_callstack = self.__org_callstack.copy()
        copy.__lexenv = LexEnv(copy.callstack, self.story.list_defs)
        copy.lexenv.copy_from(self.lexenv)
        copy.eval_stack.extend(self.eval_stack)
        copy.__org_eval_stack_height = self.__org_eval_stack_height
        if self.divert_target_obj is not None:
            copy.divert_target_obj = self.divert_target_obj
        copy.prev_ct_obj = self.prev_ct_obj
        copy.__visit_counts = self.visit_counts.copy()
        copy.__turn_indices = self.turn_indices.copy()
        copy.story_seed = self.story_seed
        copy.prev_rnd = self.prev_rnd
        copy.did_safe_exit = self.did_safe_exit
        return copy

    def reset_errors(self):
        self.current_errors = None

    def reset_output(self):
        del self.__output_stream[:]
        self.__dirty()

    def push_to_output(self, o):
        if isinstance(o, StringValue):
            list_text = self.__try_splitting_head_tail_ws(o)
            if list_text is not None:
                for txt in list_text:
                    self.__push_to_output_individual(txt)
                return
        self.__push_to_output_individual(o)
        self.__dirty()

    def push_eval_stack(self, o):
        if isinstance(o, ListValue):
            rawl = o.value
            names = rawl.orgnames
            if names is not None:
                orgs = []
                for n in names:
                    df = self.story.list_defs.get(n)
                    if df not in orgs: orgs.append(df)
                rawl.origins = orgs
            self.eval_stack.append(o)

    def pop_eval_stack(self, n=None):
        if n is None:
            return self.eval_stack.pop()
        else:
            if n > len(self.eval_stack):
                raise IndexError("Trying to pop too many objects")
            popped = self.eval_stack[-n:]
            del self.eval_stack[-n:]
            return popped

    def peek_eval_stack(self):
        return self.eval_stack[-1]

    def force_end(self):
        while self.callstack.can_pop_thread:
            self.callstack.pop_thread()
        while self.callstack.can_pop:
            self.callstack.pop()
        del self.__current_choices[:]
        self.current_content = None
        self.prev_ct_obj = None
        self.did_safe_exit = True

    def set_chosen_path(self, path):
        del self.__current_choices[:]
        self.current_path = path
        self.__current_turn_index += 1

    def start_ext_function_eval(self, func_container, *args):
        self.__org_callstack = self.callstack
        self.__org_eval_stack_height = len(self.eval_stack)
        self.callstack = CallStack(func_container)
        self.callstack.current_element.stack_type = StackType.FUNCTION
        self.lexenv.callstack = self.callstack
        self.__is_ext_fun_eval = True
        self.pass_args_to_eval_stack(*args)

    def pass_args_to_eval_stack(self, *args):
        for arg in args:
            if not (isinstance(arg, int) or isinstance(arg, float)
                    or isinstance(arg, str)):
                raise TypeError(
                    "Ink arguments to functions must be int, float, or str")
            self.push_eval_stack(Value.create(arg))

    def try_exit_ext_func_eval(self):
        if self.__is_ext_fun_eval and self.callstack_depth == 1 and self.callstack.current_element.stack_type == StackType.FUNCTION:
            self.current_content = None
            self.did_safe_exit = True
            return True
        return False

    def complete_ext_func_eval(self):
        ret = None
        while len(self.eval_stack) > self.__org_eval_stack_height:
            if ret is None:
                ret = self.pop_eval_stack()
        self.callstack = self.__org_callstack
        self.__org_callstack = None
        self.__org_eval_stack_height = 0
        self.lexenv.callstack = self.callstack
        if ret:
            if isinstance(ret, Void): return None
            if ret.value_type == ValueType.DIVERT_TARGET:
                return str(ret.value)
            return ret.value
        return None

    def add_error(self, msg):
        if self.current_errors is None:
            self.current_errors = []
        self.current_errors.append(msg)
