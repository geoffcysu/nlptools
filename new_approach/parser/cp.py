import re
from typing import List, Generic, TypeVar
from util import split_pos
from ..new_treedata import BinTree
from .xbar import XP


c_pattern: re.Pattern = re.compile(
    "((?<!</ACTION_verb>)(?<!</FUNC_inner>)<ASPECT>了</ASPECT>$" 
        #「了」前面不能有ACTION_verb,FUNC_inner
        "|<(?P<clause>CLAUSE_(particle|YesNoQ))>.+?</(?P=clause)>"
        #CLAUSE_x 前後要一致
    ")"
    )


class Cbar(BinTree):
    pass

class CP(XP[Cbar]):
    @classmethod
    def left_fold(cls, lst: List[str | BinTree])-> str | BinTree:
        return lst[0] if len(lst)>0 else "∅"

def parse_CP(src: str) -> CP:
    split = split_pos(c_pattern, src)
    if split is None:
        return CP(left = []
                  ,head = "∅"
                  ,comp = parseSTR
                  )
    else: 
        return CP(left=split_left(split[2])
                  , head=split[1]
                  , comp=split[0]
                  )


# def CP(left: List[BinTree | str],
#        head: str,
#        comp: str | BinTree
#        ) -> BinTree:
#     pass