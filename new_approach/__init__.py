
from dataclasses import dataclass
from typing import Any, Union, Generator, Optional, Literal, TypeVar
from .util import is_cjk

# prefix components:
_space =  '   '
_branch = '│  '
# pointers:
_tee =    '├──'
_last =   '└──'

def _visual_len(s:str)->int:
    return sum(2 if is_cjk(c) else 1 for c in s)

HeadType = Literal['initial','final']

@dataclass
class ViewOptions:
    folded: bool

    @staticmethod
    def default() -> 'ViewOptions':
        return ViewOptions(
            folded = False
        )

@dataclass
class _Pos_in_treestr():
    left: tuple[int,int]
    head: tuple[int,int]
    comp: tuple[int,int]

class Tree:
    left: 'Union[str,Tree]'
    head: str
    comp: 'Union[str, Tree]'
    parent: 'Optional[Tree]' = None
    head_type: HeadType = 'initial'
    
    viewOptions: ViewOptions = ViewOptions.default()

    def __setattr__(self, name: str, value: Any) -> None:
        super().__setattr__(name,value)
        if name in ['comp','left'] and isinstance(value,Tree):
            value.parent = self

    def __init__(self,l: 'Optional[Union[str,Tree]]' = None
                     ,h: Optional[str] = None
                     ,c: 'Optional[Union[str,Tree]]' = None
                     ,*
                     ,head_type: Literal['initial', 'final'] = 'initial'
                     ,left: 'Optional[Union[str,Tree]]' = None
                     ,head: Optional[str] = None
                     ,comp: 'Optional[Union[str,Tree]]' = None
                     ):
        """
        The constructor can only be used in two ways: 
        1. `Tree(l,h,c)` when `head_type='initial`
        2. `Tree(left=.., head=.., comp=..)`
        Two methods cannot be mixed.
        """
        if (not (l is None or h is None or c is None))\
           and (left is None and head is None and comp is None)\
           and head_type=='initial':
            #Tree(left,head,comp) when head_type=='initial'
            #DOES NOT ACCEPT Tree(l,h,c, head_type='final')
            self.left, self.head, self.comp = l, h, c
        elif (l is None and h is None and c is None)\
             and (not (left is None or head is None or comp is None)):
            #Tree(head=...,left=...,comp=..., head_type=...)
            self.left, self.head, self.comp = left, head, comp
        else:
            raise Exception('Wrong use of the Tree constructor. ')

    def __repr__(self) -> str:
        if isinstance(self.left, Tree):
            leftstr = f"{type(self.left).__name__}[{self.left.head}]"
        else:
            leftstr = self.left

        if isinstance(self.comp, Tree):
            compstr = f"{type(self.comp).__name__}[{self.comp.head}]"
        else:
            compstr = self.comp

        if self.head_type == 'initial':
            return f"{type(self).__name__}(left={leftstr}"\
                                        f",head={self.head}"\
                                        f",comp={compstr})"
        else:
            return f"{type(self).__name__}(left={leftstr}"\
                                        f",comp={compstr}"\
                                        f",head={self.head})"

    def __print_directory_style(self, prefix: str="") -> Generator[str,None,None]:

        left_content = "left:" + (type(self.left).__name__ + f"[{self.left.head}]" 
                                   if isinstance(self.left, Tree)
                                   else f"\"{self.left}\"")
        yield prefix + _tee + left_content
        if isinstance(self.left, Tree): 
            yield from self.left.__print_directory_style(prefix = prefix + _branch + "     ") 
        
        comp_content = "comp:" + (type(self.comp).__name__ + f"[{self.comp.head}]" 
                                   if isinstance(self.comp, Tree)
                                   else f"\"{self.comp}\"")
        yield prefix + _last + comp_content
        if isinstance(self.comp, Tree): 
            yield from self.comp.__print_directory_style(prefix = prefix + _space + "     ") 

    def print_directory_style(self) -> str:
        return (f"{type(self).__name__}[{self.head}]\n"+
                "\n".join(list(self.__print_directory_style()))
               )

    __cache_horizontal_str_array: list[list[str]] = []
    __pos_in_treestr: _Pos_in_treestr = _Pos_in_treestr((-1,-1),(-1,-1),(-1,-1))
    __str_array_needs_redrawn: bool = True
    def __print_horizontal(self, str_offset:int=0) -> list[list[str]]:
        ...
        #top branch

        #middle branch

        #bottom branch
        if type(self.comp) is str:
            ...

    def __str__(self) -> str:
        return self.print_directory_style()
    def pprint(self):
        print(self.print_directory_style())


## the algorithm is taken from https://stackoverflow.com/questions/9727673/list-directory-tree-structure-in-python
# def tree(dir_path: Path, prefix: str=''):
#     contents = list(dir_path.iterdir())
#     # contents each get pointers that are ├── with a final └── :
#     pointers = [tee] * (len(contents) - 1) + [last]
#     for pointer, path in zip(pointers, contents):
#         yield prefix + pointer + path.name
#         if path.is_dir(): # extend the prefix and recurse:
#             extension = branch if pointer == tee else space 
#             # i.e. space because last, └── , above so no more |
#             yield from tree(path, prefix=prefix+extension)

class VP(Tree):
    pass
class ClsP(Tree):
    pass
class NP(Tree):
    pass
"""
example:

VP[吃]
├──left:他
└──comp:ClsP[五碗]
        ├──left:""
        └──comp:NP[飯]
                ├──left:""
                └──comp:""

                
                 ┌────""
         ┌─NP────┴───飯
         │  └─......
 ┌─ClsP─五碗
 │  └─""
VP───吃
 └─他
                 ┌────comp:""
         ┌─NP────┴───head:飯
         │  └─left:......
 ┌─ClsP─head:五碗
 │  └─left:""
VP───head:吃
 └─left:他
               

# full NP

              ┌──""
         ┌──N'┴─飯
    ┌──N'──香香的
 ┌─N'─軟軟的
NP──""
              ┌──comp:""
         ┌──N'┴────N:飯
    ┌──N'┴─adjt:香香的
 ┌─N'─adjt:軟軟的
NP──spec:""

       ┌───────""
NP─────┴──────飯
 └─軟軟的,香香的
       ┌───────comp:""
NP─────┴──────head:飯
 └─left:軟軟的,香香的

# AspP example and movement

input = "被騙了五千元"

        ┌────────────────────────了
        │              ┌─◁ 五千元
        │       ┌──VP──┴─騙
        │       │   └─""
  ┌─AspP┴LightVP┴被
  │  │    └─""
  │  └─""
IP─""
 └─""

                       ┌─◁ 五千元
        ┌─了           │
        │       ┌──VP──┴─騙
        │       │   └─""
  ┌─AspP┴LightVP┴被
  │  │    └─""
  │  └─""
IP─""
 └─""





"""



ex1 = VP(head = "吃"
        ,left = "他"
        ,comp = ClsP(head = "五碗"
                    ,left = ""
                    ,comp = NP(head = "飯"
                              ,left = ""
                              ,comp = ""  
                              )
                    )
        )

class CP(Tree):...
class TP(Tree):...
class AspP(Tree):...
class LightVP(Tree):...
class VP(Tree):...
class ClsP(Tree):...
class NP(Tree):...

# 我昨天吃了五碗飯
ex2 = CP(left='',
   head='∅',
   comp=TP(left='',
           head='∅',
           comp=AspP(left='<ENTITY_pronoun>我</ENTITY_pronoun><TIME_day>昨天</TIME_day>',
                     head='<ASPECT>了</ASPECT>',
                     comp=LightVP(left='',
                                  head='∅',
                                  comp=VP(left='',
                                          head='<ACTION_verb>吃</ACTION_verb>',
                                          comp=ClsP(left='',
                                                    head='<ENTITY_classifier>五碗</ENTITY_classifier>',
                                                    comp=NP(left='',
                                                            head='<ENTITY_nouny>飯</ENTITY_nouny>',
                                                            comp='')))))))


"""
# 我昨天吃了五碗飯
expected print:

                                      ┌─""
                                 ┌─NP─┴飯
                                 │  └─""
                           ┌─ClsP┴五碗
                           │  └─""
              ┌─了         │
              │       ┌─VP─┴吃
              │       │  └─""
        ┌─AspP┴LightVP┴ø
        │  │    └─""
        │  └─我昨天
   ┌─TP─┴ø
   │  └─""
CP─┴ø
 └─""

                             ┌─ClsP◁ 五碗飯
                        ┌─VP─┴吃
                        │  └─""
                ┌LightVP┴ø
                │ └─""
        ┌─AspP──┴─了
        │  └─我昨天
   ┌─TP─┴ø
   │  └─""
CP─┴ø
 └─""

 
Apply EPP movement

                           ┌─ClsP◁ 五碗飯
              ┌─了         │
              │       ┌─VP─┴吃
        ┌─AspP┴LightVP┴ø
        │  │    └─""
        │  └─[]昨天
   ┌─TP─┴ø   ║
   │  └─我 <═╝
CP─┴ø
 └─""

then apply verb raising

                           ┌─ClsP◁ 五碗飯
              ┌─吃了 <══════╪╗
              │       ┌─VP─┴[]
        ┌─AspP┴LightVP┴ø
        │  │    └─""
        │  └─[]昨天
   ┌─TP─┴ø   ║
   │  └─我 <═╝
CP─┴ø
 └─""


 

 備案:
                 ┌─ClsP◁ 五碗飯
    ┌─了         │
    │       ┌─VP─┴吃
    │       │  └─""
AspP┴LightVP┴ø
 │    └─""
 └─我昨天





"""


def swap(t1:Tree, field1:str, t2:Tree, field2:str):
    temp = t1.__dict__[field1]
    t1.__dict__[field1] = t2.__dict__[field2]
    t2.__dict__[field2] = temp

if __name__ == '__main__':
    pass