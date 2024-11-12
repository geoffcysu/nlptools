#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from ArticutAPI import Articut
from dataclasses import dataclass
from pprint import pprint
from typing import Optional, Tuple, Callable, Union, TypeVar, Generic, Any

import copy
import json
import re
import os

class Static:
    def __new__(cls):
        raise TypeError('Static classes cannot be instantiated')

_E = TypeVar("_E")
_R = TypeVar("_R")
class Either(Generic[_E,_R]):
    pass
@dataclass
class Left(Either[_E,Any]):
    left: _E
@dataclass
class Right(Either[Any,_R]):
    right: _R


with open("account.info", "r", encoding="utf-8") as f:
    accountDICT = json.load(f)

username = accountDICT['username']
apikey   = accountDICT['apikey']
articut = Articut(username, apikey)

@dataclass
class Tree:
    left: str
    head: str
    comp: 'Union[str,Tree,list[str]]'

realTree = CP(left='',
   head='∅',
   comp=Tree(left='',
           head='∅',
           comp=Tree(left='',
                        head='∅',
                        comp=Tree(left='<ENTITY_pronoun>我</ENTITY_pronoun><TIME_day>昨天</TIME_day>',
                                head='<ACTION_verb>吃</ACTION_verb>',
                                comp=Tree(left='',
                                          head='<ENTITY_classifier>五碗</ENTITY_classifier>',
                                          comp=Tree(left='',
                                                  head='<ENTITY_nouny>飯</ENTITY_nouny>',
                                                  comp=''))))))