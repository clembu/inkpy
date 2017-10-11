from enum import Enum
from .object import Object


class CmdType(Enum):
    NOT_SET = -1
    EVAL_START = 0
    EVAL_OUTPUT = 1
    EVAL_END = 2
    DUPLICATE = 3
    POP_VALUE = 4
    POP_FUN = 5
    POP_TUNNEL = 6
    BEGIN_STR = 7
    END_STR = 8
    NO_OP = 9
    CHOICE_COUNT = 10
    TURNS_SINCE = 11
    READ_COUNT = 12
    RANDOM = 13
    SEED_RANDOM = 14
    VISIT_IDX = 15
    SQ_SHUFFLE_IDX = 16
    START_THREAD = 17
    DONE = 18
    END = 19
    LIST_FROM_INT = 20
    LIST_RANGE = 21


class Cmd(Object):
    def __init__(self, ctype=CmdType.NOT_SET):
        super().__init__()
        self._ctype = ctype

    @property
    def cmd_type(self):
        return self._ctype

    def copy(self):
        return Cmd(self._ctype)

    def __str__(self):
        return (str(self._ctype)).split('.')[1]

    @staticmethod
    def EVAL_START():
        return Cmd(CmdType.EVAL_START)

    @staticmethod
    def EVAL_OUTPUT():
        return Cmd(CmdType.EVAL_OUTPUT)

    @staticmethod
    def EVAL_END():
        return Cmd(CmdType.EVAL_END)

    @staticmethod
    def DUPLICATE():
        return Cmd(CmdType.DUPLICATE)

    @staticmethod
    def POP_VALUE():
        return Cmd(CmdType.POP_VALUE)

    @staticmethod
    def POP_FUN():
        return Cmd(CmdType.POP_FUN)

    @staticmethod
    def POP_TUNNEL():
        return Cmd(CmdType.POP_TUNNEL)

    @staticmethod
    def BEGIN_STR():
        return Cmd(CmdType.BEGIN_STR)

    @staticmethod
    def END_STR():
        return Cmd(CmdType.END_STR)

    @staticmethod
    def NO_OP():
        return Cmd(CmdType.NO_OP)

    @staticmethod
    def CHOICE_COUNT():
        return Cmd(CmdType.CHOICE_COUNT)

    @staticmethod
    def TURNS_SINCE():
        return Cmd(CmdType.TURNS_SINCE)

    @staticmethod
    def READ_COUNT():
        return Cmd(CmdType.READ_COUNT)

    @staticmethod
    def RANDOM():
        return Cmd(CmdType.RANDOM)

    @staticmethod
    def SEED_RANDOM():
        return Cmd(CmdType.SEED_RANDOM)

    @staticmethod
    def VISIT_IDX():
        return Cmd(CmdType.VISIT_IDX)

    @staticmethod
    def SQ_SHUFFLE_IDX():
        return Cmd(CmdType.SQ_SHUFFLE_IDX)

    @staticmethod
    def START_THREAD():
        return Cmd(CmdType.START_THREAD)

    @staticmethod
    def DONE():
        return Cmd(CmdType.DONE)

    @staticmethod
    def END():
        return Cmd(CmdType.END)

    @staticmethod
    def LIST_FROM_INT():
        return Cmd(CmdType.LIST_FROM_INT)

    @staticmethod
    def LIST_RANGE():
        return Cmd(CmdType.LIST_RANGE)
