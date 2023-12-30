
from typing import TypeVar
_A,_B,_C,_T = TypeVar('_A'),TypeVar('_B'),TypeVar('_C'),TypeVar('_T')

#----------syntax_tree example(s)--------
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

should print the below text in this case:
p1____a(x)
|_____p2____p1____a(y)
            |_____p2____b(0)
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

