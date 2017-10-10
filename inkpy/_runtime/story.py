from .state import State
from .object import Object, Void
from .listdeforg import ListDefOrigin
from .value import *
from ..error import StoryError
from random import Random
from .container import Container
from .callstack import StackType
from .path import Path
from .tag import Tag
from ..util import Event
from .divert import Divert
from io import StringIO
from .cmd import Cmd, CmdType
from .varassign import VarAssign
from .varref import VarRef
from .prim import Primitive
from .choice import Choice
from .choicepoint import ChoicePoint


class Story(Object):

    # Constructor
    def __init__(self, root_container, lists):
        self.__state = None
        self.__list_defs = None if lists is None else ListDefOrigin(lists)
        self.__prev_cont_set = None
        self.__tmp_eval_container = None
        self.__validated_exts = False
        self.__externals = {}
        self.__observers = {}
        self.__main = None
        self.allow_ext_func_fallbacks = False
        self.reset()

    # Properties
    @property
    def choices(self):
        ch = []
        for c in self.state.current_choices:
            if not c.choicepoint.is_invisible_defaults:
                c.idx = len(ch)
                ch.append(c)
        return ch

    @property
    def gtags(self):
        return self.__tags_at("")

    @property
    def state(self):
        return self.__state

    @property
    def list_defs(self):
        return self.__list_defs

    @property
    def main(self):
        if self.__tmp_eval_container: return self.__tmp_eval_container
        return self.__main

# Methods

    def continue_(self, max_=False):
        if not self.__validated_exts:
            self.validate_exts()
        if max_:
            s = StringIO()
            while self.state.can_continue:
                s.write(self.__continue())
            return s.getvalue()
        return self.__continue()

    def choose(self, idx):
        ch = self.choices
        self.__assert(0 <= idx < len(ch), "Choice out of range")
        c = ch[idx]
        self.state.callstack.current_thread = c.threadatgen
        self.goto(c.choicepoint.choice_target.path)

    def goto(self, path, *args):
        if isinstance(path, str):
            self.state.pass_args_to_eval_stack(*args)
            path = Path(path)
        self.state.set_chosen_path(path)
        self.__visit_changed()

    def tagsat(self, path):
        return self.__tags_at(path)

    def reset(self):
        self.__state = State(self)
        self.__state.lexenv.variableChanged += self.__var_changed
        self.__reset_globals()

    def watch(self, var, f):
        if self.__observers is None: self.__observers = {}
        if isinstance(var, list):
            for v in var:
                self.watch(v, f)
        else:
            if var not in self.__observers:
                self.__observers[var] = Event()
            self.__observers[var] += f

    def unwatch(self, f, var=None):
        if self.__observers is None: return
        if var:
            if var in self.__observers:
                self.__observers[var] -= f
        else:
            for observer in self.__observers.values():
                observer -= f

    def bindfun(self, fname, f, *argtypes):
        self.__assert(f is not None, "Can't bind to None")
        self.__assert(fname not in self.__externals,
                      "Function {0} has already been bound.".format(fname))
        self.__externals[fname] = f

    def unbindfun(self, fname):
        self.__assert(fname in self.__externals,
                      "Function {0} has not been found".format(fname))
        del self.__externals[fname]

    def content_at(self, path):
        return self.main.content_at_path(path)

    def validate_exts(self):
        missing = set()
        self.__validate(self.__main, missing)
        if len(missing) == 0: self.__validated_exts = True
        else:
            msg = "ERROR: Missing function binding for external{0}: '{1}' {2}".format(
                "s" if len(missing) > 1 else "", ", ".join(missing),
                ", and now fallback ink function found." if
                self.allow_ext_func_fallbacks else " (ink fallbacks disabled)")
            self.__error(msg)

    def call_ext(self, fname, nargs):
        f = None
        fallback_cont = None
        ext = self.__externals.get(fname)
        if ext is None:
            if self.allow_ext_func_fallbacks:
                fallback_cont = self.content_at(Path(fname))
                self.__assert(
                    isinstance(fallback_cont, Container),
                    "Trying to call EXTERNAL function '{0}'"
                    "which has not been bound,"
                    "and fallback ink function could not be found."
                    .format(fname))
                self.state.callstack.push(StackType.FUNCTION)
                self.divert_target_obj = fallback_cont
                return
            else:
                self.__assert(False, "Trying to call EXTERNAL function '{0}'"
                              "which has not been bound,"
                              "and fallback ink functions are disabled."
                              .format(fname))
        args = []
        for i in range(nargs):
            args.append(self.state.pop_eval_stack().value)
        args = reversed(args)
        fres = f(*args)
        ret = None
        if fres:
            ret = Value.create(fres)
            self.__assert(
                ret is not None,
                "Could not create ink value from returned object of type {0}".
                format(type(fres)))
        else:
            ret = Void()
        self.state.push_eval_stack(ret)

    def eval_expr(self, cont):
        start_csh = len(self.state.callstack.callstack)
        self.state.callstach.push(StackType.TUNNEL)
        self.__tmp_eval_container = cont
        self.state.go_to_start()
        eval_sh = len(self.state.eval_stack)
        self.continue_()
        self.__tmp_eval_container = None
        if len(self.state.callstack.callstack) > start_csh:
            self.state.callstack.pop()
        end_sh = len(self.state.eval_stack)
        if end_sh > eval_sh:
            return self.state.pop_eval_stack()
        else:
            return None

    def eval_fun(self, fname, *args):
        return self.eval_fun_with_output(fname, *args)["result"]

    def eval_fun_with_output(self, fname, *args):
        if fname is None: raise TypeError("Function is None")
        elif fname.isspace():
            raise TypeError("Function is empty or white space")

        cont = None
        try:
            cont = self.content_at(Path(fname))
            if not isinstance(cont, Container): cont = None
        except StoryError as e:
            if "not found" in e.message:
                raise NameError(
                    "Function {0} doesn't exist".format(fname)) from e
            else:
                raise e
        self.state.start_ext_function_eval(cont, *args)
        out = StringIO()
        while self.state.can_continue:
            out.write(self.continue_())
        res = self.state.complete_ext_function_eval()
        return {"output": out.getvalue(), "result": res}

    def has_fun(self, fname):
        try:
            return isinstance(self.content_at(Path(fname)), Container)
        except StoryError:
            return False

    # Private methods

    def __snapshot(self):
        return self.state.copy()

    def __restore_snapshot(self, state):
        self.__state = state

    def __continue(self):
        if not self.state.can_continue:
            raise StoryError("Can't continue")
        self.state.reset_output()
        self.state.did_safe_exit = False
        self.state.lexenv.batchObserving = True
        try:
            state_at_last_nl = None
            while True:  # Begin DO
                self.__step()
                if not self.state.can_continue:
                    self.__try_follow_default_choice()
                if not self.state.in_str_eval:
                    if state_at_last_nl:
                        curtxt = self.state.text
                        prvtxtlen = len(state_at_last_nl.text)
                        prvtagcnt = len(state_at_last_nl.tags)
                        if curtxt != state_at_last_nl.text or prvtagcnt != len(
                                self.state.tags):
                            if len(curtxt) >= prvtxtlen and curtxt[prvtxtlen -
                                                                   1] == '\n':
                                self.__restore_snapshot(state_at_last_nl)
                                break
                            else:
                                state_at_last_nl = None
                    if self.state.output_ends_in_nl:
                        if self.state.can_continue:
                            if state_at_last_nl is None:
                                state_at_last_nl = self.__snapshot()
                        else:
                            state_at_last_nl = None
                if not self.state.can_continue: break  # End DO
            if state_at_last_nl: self.__restore_snapshot(state_at_last_nl)
            if not self.state.can_continue:
                self.__assert(
                    not self.state.callstack.can_pop_thread,
                    "Thread available to pop."
                    "Threads should always be flat at the end of evaluation.")
                if (len(self.state.generated_choices) == 0
                        and not self.state.did_safe_exit
                        and self.__tmp_eval_container is None):
                    self.__assert(
                        not self.state.callstack.can_pop_t(StackType.TUNNEL),
                        "Unexpectedly reached end of content."
                        "Do you need a `->->` to return from a tunnel?")
                    self.__assert(
                        not self.state.callstack.can_pop_t(StackType.FUNCTION),
                        "Unexpectedly reached end of content."
                        "Do you need a `~ return`?")
                    self.__assert(not self.state.callstack.can_pop,
                                  "Ran out of content."
                                  "Do you need a `-> DONE` or `-> END`?")
                    self.__error("Unexpectedly reached end of content."
                                 "Reason unknown."
                                 "That's clearly a compiler bug.")
        except StoryError as e:
            self.__add_error(e.message, e.useln)
        finally:
            self.state.did_safe_exit = False
            self.state.lexenv.batchObserving = False
        return self.state.text

    def __step(self):
        shouldout = True
        cur = self.state.current_content
        if cur is None: return
        curcont = cur if isinstance(cur, Container) else None
        while curcont:
            self.__visit(curcont, True)
            if len(curcont.content) == 0: break
            cur = curcont.content[0]
            self.state.callstack.current_element.content_idx = 0
            self.state.callstack.current_element.container = curcont
            curcont = cur if isinstance(cur, Container) else None
        curcont = self.state.callstack.current_element.container
        is_flow = self.__perform_flow(cur)
        if self.state.current_content is None: return
        if is_flow: shouldout = False
        if isinstance(cur, ChoicePoint):
            ch = self.__process_choice(cur)
            if ch: self.state.generated_choices.append(ch)
            cur = None
            shouldout = False
        if isinstance(cur, Container):
            shouldout = False
        if shouldout:
            if isinstance(cur, VarPtrValue) and cur.ctx_idx == -1:
                ctx = self.state.callstack.context(cur.value)
                cur = VarPtrValue(cur.value, ctx)
            if self.state.in_expr_eval:
                self.state.push_eval_stack(cur)
            else:
                self.state.push_to_output(cur)
        self.__next()
        if isinstance(cur, Cmd) and cur.cmd_type == CmdType.START_THREAD:
            self.state.callstack.push_thread()

    def __visit(self, cont, at_start):
        if not cont.count_at_start or at_start:
            if cont.count_visits:
                self.__inc_visit_count(cont)
            if cont.count_turns:
                self.__record_turn_idx_visit(cont)

    def __visit_changed(self):
        prv = self.state.prev_ct_obj
        new = self.state.current_content
        if not new: return
        if self.__prev_cont_set is None: self.__prev_cont_set = set()
        self.__prev_cont_set.clear()
        if prv:
            prv_anc = prv if isinstance(prv, Container) else prv.parent
            while isinstance(prv_anc, Container):
                self.__prev_cont_set.add(prv_anc)
                prv_anc = prv_anc.parent
        child = new
        anc = child.parent
        while isinstance(anc, Container) and anc not in self.__prev_cont_set:
            at_start = len(anc.content) > 0 and child = anc.content[0]
            self.__visit(anc, at_start)
            child = anc
            anc = anc.parent

    def __process_choice(self, cp):
        chshow = True
        if cp.has_condition:
            condval = self.state.pop_eval_stack()
            if not self.__is_true(condval):
                chshow = False
        start_txt = ""
        chonly_txt = ""
        if cp.has_choice_only_content:
            chonly_str = self.state.pop_eval_stack()
            chonly_txt = chonly_str.value
        if cp.has_start_content:
            start_str = self.state.pop_eval_stack()
            start_txt = start_str.value
        if cp.once_only:
            visits = self.__visit_count(cp.choice_target)
            if visits > 0:
                chshow = False
        ch = Choice(cp)
        ch.threadatgen = self.state.callstack.current_thread.copy()
        if not chshow: return None
        ch.text = start_txt + chonly_txt
        return ch

    def __is_true(self, o):
        if isinstance(o, Value):
            if isinstance(o, DivertTargetValue):
                self.__error(
                    "Shouldn't use a divert target as a conditional value."
                    "Did you intend a function call `likeThis()` or a read-count check `likeThis`? (no arrows)"
                )
                return False
            return bool(o)
        return False

    def __perform_flow(self, o):
        if o is None: return False
        if isinstance(o, Divert):
            return self.__perform_flow_divert(o)
        elif isinstance(o, Cmd):
            return self.__perform_flow_cmd(o)
        elif isinstance(o, VarAssign):
            return self.__perform_flow_varass(o)
        elif isinstance(o, VarRef):
            return self.__perform_flow_varref(o)
        elif isinstance(o, Primitive):
            return self.__perform_flow_prim(o)
        return False

    def __validate(self, o, missing):
        if isinstance(o, Container):
            for c in o.content:
                if not isinstance(c, Container) or not c.has_valid_name:
                    self.__validate(c, missing)
            for c in o.named_content.values():
                self.__validate(c, missing)
            return
        if isinstance(o, Divert) and o.is_ext:
            n = o.target_path_str
            if n not in self.__externals:
                if self.allow_ext_func_fallbacks:
                    if name not in self.main.named_content: missing.add(n)
                else: missing.add(n)

    def __tags_at(self, path):
        path = Path(path)
        cont = self.content_at(path)
        while True:
            if isinstance(cont.content[0], Container): cont = cont.content[0]
            else: break
        tags = None
        for c in cont.content:
            if isinstance(c, Tag):
                tags = tags or []
                tags.append(c.txt)
            else:
                break
        return tags

    def __next(self):
        self.state.prev_ct_obj = self.state.current_content
        if self.state.divert_target_obj:
            self.state.current_content = self.state.divert_target_obj
            self.divert_target_obj = None
            self.__visit_changed()
            if self.state.current_content: return
        if not self.__inc_ct_ptr():
            didpop = False
            if (self.state.callstack.can_pop_t(StackType.FUNCTION)):
                self.state.callstack.pop(StackType.FUNCTION)
                if self.state.in_expr_eval:
                    self.state.push_eval_stack(Void())
                didpop = True
            elif self.state.callstack.can_pop_thread:
                self.state.callstack.pop_thread()
                didpop = True
            else:
                self.state.try_exit_ext_func_eval()
            if didpop and self.state.current_content: self.__next()

    def __inc_ct_ptr(self):
        success = True
        cur = self.state.callstack.current_element
        cur.content_idx += 1
        while cur.content_idx >= len(cur.container.content):
            success = False
            next_ancestor = cur.container.parent
            if not isinstance(next_ancestor, Container):
                break
            try:
                idx = next_ancestor.content.index(cur.container)
            except ValueError:
                break
            cur.container = next_ancestor
            cur.content_idx = idx + 1
            success = True
        if not success: cur.container = None
        return success

    def __try_follow_default_choice(self):
        choices = self.state.current_choices
        invis = [c for c in choices if c.choicepoint.is_invisible_default]
        if len(invis) == 0 or len(choices) > len(invis): return False
        self.goto(invis[0].choicepoint.choice_target.path)
        return True

    def __visit_count(self, cont):
        if not cont.count_visits:
            self.__error(
                "read count for target({0} on {1}) unknown."
                "The story may need to be compiled with `-c` (countAllVisits)"
                .format(cont.name, cont.debug_metadata))
            return 0
        return self.state.visit_counts.get(str(cont.path), 0)

    def __inc_visit_count(self, cont):
        count = 0
        contpathstr = str(cont.path)
        count = self.state.visit_counts.get(contpathstr, 0)
        count += 1
        self.state.visit_counts[contpathstr] = count

    def __turns_since(self, cont):
        if not cont.count_turns:
            self.__error(
                "TURNS_SINCE() for target({0} on {1}) unknown. "
                "The story may need to be compiled with `-c` (countAllVisits)."
                .format(cont.name, cont.debug_metadata))
        cont_path = str(cont.path)
        idx = self.state.turn_indices.get(cont_path)
        if idx is None: return -1
        else: return self.state.current_turn_index - idx

    def __record_turn_idx_visit(self, cont):
        self.state.turn_indices[str(cont.path)] = self.state.current_turn_index

    def __next_shuffle(self):
        num_el_int = self.state.pop_eval_stack()
        if num_el_int is None:
            self.__error(
                "Expected number of elements in sequence for shuffle index")
            return 0
        seqcont = self.state.container
        num_el = num_el_int.value
        seqcount = self.state.pop_eval_stack().value
        loop_idx = seqcount / num_el
        iter_idx = seqcount % num_el
        seqpath = str(seqcont.path)
        seqhash = sum(ord(c) for c in seqpath)
        rndseed = seqhash + loop_idx + self.state.story_seed
        rnd = Random()
        rnd.seed(rndseed)
        unpicked = list(range(num_el))
        for i in range(iter_idx + 1):
            chosen = rnd.randint(len(unpicked))
            chosen_idx = unpicked[chosen]
            del unpicked[chosen]
            if i == iter_idx: return chosen_idx
        raise NotImplementedError("Shouldn't reach this code...")

    def __error(self, msg, useln=False):
        e = StoryError(msg)
        e.useln = useln
        raise e

    def __add_error(self, msg, useln):
        if self.__dm:
            ln = self.__dm.end_ln if useln else self.__dm.start_ln
            msg = "RUNTIME ERROR: '{0}' line {1}: {2}".format(
                self.__dm.file_name, ln, msg)
        elif self.state.current_path:
            msg = "RUNTIME ERROR: ({0}): {1}".format(self.state.current_path,
                                                     msg)
        else:
            msg = "RUNTIME ERROR: " + msg
        self.state.add_error(msg)
        self.state.force_end()

    def __assert(self, cond, msg=None):
        if not cond:
            if msg is None: msg = "Story assert"
            raise AssertionError("{0} {1}".format(msg, self.__dm))

    def __reset_globals(self):
        if "global decl" in self.__main.named_content:
            org_path = self.state.current_path
            self.goto("global decl")
            self.__continue()
            self.state.current_path = org_path

    def __var_changed(self, name, newv):
        if self.__observers is None:
            return
        if not isinstance(newv, Value):
            raise TypeError(
                "Tried to get the value of a variable that is not a standard type"
            )
        observers = self.__observers.get(name)
        if observers is not None:
            observers(name, newv.value)

    def __perform_flow_divert(self, o):
        assert isinstance(o, Divert), "Did not get a divert"
        if o.is_conditional:
            cond_val = self.state.pop_eval_stack()
            if not cond_val: return True
        if o.has_variable_target:
            vname = o.variable_divert_name
            vcont = self.__state.lexenv.get_var(vname)
            if not isinstance(vcont, DivertTargetValue):
                err = (
                    "Tried to divert to a target from a variable,"
                    "but the variable ({0}) didn't contain a divert target, it {1}"
                    .format(vname, "was empty or nil." if vcont.value == 0 else
                            "contained {0}".format(vcont)))
                self.__error(err)
            self.__state.divert_target_obj = self.content_at(vcont.value)
        elif o.is_external:
            self.call_ext(o.target_path_str, o.ext_args)
            return True
        else:
            self.__state.divert_target_obj = o.target_content
        if o.pushes_to_stack:
            self.__state.callstack.callstack(o.stack_type)
        if self.__state.divert_target_obj is None and not o.is_external:
            if o.debug_metadata.src_name is not None:
                self.__error("Divert target doesn't exist: {0}".format(
                    o.debug_metadata.src_name))
            else:
                self.__error("Divert resolution failed: {0}".format(o))
        return True

    def __eval_ev_start(self, cmd):
        self.__assert(self.__state.in_expr_eval == False,
                      "Already in expression evaluation")
        self.__state.in_expr_eval = True

    def __eval_ev_end(self, cmd):
        self.__assert(self.in_expr_eval == True,
                      "Not in expression evaluation mode")
        self.__state.in_expr_eval = False

    def __eval_ev_output(self, cmd):
        if len(self.__state.eval_stack) > 0:
            o = self.__state.pop_eval_stack()
            if not isinstance(o, Void):
                self.__state.push_to_output(StringValue(str(o)))

    def __eval_noop(self, cmd):
        pass

    def __eval_dup(self, cmd):
        self.__state.push_eval_stack(self.__state.peek_eval_stack())

    def __eval_pop_val(self, cmd):
        self.__state.pop_eval_stack()

    def __eval_pop(self, cmd):
        t = StackType.TUNNEL if cmd.cmd_type == CmdType.POP_TUNNEL else StackType.FUNCTION
        override = None
        if t == StackType.TUNNEL:
            popped = self.__state.pop_eval_stack()
            if not isinstance(popped, DivertTargetValue):
                self.__assert(
                    isinstance(popped, Void),
                    "Expected void id `->->` doesn't override target")
            else:
                override = popped
        if self.__state.try_exit_ext_func_eval():
            return
        elif not self.__state.callstack.can_pop_t(t):
            names = {
                StackType.FUNCTION: "function return statement (~ return)",
                StackType.TUNNEL: "tunnel onwards statement (->->)"
            }
            expected = names[self.__state.callstack.current_element.stack_type]
            if not self.__state.callstack.can_pop:
                expected = "end of flow (-> END or choice)"
            errormsg = "Found {0}, when expected {1}".format(
                names[t], expected)
            self.__error(errormsg)
        else:
            self.__state.callstack.pop()
            if override:
                self.__state.divert_target_obj = self.content_at(
                    override.value)

    def __eval_beg_str(self, cmd):
        self.__state.push_to_output(cmd)
        self.__assert(
            self.__state.in_expr_eval,
            "Expected to be in expression evaluation when evaluating a string")
        self.__state.in_expr_eval = False

    def __eval_end_str(self, cmd):
        content_stack = []
        output_consumed = 0
        for o in reversed(self.__state.output_stream):
            output_consumed += 1
            if isinstance(o, Cmd):
                if o.cmd_type == CmdType.BEGIN_STR: return
            if isinstance(o, StringValue):
                content_stack.append(o)
        del self.__state.output_stream[-output_consumed:]
        s = StringIO()
        for c in content_stack:
            s.write(str(c))
        self.__state.in_expr_eval = True
        self.__state.push_eval_stack(StringValue(s.getvalue()))

    def __eval_choice_count(self, cmd):
        self.__state.push_eval_stack(
            IntValue(len(self.__state.generated_choices)))

    def __eval_ts_rc(self, cmd):
        t = self.__state.pop_eval_stack()
        if not isinstance(t, DivertTargetValue):
            extra = ""
            if isinstance(t, IntValue):
                extra = ". Did you accidentally pass a read count ('knot_name') instead of a target ('-> knot_name?)"
            self.__error("TURNS_SINCE expected a divert target, but saw " + t +
                         extra)
            return
        cont = self.content_at(t.value)
        either_count = 0
        if cmd.cmd_type == CmdType.TURNS_SINCE:
            either_count = self.__turns_since(cont)
        else:
            either_count = self.__visit_count(cont)
        self.__state.push_eval_stack(IntValue(either_count))

    def __eval_rn(self, cmd):
        mx = self.__state.pop_eval_stack()
        mn = self.__state.pop_eval_stack()
        self.__assert(
            isinstance(mn, IntValue),
            "Invalid value for minimum parameter of RANDOM(min,max)")
        self.__assert(
            isinstance(mx, IntValue),
            "Invalid value for maximum parameter of RANDOM(min,max)")
        rng = mx.value - mn.value + 1
        self.__assert(
            rng <= 0,
            "RANDOM was called with min: {0} and max:{1}. Maximum must be larger".
            format(mn, mx))
        res_seed = self.__state.story_seed + self.__state.prev_rnd
        rnd = Random(res_seed)
        nxt_rnd = rnd.randint(0, rng)
        rnd_val = (nxt_rnd % rng) + mn.value
        self.__state.push_eval_stack(IntValue(rnd_val))
        self.__state.prev_rnd = nxt_rnd

    def __eval_seed_rn(self, cmd):
        seed = self.__state.pop_eval_stack()
        if not isinstance(seed, IntValue):
            self.__error("Invalid value passed to SEED_RANDOM")
        self.__state.story_seed = seed.value
        self.__state.prev_rnd = 0
        self.__state.push_eval_stack(Void())

    def __eval_visit_idx(self, cmd):
        self.__state.push_eval_stack(
            IntValue(self.__visit_count(self.__state.current_container) - 1))

    def __eval_seq_shuffle(self, cmd):
        self.__state.push_eval_stack(IntValue(self.__next_shuffle()))

    def __eval_done(self, cmd):
        if self.__state.callstack.can_pop_thread:
            self.__state.callstack.pop_thread()
        else:
            self.__state.did_safe_exit = True
            self.__state.current_content = None

    def __eval_end(self, cmd):
        self.__state.force_end()

    def __eval_itol(self, cmd):
        ival = self.__state.pop_eval_stack()
        lnval = self.__state.pop_eval_stack()
        self.__assert(
            isinstance(ival, IntValue),
            "Passed non-integer when creating a list from a numerical value")
        gen = None
        fldef = self.__list_defs.get(lnval.value)
        if fldef:
            fitem = fldef.get_item(ival.value)
            if fitem:
                gen = ListValue(fitem, ival.value)
        else:
            self.__error("Failed to find LIST called {0}".format(lnval.value))
        if gen is None: gen = ListValue()
        self.__state.push_eval_stack(gen)

    def __eval_lr(self, cmd):
        mx = self.__state.pop_eval_stack()
        mn = self.__state.pop_eval_stack()
        tl = self.__state.pop_eval_stack()
        mx = mx if isinstance(mx, int) else mx.value.max["value"]
        mn = mn if isinstance(mn, int) else mn.value.max["value"]
        res = ListValue()
        orgs = tl.value.origins
        if orgs:
            for org in orgs:
                r = org.range(mn, mx)
                for k, v in r.value.items():
                    res.value._add(k, v)
        self.__state.push_eval_stack(res)

    def __eval_def(self, cmd):
        self.__error("unhandled ControlCommand: " + cmd)

    def __perform_flow_cmd(self, cmd):
        assert isinstance(cmd, Cmd), "Did not get a control command"
        fs = {
            CmdType.EVAL_START: self.__eval_ev_start,
            CmdType.EVAL_END: self.__eval_ev_end,
            CmdType.EVAL_OUTPUT: self.__eval_output,
            CmdType.BEGIN_STR: self.__eval_beg_str,
            CmdType.END_STR: self.__eval_end_str,
            CmdType.CHOICE_COUNT: self.__eval_choice_count,
            CmdType.VISIT_IDX: self.__eval_visit_idx,
            CmdType.DONE: self.__eval_done,
            CmdType.DUPLICATE: self.__eval_dup,
            CmdType.END: self.__eval_end,
            CmdType.LIST_FROM_INT: self.__eval_itol,
            CmdType.LIST_RANGE: self.__eval_lr,
            CmdType.NO_OP: self.__eval_noop,
            CmdType.POP_FUN: self.__eval_pop,
            CmdType.POP_TUNNEL: self.__eval_pop,
            CmdType.POP_VALUE: self.__eval_pop_val,
            CmdType.RANDOM: self.__eval_rn,
            CmdType.SEED_RANDOM: self.__eval_seed_rn,
            CmdType.READ_COUNT: self.__eval_ts_rc,
            CmdType.TURNS_SINCE: self.__eval_ts_rc,
            CmdType.SQ_SHUFFLE_IDX: self.__eval_seq_shuffle,
            CmdType.START_THREAD: self.__eval_noop
        }
        fs.get(cmd.cmd_type, self.__eval_def)(cmd)
        return True

    def __perform_flow_varass(self, varass):
        assval = self.state.pop_eval_stack()
        self.state.lexenv.assign(varass, assval)
        return True

    def __perform_flow_varref(self, varref):
        val = None
        if varref.path_for_count:
            cont = varref.container_for_count
            count = self.__visit_count(cont)
            val = IntValue(count)
        else:
            val = self.state.lexenv.get_var(varref.name)
            if val is None:
                self.__error("Uninitialised variable: {0}".format(varref.name))
        self.state.push_eval_stack(val)
        return True

    def __perform_flow_prim(self, prim):
        params = self.state.pop_eval_stack(prim.nargs)
        res = prim(*params)
        self.state.push_eval_stack(res)
        return True

    @property
    def __dm(self):
        dm = None
        cnt = self.state.current_content
        if cnt:
            dm = cnt.debug_metadata
            if dm: return dm
        for i, e in reversed(self.state.callstack.callstack):
            o = e.obj
            if o and o.debug_metadata:
                return o.debug_metadata
        for i, o in reversed(self.state.output_stream):
            dm = o.debug_metadata
            if dm: return dm
        return None

    @property
    def __ln(self):
        if self.__dm: return self.dm.start_ln
        return 0
