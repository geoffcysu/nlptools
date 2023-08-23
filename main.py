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

#inputSTR = "戴克斯的原始版本僅適用於找到兩個頂點之間的最短路徑"
inputSTR= '蓼葉堇菜（學名：）是堇菜科堇菜屬的植物。分布在朝鮮以及中國大陸的吉林等地，生長於海拔650米至900米的地區，一般生長在山地疏林中，目前尚未由人工引種栽培。'
# resultDICT = articut.parse(inputSTR, level="lv2")

# pp.pprint(articut.getVerbStemLIST(resultDICT))
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

class RoseTree:
    _children:list['RoseTree']
    def __init__(self,content,*args:'RoseTree'):
        self.content = content
        self._children = list(args)
    @property
    def children(self):
        return self._children

class SyntaxTreeParentAssignmentError(Exception):
    pass

class SyntaxTree(RoseTree):
    _content : Union[str,Token]
    _children : list['SyntaxTree']
    _parent : Optional['SyntaxTree']
    _parent_is_setable:int
    def __init__(self,content:str, children:list['SyntaxTree'] = [], parent:Optional['SyntaxTree'] = None):
        self._content = content
        self._children = children
        self._parent = parent
        _parent_is_setable = True if parent is None else False
    @property
    def content(self):
        return self._content
    @property
    def children(self):
        return self._children
    @property
    def parent(self):
        return self._parent
    @parent.setter
    def parent(self, newParent):
        if self._parent_is_setable:
            self._parent = newParent
            self._parent_is_setable = False
        else:
            raise SyntaxTreeParentAssignmentError("A syntaxTree can only be assigned to a parent once.")

    def addChild(self,child:'SyntaxTree'):
        self._children.append(child)
        child.parent = self
    def addChildren(self,children:list['SyntaxTree']):
        for child in children:
            self.addChild(child)
    def __repr__(self):
        return f"Tree({self.content},{self._children})"


def posToken(pos:str):
    tokenParser = (parsy.string(f'<{pos}>') 
                >> parsy.regex(r'[^<]*') 
                << parsy.string(f'</{pos}>')).map(lambda x:Token(pos,x))
    return tokenParser.map(lambda t:SyntaxTree(t))

# def optParser(parser:Optional[parsy.Parser]):
#     if parser is None:
#         return parsy.success(None)
#     else:
#         return parser

def phrase(name:str,*subs:parsy.Parser):
    def f(*subs):
        nsubs = list(filter(lambda x:x is not None, subs))
        return SyntaxTree(name,nsubs)
    return parsy.seq(*subs).combine(f)


# t phrasal rule: <t1>aaa</t1><t2>bbb</t2> (let t2 be optional)

tt = phrase( 't'
           , posToken('t1')  
           , posToken('t2').optional())

# recursion: <cons>xxx</cons><cons>ggg</cons><nil>hhh</nil>



    

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



# NodeInfo = str
# #[MID],[END],or the label of the node
# _MID = "[MID]"
# _END = "[END]"

# @dataclass
# class Context:
#     nodeInfo : NodeInfo
#     padding : int

T = TypeVar('T')
def rindex(pred:Callable[[T],bool],l:Sequence[T])->int:
    for i in range(len(l)-1, -1, -1): # Iterating index in reverse order.
        if pred(l[i]):
            return i
    return -1

# def strParseTree(tree:RoseTree, indent=0, alignLeaves=0, layerLength=6)->str:
#     def collectPathInfos(t:RoseTree,ctxs=[])->list[tuple[list[Context],str]]:
#         if len(t.children)==0:
#             return [(ctxs,str(t.content))]
#         else:
#             padding = 0 if len(tree.content)<layerLength else len(tree.content)+1
#             head = collectPathInfos(t.children[0], ctxs+[Context(str(t.content), padding)])
#             middles = list(chain(*map( partial(collectPathInfos,ctxs=ctxs+[Context(_MID,padding)])
#                                      , t.children[1:-1])))
#             last= collectPathInfos(t.children[-1], ctxs+[Context(_END,padding)]) if len(t.children)>1 else []
#             return head + middles + last
#     pathInfos = collectPathInfos(tree)

#     def renderLeaf(ctxs:list[Context], leafContent:str)->Iterable[str]:
#         # The rule for horz: scan from right, horz line stops at first non-HEAD (MID or END).
#         # The rules for vert: only when END should it be " " except the next ctx is HEAD, otherwise "|".
        
#         # horz-rule: splitting
#         splitIndex = rindex(lambda x:x.nodeInfo in [_MID,_END],ctxs)
#         splitIndex = 0 if splitIndex==-1 else splitIndex
#         #splitIndex==-1 means no non-head, so every segment should be rendered with horz line.
#         print(leafContent)
#         print(ctxs)
#         # vert-rule
#         def vertSymb(i:int,printHead:bool)->str:
#             if printHead and ctxs[i].nodeInfo not in [_MID,_END]:
#                 return ctxs[i].nodeInfo
#             elif ctxs[i].nodeInfo==_END and\
#                  i+1<len(ctxs) and (ctxs[i+1].nodeInfo in [_MID,_END]):
#                 return " "
#             else:
#                 return "|"
#         return (*(vertSymb(i,False).ljust(layerLength+ctxs[i].padding," ") for i in range(0,splitIndex))
#                ,*(vertSymb(i,True).ljust(layerLength+ctxs[i].padding,"_") for i in range(splitIndex,len(ctxs)))
#                ,leafContent
#                ,'\n'
#                )
#     return ''.join(chain(*starmap(renderLeaf,pathInfos)))

        


# def strParseTree(tree:RoseTree, indent=0, padding=0, alignLeaves=0, layerLength=6): #->list[str]
#     def collectInfo
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

