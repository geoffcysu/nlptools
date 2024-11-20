from dataclasses import dataclass
from misc import is_cjk
from treedata import Tree
from typing import Union, Optional

def _visual_len(s:str)->int:
    return sum(2 if is_cjk(c) else 1 for c in s)

@dataclass
class HorzPrint_conf():
    cache: Optional[list[list[str]]] = None
    def clear_cache(self)->None:
        self.cache = None

# concepts that need explainations:
# - tree block: the block of string starting from "XP" to the end of the
#               string of the deepest subtree,
#               and all the branches inside XP
#   == str_array
# - str_offset: offset starting from the start of the tree block
# - branch: the "XP" tree name and the connection branches (the └─┌ symbols)
def render_block(input:Union[str, Tree], horzPrint_conf: HorzPrint_conf) \
                -> list[list[str]]:
    if type(input) is str:
        return [[input]]
    elif isinstance(input, Tree):
        if input._horzPrint_conf.cache:
            return input._horzPrint_conf.cache
        top_subtree = input.comp if input.head_type == 'initial' \
                                else input.head
        middle_subtree = input.head if input.head_type == 'initial' \
                                   else input.comp
        #bottom tree block
        # The bottom tree block always has enough space, and the offset for 
        # deeper tree blocks should be calculated here.
        # Information needed to be calculated:
        # - string length
        # - stem (the "XP" part of the branch) position (a coordinate on str_array)
        
    else:
        raise TypeError("Unexpected input in render_block.")