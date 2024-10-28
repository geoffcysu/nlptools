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
    Mod_pat =  re.compile("(<MODAL>[^<]+</MODAL>|<MODIFIER>可能</MODIFIER>)")
    Neg_pat = re.compile("(<FUNC_negation>[^<]+</FUNC_negation>)")
    LightV_pat = re.compile("(<ACTION_lightVerb>[^<]+</ACTION_lightVerb>)")
    #Asp_pat = re.compile("<ASPECT>了</ASPECT>") I am not sure about this yet. Maybe a head-final structure.
    Det_pat = re.compile("(<FUNC_degreeHead>很</FUNC_degreeHead>)") #I leave possibility for adj. predicates. e.g., 我很高。
    #Adv_pat = re.compile("<ModifierP>[^<]+(地)</ModifierP>")
    V_pat = re.compile("(?<!<FUNC_inner>的</FUNC_inner>)(<(ACTION_verb|VerbP)>[^<]+</(ACTION_verb|VerbP)>|<AUX>是</AUX>|<FUNC_inner>在</FUNC_inner>)(?!<FUNC_inner>的</FUNC_inner>)")
    Cls_pat =  re.compile("(<ENTITY_classifier>[^<]+</ENTITY_classifier>)")
    RC_pat = re.compile("(<FUNC_inner>的</FUNC_inner>)")
    De_Comp_pat = re.compile("(<FUNC_inner>得</FUNC_inner>)")
    N_pat = re.compile("(<ENTITY_(nounHead|nouny|noun|oov|pronoun)>[^<]+</ENTITY_(nounHead|nouny|noun|oov|pronoun)>)")
    
    patDICT = {
        "C_pat": C_pat,
        "Mod_pat": Mod_pat,
        "Neg_pat": Neg_pat, 
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

def parse_IP(CP_comp, patDICT):
    IP = {
        "LEFT": "",
        "HEAD": "∅",
        "COMP": CP_comp
    }
    
    return IP

def parse_ModP(IP_comp, patDICT):
    try:        
        Mod = re.search(patDICT['Mod_pat'], IP_comp).group(1)
        ModP_comp = IP_comp.split(Mod)[-1]
        ModP_left = IP_comp.split(Mod)[0]
    except:
        Mod = ""
        ModP_comp = IP_comp
        ModP_left = ""      
    
    ModP =  {
        "LEFT": ModP_left,
        "HEAD": Mod,
        "COMP": ModP_comp
    }    
    
    return ModP

def parse_NegP(ModP_comp, patDICT):
    try:
        Neg = re.search(patDICT['Neg_pat'], ModP_comp).group(1)
        NegP_comp = ModP_comp.split(Neg)[-1]
        NegP_left = ModP_comp.split(Neg)[0]           
    except:
        Neg = ""
        NegP_comp = ModP_comp
        NegP_left = ""
        
    NegP =  {
        "LEFT": NegP_left,
        "HEAD": Neg,
        "COMP": NegP_comp
    }    
    
    return NegP    

def parse_LightVP(NegP_comp, patDICT):
    try:
        LightV = re.search(patDICT['LightV_pat'], NegP_comp).group(1)
        LightVP_comp = NegP_comp.split(LightV)[-1]
        LightVP_left = NegP_comp.split(LightV)[0]           
    except:
        LightV = "∅"
        LightVP_comp = NegP_comp
        LightVP_left = "∅"
        
    LightVP =  {
        "LEFT": LightVP_left,
        "HEAD": LightV,
        "COMP": LightVP_comp
    }    
    
    return LightVP

def parse_VP(LightVP_comp, NegP, patDICT):
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
            if NegP["HEAD"] == "":                
                print("--------------------------------------------------------------------------")
                print("\nCannot Find Predicate.\nThis Is NOT A Complete Grammatical Sentence.")
                VP =  {
                    "LEFT": "",
                    "HEAD": "",
                    "COMP": ""
                }    
                return VP
            
            else:
                VP = NegP
                
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
    try:            
        RC_De = re.search(patDICT['RC_pat'], ClsP_comp).group(1)
        RC_right = ClsP_comp.split(RC_De)[-1]
        RC_left = ClsP_comp.split(RC_De)[0]
        
        RC =  {
            "LEFT": RC_left,
            "HEAD": RC_De,
            "RIGHT": RC_right
        }    
        
        return RC        
    except:
        return None
    
def parse_NP(ClsP_comp, patDICT):
    RC = parse_RC(ClsP_comp, patDICT)
    if RC == None:
        try:
            N = re.search(patDICT['N_pat'], ClsP_comp).group(1)
            NP_comp = ClsP_comp.split(N)[-1]
            NP_left = ClsP_comp.split(N)[0]
        except:
            N = "∅"
            NP_comp = ClsP_comp.split(N)[-1]
            NP_left = "∅"            
    
    else:
        N = RC["RIGHT"]
        NP_comp = ClsP_comp.split(N)[-1]
        NP_left = RC["LEFT"] + RC["HEAD"]
    
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
    
    IP = parse_IP(CP["COMP"], patDICT)
    print("\n IP")
    pprint(IP)    
    
    ModP = parse_ModP(IP["COMP"], patDICT)
    if ModP["HEAD"] == "":
        pass
    else:    
        print("\n ModP")
        pprint(ModP)
        
    NegP = parse_NegP(ModP["COMP"], patDICT)
    if NegP["HEAD"] == "":
        pass
    else:    
        print("\n NegP")
        pprint(NegP)    
    
    LightVP = parse_LightVP(NegP["COMP"], patDICT)
    print("\n LightVP")
    pprint(LightVP)
    
    VP = parse_VP(LightVP["COMP"], NegP, patDICT)
    if VP["HEAD"] == "" and NegP["HEAD"] == "":
        return "UNGRAMMATICAL SENTENCE."
    elif VP["HEAD"] == "" and NegP["HEAD"] != "":
        print("\n VP/ADJ PredicateP")
        pprint(NegP)      
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
        "IP": IP,
        "ModP": ModP,
        "NegP": NegP,
        "LightVP": LightVP,
        "VP/PredP": VP,
        "ClsP": ClsP,
        "NP": NP,
        "De_CompP": De_CompP
    }
    
    return S

def EPP_movement(treeDICT, patDICT):
    if treeDICT["IP"]["LEFT"] == '':
        for max_proj, inter_proj in treeDICT.items():
            if inter_proj.get("LEFT") != '' and inter_proj.get("LEFT") != '∅':
                Subj_P = parse_NP(treeDICT[max_proj]["LEFT"], patDICT)
                treeDICT["IP"]["COMP"] = treeDICT["IP"]["COMP"].replace("{}".format(treeDICT[max_proj]["LEFT"]), "<trace>t</trace>")
                treeDICT[max_proj]["LEFT"] = "<trace>t</trace>"
                break
        try:
            treeDICT["IP"]["LEFT"] = Subj_P
        except UnboundLocalError:
            treeDICT["IP"]["LEFT"] = "<Pro>Pro_Support</Pro>"
            
    else:
        pass
    
    return treeDICT

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
    userINPUT = "我同學的弟弟喜歡我哥哥的女朋友。"
    inputLIST = userINPUT.split("，")
    
    for inputSTR in inputLIST:
        patDICT = render_pat()
        resultDICT = articut.parse(inputSTR, level="lv1")
        parseSTR = ''.join(resultDICT['result_pos'])
        pprint(parseSTR)
        
        S = parse_S(parseSTR)
        print("\n")
        print("--------------------------------------------------------------------------")
        print("EPP: Subject NP/DP moves from theta position (vP/VP) to SpecTP.")
        print("\n")
        pprint(userINPUT)
        
        try:
            EPP_mv = EPP_movement(S, patDICT)
            print("\n Overt Subject")
            pprint(EPP_mv["IP"]["LEFT"])
            
            print("\n IP")
            pprint(EPP_mv["IP"])
            print("\n VP/PredP")
            pprint(EPP_mv["VP/PredP"])     
        
        except:
            print("\n Ungrammatical")
        
        #Subj = parse_NP(S["VP/PredP"]["LEFT"], patDICT)
        #pprint(Subj)
        #print("\n")
        #print("--------------------------------------------------------------------------")
        
        #pprint(S)
        
        #Subj_P = parse_NP(S["IP"]["COMP"], patDICT)
        #pprint(Subj_P)
        
        
        #for max_proj, inter_proj in S.items():
            #if inter_proj.get("LEFT") != '∅':
                #Subj_P = parse_NP(S[max_proj]["LEFT"], patDICT)
                #break
        
        #S["IP"]["LEFT"] = Subj_P
        
        #pprint(userINPUT)
        #print("\n")
        #print("IP")
        #pprint(S["IP"])
        #print("VP/PredP")
        #pprint(S["VP/PredP"])

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