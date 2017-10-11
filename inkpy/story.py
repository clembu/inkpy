from io import IOBase
from ._runtime import Story as RStory, InkList as RInkList, Path as RPath
from .choice import Choice
from .inklist import InkList
from .js import dec
import json


class Story:

    # Constructor
    def __init__(self, file_):
        if isinstance(file_, str):
            closefile = True
            file_ = open(file_, encoding='utf-8-sig')
            # create from file path
        elif isinstance(file_, IOBase):
            pass
            # create from readable stream
        else:
            raise TypeError(
                "Cannot create story from {0} type".format(type(file_)))
        jtree = json.load(
            file_,
            object_hook=dec.jobj_to_object,
            parse_float=dec.decode_num,
            parse_int=dec.decode_num)
        if closefile: file_.close()
        self.__s = RStory(jtree["root"], jtree.get("listDefs"))

    # Properties
    @property
    def can_continue(self):
        return self.__s.state.can_continue

    @property
    def choices(self):
        return [Choice(c=c) for c in self.__s.choices]

    @property
    def text(self):
        return self.__s.state.text

    @property
    def tags(self):
        return self.__s.state.tags

    @property
    def gtags(self):
        return self.__s.gtags

    @property
    def has_errors(self):
        return self.__s.state.has_errors

    @property
    def errors(self):
        return self.__s.state.current_errors

    # Specials
    def __getitem__(self, vname):
        v = self.__s.state.lexenv[vname]
        if isinstance(v, RPath): v = str(v)
        elif isinstance(v, RInkList): v = InkList(l=v)
        return v

    def __setitem__(self, vname, v):
        if isinstance(v, InkList): v = v._l
        if isinstance(v, str):
            try:
                v = RPath(v)
            except:
                pass
        self.__s.state.lexenv[vname] = v

    # Methods
    def continue_(self, max_=False):
        return self.__s.continue_(max_)

    def choose(self, idx):
        self.__s.choose(idx)

    def goto(self, path):
        self.__s.goto(path)

    def tagsat(self, path):
        return self.__s.tagsat(path)

    def save(self, file_):
        raise NotImplementedError

    def load(self, file_):
        raise NotImplementedError

    def reset(self):
        self.__s.reset()

    def force_end(self):
        self.__s.state.force_end()

    def watch(self, var, f):
        self.__s.watch(var, f)

    def unwatch(self, f):
        self.__s.unwatch(f)

    def bindfun(self, fname, f):
        self.__s.bindfun(fname, f)

    def unbindfun(self, fname):
        self.__s.unbindfun(fname)

    def inklist(self, lname):
        return RInkList.from_story(self.__s)
