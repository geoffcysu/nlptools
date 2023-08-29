
import parsy
from typing import Optional, TypeVar, Generic, Literal, Union
from itertools import chain, starmap
from functools import partial, reduce
from collections.abc import Sequence, Callable, Iterable
from dataclasses import dataclass

_A,_B,_C = TypeVar('_A'),TypeVar('_B'),TypeVar('_C')
# function composition
def c(f:Callable[[_B],_C], g:Callable[[_A],_B])->Callable[[_A],_C]:
    return lambda x:f(g(x))

class Token:
    pos : str
    text : str
    def __init__(self,pos:str,text:str):
        self.pos = pos
        self.text = text
    def __str__(self):
        return self.pos + "___" + self.text
    def __repr__(self):
        return f'Token({self.pos},{self.text})'

class RoseTree:
    _children:list['RoseTree']
    def __init__(self,content,*args:'RoseTree'):
        self.content = content
        self._children = list(args)
    @property
    def children(self):
        return self._children
    def compactFormatStr(self, layerLength=6)->str:
        def render(tree:RoseTree)->list[str]:
            if len(tree.children)==0:
                return [str(tree.content)]
            else:
                contLen = len(tree.content)
                padding = contLen-layerLength+1 if contLen>=layerLength else 0
                        # +1 is an additional "_" character to separate parent and child nodes
                contentStr = str(tree.content).ljust(layerLength+padding, '_')
                newLayerLength = layerLength+padding

                def prependingFirstLeaf(leaf:str)->str:
                    return contentStr + leaf
                def prependingHead(leaf:str)->str:
                    return '|'.ljust(newLayerLength, '_') + leaf
                def prependingNonchildLeaf(leaf:str)->str:
                    return '|'.ljust(newLayerLength, ' ') + leaf
                def prependingEnd(leaf:str)->str:
                    return ' '.ljust(newLayerLength, ' ') + leaf
                
                def renderFirstChild(t:RoseTree)->list[str]:
                    allLeaves = render(t)
                    return [ prependingFirstLeaf(allLeaves[0])
                        , *map(prependingNonchildLeaf,allLeaves[1:])]
                def renderMiddleChildren(t:RoseTree)->list[str]:
                    allLeaves = render(t)
                    return [ prependingHead(allLeaves[0])
                        , *map(prependingNonchildLeaf,allLeaves[1:])]
                def renderLastChild(t:RoseTree)->list[str]:
                    allLeaves = render(t)
                    return [ prependingHead(allLeaves[0])
                        , *map(prependingEnd,allLeaves[1:])]
                def renderSoleChild(t:RoseTree)->list[str]:
                    allLeaves = render(t)
                    return [ prependingFirstLeaf(allLeaves[0])
                        , *map(prependingEnd,allLeaves[1:])]
                
                if len(tree.children) > 1:
                    return [ *renderFirstChild(tree.children[0])
                        , *chain(*map(renderMiddleChildren, tree.children[1:-1]))
                        , *renderLastChild(tree.children[-1])
                        ]
                else: #len(tree.children)==1
                    return renderSoleChild(tree.children[0])

        return "\n".join(render(self))


class SyntaxTree(RoseTree):
    _content : Union[str,Token]
    _children : list['SyntaxTree']
    _parent : Optional['SyntaxTree']
    def __init__(self,content:str, children:list['SyntaxTree'] = [], parent:Optional['SyntaxTree'] = None):
        self._content = content
        self._children = children
        self._parent = parent
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
        self._parent = newParent
        
    def addChild(self,child:'SyntaxTree'):
        self._children.append(child)
        child.parent = self
    def addChildren(self,children:list['SyntaxTree']):
        for child in children:
            self.addChild(child)
    def __repr__(self):
        return f"Tree({self.content},{self._children})"
    def compactFormatStr(self, layerLength=6) -> str:
        return super().compactFormatStr(layerLength)
    def ppstr(self, *args):
        return self.compactFormatStr(*args)
    def pprint(self, *args):
        print(self.compactFormatStr(*args))
    
    




@dataclass
class Pos:
    name : str




class Phrase:
    _opt_rules : list[list[Union[Pos, 'Phrase']]]
    # list represents optional rules
    # second list represents the sequence of each rule
    _parser : Optional[parsy.Parser]
    name : str
    def __init__(self, name:str):
        self.name = name
        self._opt_rules = []
    
    def to(self, *seqRule:Union[Pos,'Phrase']):
        for (i,p) in enumerate(seqRule):
            assert type(p)==Pos or type(p)=='Phrase', f"The {i}th input should be a Pos or Phrase."
        self._opt_rules.append(list(seqRule))
        self._parser = None
    
    def compileParser(self)->parsy.Parser:

        def _genPosParser(p:Pos)->parsy.Parser:
            tokenParser = (parsy.string(f'<{p.name}>') 
                        >> parsy.regex(r'[^<]*') 
                        << parsy.string(f'</{p.name}>')).map(lambda x:Token(p.name,x))
            return tokenParser.map(lambda t:SyntaxTree(t))
        
        def _genPhraseParser(ph : 'Phrase')->parsy.Parser:
            def shunt(x:Union[Pos,'Phrase'])->parsy.Parser:
                if isinstance(x,Pos):
                    return _genPosParser(x)
                elif isinstance(x,'Phrase'):
                    return _genPhraseParser(x)
                else:
                    raise TypeError("Received something other than Pos or Phrase.")
            
            def buildSeqSyntaxTreeParser(iterseq:Iterable[parsy.Parser])->parsy.Parser:
                def f(*subs):
                    nsubs = list(filter(lambda x:x is not None, subs))
                    return SyntaxTree(self.name,nsubs)
                return parsy.seq(*iterseq).combine(f)
            
            def compileOneRule(x:list[Union[Pos,'Phrase']])->parsy.Parser:
                return buildSeqSyntaxTreeParser(map(shunt,x))
            
            return parsy.alt(*map(compileOneRule, self._opt_rules))
            

        self._parser = _genPhraseParser(self)
        return self._parser
        
    def parse(self,source:str):
        if self._parser is None:
            self._parser = self.compileParser()
        return self._parser.parse(source)

tt = Phrase('tt')
tt.to()


###################################################

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

def phrase(name:str,*subs:parsy.Parser)->parsy.Parser:
    def f(*subs):
        nsubs = list(filter(lambda x:x is not None, subs))
        return SyntaxTree(name,nsubs)
    return parsy.seq(*subs).combine(f)


# t phrasal rule: <t1>aaa</t1><t2>bbb</t2> (let t2 be optional)

_tt = phrase( 't'
           , posToken('t1')  
           , posToken('t2').optional())

# recursion: <cons>xxx</cons><cons>ggg</cons><nil>hhh</nil>

_lst = parsy.forward_declaration()
_lst.become(phrase( 'lst' 
            , posToken('cons')
            , _lst | posToken('nil')
            )
)


    
_rt_sample1 = RoseTree('P',
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



