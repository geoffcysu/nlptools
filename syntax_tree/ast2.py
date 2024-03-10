
from dataclasses import dataclass

# """
# TokenOfPOS(s:str)
#   a proper name
# RuleName(s:str)
#   a proper name
# RegexTerm(s:str)
#   r{ENTITY_.*}
# Alt(ts:list[RuleTerm])
#   a | b | c
# Seq(ts:list[RuleTerm])
#   a b c
# Opt(t:RuleTerm)
#   a?

# Many Optional[int] RuleTerm
# """


""" adt:
data RuleTerm = TokenOfPOS(s:str)
              | RuleName(s:str)
              | RegexTerm(s:str)
              | Alt(ts:list[RuleTerm])
              | Seq(ts:list[RuleTerm])
              | Opt(t:RuleTerm)
"""
# The code below is generated according to the definition above; hash=ed632fca95

from typing import TypeVar,Generic,Callable

_T_ = TypeVar('_T_')
class RuleTerm:
    "Can be either TokenOfPOS, RuleName, RegexTerm, Alt, Seq, or Opt."
    def match(self,*,
              tokenOfPOS: Callable[[str], _T_],
              ruleName: Callable[[str], _T_],
              regexTerm: Callable[[str], _T_],
              alt: Callable[['list[RuleTerm]'], _T_],
              seq: Callable[['list[RuleTerm]'], _T_],
              opt: Callable[['RuleTerm'], _T_],
             )->_T_:
        ...

class TokenOfPOS(RuleTerm):
    s: str
    def __init__(self,s:str):
        self.s = s
    def match(self,*,
              tokenOfPOS: Callable[[str], _T_],
              ruleName: Callable[[str], _T_],
              regexTerm: Callable[[str], _T_],
              alt: Callable[['list[RuleTerm]'], _T_],
              seq: Callable[['list[RuleTerm]'], _T_],
              opt: Callable[['RuleTerm'], _T_],
             )->_T_:
        return tokenOfPOS(self.s)

class RuleName(RuleTerm):
    s: str
    def __init__(self,s:str):
        self.s = s
    def match(self,*,
              tokenOfPOS: Callable[[str], _T_],
              ruleName: Callable[[str], _T_],
              regexTerm: Callable[[str], _T_],
              alt: Callable[['list[RuleTerm]'], _T_],
              seq: Callable[['list[RuleTerm]'], _T_],
              opt: Callable[['RuleTerm'], _T_],
             )->_T_:
        return ruleName(self.s)

class RegexTerm(RuleTerm):
    s: str
    def __init__(self,s:str):
        self.s = s
    def match(self,*,
              tokenOfPOS: Callable[[str], _T_],
              ruleName: Callable[[str], _T_],
              regexTerm: Callable[[str], _T_],
              alt: Callable[['list[RuleTerm]'], _T_],
              seq: Callable[['list[RuleTerm]'], _T_],
              opt: Callable[['RuleTerm'], _T_],
             )->_T_:
        return regexTerm(self.s)

class Alt(RuleTerm):
    ts: list[RuleTerm]
    def __init__(self,ts:list[RuleTerm]):
        self.ts = ts
    def match(self,*,
              tokenOfPOS: Callable[[str], _T_],
              ruleName: Callable[[str], _T_],
              regexTerm: Callable[[str], _T_],
              alt: Callable[['list[RuleTerm]'], _T_],
              seq: Callable[['list[RuleTerm]'], _T_],
              opt: Callable[['RuleTerm'], _T_],
             )->_T_:
        return alt(self.ts)

class Seq(RuleTerm):
    ts: list[RuleTerm]
    def __init__(self,ts:list[RuleTerm]):
        self.ts = ts
    def match(self,*,
              tokenOfPOS: Callable[[str], _T_],
              ruleName: Callable[[str], _T_],
              regexTerm: Callable[[str], _T_],
              alt: Callable[['list[RuleTerm]'], _T_],
              seq: Callable[['list[RuleTerm]'], _T_],
              opt: Callable[['RuleTerm'], _T_],
             )->_T_:
        return seq(self.ts)

class Opt(RuleTerm):
    t: RuleTerm
    def __init__(self,t:RuleTerm):
        self.t = t
    def match(self,*,
              tokenOfPOS: Callable[[str], _T_],
              ruleName: Callable[[str], _T_],
              regexTerm: Callable[[str], _T_],
              alt: Callable[['list[RuleTerm]'], _T_],
              seq: Callable[['list[RuleTerm]'], _T_],
              opt: Callable[['RuleTerm'], _T_],
             )->_T_:
        return opt(self.t)


# End of generated code.

@dataclass
class RuleDef:
    ruleName:str
    ruleTerm:RuleTerm

