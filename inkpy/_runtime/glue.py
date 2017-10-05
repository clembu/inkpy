from .object import Object
from enum import Enum


class GlueType(Enum):
    BI = 0
    LEFT = 1
    RIGHT = 2


class Glue(Object):
    def __init__(self, gtype):
        self.glue_type = gtype

    @property
    def glue_type(self):
        return self.__glue_type

    @glue_type.setter
    def glue_type(self, value):
        if not isinstance(value, GlueType): raise TypeError
        self.__glue_type = value

    @property
    def is_bi(self):
        return self.glue_type == GlueType.BI

    @property
    def is_left(self):
        return self.glue_type == GlueType.LEFT

    @property
    def is_right(self):
        return self.glue_type == GlueType.RIGHT

    def __str__(self):
        if self.is_bi: return "BidirGlue"
        if self.is_left: return "LeftGlue"
        if self.is_right: return "RightGlue"
        return "UnexpectedGlueType"
