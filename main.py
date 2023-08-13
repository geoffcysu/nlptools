from ArticutAPI import Articut
import json
import re
import pprint as pp
import parsy
from typing import Optional

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