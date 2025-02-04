
from dataclasses import dataclass
from typing import Union,Callable,TypeVar,Optional, Literal

import treeart


@dataclass
class BinTree:
    label:str
    l: 'str | BinTree'
    r: 'str | BinTree'
    def __repr__(self)->str:
        return f"{self.label}({self.l},{self.r})"
    

    def pstr(self)-> str:
        def f(t:BinTree)->str:
            left = f(t.l) if type(t.l) is BinTree else t.l
            right = f(t.r) if type(t.r) is BinTree else t.r
            return treeart.binary_edge(t.label,left,right,align='center')
        return f(self)
    def pprint(self)-> None:
        print(self.pstr())


ex = BinTree('NP','SPEC', BinTree('N\'','N','comp'))

# ex1 = VP(head = "吃"
#         ,left = ["他"]
#         ,comp = ClsP(head = "五碗"
#                     ,left = [""]
#                     ,comp = NP(head = "飯"
#                               ,left = [""]
#                               ,comp = ""  
#                               )
#                     )
#         )
