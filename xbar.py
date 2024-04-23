
from icecream import ic
from syntax_tree.parser import parserOfRules

"""
recently implemented:
    * comment in rule def
    * "findP" function (given a POS-tagged-string and find out the given phrase parser)


TODO:
r{t[^>]*} ==> r{t.*}
logging parsing process
leave a space for SPEC, but not adjunct
    and binary tree printing issue
problem of infinite loop
    X' -> X' ADJUNCT
<MODIFIER>(very|so)</MODIFIER>

"""

new_rules = """
NP -> NP_SPEC? N'
NP_SPEC -> DP
N' -> N NP_COMP?
    | NP_ADJUNCT N'
    | N' NP_ADJUNCT
NP_ADJUNCT -> PP | AP
N -> r{ENTITY_[^>]*} | LOCATION
N_COMP -> NP

DP -> D'
D' -> D
D  -> ENTITY_possessive
    | ENTITY_num
    | FUNC_determiner


VP -> VP_SPEC V'
VP_SPEC -> NP
V' -> V VP_COMP
    | VP_ADJUNCT V'
    | V' VP_ADJUNCT
VP_ADJUNCT -> AP
V -> r{ACTION_[^>]*} | AUX | VerbP | MODAL
VP_COMP -> AP | NP | PP | VP 

AP -> AP_SPEC? A'
AP_SPEC -> DegreeP
A' -> A AP_COMP?
    | AP_ADJUNCT A'
    | A' AP_ADJUNCT
AP_ADJUNCT -> AP
A  -> MODIFIER
AP_COMP -> PP

PP -> PP_SPEC? P'
PP_SPEC -> DegreeP
P' -> P PP_COMP
    | PP_ADJUNCT P'
    | P' PP_ADJUNCT
PP_ADJUNCT -> PP
P  -> FUNC_inner | RANGE_locality
PP_COMP -> NP | PP

DegreeP -> Degree'
Degree' -> Degree

"""

simple_rules = """
VP -> VP_SPEC V'
V' -> V VP_COMP?
VP_SPEC -> DP
V -> r{ACTION_[^>]*} | AUX | ACTION_Verb | MODAL
VP_COMP -> DP

DP -> DP_SPEC? D'
D' -> D DP_COMP?
DP_SPEC -> ENTITY_person | DP
D -> ENTITY_possessive | FUNC_determiner
DP_COMP -> NP

NP -> N'
N' -> N NP_COMP?
N -> r{ENTITY_[^>]*}
NP_COMP -> PP

PP -> SPEC_PP? P'
P' -> P PP_COMP
P -> FUNC_inner
PP_SPEC -> AP
PP_COMP -> NP
"""
parserDict = parserOfRules(simple_rules)
# ic(parserDict)

t1 = "<ENTITY_pronoun>He</ENTITY_pronoun><AUX>is</AUX><MODIFIER>so</MODIFIER><MODIFIER>envious</MODIFIER><FUNC_inner>of</FUNC_inner><ENTITY_possessive>his</ENTITY_possessive><ENTITY_pronoun>sister</ENTITY_pronoun>"
t2 = "<FUNC_determiner>The</FUNC_determiner><ENTITY_noun>dog</ENTITY_noun><AUX>is</AUX><ENTITY_possessive>my</ENTITY_possessive><ENTITY_possessive>sister's</ENTITY_possessive><ENTITY_nouny>classmate</ENTITY_nouny><AUX>is</AUX><ENTITY_noun>dog</ENTITY_noun>"
test_VP = parserDict.ruleParser['VP']
test_VP.parse(t2).pprint()
#ic(parserDict.ruleParser['VP'].parse(t2))
# Degree  -> MODIFIER>(very|so|quite)</MODIFIER>


parserDict = parserOfRules(new_rules)

# t1 = "<ENTITY_pronoun>He</ENTITY_pronoun><AUX>is</AUX><Degree>so</Degree><MODIFIER>envious</MODIFIER><FUNC_inner>of</FUNC_inner><ENTITY_possessive>his</ENTITY_possessive><ENTITY_pronoun>sister</ENTITY_pronoun>"
# t2 = "<ENTITY_pronoun>He</ENTITY_pronoun> <AUX>is</AUX> <MODIFIER>friendly</MODIFIER>"
# t2 = "<ENTITY_pronoun>He</ENTITY_pronoun><AUX>is</AUX><MODIFIER>happy</MODIFIER>"
# t3 = "<MODIFIER>happy</MODIFIER>"
# parserDict.ruleParser['VP'].parse(t1).pprint()
# parserDict.ruleParser['VP'].parse(t2).pprint()
# parserDict.ruleParser['AP'].parse(t3).pprint()

