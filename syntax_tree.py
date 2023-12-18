from __future__ import annotations
import parsy
from typing import Optional, TypeVar, Generic, Literal, Union, Any, Type, Callable, Tuple, Dict
from itertools import chain, starmap
from functools import partial, reduce
from collections.abc import Sequence, Callable, Iterable, Set
import operator
import re
from dataclasses import dataclass
from typing_extensions import Protocol

_A,_B,_C,_T = TypeVar('_A'),TypeVar('_B'),TypeVar('_C'),TypeVar('_T')
# function composition
def c2(f:Callable[[_B],_C], g:Callable[[_A],_B])->Callable[[_A],_C]:
    return lambda x:f(g(x))

class Token:
    pos : str
    text : str
    def __init__(self,pos:str,text:str):
        self.pos = pos
        self.text = text
    def __str__(self):
        return f'{self.pos}({self.text})'
    def __repr__(self):
        return f'Token({self.pos},{self.text})'

class RoseTree:
    children:list['RoseTree']
    def __init__(self,content, children:Sequence['RoseTree']=[]):
        self.content = content
        self.children = list(children)

    def copy(self)->RoseTree:
        "The content will be the reference if it's an object."
        if len(self.children)==0:
            return RoseTree(self.content,[])
        else:
            return RoseTree(self.content, 
                            list(map(RoseTree.copy, self.children)))
        
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
    content : Union[str,Token]
    children : list['SyntaxTree']
    parent : Optional['SyntaxTree']
    def __init__(self,content:Union[str,Token], children:list['SyntaxTree'] = [], parent:Optional['SyntaxTree'] = None):
        self.content = content
        self.children = children
        self.parent = parent
        
    def addChild(self,child:'SyntaxTree'):
        self.children.append(child)
        child.parent = self
    def addChildren(self,children:list['SyntaxTree']):
        for child in children:
            self.addChild(child)
    def registerParentInfo(self)->'SyntaxTree':
        """
        Used to update parenthood info to a non-parent-registered tree.
        """
        for c in self.children:
            c.parent = self
            if isinstance(c.content, str):
                c.registerParentInfo()
        return self
    
    def copy(self)->'SyntaxTree':
        if len(self.children)==0:
            return SyntaxTree(self.content,children=[],parent=self.parent)
        else:
            return SyntaxTree(self.content, 
                              list(map(SyntaxTree.copy, self.children)), 
                              self.parent)

    def __repr__(self):
        return f"Tree({self.content},{self.children})"
    def compactFormatStr(self, layerLength=6) -> str:
        return super().compactFormatStr(layerLength)
    def ppstr(self, *args):
        return self.compactFormatStr(*args)
    def pprint(self, *args):
        print(self.compactFormatStr(*args))
    
#### wrapped parser-------------

class Parser(Generic[_A]):
    _parser: parsy.Parser
    def __init__(self,p:parsy.Parser):
        self._parser = p
    def parse(self,str)->_A:
        return self._parser.parse(str)
    def map(self,f:Callable[[_A],_T])->Parser[_T]:
        return Parser(self._parser.map(f))
    
    def combine(self, f:Callable[[Any],_B])->Parser[_B]:
        return Parser(self._parser.combine(f))
    def combine_dict(self, f:Callable[[Any],_B])->Parser[_B]:
        return Parser(self._parser.combine_dict(f))
    def become(self, p:Parser[_A])->Parser[_A]:
        if 'become' in dir(self._parser):
            self._parser.become(p._parser) #type:ignore
            return self
        else:
            raise Exception("No `become` method.")
    def __or__(self, other: Parser[_A]) -> Parser[_A]:
        return alt(self,other)

def alt(*parsers: Parser[_T]) -> Parser[_T]:
    return Parser(parsy.alt(*[p._parser for p in parsers]))

def seq(*args:Parser, **kwargs:Parser)->Parser[Tuple[Parser,...]]:
    return Parser(parsy.seq(*map(lambda p:p._parser,args),
                             **dict(map(lambda k_v:(k_v[0], k_v[1]._parser), 
                                        kwargs.items()))))

def forward_declaration()->Parser[Any]:
    return Parser(parsy.forward_declaration())


#####---------------     



###################################################

def _regToken(reg:str)->parsy.Parser:
    @parsy.generate
    def f():
        yield parsy.string('<')
        pos = yield parsy.regex(reg)
        yield parsy.string('>')
        content = yield parsy.regex('[^<]*')
        yield parsy.regex(f'</{pos}>')
        return SyntaxTree(Token(pos,content))
    
    f.desc('regToken')
    return f

def regToken(reg:str)->Parser[SyntaxTree]:
    return Parser(_regToken(reg))

def posToken(pos:str)->Parser[SyntaxTree]:
    res = regToken(pos)
    res._parser.desc('posToken')
    return res

def addParent_im(parent:SyntaxTree, p:Parser[SyntaxTree])->Parser[SyntaxTree]:
    "Copy the result SyntaxTree of the parser then add the parent to it. "
    def f(st:SyntaxTree)->SyntaxTree:
        newst = st.copy()
        newst.parent = parent
        return st
    return p.map(f)

def addParent(parent:SyntaxTree, p:Parser[SyntaxTree])->Parser[SyntaxTree]:
    """
    This alters the result of the given parser, instead of generating a new one.
    """
    def f(st:SyntaxTree)->SyntaxTree:
        st.parent = parent
        return st
    return p.map(f)

def starSyntaxTree(name:str,parent:Optional[SyntaxTree]=None)->Callable[[Any],SyntaxTree]:
    "If the argument contains any None, it will be filtered out."
    
    def filterNone(lst):
        "Used for when a parser is an optional."
        return [x for x in lst if x is not None]
    def f(*args)->SyntaxTree:
        return SyntaxTree(name,filterNone(args),parent)
    return f




# IS THIS USED?
def phrase(name:str,*subs:Parser[Optional[SyntaxTree]])->Parser[SyntaxTree]:
    def f(*subs):
        nsubs = list(filter(lambda x:x is not None, subs))
        return SyntaxTree(name,nsubs)
    return seq(*subs).combine(f)


# t phrasal rule: <t1>aaa</t1><t2>bbb</t2> (let t2 be optional)

# tt = parsy.seq( posToken('t1')  
#                , posToken('t2').optional()
#                ).combine()

# recursion: <cons>xxx</cons><cons>ggg</cons><nil>hhh</nil>


# new approach: generate parser that build into this form:
#new problem: is nested (parens rule) structure applicable?
lst = parsy.forward_declaration()
lst.become(
    posToken('nil')
    | parsy.seq(posToken('cons'), lst).combine(starSyntaxTree('lst'))
)
listExample = "<cons>a</cons><cons>b</cons><nil>e</nil>"
'''

lst -> nil
       | cons lst?

[[['nil',None]]
,[['cons',None],['lst','?']]
]

Remember to consider the usage that ENTITY -> ENTITY_noun | ENTITY_oov | ...
Now it seems fine to just let 'ENTITY' be a phrase-like thing.
'''

'''
VP -> Specifier V'
V' -> 
       V NP
   | Adjunct V'
   | V' Adjunct

'''

ruleEx0 = '''
NP -> adj NP
    | n

'''
ruleEx1 = ''' 
lst -> nil
    | cons lst
'''
ruleEx2 = 'rule -> abc  (dce? | GGG+ ) FFF*'  
ruleEx3 = '''
p1 -> a | p2
p2 -> p1 | b
'''

# use this wrapper inside @parsy.generate functions (due to the inconsistent behaviour when output is a parser)
class ParserWrapper:
    _parser : parsy.Parser
    def __init__(self,parser):
        self._parser = parser
    def __call__(self):
        return self._parser

def match_items(xs:Sequence)->parsy.Parser:
    if len(xs)==0:
        return parsy.fail("no item to match")
    else:
        return reduce(lambda p,i: p | parsy.match_item(i)
                    , xs[1:]
                    , parsy.match_item(xs[0]))


class ParsingContext:
    """
    Initialized with a set of phrase(rule) name, then update the actual parser 
    (with `setPhraseParser`) throughout the parsing procedure.
    Usage: 
    1. `parsingPhrase`: setting/getting the parsing phrase(rule) name.
    2. `phraseParser(str)`: getting the parser of the phrase name.
    3. `setPhraseParser(str,parsy.Parser)`: assigning the finished parser to the phrase.
    """
    _parsingPhrase : Optional[str]
    _phraseSet : Set[str]
    _phraseParser : dict[str,Parser[SyntaxTree]]
    "Initially empty, see _initPP."
    _initPP : dict[str,Parser[SyntaxTree]]
    '''
    Will be initialized with `parsy.forword_declaration()`, then updated 
    when the phrase parser is completed; the new parser will then be moved to phraseParser.
    The updating behaviour should be done through the `setPhraseParser` method.
    (currently doing in the `ruleOf` function.)
    '''
    
    def __init__(self,phraseSet:Set[str]):
        self._phraseSet = phraseSet
        d : Dict[str,Parser[SyntaxTree]]= {}
        for w in phraseSet:
            assert re.fullmatch(r'\w+',w), "phrase should be matched with '\\w+'"
            d[w] = forward_declaration()
        self._initPP = d
        self._phraseParser = {}
        self._parsingPhrase = None
    @property
    def parsingPhrase(self):
        return self._parsingPhrase
    @parsingPhrase.setter
    def parsingPhrase(self,pp):
        assert (pp is None) or (pp in self._phraseSet), "parsingPhrase should be a member of phraseSet"
        #
        self._parsingPhrase = pp 
    @property
    def phraseSet(self)->Set[str]:
        return self._phraseSet
    
    
    def phraseParser(self,key:str)->Parser[SyntaxTree]:
        if key in self._phraseParser.keys():
            return self._phraseParser[key]
        elif key in self._initPP.keys():
            return self._initPP[key]
        else:
            raise KeyError("The phrase to lookup doesn't exist.")
        
    def setPhraseParser(self,phrase:str,p:Parser[SyntaxTree])->Parser[SyntaxTree]:
        assert phrase in self._initPP.keys(), "The phrase doesn't exist, or it might have been set already."
        self._initPP[phrase].become(p)
        self._phraseParser[phrase] = self._initPP.pop(phrase)
        return p

# bar = parsy.forward_declaration()
# term = parsy.forward_declaration()
# def ruleOf(phrase:str)->parsy.Parser:#Parser[Parser[Syntax]]
#     ...
# @parsy.generate
# def _term_posToken(): #ParsesrWrapper[Parser[SyntaxTree]]
#     w = yield test_regex(r'\w+','posToken')
#     op = yield match_items('?+*').optional()
#     wp = posToken(w)
#     if op is None:
#         return ParserWrapper(wp)
#     elif op == '?':
#         return ParserWrapper(wp.optional())
#     elif op == '+':
#         return ParserWrapper(wp.at_least(1))
#     elif op == '*':
#         return ParserWrapper(wp.many())
#     else:
#         raise Exception('none exhaustive error')

# term:parsy.Parser = _term_posToken.map(lambda f:f()) #| (parsy.match_item('(') >> ruleOf << parsy.match_item(')'))
def termOf(ctx:ParsingContext)->parsy.Parser: #Parser[Parser[SyntaxTree]]
    def addComb(op:Optional[str], p:parsy.Parser)->parsy.Parser:
        if op is None:
            return p
        elif op == '?':
            return p.optional()
        elif op == '+':
            return p.at_least(1)
        elif op == '*':
            return p.many()
        else:
            raise Exception('non-exhaustive error')
        
    def f(res:tuple[str,Optional[Literal['?','+','*']]])->parsy.Parser: #Parser[Parser[SyntaxTree]]
        termName:str = res[0]
        combMatch:Optional[Literal['?','+','*']] = res[1] 
        return addComb(combMatch
                       , ctx.phraseParser(termName) if termName in ctx.phraseSet 
                         else posToken(termName)
                       )
        
    return parsy.alt(
             #(parsy.match_item('(') >> altOf(ctx) << parsy.match_item(')')), 
             parsy.seq(test_regex(r'\w+','term')
                       , match_items('?+*').optional()
               ).map(c2(f,tuple))
                #note: map is used to transfer the parsing result into the parser we want.
             )


def plusOf(ctx:ParsingContext)->parsy.Parser: #Parser[Parser[SyntaxTree]]
    assert ctx.parsingPhrase is not None,\
      "A parsingPhrase should be given to the parsing context \
       (through 'ctx.parsingPhrase = ...') before starting to parse."
    
    pp = ctx.parsingPhrase
    def f(lp:list[parsy.Parser])->parsy.Parser: #list[Parser[SyntaxTree]] -> Parser[SyntaxTree]
        return parsy.seq(*lp).combine(starSyntaxTree(pp))
    return termOf(ctx).at_least(1).map(f)

def altOf(ctx:ParsingContext)->parsy.Parser: #Parser[Parser[SyntaxTree]]
    return plusOf(ctx)\
           .sep_by(parsy.match_item('|'), min=1)\
           .map(lambda pl:parsy.alt(*pl))
    

def ruleOf(ctx:ParsingContext,parsingPhrase:str)->parsy.Parser: #Parser[Parser[SyntaxTree]]
    ctx.parsingPhrase = parsingPhrase
    result = altOf(ctx)
    ctx.setPhraseParser(parsingPhrase,result)
    ctx.parsingPhrase = None
    return result

def test_regex(regex:str, desc:str)->parsy.Parser:
    return parsy.test_item(lambda x: re.match(regex,x) is not None, desc)

# term.become(
#     parsy.seq( parsy.match_item('(') >> rule << parsy.match_item(')')
#              , match_items('?+*').optional()
#              )
#     | parsy.seq( test_regex(r'\w+','word')
#                , match_items('?+*').optional()
#                ).combine(lambda w,o:posToken(w))
#     )

# syntaxRulesParser = parsy.seq( test_regex(r'\n\w+','\\nword')
#                        , parsy.match_item('->')
#                        , rule
#                        ).many()

@dataclass
class FinalParsingResult:
    rules: Dict[str, Parser[SyntaxTree]]

    def singleEntry(self)->Parser[SyntaxTree]:
        return alt(*self.rules.values())
        

def syntaxRulesParser(ctx:ParsingContext)->Parser[FinalParsingResult]:
    @parsy.generate
    def _oneRule():
        """
        Parses a rule such as:
        P -> a | b
        """
        phraseName = yield test_regex(r'\n\w+','\\nword')
        yield parsy.match_item('->')
        return (phraseName,ruleOf(ctx,phraseName))
    #oneRule:Parser[Tuple[str,Parser[SyntaxTree]]] = Parser(_oneRule)

    @parsy.generate
    def _manyRules():
        result = FinalParsingResult({})
        while True:
            rule : Optional[Tuple[str,Parser[SyntaxTree]]] = yield _oneRule.optional()
            if rule is None:
                return result
            else:
                result.rules[rule[0]] = rule[1]
    manyRules : Parser[FinalParsingResult] = Parser(_manyRules)
    # Just wrapping it.

    return manyRules


class DuplicateRule(Exception):
    "Raised when duplicated phrase appears."
    def __init__(self,word:str):
        super().__init__(f'The rule: \"{word}\" is duplicated.')


# The entrypoint
def parserOfRules(ruleStr:str)->FinalParsingResult:
    
    # Finding all phrase token and POS token.
    words = re.findall(r'\n\w+|\w+', ruleStr)
    def identifyWords(ws:list[str])->tuple[set[str], set[str]]:
        phraseSet = set([])
        posSet = set([])
        for w in ws:
            if w[0]=='\n':
                if w[1:] in phraseSet:
                    raise DuplicateRule(w[1:])
                else:
                    phraseSet.add(w[1:])
            elif w not in phraseSet:
                posSet.add(w)
            else:
                pass
        return (phraseSet,posSet)
    phraseSet, posSet = identifyWords(words)

    # Tokenizing
    toks = re.findall(r'\n\w+|\w+|\||[?+*]|\(|\)|->', ruleStr)
    return syntaxRulesParser(ParsingContext(phraseSet)).parse(toks)
    


_rt_sample1 = RoseTree('P',
    [RoseTree('P1',
        [RoseTree('1')
        ,RoseTree('2')
        ])
        
    ,RoseTree('P2',
        [RoseTree('3')])
    ,RoseTree('P3',
        [RoseTree('P4', 
            [RoseTree('4')
            ,RoseTree('P5',
                [RoseTree('5')
                ,RoseTree('6')]
                )
            ])
        ,RoseTree('7')
        ])
    ]
)
# P___P1____1
# |   |_____2
# |___P2____3
# |___P3___P4___4
#     |    |____P5___5
#     |         |____6
#     |____7

