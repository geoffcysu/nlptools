from ArticutAPI import Articut
from dataclasses import dataclass
from pprint import pprint
from typing import Optional, Tuple, Callable, Union, TypeVar, Generic, Any

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



class HeadPatterns(Static):
    C_pat: re.Pattern = re.compile("</ACTION_verb>(<ACTION_verb>說</ACTION_verb>)")
    "\</ACTION_verb>(\<ACTION_verb>說\</ACTION_verb>)"

    Mod_pat: re.Pattern =  re.compile("(<MODAL>[^<]+</MODAL>|<MODIFIER>可能</MODIFIER>)")
    "(\<MODAL>[^<]+\</MODAL>)"

    Neg_pat: re.Pattern = re.compile("(<FUNC_negation>[^<]+</FUNC_negation>)")
    "(\<FUNC_negation>[^\<]+\</FUNC_negation>)"

    LightV_pat: re.Pattern = re.compile("(<ACTION_lightVerb>[^<]+</ACTION_lightVerb>)")
    "(\<ACTION_lightVerb>[^\<]+\</ACTION_lightVerb>)"

    Asp_pat: re.Pattern = re.compile("(</ACTION_verb>(<ASPECT>[過了著]+</ASPECT>)|(<ASPECT>[在]</ASPECT>)<ACTION_verb>|<ACTION_verb>[^<]+([過了著])</ACTION_verb>)")
    "(\</ACTION_verb>(\<ASPECT>[過了著]+\</ASPECT>)|(\<ASPECT>[在]\</ASPECT>)\<ACTION_verb>)"

    Deg_pat: re.Pattern = re.compile("(<FUNC_degreeHead>很</FUNC_degreeHead>)") #I leave possibility for adj. predicates. e.g., 我很高。
    "(\<FUNC_degreeHead>很\</FUNC_degreeHead>)"

    #Adv_pat = re.compile("<ModifierP>[^<]+(地)</ModifierP>")

    V_pat: re.Pattern = re.compile("(?<!<FUNC_inner>的</FUNC_inner>)(<(ACTION_verb|VerbP)>[^<]+</(ACTION_verb|VerbP)>|<AUX>是</AUX>|<FUNC_inner>在</FUNC_inner>)(?!<FUNC_inner>的</FUNC_inner>)")
    "(\<(ACTION_verb|VerbP)>[^\<]+\</(ACTION_verb|VerbP)>)"

    Cls_pat: re.Pattern =  re.compile("(<ENTITY_classifier>[^<]+</ENTITY_classifier>)")
    "(\<ENTITY_classifier>[^\<]+\</ENTITY_classifier>)"

    RC_pat: re.Pattern = re.compile("(<FUNC_inner>的</FUNC_inner>)")
    "(\<FUNC_inner>的\</FUNC_inner>)"

    De_Comp_pat: re.Pattern = re.compile("(<FUNC_inner>得</FUNC_inner>)")
    "(\<FUNC_inner>得\</FUNC_inner>)"

    N_pat: re.Pattern = re.compile("(<ENTITY_(nounHead|nouny|noun|oov|pronoun)>[^<]+</ENTITY_(nounHead|nouny|noun|oov|pronoun)>)+")
    "(\<ENTITY_(nounHead|nouny|noun|oov|pronoun)>[^\<]+\</ENTITY_(nounHead|nouny|noun|oov|pronoun)>)"

@dataclass
class Tree:
    left: str
    head: str
    comp: 'Union[str,Tree,list[str]]'


@dataclass
class Adjunct:
    left:str
    head:str
    right:str

# We consider only head-init for now.




def split_pos(pat:re.Pattern, src:str) -> Optional[Tuple[str,str,str]]:
    m = pat.search(src)
    if m is None:
        return None

    head_span = m.span()
    return (src[0:head_span[0]], #the string before pat
            m.group(1),          #the string that matches pat
            src[head_span[1]:])  #the string after pat


class CP(Tree):
    pass

def parse_CP(parseSTR: str)->CP:
    '''
    1. Target the "C".
    2. Take the string on the right as "COMP" and leave the rest as "LEFT".
    '''
    split = split_pos(HeadPatterns.C_pat, parseSTR)
    if split is None:
        return CP(left = ""
                  ,head = "∅"
                  ,comp = parseSTR
                  )
    else: 
        return CP(left=split[0], head=split[1], comp=split[2])
        #or simply `Tree(*split)`


class IP(Tree):
    pass

def parse_IP(CP_comp: str) -> IP:
    return IP(left = ""
              ,head = "∅"
              ,comp = CP_comp
              )


class ModP(Tree):
    pass

def parse_ModP(IP_comp: str) -> ModP:
    split = split_pos(HeadPatterns.Mod_pat, IP_comp)
    if split is None:
        return ModP(left = ""
                    ,head = ""
                    ,comp = IP_comp
                    )
    else:
        return ModP(*split)


class NegP(Tree):
    pass

def parse_NegP(ModP_comp: str) -> NegP:
    split = split_pos(HeadPatterns.Neg_pat, ModP_comp)
    if split is None:
        return NegP(left = ""
                    ,head = ""
                    ,comp = ModP_comp
                    )
    else:
        return NegP(*split)


class AspP(Tree): #https://www.persee.fr/doc/clao_0153-3320_1995_num_24_1_1466 Some reference for AspP, FYI. :)
    pass 

def parse_AspP(NegP_comp: str) -> AspP:
    split = split_pos(HeadPatterns.Asp_pat, NegP_comp)
    if split is None:
        return AspP(left = ""
                       ,head = ""
                       ,comp = NegP_comp
                       )
    else:
        '''
        I added the following lines to alter output.
        
        from:
        AspP(left='',
        head='<ASPECT>在</ASPECT><ACTION_verb>',
        comp='抽菸</ACTION_verb><ASPECT>了</ASPECT>')
        
        to:
        AspP(left='',
        head='<ASPECT>在</ASPECT>',
        comp='<ACTION_verb>抽菸</ACTION_verb><ASPECT>了</ASPECT>')
        '''
        
        if split[1].endswith("<ACTION_verb>") == True and split[2].startswith("<") == False:
            return AspP(left = split[0]
                        ,head = split[1][:-len("<ACTION_verb>")]
                        ,comp = "<ACTION_verb>" + split[2]
            )
        elif split[0].endswith(">") == False and split[1].startswith("</ACTION_verb>") == True:
            return AspP(left = split[0] + "</ACTION_verb>"
                        ,head = split[1][len("<ACTION_verb>") + 1:]
                        ,comp = split[2]
            )
        elif split[1].endswith("</ACTION_verb>") == True and split[1].startswith("<ACTION_verb>") == True:
            return AspP(left = split[0] + split[1][:len(split[1])-15:] + split[1][len(split[1])-14:]
                        ,head = "<ASPECT>" + split[1][len(split[1])-15] + "</ASPECT>"
                        ,comp = split[2]
            )            
        
        else:
            return AspP(*split)

class LightVP(Tree):
    pass

def parse_LightVP(NegP_comp: str) -> LightVP:
    split = split_pos(HeadPatterns.LightV_pat, NegP_comp)
    if split is None:
        return LightVP(left = ""
                       ,head = "∅"
                       ,comp = NegP_comp
                       )
    else:
        return LightVP(*split)


class VP(Tree):
    pass

class DegP(Tree):
    pass

def parse_VP(LightVP_comp: str, NegP:NegP)->Optional[Union[VP, DegP]]:
    split = split_pos(HeadPatterns.V_pat, LightVP_comp)
    #pprint(split)
    if split:
        return VP(*split)

    split = split_pos(HeadPatterns.Deg_pat, LightVP_comp)
    if split:
        return DegP(*split)

    if NegP.head == "":
        return VP(left = ""
                ,head = ""
                ,comp= ""
             )

    return VP(NegP.left
              ,NegP.head
             ,NegP.comp
             )


class ClsP(Tree):
    pass

def parse_ClsP(VP_comp: str) -> ClsP:
    split = split_pos(HeadPatterns.Cls_pat, VP_comp)
    if split is None:
        return ClsP(left = ""
                    ,head = ""
                    ,comp = VP_comp
                    )
    else:
        return ClsP(*split)

def parse_RC(ClsP_comp: str) -> Optional[Adjunct]:
    split = split_pos(HeadPatterns.RC_pat, ClsP_comp)
    if split is None:
        return None
    else: 
        return Adjunct(left=split[0], head=split[1], right=split[2])


class NP(Tree):
    pass

"""
issue here about parsing NP?
- Checking Cls_pat first or N_pat first?
"""

def parse_NP(ClsP: Tree, checkCLS: bool) -> NP:
    rc = parse_RC(ClsP.comp)
    if rc is None:
        '''
        here's a new sample for the n_head
        suppose N_COMP will always be ""
        when we find N + N (e.g., 我同學)
        instead of always getting the first 我
        i add line 284 285 as an example to capture longer nouns seperated by Articut
        
        p.s. Articut "我" will only be parsed as possessive when followed by a pronoun.
        when its possessive, it will be viewed as NP.left, which is perfectly correct.
        While its not, we might just see all the N+N as an N instead
        '''
        n_match = re.finditer(HeadPatterns.N_pat, ClsP.comp)
        n_head = ''.join(match.group(0) for match in n_match)
        split_n = split_pos(HeadPatterns.N_pat, ClsP.comp)
        if checkCLS == True and split_n is None:
            if ClsP.head != "":
                return NP(left = ""
                          ,head = "∅"
                          ,comp = ""
                          )
            else:
                return NP(left = ""
                          ,head = ""
                          ,comp = ""
                          )
        else:
                            
            #我吃五碗飯
            return NP(left = split_n[0],
                      head = n_head,
                      comp = ""
                      )
    else:
        #xx的yy
        return NP(
            left = rc.left + rc.head,
            head = rc.right,
            comp = "" #rc.comp.split(N)[-1] ??
        )


class De_CompP(Tree):
    pass

def parse_De_CompP(VP_comp: str) -> De_CompP:
    split = split_pos(HeadPatterns.De_Comp_pat, VP_comp)
    if split is None:
        return De_CompP(left = ""
                        ,head = ""
                        ,comp = VP_comp
                        )
    else:
        return De_CompP(*split)

"""
equivalent to writing:
CP -> ? !c_pat IP
    | ø ø IP
IP -> ø ModP
ModP -> ? !mod_pat NegP
    | "" "" NegP
NegP -> ? neg_pat LightVP
    | "" "" LightVP
LightVP -> ? lightV_pat (VP | DegP | [pred_on_neg])
    | ø ø (VP | DegP | [pred_on_neg])
VP -> ? v_pat (CP | ClsP)
DegP -> ? deg_pat ClsP
ClsP -> ? cls_pat NP
    | ø ø NP
NP -> (? rc_pat) ? ??
    | ? n_pat ?
    | ø ø ?

"""
# pred_on_neg: Tree -> input:str -> Either[Err,Tree] #how to represent the continuation?


def parse_S(parseSTR: str) -> dict:
    tCP = parse_CP(parseSTR)
    tIP = parse_IP(tCP.comp)
    tModP = parse_ModP(tIP.comp)
    tNegP = parse_NegP(tModP.comp)
    tAspP = parse_AspP(tNegP.comp)
    tLightVP = parse_LightVP(tNegP.comp)
    tVP = parse_VP(tLightVP.comp, tNegP)
    tClsP = parse_ClsP(tVP.comp)
    tNP = parse_NP(tClsP, True)
    tDe_CompP = parse_De_CompP(tVP.comp)

    treeDICT = {
        "CP": tCP,
        "IP": tIP,
        "ModP": tModP,
        "NegP": tNegP,
        "AspP": tAspP,
        "LightVP": tLightVP,
        "VP/PredP": tVP,
        "ClsP": tClsP,
        "NP": tNP,
        "De_CompP": tDe_CompP
    }
    
    '''
    Move LightV and V -- I haven't come up with a better solution so far.
    
    e.g., 被騙了五張卡
    
    AspP
    left 被騙
    head 了
    comp 五張卡
    
    TO
    
    AspP
    left 被
    head 了
    comp 騙五張卡
    
    TO
    
    AspP
    left 
    head 了
    comp 被騙五張卡
    '''
    if treeDICT["VP/PredP"].head in treeDICT["AspP"].left:
        v_index = treeDICT["AspP"].left.rfind(treeDICT["VP/PredP"].head)
        treeDICT["AspP"].comp = (treeDICT["AspP"].left[v_index:v_index + len(treeDICT["VP/PredP"].head)] +
                                 treeDICT["AspP"].comp)        
        treeDICT["AspP"].left = (treeDICT["AspP"].left[:v_index] +
                                 treeDICT["AspP"].left[v_index +len(treeDICT["VP/PredP"].head):])
        
    if treeDICT["LightVP"].head in treeDICT["AspP"].left:
        lightv_index = treeDICT["AspP"].left.rfind(treeDICT["LightVP"].head)
        treeDICT["AspP"].comp = (treeDICT["AspP"].left[lightv_index:lightv_index + len(treeDICT["LightVP"].head):] +
                                 treeDICT["AspP"].comp)        
        treeDICT["AspP"].left = (treeDICT["AspP"].left[:lightv_index] +
                                 treeDICT["AspP"].left[lightv_index + len(treeDICT["LightVP"].head):])
        
    '''
    from #419 to 431 is just a dumb way to get rid of the problem you mentioned 11/8 06:41.
    It works for all scenarios I can think of but still, it should be optimized.
    '''

    tLightVP = parse_LightVP(tAspP.comp)
    tVP = parse_VP(tLightVP.comp, tNegP)
    tClsP = parse_ClsP(tVP.comp)
    tNP = parse_NP(tClsP, True)
    tDe_CompP = parse_De_CompP(tVP.comp)
    
    treeDICT["LightVP"] = tLightVP
    treeDICT["VP/PredP"] = tVP
    treeDICT["ClsP"] = tClsP
    treeDICT["NP"] = tNP
    treeDICT["De_CompP"] = tDe_CompP
    
    return treeDICT

@dataclass
class EPP_movement():
    target_phrase: 'Union[str, Tree]'
    original_pos: str
    target_pos: str
    

def ex_EPP_movement(treeDICT: dict) -> (EPP_movement, dict):    
    if treeDICT["VP/PredP"].head == "" and treeDICT["NegP"].head == "":
        return None
    else:
        if treeDICT["IP"].left == "":
            for max_proj in ["ModP","NegP","AspP","LightVP","VP/PredP"]:
                try:
                    if treeDICT[max_proj].left != "":
                        subj = Tree(left="",
                                    head="",
                                    comp=treeDICT[max_proj].left)
                        treeDICT["IP"].left = parse_NP(subj, False)
                        treeDICT["IP"].comp = treeDICT["IP"].comp.replace("{}".format(treeDICT[max_proj].left), "<trace>t</trace>", 1)
                        treeDICT["LightVP"].left = "<trace>Subj_trace</trace>"
                        treeDICT[max_proj].left = treeDICT[max_proj].left.replace(treeDICT["IP"].left.left + treeDICT["IP"].left.head, "<trace>Subj_trace</trace>") # I considered the possibility which the max_proj.left contains ADVs other than just the Subject. So now only the Subject will be replaced.
                        try:    
                            for trace_pos in ["LightVP","AspP","NegP","ModP"]:
                                if "<trace>Subj_trace</trace>" not in treeDICT[trace_pos].left:
                                    treeDICT[trace_pos].left = "<trace>Subj_trace</trace>" + treeDICT[trace_pos].left
                        except KeyError:
                            continue
                        
                        return (EPP_movement(target_phrase = parse_NP(subj, False)
                                            , original_pos = max_proj + "_left"
                                            ,target_pos = "IP_left"
                                            ), 
                                treeDICT)
                except KeyError:
                    continue
            else:
                treeDICT["IP"].left = "<Pro>Pro_Support</Pro>"
                treeDICT["IP"].comp = "<trace>Subj_trace</trace>" + treeDICT["IP"].comp
                treeDICT["LightVP"].left = "<trace>Subj_trace</trace>"
                for trace_pos in ["LightVP","AspP","NegP","ModP"]:
                    try:    
                        if "<trace>Subj_trace</trace>" not in treeDICT[trace_pos].left:
                            treeDICT[trace_pos].left = "<trace>Subj_trace</trace>" + treeDICT[trace_pos].left
                    except KeyError:
                        continue
                return (EPP_movement(target_phrase = "<Pro>Pro_Support</Pro>" 
                                    , original_pos = "LightVP_left"
                                    ,target_pos = "IP_left"
                                    ),
                        treeDICT)


def output_tree(treeDICT: dict):
    if treeDICT["VP/PredP"].head == "" and treeDICT["NegP"].head == "":    
        print("--------------------------------------------------------------------------------------------------------------------------------")
        print("\nCannot Find Predicate.\nThis Is NOT A Complete Grammatical Sentence.")
        print("--------------------------------------------------------------------------------------------------------------------------------")
        
        return None
    
    else:        
        try:
            print("\n [CP]:")
            pprint(treeDICT["CP"])
            
            print("\n [IP]:")
            pprint(treeDICT["IP"])
            
            if treeDICT["ModP"].head == "":
                pass
            else:    
                print("\n [ModP]:")
                pprint(treeDICT["ModP"])
                
            if treeDICT["NegP"].head == "":
                pass
            else:    
                print("\n [NegP]:")
                pprint(treeDICT["NegP"])
                
            if treeDICT["AspP"].head == "":
                pass
            else:    
                print("\n [AspP]:")
                pprint(treeDICT["AspP"])            
            
            print("\n [LightVP]:")
            pprint(treeDICT["LightVP"])
                
            if treeDICT["VP/PredP"].head == "" and treeDICT["NegP"].head == "":
                pass
            elif treeDICT["VP/PredP"].head == "" and treeDICT["NegP"].head != "":
                print("\n [VP/ADJ PredicateP]:")
                pprint(treeDICT["NegP"])      
            else:
                print("\n [VP/ADJ PredicateP]:")
                pprint(treeDICT["VP/PredP"])
            
            if treeDICT["ClsP"].head != "":        
                print("\n [ClsP]:")
                pprint(treeDICT["ClsP"])
            else:
                pass
            
            if treeDICT["NP"].head == "":
                pass
            elif treeDICT["NP"].head == "∅":
                print("\n [NP: Is There An Elided NP?]")
                pprint(treeDICT["NP"])
            else:
                print("\n [NP]:")
                pprint(treeDICT["NP"])                    
            
            if treeDICT["De_CompP"].head != "":
                print("\n [De_CompP]:")
                pprint(treeDICT["De_CompP"])
            else:
                pass
            
            return "Successfully"
    
        except Exception as e:
            print("\n", e)
            raise

if __name__ == '__main__':
    inputSTR: int = "我昨天可能在修理汽車。" 
    
    #"我覺得說他可以被吃五碗他喜歡的飯。他可以吃五碗飯。他吃五碗飯。她參加比賽。他很高。他跑得很快。他吃了他喜歡的零食。他吃了五包他喜歡的零食。他白飯。樹上沒有葉子。"
    parseLIST = [i for i in articut.parse(inputSTR, level="lv1")["result_pos"] if len(i) > 1]
    for parseSTR in parseLIST:
    #parseSTR = parseLIST[0]
        print("*InputSTR:{}".format(inputSTR))
        treeDICT = parse_S(parseSTR)
        output_tree(treeDICT)
    
    print("\n")
    mvd_tree = ex_EPP_movement(treeDICT)
    print("*Narrow Syntax Operations:")
    pprint(mvd_tree[0])
    print("\n (Subject Will Be Replaced Back To Theta Position Beforehand. See Tree:)")
    print("\n")
    output_tree(mvd_tree[1])
    
    #EPP_mv = EPP_movement(treeDICT)
    #output_tree(EPP_mv)
    
    '''
    These examples help understand the parsing process.

    我覺得說他可以被吃五碗他喜歡的飯。(It's a weird but I just want to display all the Ps.)
    他可以吃五碗飯。(without a C)
    他吃五碗飯。(without a Modal)
    她參加比賽。(without a Classifier)
    他很高。(without a Verb. But MC allows Deg-Adj Predicate/VP Predicate.)
    他跑得很快。（VP without Complement NP but a "De" complement instead.）
    他吃了他喜歡的零食。(RC）
    他吃了五包他喜歡的零食。(RC and Classifier）
    他白飯。(Ungrammatical)
    樹上沒有葉子。(Neg)
    '''
    #userINPUT = "我覺得說他可以被吃五碗他喜歡的飯。他可以吃五碗飯。他吃五碗飯。她參加比賽。他很高。他跑得很快。他吃了他喜歡的零食。他吃了五包他喜歡的零食。他白飯。樹上沒有葉子。"
    #inputLIST = userINPUT.split("。")

    #pos_pat = "<[^>]+>[^<]+</[^>]+"

    #for inputSTR in inputLIST:
        #patDICT = render_pat()
        #if len(inputSTR) <= 1:
            #print("*************************************************************START-PARSE**************************************************************")
            #pprint("{} Is Not A Valid Input.".format(inputSTR))
            #print("\n")
            #print("*************************************************************END OF PARSE**************************************************************")
            #print("\n\n")
            #continue
        #else:
            #print("userINPUT: {}".format(inputSTR))
            #print("*************************************************************START-PARSE**************************************************************")
            #resultDICT = articut.parse(inputSTR, level="lv1")
            #parseSTR = ''.join(resultDICT['result_pos'])
            #wordLIST = re.findall(r'<[^>]+>[^<]+</[^>]+>', parseSTR)
            #print("Articut Result:\n")
            #pprint(wordLIST)
            #print("--------------------------------------------------------------------------------------------------------------------------------")

            #treeDICT = parse_S(parseSTR)
            #print("D-structure:")
            #output_tree(treeDICT)

        #try:
            #EPP_mv = EPP_movement(treeDICT, patDICT)
            ##pprint(inputSTR)            
            #if EPP_mv != False:
                #print("--------------------------------------------------------------------------------------------------------------------------------")
                #print("EPP: Subject NP/DP moves from theta position (vP/VP) to SpecTP.")                
                ##pprint(EPP_mv)
                #print("\n Overt Subject:")
                #pprint(EPP_mv[1][0]["LEFT"])

                #print("\n IP")
                #pprint(EPP_mv[1][0])
                #print("\n θ Theta PositionP")
                #pprint(EPP_mv[1][1])
                #print("================================================================================================================================")
                #print("*************************************************************SEND TO LF**************************************************************")
                #print("\n\n\n\n\n\n\n\n\n\n")

            #else:
                #print("================================================================================================================================")
                #print("*************************************************************SEND TO LF**************************************************************")
                #print("\n\n\n\n\n\n\n\n\n\n")

        #except:
            #print("\n Cannot Find [+EPP].")
            #print("================================================================================================================================")
            #print("*************************************************************SEND TO LF**************************************************************")
            #print("\n\n\n\n\n\n\n\n\n\n")           

    '''
    I hope the output goes like:

    /S
    /CP---+---CP.json {
          |               "SPEC_CP":"",
          |               "C":"",
          |               "COMP_CP":ModP
          |              }
          |
          |
          |---/ModP---+---ModP.json {
                                  "SPEC_ModP":"",
                                  "Mod":"",
                                  "COMP_ModP":LightVP
                                 }
    '''
    #os.mkdir("S")
    #CP_path = os.path.join("./S", "CP")
    #os.mkdir(CP_path)

    #with open("./S/CP/CP.json", "w", encoding="utf-8") as CP_file:
            #json.dump(S["CP"], CP_file, indent=4, ensure_ascii=False)