from typing import Generic, TypeVar, List
from ..new_treedata import BinTree


# class Bar_config(type):
#     def __new__(cls, name, bases, class_dict, bar=None):
#         if bar is None:
#             raise TypeError(f"{name} must specify a bar argument (the XBar class).")
        
#         if not isinstance(bar, type):
#             raise TypeError(f"{name}: bar must be a type, got {type(bar).__name__}")

#         if not issubclass(bar, BinTree):
#             raise TypeError(f"{name}: bar must be a subclass of BinTree.")

#         class_dict["_bar"] = bar  # Store the required type
#         return super().__new__(cls, name, bases, class_dict)

BarType = TypeVar('BarType', bound=BinTree)

class XP(BinTree, Generic[BarType]):
    # _bar: type[BinTree]

    @classmethod
    def left_fold(cls,lst: List[str | BinTree])-> str | BinTree:
        """
        The implementation of how the left list is to be constructed as a tree
        varies across different P.
        """
        raise Exception(f"The left_fold method of {cls.__name__} lacks implementation.")

    def __init__(self,
                 left: List[str | BinTree],
                 head: str,
                 comp: str | BarType):
        self.l = type(self).left_fold(left)
        self.label = head
        self.r = comp