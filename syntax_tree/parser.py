from __future__ import annotations
from typing import TypeVar, Generic, Callable, Any, Tuple, Optional, Set, Dict\
                   ,Generator, Sequence
import re
from functools import wraps,partial
from dataclasses import dataclass
from syntax_tree.type import SyntaxTree,TokenOfPos
# import syntax_tree.ast as ast
import syntax_tree.ast2 as ast2

import parsy

_A,_B,_C,_T = TypeVar('_A'),TypeVar('_B'),TypeVar('_C'),TypeVar('_T')


#### wrapped parser-------------
import operator
class Parser(Generic[_A]):
    _parser: parsy.Parser
    def __init__(self,p:parsy.Parser):
        self._parser = p
    def desc(self, description: str) -> Parser[_A]:
        return Parser(self._parser.desc(description))
    def parse(self,str)->_A:
        return self._parser.parse(str)
    def map(self,f:Callable[[_A],_T])->Parser[_T]:
        return Parser(self._parser.map(f))
    def times(self, min: int, max: int = None) -> Parser:#type:ignore 
            #reason: just following the original doc of parsy
        return Parser(self._parser.times(min,max))
    def combine(self, f:Callable[...,_B])->Parser[_B]:
        return Parser(self._parser.combine(f))
    def combine_dict(self, f:Callable[...,_B])->Parser[_B]:
        return Parser(self._parser.combine_dict(f))
    def sep_by(self, sep: Parser[Any], *, min: int = 0, max: int = float("inf")) -> Parser[list[_A]]: #type:ignore
        return Parser(self._parser.sep_by(sep._parser,min=min,max=max))
    def become(self, p:Parser[_A])->Parser[_A]:
        if 'become' in dir(self._parser):
            self._parser.become(p._parser) #type:ignore
            return self
        else:
            raise Exception("No `become` method.")
    
    def optional(self)->Parser[Optional[_A]]:
        return Parser(self._parser.optional())
    def many(self)->Parser[list[_A]]:
        return self.times(0, float("inf"))#type:ignore
    def at_least(self, n: int) -> Parser:
        return self.times(n) + self.many()
    def then(self, other: Parser[_A]) -> Parser[_A]:
        return seq(self, other).combine(lambda left, right: right)
    def skip(self, other: Parser[Any]) -> Parser[_A]:
        return seq(self, other).combine(lambda left, right: left)
    def __add__(self, other: Parser) -> Parser:
        return seq(self, other).combine(operator.add)
    def __or__(self, other: Parser[_A]) -> Parser[_A]:
        return alt(self,other)
    def __rshift__(self, other: Parser) -> Parser:
        return self.then(other)
    def __lshift__(self, other: Parser) -> Parser:
        return self.skip(other)

def alt(*parsers: Parser[_T]) -> Parser[_T]:
    return Parser(parsy.alt(*[p._parser for p in parsers]))

def seq(*args:Parser, **kwargs:Parser)->Parser[Tuple[Parser,...]]:
    return Parser(parsy.seq(*map(lambda p:p._parser,args),
                             **dict(map(lambda k_v:(k_v[0], k_v[1]._parser), 
                                        kwargs.items()))))
def homSeq(*args:Parser[_T])->Parser[list[_T]]:
    return Parser(parsy.seq(*map(lambda p:p._parser,args)))

def generate(fn:Callable[[],Generator[Parser,Any,_T]])->Parser[_T]:
    iterator = fn()
    @parsy.generate
    @wraps(fn)
    def gen():
        value = None
        try:
            while True:
                next_parser = iterator.send(value) #type:ignore
                    #reason: only the first value is None, which is a special case,
                    #the rest are of type _A.
                value = yield next_parser._parser
        except StopIteration as stop:
            return stop.value
    return Parser(gen)

def forward_declaration()->Parser[Any]:
    return Parser(parsy.forward_declaration())

# class LazyParser(Generic[_A],Parser[_A]):
#     def __init__(self,parserStr:str,globalscope:Dict,localscope:Dict):
#         self.parserStr = parserStr
#         self.globalscope = globalscope
#         self.localscope = localscope
# ###try eval at __call__
#     @property
#     def _parser(self):
#         return eval(self.parserStr,self.globalscope, self.localscope)._parser

#####---------------     


class ParsingContext:
    """
    Initialized with a set of phrase(rule) name, then update the actual parser 
    (with `setPhraseParser`) throughout the parsing procedure.
    Usage: 
    1. `parsingPhrase`: setting/getting the parsing phrase(rule) name.
    2. `phraseParser(str)`: getting the parser of the phrase name.
    3. `setPhraseParser(str,parsy.Parser)`: assigning the finished parser to the phrase.
    """
    # _parsingPhrase : Optional[str]
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
            assert re.fullmatch(r'[a-zA-Z_][\w]*',w), "phrase should be an identifier"
            d[w] = forward_declaration()
        self._initPP = d
        self._phraseParser = {}
        self._parsingPhrase = None
    # @property
    # def parsingPhrase(self):
    #     return self._parsingPhrase
    # @parsingPhrase.setter
    # def parsingPhrase(self,pp):
    #     assert (pp is None) or (pp in self._phraseSet), "parsingPhrase should be a member of phraseSet"
    #     #
    #     self._parsingPhrase = pp 
    @property
    def phraseSet(self)->Set[str]:
        return self._phraseSet
    
    
    def phraseParser(self,key:str)->Parser[SyntaxTree]:
        try:
            return self._phraseParser[key]
        except KeyError:
            try:
                return self._initPP[key]
            except KeyError:
                raise KeyError("The phrase to lookup doesn't exist.")
        # if key in self._phraseParser.keys():
        #     return self._phraseParser[key]
        # elif key in self._initPP.keys():
        #     return self._initPP[key]
        # else:
        #     raise KeyError("The phrase to lookup doesn't exist.")
        
    def setPhraseParser(self,phrase:str,p:Parser[SyntaxTree])->Parser[SyntaxTree]:
        assert phrase in self._initPP.keys(), "The phrase doesn't exist, or it might have been set already."
        self._initPP[phrase].become(p)
        self._phraseParser[phrase] = self._initPP.pop(phrase)
        return p
    

#-------------- Utility parsers------------

_idRegex:str = r'(?P<id>[a-zA-Z_][\w]*)'
_typRegex:str = r'[A-Z][\w]*'
_headIdRegex:str = r'(?P<headId>(^\s*|\r\n\s*|\n\s*)(?P<idbody>[a-zA-Z_][\w]*))'

# Turns all possible format of newline into '\n'.
def _tokenize(input:str)->list[str]:
    ms = re.finditer(r'r\{.*?\}'                    # for RegexTerm
                     + f'|{_headIdRegex}|{_idRegex}'  # for TokenOfPOS, RuleName
                     + r'|[|()]|->|\?'
                    , input)
    res = []
    for m in ms:
        d = m.groupdict()
        x = d['idbody']
        if x:
            res.append('\n'+x)
        else:
            res.append(m.group(0))
    return res


def _regexP(regex:str,group=0)->Parser[str]:
    @parsy.Parser
    def p(stream, index):
        if index < len(stream):
            tok = stream[index]
            m = re.match(regex,tok)
            if m and m.span()[1]==len(tok):
                return parsy.Result.success(index+1, m.group(group))
        return parsy.Result.failure(index, "token fully matching '{0}'".format(regex))
    return Parser(p)

_identifier = _regexP(_idRegex)
_typeIdentifier = _regexP(_typRegex)

def _oneOf(items:Sequence[_T])->Parser[_T]:
    return Parser(parsy.alt(*(parsy.match_item(item,description=str(item)) 
                              for item in items)))
def _tokP(item:_T)->Parser[_T]:
    return Parser(parsy.match_item(item,description=str(item)))

@parsy.Parser
def __headIdentifier(stream,i):
    if i<len(stream):
        tok = stream[i]
        if re.fullmatch(r'\n'+_idRegex, tok):
            return parsy.Result.success(i+1, tok[1:])
    return parsy.Result.failure(i, "first identifier in a new line")
# Receive a token starting with '\n', return the token without '\n'
_headIdentifier:Parser[str] = Parser(__headIdentifier)



#-------------- utility for the result parser-----

def _regToken(reg:str)->parsy.Parser:
    @parsy.generate
    def f():
        yield parsy.string('<')
        pos = yield parsy.regex(reg)
        yield parsy.string('>')
        content = yield parsy.regex('[^<]*')
        yield parsy.regex(f'</{pos}>')
        return SyntaxTree(TokenOfPos(pos,content))
    
    f.desc('regToken')
    return f


def _tokenOfPos(pos:str)->Parser[SyntaxTree]:
    res = Parser(_regToken(pos))
    res._parser.desc('token of POS: '+pos)
    return res



#-------------- The entrypoint --------------------

@dataclass
class FinalParsingResult:
    ruleDef: Dict[str, ast2.RuleTerm]
    ruleParser: Dict[str, Parser[SyntaxTree]]

    def singleEntry(self)->Parser[SyntaxTree]:
        return alt(*self.ruleParser.values())

def parserOfRules(ruleStr:str)->FinalParsingResult:
    # Tokenizing
    toks = _tokenize(ruleStr)
    ruleNames = list(map(lambda htok:htok[1:], filter(lambda tok:tok[0]=='\n',toks)))
    for name in ruleNames:
        if ruleNames.count(name)>1:
            raise DuplicateRule(name)
    
    pc = ParsingContext(set(ruleNames))
    
    # Parse AST
    ruleDefs:list[ast2.RuleDef] = _ruleDefOf(pc).many().parse(toks)
    ruleDefDict:Dict[str, ast2.RuleTerm] = dict((rd.ruleName,rd.ruleTerm) for rd in ruleDefs)

    # Generate parser according to the AST
    ruleParserDict = dict((rd.ruleName, _ruleTermToParser(pc,rd.ruleName,rd.ruleTerm)) 
                            for rd in ruleDefs)
    for rn,p in ruleParserDict.items():
        pc.setPhraseParser(rn,p)
    return FinalParsingResult(ruleDefDict, ruleParserDict)



def _ruleTermToParser(pc:ParsingContext, ruleName:str, rt:ast2.RuleTerm)->Parser[SyntaxTree]:
    
    return rt.match( #-> Parser[SyntaxTree]
        posToken=lambda pos: _tokenOfPos(pos),
        ruleName=lambda rule: pc.phraseParser(rule),
        seq=lambda ruleTerms:\
            #homSeq: ...->Parser[list[SyntaxTree]]
            homSeq(*map(partial(_ruleTermToParser,pc,ruleName), 
                        ruleTerms)
            ).map(lambda children: SyntaxTree(ruleName,children)),
        alt=lambda ruleTerms:\
            #alt: ...->Parser[SyntaxTree]
            alt(*map(partial(_ruleTermToParser,pc,ruleName), 
                     ruleTerms))
    )


class _RuleTermParsersOfCtx:
    pc: ParsingContext

    ruleDef: Parser[ast2.RuleDef]
    alt_terms: Parser[ast2.RuleTerm]
    term_seq: Parser[ast2.RuleTerm]
    opt_term: Parser[ast2.RuleTerm]
    term: Parser[ast2.RuleTerm]

    def __init__(self, pc:ParsingContext):
        self.pc = pc

        alt_terms: Parser[ast2.RuleTerm] = forward_declaration()

        def decideId(id:str)->ast2.RuleTerm:
            if id in pc.phraseSet:
                return ast2.RuleName(id)
            else:
                return ast2.TokenOfPOS(id)
        term: Parser[ast2.RuleTerm] = \
            alt(
                _tokP('(') >> alt_terms << _tokP(')'),
                _regexP(r'r\{(.*?)\}',group=1).map(ast2.RegexTerm),
                _identifier.map(decideId),
            )
        self.term = term

        opt_term: Parser[ast2.RuleTerm] = \
            seq( term
               , _tokP('?').optional()
            ).combine(lambda t,o: ast2.Opt(t) if o else t)
        self.opt_term = opt_term

        term_seq: Parser[ast2.RuleTerm] =\
            term.at_least(1).map(ast2.Seq)
        self.term_seq = term_seq

        def lst2Alts(a:list[ast2.RuleTerm])->ast2.RuleTerm:
            if len(a)==1:
                return a[0]
            else:
                return ast2.Alt(a)
        alt_terms.become( #Parser[ast2.RuleTerm]
            term_seq\
                .sep_by(_tokP('|'), min=1)\
                .map(lst2Alts)
        )
        self.alt_terms = alt_terms
        
        ruleDef:Parser[ast2.RuleDef] = \
             seq((_headIdentifier << _tokP('->')),
                 alt_terms
                ).map(lambda t:ast2.RuleDef(t[0],t[1]))#type:ignore
        self.ruleDef = ruleDef


# def _termOf(pc:ParsingContext)-> Parser[ast.RuleTerm]:
    
#     def decideId(id:str)->ast.RuleTerm:
#         if id in pc.phraseSet:
#             return ast.RuleName(id)
#         else:
#             return ast.PosToken(id)
    
#     return _identifier.map(decideId)
#     # return alt(
#     #     _tokP('(') >> LazyParser("_altOf(pc)",globals(),locals()) << _tokP(')'),
#     #     _identifier.map(decideId),
#     # )
# def _seqOf(pc:ParsingContext)->Parser[ast.RuleTerm]:
#     return _termOf(pc).at_least(1).map(ast.Seq)
# def _altOf(pc:ParsingContext)->Parser[ast.RuleTerm]:
#     def f(a:list[ast.RuleTerm])->ast.RuleTerm:
#         if len(a)==1:
#             return a[0]
#         else:
#             return ast.Alt(a)
    
#     return _seqOf(pc)\
#            .sep_by(_tokP('|'),min=1)\
#            .map(f)

# def _ruleDef(pc:ParsingContext)->Parser[ast.RuleDef]:
#     return seq((_headIdentifier << _tokP('->')),
#                 _altOf(pc)
#            ).map(lambda t:ast.RuleDef(t[0],t[1]))#type:ignore
#     # @generate
#     # def p():
#     #     ruleName = yield _headIdentifier
#     #     yield Parser(parsy.match_item('->'))
#     #     ruleTerm:ast.RuleTerm = yield _altOf(pc)
#     #     return ast.RuleDef(ruleName,ruleTerm)
#     # return p




class DuplicateRule(Exception):
    "Raised when duplicated phrase appears."
    def __init__(self,word:str):
        super().__init__(f'The rule: \"{word}\" is duplicated.')
