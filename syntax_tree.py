from __future__ import annotations
import parsy
from typing import Optional, TypeVar, Generic, Literal, Union, Any
from itertools import chain, starmap
from functools import partial, reduce
from collections.abc import Sequence, Callable, Iterable, Set
import operator
import re
from dataclasses import dataclass

_A,_B,_C = TypeVar('_A'),TypeVar('_B'),TypeVar('_C')
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
    def surveyParentInfo(self):
        for c in self._children:
            c._parent = self
            if isinstance(c.content, str):
                c.surveyParentInfo()

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

# Made a mistake here: trying to handle what has been done by parsy already.
class Phrase:
    _opt_rules : list[list[Union[Pos, Phrase]]]
    # list represents optional rules
    # second list represents the sequence of each rule
    _parser : Optional[parsy.Parser]
    name : str
    def __init__(self, name:str):
        self.name = name
        self._opt_rules = []
    
    def to(self, *seqRule:Union[Pos,Phrase]):
        for (i,p) in enumerate(seqRule):
            assert isinstance(p,Pos) or isinstance(p,Phrase), f"The {i}th input should be a Pos or Phrase."
        self._opt_rules.append(list(seqRule))
        self._parser = None
    
    def compileParser(self)->parsy.Parser:

        def _genPosParser(p:Pos)->parsy.Parser:
            tokenParser = (parsy.string(f'<{p.name}>') 
                        >> parsy.regex(r'[^<]*') 
                        << parsy.string(f'</{p.name}>')).map(lambda x:Token(p.name,x))
            return tokenParser.map(lambda t:SyntaxTree(t))
        
        def _genPhraseParser(ph : Phrase)->parsy.Parser: #need to check if it's strictly Parser[SyntaxTree]
            def shunt(x:Union[Pos,Phrase])->parsy.Parser:
                if isinstance(x,Pos):
                    return _genPosParser(x)
                elif isinstance(x,Phrase):
                    return _genPhraseParser(x)
                else:
                    raise TypeError("Received something other than Pos or Phrase.")
            
            def buildSeqSyntaxTreeParser(iterseq:Iterable[parsy.Parser])->parsy.Parser:
                def f(*subs):
                    nsubs = list(filter(lambda x:x is not None, subs))
                    return SyntaxTree(self.name,nsubs)
                return parsy.seq(*iterseq).combine(f)
            
            def compileOneRule(x:list[Union[Pos,Phrase]])->parsy.Parser:
                return buildSeqSyntaxTreeParser(map(shunt,x))
            
            return parsy.alt(*map(compileOneRule, self._opt_rules))
            

        self._parser = _genPhraseParser(self)
        return self._parser
        
    def parse(self,source:str):
        if self._parser is None:
            self._parser = self.compileParser()
        return self._parser.parse(source)


# another implimentation idea: Phrase should return a real parser
# what about the rules?

# npExample = '<adj>beautiful</adj><adj>white</adj><noun>fall</noun>'
# NP = Phrase('NP')
# NP.to(Pos('adj'), NP)
# NP.to(Pos('noun'))


###################################################

def posToken(pos:str):#Parser[SyntaxTree]
    tokenParser = (parsy.string(f'<{pos}>') 
                >> parsy.regex(r'[^<]*') 
                << parsy.string(f'</{pos}>')).map(lambda x:Token(pos,x))
    return tokenParser.map(lambda t:SyntaxTree(t))

def posTokenOf(pos:str, parent:SyntaxTree):#Parser[SyntaxTree]
    tokenParser = (parsy.string(f'<{pos}>') 
                >> parsy.regex(r'[^<]*') 
                << parsy.string(f'</{pos}>')).map(lambda x:Token(pos,x))
    return tokenParser.map(lambda t:SyntaxTree(t,[],parent))


def starSyntaxTree(name:str,parent:Optional[SyntaxTree]=None)->Callable[[Any],SyntaxTree]:
    def f(*args)->SyntaxTree:
        return SyntaxTree(name,list(args),parent)
    return f




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

# tt = parsy.seq( posToken('t1')  
#                , posToken('t2').optional()
#                ).combine()

# recursion: <cons>xxx</cons><cons>ggg</cons><nil>hhh</nil>


# new approach: generate parser that build into this form:
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
    | 
'''
ruleEx1 = ''' 
lst -> nil
    | cons lst?
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
    _parsingPhrase : Optional[str]
    _phraseSet : Set[str]
    _phraseParser : dict[str,parsy.Parser]
    "Initially empty, see _initPP."
    _initPP : dict[str,parsy.forward_declaration]
    '''
    Will be initialized with `parsy.forword_declaration()`, then updated 
    when the phrase parser is completed; the new parser will then be moved to phraseParser.
    The updating behaviour should be done through the `setPhraseParser` method.
    (currently doing in the `ruleOf` function.)
    '''
    
    def __init__(self,phraseSet:Set[str]):
        self._phraseSet = phraseSet
        d = {}
        for w in phraseSet:
            assert re.fullmatch(r'\w+',w), "phrase should be matched with '\\w+'"
            d[w] = parsy.forward_declaration()
        self._initPP = d
        self._phraseParser = {}
        self._parsingPhrase = None
    @property
    def parsingPhrase(self):
        return self._parsingPhrase
    @parsingPhrase.setter
    def parsingPhrase(self,pp):
        assert (pp is None) or (pp in self._phraseSet), "parsingPhrase should be a member of phraseSet"
        self._parsingPhrase = pp 
    @property
    def phraseSet(self)->Set[str]:
        return self._phraseSet
    
    
    def phraseParser(self,key:str)->parsy.Parser:
        if key in self._phraseParser.keys():
            return self._phraseParser[key]
        elif key in self._initPP.keys():
            return self._initPP[key]
        else:
            raise KeyError("The phrase to lookup doesn't exist.")
        
    def setPhraseParser(self,phrase:str,p:parsy.Parser)->parsy.Parser:
        assert phrase in self._initPP.keys(), "A phrase can be set only once, or that the phrase doesn't exist."
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
            raise Exception('none exhaustive error')
        
    def f(res:tuple[str,Optional[Literal['?','+','*']]])->parsy.Parser: #Parser[Parser[SyntaxTree]]
        termName:str = res[0]
        combMatch:Optional[Literal['?','+','*']] = res[1] 
        return addComb(combMatch
                       , ctx.phraseParser(termName) if termName in ctx.phraseSet 
                         else posToken(termName)
                       )
        
    return parsy.alt(
             #(parsy.match_item('(') >> ruleOf(ctx) << parsy.match_item(')')), 
             parsy.seq(test_regex(r'\w+','term')
                       , match_items('?+*').optional()
               ).map(c2(f,tuple))
             )


def plusOf(ctx:ParsingContext)->parsy.Parser: #Parser[Parser[SyntaxTree]]
    assert ctx.parsingPhrase is not None,\
      "A parsingPhrase should be given to the parsing context \
       (through 'ctx.parsingPhrase = ...') before starting to parse."
    
    pp = ctx.parsingPhrase
    def f(lp:list[parsy.Parser])->parsy.Parser: #list[Parser[SyntaxTree]] -> Parser[SyntaxTree]
        return parsy.seq(*lp).combine(starSyntaxTree(pp))
    return termOf(ctx).at_least(1).map(f)

def ruleOf(ctx:ParsingContext,parsingPhrase:str)->parsy.Parser: #Parser[Parser[SyntaxTree]]
    ctx.parsingPhrase = parsingPhrase
    result = plusOf(ctx)\
             .sep_by(parsy.match_item('|'), min=1)\
             .map(lambda pl:parsy.alt(*pl))
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

def syntaxRulesParser(ctx:ParsingContext)->parsy.Parser: #Parser[Parser[SyntaxTree]]
    @parsy.generate
    def oneRule():
        phraseName = yield test_regex(r'\n\w+','\\nword')
        yield parsy.match_item('->')
        return (phraseName,ruleOf(ctx,phraseName))
    oneRule.many() #list[Parser[SyntaxTree]]
    return parsy.success('') #oneRule.many().#getting a list of parsers, need to combine them into a new parser


def tokenize(s:str)->list[str]:
    return re.findall(r'\w+|\||[?+*]|\(|\)',s)

class DuplicateRule(Exception):
    "Raised when duplicated phrase appears."
    def __init__(self,word:str):
        super().__init__(f'The rule: \"{word}\" is duplicated.')

def parserOfRules(ruleStr:str): #->Parser[SyntaxTree]
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
    toks = re.findall(r'\n\w+|\w+|\||[?+*]|\(|\)|->', ruleStr)
    return syntaxRulesParser(phraseSet,posSet).parse(toks)
    


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

