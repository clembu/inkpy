from .._runtime.value import *
from .._runtime.glue import *
from .._runtime.cmd import *
from .._runtime.prim import *
from .._runtime.object import *
from .._runtime.divert import *
from .._runtime.path import *
from .._runtime.choice import *
from .._runtime.choicepoint import *
from .._runtime.varref import *
from .._runtime.varassign import *
from .._runtime.tag import *
from .._runtime.inklist import *
from .._runtime.listdef import *
from .._runtime.listdeforg import *

cmds = {
    CmdType.EVAL_START: "ev",
    CmdType.EVAL_OUTPUT: "out",
    CmdType.EVAL_END: "/ev",
    CmdType.DUPLICATE: "du",
    CmdType.POP_VALUE: "pop",
    CmdType.POP_FUN: "~ret",
    CmdType.POP_TUNNEL: "->->",
    CmdType.BEGIN_STR: "str",
    CmdType.END_STR: "/str",
    CmdType.NO_OP: "nop",
    CmdType.CHOICE_COUNT: "choiceCnt",
    CmdType.TURNS_SINCE: "turns",
    CmdType.READ_COUNT: "readc",
    CmdType.RANDOM: "rnd",
    CmdType.SEED_RANDOM: "srnd",
    CmdType.VISIT_IDX: "visit",
    CmdType.SQ_SHUFFLE_IDX: "seq",
    CmdType.START_THREAD: "thread",
    CmdType.DONE: "done",
    CmdType.END: "end",
    CmdType.LIST_FROM_INT: "listInt",
    CmdType.LIST_RANGE: "range"
}


def decode_num(nstr):
    try:
        return Value.create(int(nstr))
    except ValueError:
        pass
    try:
        return Value.create(float(nstr))
    except ValueError:
        pass
    return None


def decode_str(s):
    fchar = s[0]
    if fchar == '^': return StringValue(s[1:])
    elif s == "\n": return StringValue("\n")
    if s == "<>": return Glue(GlueType.BI)
    elif s == "G<": return Glue(GlueType.LEFT)
    elif s == "G>": return Glue(GlueType.RIGHT)
    for ct, cn in cmds.items():
        if s == cn: return Cmd(ct)
    if s == "L^": s = "^"
    if Primitive.exists(s):
        return Primitive.get(s)
    if s == "->->": return Cmd.POP_TUNNEL()
    elif s == "~ret": return Cmd.POP_FUN()
    if s == "void": return Void()
    return s


def jobj_to_choice(j):
    c = Choice()
    c.text = j["text"]
    c.idx = j["index"]
    c.org_choice_path = j["originalChoicePath"]
    c.org_thread_idx = j["originalThreadIndex"]
    return c


def jarr_to_cont(a):
    a[:] = [jtok_to_inkpy(t) for t in a]
    cont = Container()
    cont.content = a[:-1]
    t = a[-1]
    if t:
        named = {}
        for k, v in t.items():
            if k == "#f":
                cont.flags = v
            elif k == "#n":
                cont.name = v
            else:
                if isinstance(v, list):
                    c = jarr_to_cont(v)
                    c.name = k
                named[k] = v
        cont.named_only = named
    return cont


def jtok_to_inkpy(t):
    if isinstance(t, str):
        return decode_str(t)
    if isinstance(t, list):
        return jarr_to_cont(t)
    return t


def jobj_to_inkpy(j):
    # Divert Target
    try:
        return DivertTargetValue(Path.from_string(j["^->"]))
    except KeyError:
        pass

    # Var Pointer
    try:
        vptr = VarPtrValue(j["^var"])
        try:
            vptr.context_index = j["ci"]
        except KeyError:
            pass
        return vptr
    except KeyError:
        pass

    # Divert
    try:
        d = Divert()
        d.pushes_to_stack = True
        d.stack_type = StackType.TUNNEL
        d.is_external = False
        d.is_conditional = "c" in j
        try:
            target = str(j["->t->"])
        except KeyError:
            try:
                d.stack_type = StackType.FUNCTION
                target = str(j["f()"])
            except KeyError:
                try:
                    d.pushes_to_stack = False
                    d.is_external = True
                    target = str(j["x()"])
                except KeyError:
                    try:
                        d.is_external = False
                        target = str(j["->"])
                    except KeyError as e:
                        del d
                        raise e
        if "var" in j: d.variable_divert_name = target
        else: d.target_path_str = target
        try:
            d.ext_args = j["exArgs"]
        except KeyError:
            pass
        return d
    except KeyError:
        pass

    # Choice
    try:
        ch = ChoicePoint()
        ch.path_str = str(j["*"])
        try:
            ch.flags = j["flg"]
        except KeyError:
            pass
        return ch
    except KeyError:
        pass

    # Var Ref
    try:
        return VarRef(str(j["VAR?"]))
    except KeyError:
        pass
    try:
        rc = VarRef()
        rc.path_str_for_count = str(j["CNT?"])
        return rc
    except KeyError:
        pass

    # Var Assign
    try:
        globl = True
        try:
            vname = j["VAR="]
        except KeyError:
            try:
                vname = j["temp="]
                globl = False
            except KeyError as e:
                raise e
        vass = VarAssign(vname, "re" not in j)
        vass.is_global = globl
        return vass
    except KeyError:
        pass

    # Tag
    try:
        return Tag(j["#"])
    except KeyError:
        pass

    # List Value
    try:
        rawl = InkList()
        try:
            rawl.set_initial_orgnames(str(n) for n in j["origins"])
        except KeyError:
            pass
        try:
            for n, v in j["list"].items():
                rawl._add(InkListItem(n), v)
        except KeyError as e:
            del rawl
            raise e
        return ListValue(rawl)
    except KeyError:
        pass

    # Save State orgchoicepath
    try:
        return jobj_to_choice(j)
    except KeyError:
        pass

    return j


def jobj_to_ldef(j):
    alld = []
    for k, v in j.items():
        alld.append(ListDef(k, v))
    return ListDefOrigin(alld)


def jobj_to_object(j):
    j.update({n: jtok_to_inkpy(t) for n, t in j.items()})
    return jobj_to_inkpy(j)
