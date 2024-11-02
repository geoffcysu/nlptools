
from dataclasses import dataclass
from typing import Any, Union, Generator, Optional

# prefix components:
_space =  '   '
_branch = '│  '
# pointers:
_tee =    '├──'
_last =   '└──'

@dataclass
class Tree:
    left: 'Union[str,Tree]'
    head: str
    comp: 'Union[str,Tree]'
    parent: 'Optional[Tree]' = None

    def __setattr__(self, name: str, value: Any) -> None:
        super().__setattr__(name,value)
        if name in ['comp','left'] and isinstance(value,Tree):
            value.parent = self

        

    def __printTree(self, prefix: str="") -> Generator[str,None,None]:

        left_content = "left:" + (type(self.left).__name__ + f"[{self.left.head}]" 
                                   if isinstance(self.left, Tree)
                                   else f"\"{self.left}\"")
        yield prefix + _tee + left_content
        if isinstance(self.left, Tree): 
            yield from self.left.__printTree(prefix = prefix + _branch + "     ") 
        
        comp_content = "comp:" + (type(self.comp).__name__ + f"[{self.comp.head}]" 
                                   if isinstance(self.comp, Tree)
                                   else f"\"{self.comp}\"")
        yield prefix + _last + comp_content
        if isinstance(self.comp, Tree): 
            yield from self.comp.__printTree(prefix = prefix + _space + "     ") 


    def pstr(self) -> str:
        return (f"{type(self).__name__}[{self.head}]\n"+
                "\n".join(list(self.__printTree()))
               )
    def __str__(self) -> str:
        return self.pstr()
    def __repr__(self) -> str:
        return self.pstr()
    def pprint(self):
        print(self.pstr())


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

                
                       ┌──comp:""
        ┌────comp:N------head:飯
        │          └──left:[.........]
┌──comp:ClsP-head:五碗
│       └────left:""
VP[吃]
└──left:他
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

def swap(t1:Tree, field1:str, t2:Tree, field2:str):
    temp = t1.__dict__[field1]
    t1.__dict__[field1] = t2.__dict__[field2]
    t2.__dict__[field2] = temp

if __name__ == '__main__':
    pass