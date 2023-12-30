from __future__ import annotations
import parsy
from typing import Optional, TypeVar, Generic, Literal, Union, Any, Type, Callable, Tuple, Dict
from itertools import chain, starmap
from functools import partial, reduce
from collections.abc import Sequence, Callable, Iterable, Set
import operator
import re
from dataclasses import dataclass
_A,_B,_C,_T = TypeVar('_A'),TypeVar('_B'),TypeVar('_C'),TypeVar('_T')

#-------------
from syntax_tree.parser import parserOfRules

rule1 = '''
p1 -> a p2
p2 -> p1 | b
'''
text1 = "<a>x</a><a>y</a><b>0</b>"

parserDict = parserOfRules(rule1)
tree = parserDict.ruleParser['p1'].parse(text1)
"""
Use tree.ppstr() to get the string of the pretty-printting-string,
or tree.pprint() to directly print it.
"""

#------------RoseTree example------------
from syntax_tree.type import RoseTree

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

