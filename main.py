from ArticutAPI import Articut
import json
import re
import pprint as pp
from typing import Optional

username = ""
apikey   = ""

with open('DROIDTOWN.json') as f:
    try:
        r = json.load(f)
        username = r["username"]
        apikey = r["key"]
    except:
        print("Please fill the DROIDTOWN.json file")

articut = Articut(username, apikey)

# inputSTR = "戴克斯的原始版本僅適用於找到兩個頂點之間的最短路徑"
# resultDICT = articut.parse(inputSTR, level="lv2")
# pp.pprint(resultDICT)


class Word:
    pos : str
    text : str
    def __init__(self,pos:str,text:str):
        self.pos = pos
        self.text = text
    def __str__(self):
        return f'Word({self.pos},{self.text})'
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

# def treeParsing(input:)->:
#     pass