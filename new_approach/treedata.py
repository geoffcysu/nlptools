from dataclasses import dataclass
from horz_print import render_block, HorzPrint_conf
from typing import Literal, Union, Optional, Generator, Any


# prefix components:
_space =  '   '
_branch = '│  '
# pointers:
_tee =    '├──'
_last =   '└──'


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
    
    def _leaf_num(self) -> int:
        # practicing doing this without recursion
        counter = 0
        stack:list[Tree] = [self]
        while stack:
            t = stack.pop()
            counter += 1 # count on head
            if isinstance(t.left, Tree):
                stack.append(t.left)
            else:
                counter += 1 # count on string left
            if isinstance(t.comp, Tree):
                stack.append(t.comp)
            else:
                counter += 1 # count on string comp
        return counter
            



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

    def str_directory_style(self) -> str:
        return (f"{type(self).__name__}[{self.head}]\n"+
                "\n".join(list(self.__print_directory_style()))
               )

    __pos_in_treestr: _Pos_in_treestr = _Pos_in_treestr((-1,-1),(-1,-1),(-1,-1))
    _horzPrint_conf: HorzPrint_conf = HorzPrint_conf()
    def _horizontal_strarray(self, str_offset:int=0) -> list[str]:
        if self._horzPrint_conf.cache:
            return self._horzPrint_conf.cache
        else:
            return render_block(self, self._horzPrint_conf)
    
    def str_horizontal_tyle(self)->str:
       return '\n'.join(self._horizontal_strarray())


    def __str__(self) -> str:
        # return self.str_directory_style()
        return self.str_horizontal_tyle()
    def pprint(self):
        print(self.str_directory_style())


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

class CP(Tree):...
class TP(Tree):...
class AspP(Tree):...
class LightVP(Tree):...
class VP(Tree):...
class ClsP(Tree):...
class NP(Tree):...