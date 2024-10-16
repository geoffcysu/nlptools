from ArticutAPI import Articut
from pprint import pprint

import json
import re
import os

with open("account.info", "r", encoding="utf-8") as f:
    accountDICT = json.load(f)
    
username = accountDICT['username']
apikey   = accountDICT['apikey']
articut = Articut(username, apikey)

def render_pat():
    '''
    For me, I will just assume some possible "Cs" here. This is just a rough sketch of a parsing process.
    This process will further be formalized. e.g., parseCP(parseSTR, head_dir=FALSE, patDICT)
    The "head_dir" parameter decides whether it should be "LEFT/COMP" or "RIGHT/COMP".
    The patterns for heads and funciton parameters will be continuously updated to align with linguistic studies.
    '''
    C_pat = re.compile("</ACTION_verb>(<ACTION_verb>說</ACTION_verb>)")
    Mod_pat =  re.compile("(<MODAL>[^<]+</MODAL>)")
    LightV_pat = re.compile("(<ACTION_lightVerb>[^<]+</ACTION_lightVerb>)")
    #Asp_pat = re.compile("<ASPECT>了</ASPECT>") I am not sure about this yet. Maybe a head-final structure.
    Det_pat = re.compile("(<FUNC_degreeHead>很</FUNC_degreeHead>)") #I leave possibility for adj. predicates. e.g., 我很高。
    #Adv_pat = re.compile("<ModifierP>[^<]+(地)</ModifierP>")
    V_pat = re.compile("(<(ACTION_verb|VerbP)>[^<]+</(ACTION_verb|VerbP)>)")
    Cls_pat =  re.compile("(<ENTITY_classifier>[^<]+</ENTITY_classifier>)")
    RC_pat = re.compile("(<FUNC_inner>的</FUNC_inner>)")
    De_Comp_pat = re.compile("(<FUNC_inner>得</FUNC_inner>)")
    N_pat = re.compile("(<ENTITY_(nounHead|nouny|noun|oov)>[^<]+</ENTITY_(nounHead|nouny|noun|oov)>)")
    
    patDICT = {
        "C_pat": C_pat,
        "Mod_pat": Mod_pat,
        "LightV_pat": LightV_pat,
        #"Asp_pat": Asp_pat,
        "Det_pat": Det_pat,
        "V_pat": V_pat,
        "Cls_pat": Cls_pat,
        "RC_pat": RC_pat,
        "De_Comp_pat": De_Comp_pat,
        "N_pat": N_pat
    }
    
    return patDICT


def parse_CP(parseSTR, patDICT):
    '''
    1. Target the "C".
    2. Take the string on the right as "COMP" and leave the rest as "LEFT".
    '''
    try:
        C = re.search(patDICT['C_pat'], parseSTR).group(1)
        CP_comp = parseSTR.split(C)[-1]
        CP_left = parseSTR.split(C)[0]        
    except:
        C = "∅"
        CP_comp = parseSTR
        CP_left = "∅"
            
    CP =  {
        "LEFT": CP_left,
        "HEAD": C,
        "COMP": CP_comp
    }
    
    return CP 

def parse_ModP(CP_comp, patDICT):
    try:        
        Mod = re.search(patDICT['Mod_pat'], CP_comp).group(1)
        ModP_comp = CP_comp.split(Mod)[-1]
        ModP_left = CP_comp.split(Mod)[0]
    except:
        Mod = "∅"
        ModP_comp = CP_comp
        ModP_left = "∅"      
    
    ModP =  {
        "LEFT": ModP_left,
        "HEAD": Mod,
        "COMP": ModP_comp
    }    
    
    return ModP

def parse_LightVP(ModP_comp, patDICT):
    try:
        LightV = re.search(patDICT['LightV_pat'], ModP_comp).group(1)
        LightVP_comp = ModP_comp.split(LightV)[-1]
        LightVP_left = ModP_comp.split(LightV)[0]           
    except:
        LightV = "∅"
        LightVP_comp = ModP_comp
        LightVP_left = "∅"
        
    LightVP =  {
        "LEFT": LightVP_left,
        "HEAD": LightV,
        "COMP": LightVP_comp
    }    
    
    return LightVP

def parse_VP(LightVP_comp, patDICT):
    try:
        V = re.search(patDICT['V_pat'], LightVP_comp).group(1)
        VP_comp = LightVP_comp.split(V)[-1]
        VP_left = LightVP_comp.split(V)[0]
        VP =  {
            "LEFT": VP_left,
            "HEAD": V,
            "COMP": VP_comp
        }    
        
        return VP
    
    except:
        try:    
            Det = re.search(patDICT['Det_pat'], LightVP_comp).group(1)
            DetP_comp = LightVP_comp.split(Det)[-1]
            DetP_left = LightVP_comp.split(Det)[0]
            DetP =  {
                "LEFT": DetP_left,
                "HEAD": Det,
                "COMP": DetP_comp
            }
            return DetP
        
        except:
            print("--------------------------------------------------------------------------")
            print("\nCannot Find Predicate.\nThis Is NOT A Complete Grammatical Sentence.")
            VP =  {
                "LEFT": "∅",
                "HEAD": "∅",
                "COMP": "∅"
            }    
            return VP            
            
def parse_ClsP(VP_comp, patDICT):
    try:
        Cls = re.search(patDICT['Cls_pat'], VP_comp).group(1)
        ClsP_comp = VP_comp.split(Cls)[-1]
        ClsP_left = VP_comp.split(Cls)[0]
    except:
        Cls = "∅"
        ClsP_comp = VP_comp
        ClsP_left = "∅"
    
    ClsP =  {
        "LEFT": ClsP_left,
        "HEAD": Cls,
        "COMP": ClsP_comp
    }    
    
    return ClsP

def parse_RC(ClsP_comp, patDICT):
    RC_De = re.search(patDICT['RC_pat'], ClsP_comp).group(1)
    RC_right = ClsP_comp.split(RC_De)[-1]
    RC_left = ClsP_comp.split(RC_De)[0]    
    
    RC =  {
        "LEFT": RC_left,
        "HEAD": RC_De,
        "RIGHT": RC_right
    }    
    
    return RC    

def parse_NP(ClsP_comp, patDICT):
    try:    
        N = re.search(patDICT['N_pat'], ClsP_comp).group(1)
        try:
            RC = parse_RC(ClsP_comp, patDICT)
            N = RC["RIGHT"]
            NP_comp = ClsP_comp.split(N)[-1]
            NP_left = RC["LEFT"] + RC["HEAD"]
        except:
            NP_comp = ClsP_comp.split(N)[-1]
            NP_left = ClsP_comp.split(N)[0]            
            
    except:
        N = "∅"
        NP_comp = ClsP_comp.split(N)[-1]
        NP_left = "∅"   
    
    NP =  {
        "LEFT": NP_left,
        "HEAD": N,
        "COMP": NP_comp
    }    
    
    return NP

def parse_De_CompP(VP_comp, patDICT):
    try:
        De_Comp = re.search(patDICT['De_Comp_pat'], VP_comp).group(1)
        De_CompP_comp = VP_comp.split(De_Comp)[-1]
        De_CompP_left = VP_comp.split(De_Comp)[0]
    except:
        De_Comp = "∅"
        De_CompP_comp = VP_comp
        De_CompP_left = "∅"
    
    De_CompP =  {
        "LEFT": De_CompP_left,
        "HEAD": De_Comp,
        "COMP": De_CompP_comp
    }    
    
    return De_CompP    

def parse_S(parseSTR):
    patDICT = render_pat()
    
    CP = parse_CP(parseSTR, patDICT)
    print("\n CP")
    pprint(CP)
    
    print("\n IP")
    pprint(CP)    
    
    ModP = parse_ModP(CP["COMP"], patDICT)
    print("\n ModP")
    pprint(ModP)
    
    LightVP = parse_LightVP(ModP["COMP"], patDICT)
    print("\n LightVP")
    pprint(LightVP)
    
    VP = parse_VP(LightVP["COMP"], patDICT)
    if list(VP.values()) == ["∅","∅","∅"]:
        return "UNGRAMMATICAL SENTENCE."
    else:
        print("\n VP/ADJ PredicateP")
        pprint(VP)
    
    ClsP = parse_ClsP(VP["COMP"], patDICT)
    if ClsP["HEAD"] != "∅":        
        print("\n ClsP")
        pprint(ClsP)
    else:
        pass
    
    NP = parse_NP(ClsP["COMP"], patDICT)
    if NP["HEAD"] != "∅":
        print("\n NP")
        pprint(NP)
    else:
        pass    
    
    De_CompP = parse_De_CompP(VP["COMP"], patDICT)
    if De_CompP["HEAD"] != "∅":
        print("\n De_CompP")
        pprint(De_CompP)
    else:
        pass     
    
    S = {
        "CP": CP,
        "ModP": ModP,
        "LightVP": LightVP,
        "VP/PredP": VP,
        "ClsP": ClsP,
        "NP": NP,
        "De_CompP": De_CompP
    }
    
    return S

if __name__ == '__main__':
    '''
    These examples help understand the parsing process.
    
    我覺得說他可以被吃五碗他喜歡的飯。(It's a weird but I just want to display all the Ps.)
    他可以吃五碗飯。(without a C)
    他吃五碗飯。(without a Modal)
    她參加比賽。(without a Classifier)
    他很高。(without a Verb. But MC allows Det-Adj Predicate/VP Predicate.)
    他跑得很快（VP without Complement NP but a "De" complement instead.）
    他吃了他喜歡的零食。(RC）
    他吃了五包他喜歡的零食。(RC and Classifier）
    他白飯。(Ungrammatical)
    '''
    userINPUT = "我覺得說他可以被吃五碗他喜歡的飯，他可以吃五碗飯，他吃五碗飯，她參加比賽，他很高，他跑得很快，他吃了他喜歡的零食，他吃了五包他喜歡的零食，他白飯。"
    inputLIST = userINPUT.split("，")
    
    for inputSTR in inputLIST:
        resultDICT = articut.parse(inputSTR, level="lv1")
        parseSTR = ''.join(resultDICT['result_pos'])
        pprint(parseSTR)
        
        S = parse_S(parseSTR)
        print("\n")
        print("--------------------------------------------------------------------------")
    #S2 = parse_S(S["CP"]["LEFT"])
    #print("\n S")
    #pprint(S)
    
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