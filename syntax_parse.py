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
    V_pat = re.compile("(<(ACTION_verb|VerbP)>[^<]+</(ACTION_verb|VerbP)>)")
    Cls_pat =  re.compile("(<ENTITY_classifier>[^<]+</ENTITY_classifier>)")
    N_pat = re.compile("(<ENTITY_(nounHead|nouny|noun|oov)>[^<]+</ENTITY_(nounHead|nouny|noun|oov)>)")
    
    patDICT = {
        "C_pat": C_pat,
        "Mod_pat": Mod_pat,
        "LightV_pat": LightV_pat,
        #"Asp_pat": Asp_pat,
        "Det_pat": Det_pat,
        "V_pat": V_pat,
        "Cls_pat": Cls_pat,
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
            pprint("Cannot Find Predicate.")
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

def parse_NP(ClsP_comp, patDICT):
    try:    
        N = re.search(patDICT['N_pat'], ClsP_comp).group(1)
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

def parse_S(parseSTR):
    patDICT = render_pat()
    
    CP = parse_CP(parseSTR, patDICT)
    print("\n CP")
    pprint(CP)
    
    ModP = parse_ModP(CP["COMP"], patDICT)
    print("\n ModP")
    pprint(ModP)
    
    LightVP = parse_LightVP(ModP["COMP"], patDICT)
    print("\n LightVP")
    pprint(LightVP)
    
    VP = parse_VP(LightVP["COMP"], patDICT)
    print("\n VP/ADJ PredicateP")
    pprint(VP)
    
    ClsP = parse_ClsP(VP["COMP"], patDICT)
    print("\n ClsP")
    pprint(ClsP)
    
    NP = parse_NP(ClsP["COMP"], patDICT)
    print("\n NP")
    pprint(NP)
    
    S = {
        "CP": CP,
        "ModP": ModP,
        "LightVP": LightVP,
        "VP": VP,
        "ClsP": ClsP,
        "NP": NP
    }
    
    return S

if __name__ == '__main__':
    inputSTR = "他很高"
    resultDICT = articut.parse(inputSTR, level="lv1")
    parseSTR = ''.join(resultDICT['result_pos'])
    pprint(parseSTR)
    
    S = parse_S(parseSTR)
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