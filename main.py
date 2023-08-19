from ArticutAPI import Articut
import json
import re
import pprint as pp
import parsy
from typing import Optional, TypeVar, Generic, Literal, Union
from itertools import chain, starmap
from functools import partial
from dataclasses import dataclass
from collections.abc import Sequence, Callable, Iterable


username = ""
apikey   = ""

with open('DROIDTOWN.json') as f:
    try:
        r = json.load(f)
        username = r["username"]
        apikey = r["key"]
    except:
        raise Exception("Please fill the DROIDTOWN.json file (an object with \"username\" and \"key\" fields).)")

articut = Articut(username, apikey)

inputSTR = "戴克斯的原始版本僅適用於找到兩個頂點之間的最短路徑"
# resultDICT = articut.parse(inputSTR, level="lv2")
# #pp.pprint(resultDICT)
# with open("sample.json", "w",encoding='utf-8') as outfile:
#     json.dump(resultDICT, outfile, ensure_ascii=False, indent=4)

resultDICT = {}
with open('sample.json','r+') as f:
    resultDICT = json.load(f)


class Token:
    pos : str
    text : str
    def __init__(self,pos:str,text:str):
        self.pos = pos
        self.text = text
    def __str__(self):
        return f'Token({self.pos},{self.text})'
    def __repr__(self):
        return str(self)

class Tree:
    label : str
    left  : Optional['Tree']
    right : Optional['Tree']
    def __init__(self,label:str, left:Optional['Tree'], right:Optional['Tree']):
        self.label = label
        self.left = left
        self.right = right
    def __repr__(self):
        return f"Tree({self.label},left:{str(self.left)},right:{str(self.right)})"


def posToken(pos:str):
    return (parsy.string(f'<{pos}>') 
            >> parsy.regex(r'[^<]*') 
            << parsy.string(f'</{pos}>')).map(lambda x:Token(pos,x))

def optParser(parser:Optional[parsy.Parser]):
    if parser is None:
        return parsy.success(None)
    else:
        return parser

def phrase(name:str,left:Optional[parsy.Parser]=None,right:Optional[parsy.Parser]=None):
    return parsy.seq( optParser(left)
                    , optParser(right) 
                    ).combine(lambda l,r:Tree(name,l,r))


# t phrasal rule: <t1>aaa</t1><t2>bbb</t2> (let t2 be optional)

tt = phrase( 't'
           , posToken('t1')  
           , posToken('t2').optional())

# recursion: <cons>xxx</cons><cons>ggg</cons><nil>hhh</nil>


class RoseTree:
    _children:list['RoseTree']
    def __init__(self,content,*args:'RoseTree'):
        self.content = content
        self._children = list(args)
    @property
    def children(self):
        return self._children
    # @property
    # def content(self):
    #     return self._content
    # @content.setter
    # def content(self,content):
    #     assert type(self.content) == type(content), "Cannot change the content type of a tree"
    

# use this string method: string.ljust(width, fillchar)    
# >>> words = ['this', 'is', 'a', 'sentence']
# >>> '-'.join(words)
sample1 = RoseTree('P',
    RoseTree('P1', 
        RoseTree('1'),
        RoseTree('2')),
    RoseTree('P2',
        RoseTree('3')),
    RoseTree('P3',
        RoseTree('P4', 
            RoseTree('4'),
            RoseTree('P5',
                RoseTree('5'),
                RoseTree('6'))),
        RoseTree('7')
    )
)
# P___P1____1
# |   |_____2
# |___P2____3
# |___P3___P4___4
#     |    |____P5___5
#     |         |____6
#     |____7


# P___P1_____________1 : P P1 1        ctx: [(P,'|'), (P1,'|')] -> 
# |   |______________2 : ? |_2         ctx: [(P,'|'), '|']
# |___P2_____________3 : | P2_3
# |___P3___P4________4 : | P3_P4_4
#     |    |____P5___5 : ? ?  |_P5_5   -> passing the context of P:' ',P3:'|'
#     |         |____6 : ? ? ? |_6
#     |______________7 : ? |_7

# @adt
# class ParentInfo:
#     HEAD: Case[str]
#     MIDDLE: Case
#     END:Case
# PI = ParentInfo

# T = TypeVar('T')
# @adt
# class LList(Generic[T]):
#     NIL: Case
#     CONS: Case[T, 'LList[T]']
# nil = LList.NIL
# cons = LList.CONS

NodeInfo = str
#[MID],[END],or the label of the node
_MID = "[MID]"
_END = "[END]"

@dataclass
class Context:
    nodeInfo : NodeInfo
    padding : int

T = TypeVar('T')
def rindex(pred:Callable[[T],bool],l:Sequence[T])->int:
    for i in range(len(l)-1, -1, -1): # Iterating index in reverse order.
        if pred(l[i]):
            return i
    return -1

def strParseTree(tree:RoseTree, indent=0, alignLeaves=0, layerLength=6)->str:
    def collectPathInfos(t:RoseTree,ctxs=[])->list[tuple[list[Context],str]]:
        if len(t.children)==0:
            return [(ctxs,str(t.content))]
        else:
            padding = 0 if len(tree.content)<layerLength else len(tree.content)+1
            head = collectPathInfos(t.children[0], ctxs+[Context(str(t.content), padding)])
            middles = list(chain(*map( partial(collectPathInfos,ctxs=ctxs+[Context(_MID,padding)])
                                     , t.children[1:-1])))
            last= collectPathInfos(t.children[-1], ctxs+[Context(_END,padding)]) if len(t.children)>1 else []
            return head + middles + last
    pathInfos = collectPathInfos(tree)

    def renderLeaf(ctxs:list[Context], leafContent:str)->Iterable[str]:
        # The rule for horz: scan from right, horz line stops at first non-HEAD (MID or END).
        # The rules for vert: only when END should it be " " except the next ctx is HEAD, otherwise "|".
        
        # horz-rule: splitting
        splitIndex = rindex(lambda x:x.nodeInfo in [_MID,_END],ctxs)
        splitIndex = 0 if splitIndex==-1 else 0 
        #splitIndex==-1 means no non-head, so every segment should be rendered with horz line.

        # vert-rule
        def vertSymb(i:int)->str:
            if ctxs[i].nodeInfo not in [_MID,_END]:
                return ctxs[i].nodeInfo
            elif ctxs[i].nodeInfo==_END and\
                ((i+1<len(ctxs) and (ctxs[i+1].nodeInfo in [_MID,_END]))
                 or i+1==len(ctxs)):
                return " "
            else:
                return "|"
        return (*(vertSymb(i).ljust(layerLength+ctxs[i].padding," ") for i in range(0,splitIndex))
               ,*(vertSymb(i).ljust(layerLength+ctxs[i].padding,"_") for i in range(splitIndex,len(ctxs)))
               ,leafContent
               ,'\n'
               )
    return ''.join(chain(*starmap(renderLeaf,pathInfos)))

        


# supposed treetype: 
# def strParseTree(tree:TreeLike, indent=0, padding=0, alignLeaves=0, layerLength=6)->list[str]:
#     if len(tree.children)==0:
#         return [str(tree.content)]
#     else:
#         contLen = len(tree.content)
#         # padding = contLen-layerLength+1 if contLen>=layerLength else padding
#         #         # +1 is an additional "_" character to separate parent and child nodes
#         childrenStr = [strParseTree(i, indent=indent+1) for i in tree.children]

#         contentStr = str(tree.content).ljust(layerLength, '_')
#         if contLen>=layerLength:
#             contentStr+='_'
#         r_firstLine:str = contentStr + childrenStr[0][0]

#         def prepending(vertBar:bool):


#         localPaddingForFirstChild = (' ' if len(childrenStr)<2 else '|').ljust(layerLength,'_')
#         r_firstChildsLines:list[str] = [
#             ' '*indent*layerLength + localPaddingForFirstChild + firstChildsChild
#             for firstChildsChild in childrenStr[0]
#         ]

#         r_middleChildrenLines:list[str] = list(itertools.chain(*[
#             ['a','b']
#             for middleChild in childrenStr[1:-1]
#         ]))

#         r_lastChildsLines:list[str]


        # Another way of doing this: use DFS order to fetch each node's information, 
        # then format each line at once (in a single loop).
        # I guess this could reduce string manipulations, which make the method more efficient.

