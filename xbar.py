
from icecream import ic
from syntax_tree.parser import parserOfRules

rules="""
VP -> VP_SPEC? VP'
VP' -> 
    | AP VP'
    | VP' AP
    | V VP_COMP
VP_SPEC -> FUNC_negation | ENTITY_pronoun
V -> r{ACTION_.*} | AUX | ACTION_Verb | MODAL
VP_COMP -> NP | PP | CP 

AP -> AP_SPEC? A'
A' -> AP_ADJUNCT A'
    | A AP_COMP
A -> MODIFIER
AP_ADJUNCT -> not_defined_yet
AP_COMP -> FUNC_inner ENTITY_possessive ENTITY_pronoun
"""

test_rules = """
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
parserDict = parserOfRules(test_rules)
# ic(parserDict)

t1 = "<ENTITY_pronoun>He</ENTITY_pronoun><AUX>is</AUX><MODIFIER>so</MODIFIER><MODIFIER>envious</MODIFIER><FUNC_inner>of</FUNC_inner><ENTITY_possessive>his</ENTITY_possessive><ENTITY_pronoun>sister</ENTITY_pronoun>"
t2 = "<FUNC_determiner>The</FUNC_determiner><ENTITY_noun>dog</ENTITY_noun><AUX>is</AUX><ENTITY_possessive>my</ENTITY_possessive><ENTITY_possessive>sister's</ENTITY_possessive><ENTITY_nouny>classmate</ENTITY_nouny><AUX>is</AUX><ENTITY_noun>dog</ENTITY_noun>"
test_VP = parserDict.ruleParser['VP']
test_VP.parse(t2).pprint()
#ic(parserDict.ruleParser['VP'].parse(t2))
