
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
parserDict = parserOfRules(rules)
# ic(parserDict)

t1 = "<ENTITY_pronoun>He</ENTITY_pronoun><AUX>is</AUX><MODIFIER>so</MODIFIER><MODIFIER>envious</MODIFIER><FUNC_inner>of</FUNC_inner><ENTITY_possessive>his</ENTITY_possessive><ENTITY_pronoun>sister</ENTITY_pronoun>"
t2 = "<ENTITY_pronoun>He</ENTITY_pronoun> <AUX>is</AUX> <MODIFIER>friendly</MODIFIER>"
ic(parserDict.ruleParser['VP'].parse(t1))