
# moving code in parse_syntax.py to here

from ArticutAPI import Articut
from dataclasses import dataclass
import json
import re

class Static:
    def __new__(cls):
        raise TypeError('Static classes cannot be instantiated')

has_articut_account = False    
try:
    with open("account.info", "r", encoding="utf-8") as f:
        accountDICT = json.load(f)

    username = accountDICT['username']
    apikey   = accountDICT['apikey']
    articut = Articut(username, apikey)
    has_articut_account = True
except Exception as e:
    print("Warning, Articut account info (account.info) wasn't successfully loaded.")

# RE notes:
# 0. (?P<name>pat)  the matched string can be retrieved with the name
#     re.search(r'\[(?P<content>\w)]', '[x]').group('content') === 'x' 
#     re.search('(?P<word>\w)(?P=word)','aa')  matches with two same characters
# 1. group order of nested parentheses is outer->inner. For example:
#     re.search(r'((ab)+)',"abab").group(1) === "abab"
#     re.search(r'((ab)+)',"abab").group(2) === "ab"
# 2. (?:...) 
#     the pattern (the ... part) cannot be retrieved by group
# 3. (?<!pat1)pat2  the negative lookbehind assertion (the positive version: (?<=pat1)pat2)
#     the matched pat2 string shouldn't be preceded by pat1
#     re.search(r'(?<!-)\w','-a b') === match='b'
# 4. pat1(?=pat2)  the lookahead assertion
#     re.search('Issac (?=Asimov)','Issac Asimov') === match='Issac '
#     re.search('Issac (?=Asimov)','Issac Ryan') === fails
# 5. +? *? ??  non-greedy quantifiers
#     re.search(r'<.+>','<a>b</a>') === match='<a>b</a>' 
#     re.search(r'<.+?>','<a>b</a>') === match='<a>' 
class HeadPatterns(Static):
    C_pat: re.Pattern = re.compile(
        "((?<!</ACTION_verb>)(?<!</FUNC_inner>)<ASPECT>了</ASPECT>$" 
            #「了」前面不能有ACTION_verb,FUNC_inner
         "|<(?P<clause>CLAUSE_(particle|YesNoQ))>.+?</(?P=clause)>"
            #CLAUSE_x 前後要一致
        ")"
        )

    Mod_pat: re.Pattern =  re.compile(
        "((<MODAL>.+?</MODAL>"
         "|<MODIFIER>可能</MODIFIER>"
         "|<ACTION_verb>要</ACTION_verb>"
         "|<CLAUSE_AnotAQ>.+?會</CLAUSE_AnotAQ>)"
        ")"
        )

    #!!TODO redundant parentheses? 
    #?? [就卻是]+ not [就卻是] ??
    # need evidence or proof for the patterns?
    Aux_pat: re.Pattern = re.compile(
        "(((?:<FUNC_inner>就</FUNC_inner>)?(?<!<FUNC_inner>還</FUNC_inner>)<AUX>[就卻是]+</AUX>"
          "|<CLAUSE_AnotAQ>[^<]+[^會]</CLAUSE_AnotAQ>"
         ")"
        ")"
        )
    
    Neg_pat: re.Pattern = re.compile(
        "(<FUNC_negation>[^<]+</FUNC_negation>(<ACTION_verb>要</ACTION_verb>)?)")

    LightV_pat: re.Pattern = re.compile("(<ACTION_lightVerb>[^<]+</ACTION_lightVerb>)")

    Asp_pat: re.Pattern = re.compile(
        "(((<ASPECT>[過了完著]+</ASPECT>)+)(?=<ACTION_lightVerb>)"
         "|((<ASPECT>[過了完著]+</ASPECT>)+)(?=<ACTION_verb>)"
         "|(<ASPECT>(?:(正在|在|已經))</ASPECT>)(?=<ACTION_verb>)"
         "|<ACTION_verb>[^<]+([過了完著])</ACTION_verb>)"
        )

    Deg_pat: re.Pattern = re.compile("(<FUNC_degreeHead>[太很]</FUNC_degreeHead>)") #I leave possibility for adj. predicates. e.g., 我很高。

    Adv_pat = re.compile(
        "((?:<FUNC_inner>所</FUNC_inner>)?<ModifierP>[^<]+地</ModifierP>"
         "|<FUNC_inner>從</FUNC_inner><[^>]+>[^<]+</[^>]+>"
         "|<FUNC_inter>[^<]+</FUNC_inter>"
         "|(?:<FUNC_inner>所</FUNC_inner>)?<[^>]+>[^<]+</[^>]+><FUNC_modifierHead>地</FUNC_modifierHead>"
         "|(?:<TIME_[a-z]+>[^<]+</TIME_[a-z]+>){1,10}(?:<RANGE_period>[^<]+</RANGE_period>)?"
         "|<QUANTIFIER>[^<]+</QUANTIFIER>"
        ")"
        )

    #Adj_pat = re.compile("(<MODIFIER>[^<]+</MODIFIER>(?:<FUNC_inner>的</FUNC_inner>)?)")
    
    P_pat: re.Pattern = re.compile("(<FUNC_inner>[從在]</FUNC_inner>|<ACTION_verb>到</ACTION_verb>)") #I did not know how to parse 在...裡面 yet.
    
    V_pat: re.Pattern = re.compile("(?<!<FUNC_inner>的</FUNC_inner>)((<(ACTION_verb|VerbP)>[^<用到]+</(ACTION_verb|VerbP)>|<FUNC_negation>沒有</FUNC_negation>)+(?:<FUNC_inner>[成向]</FUNC_inner>)?)(?!<FUNC_inner>的</FUNC_inner>)")

    Cls_pat: re.Pattern =  re.compile("(<ENTITY_classifier>[^<]+</ENTITY_classifier>)")

    RC_pat: re.Pattern = re.compile("(<FUNC_inner>的</FUNC_inner>|<MODIFIER_color>[^<]+</MODIFIER_color>)")

    De_Comp_pat: re.Pattern = re.compile("(<FUNC_inner>得</FUNC_inner>)")

    N_pat: re.Pattern = re.compile("((<ENTITY_(nounHead|nouny|noun|oov|pronoun)>[^<]+</ENTITY_(nounHead|nouny|noun|oov|pronoun)>|<TIME_[a-z]+>[^<]+</TIME_[a-z]+>|<LOCATION>[^<]+</LOCATION>|<RANGE_locality>[^<]+</RANGE_locality>|<FUNC_determiner>[^<]+</FUNC_determiner>|<CLAUSE_(What|Where|Who)Q>[^<]+</CLAUSE_(What|Where|Who)Q>)+)")
    
    Conj_pat: re.Pattern = re.compile("(<FUNC_conjunction>[^<]+</FUNC_conjunction>|<FUNC_inner>還</FUNC_inner><AUX>是</AUX>)")
