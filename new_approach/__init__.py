# -*- coding:utf-8 -*-

from treedata import VP,CP,ClsP,TP,AspP,NP,LightVP, Tree

"""
example:

VP[吃]
├──left:他
└──comp:ClsP[五碗]
        ├──left:""
        └──comp:NP[飯]
                ├──left:""
                └──comp:""

                
                 ┌────""
         ┌─NP────┴───飯
         │  └─......
 ┌─ClsP─五碗
 │  └─""
VP───吃
 └─他
                 ┌────comp:""
         ┌─NP────┴───head:飯
         │  └─left:......
 ┌─ClsP─head:五碗
 │  └─left:""
VP───head:吃
 └─left:他
               

# full NP

              ┌──""
         ┌──N'┴─飯
    ┌──N'──香香的
 ┌─N'─軟軟的
NP──""
              ┌──comp:""
         ┌──N'┴────N:飯
    ┌──N'┴─adjt:香香的
 ┌─N'─adjt:軟軟的
NP──spec:""

       ┌───────""
NP─────┴──────飯
 └─軟軟的,香香的
       ┌───────comp:""
NP─────┴──────head:飯
 └─left:軟軟的,香香的

# AspP example and movement

input = "被騙了五千元"

        ┌────────────────────────了
        │              ┌─◁ 五千元
        │       ┌──VP──┴─騙
        │       │   └─""
  ┌─AspP┴LightVP┴被
  │  │    └─""
  │  └─""
IP─""
 └─""

                       ┌─◁ 五千元
        ┌─了           │
        │       ┌──VP──┴─騙
        │       │   └─""
  ┌─AspP┴LightVP┴被
  │  │    └─""
  │  └─""
IP─""
 └─""





"""



ex1 = VP(head = "吃"
        ,left = "他"
        ,comp = ClsP(head = "五碗"
                    ,left = ""
                    ,comp = NP(head = "飯"
                              ,left = ""
                              ,comp = ""  
                              )
                    )
        )


# 我昨天吃了五碗飯
ex2 = CP(left='',
   head='∅',
   comp=TP(left='',
           head='∅',
           comp=AspP(left='<ENTITY_pronoun>我</ENTITY_pronoun><TIME_day>昨天</TIME_day>',
                     head='<ASPECT>了</ASPECT>',
                     comp=LightVP(left='',
                                  head='∅',
                                  comp=VP(left='',
                                          head='<ACTION_verb>吃</ACTION_verb>',
                                          comp=ClsP(left='',
                                                    head='<ENTITY_classifier>五碗</ENTITY_classifier>',
                                                    comp=NP(left='',
                                                            head='<ENTITY_nouny>飯</ENTITY_nouny>',
                                                            comp='')))))))


"""
# 我昨天吃了五碗飯
expected print:

                                      ┌─""
                                 ┌─NP─┴飯
                                 │  └─""
                           ┌─ClsP┴五碗
                           │  └─""
              ┌─了         │
              │       ┌─VP─┴吃
              │       │  └─""
        ┌─AspP┴LightVP┴ø
        │  │    └─""
        │  └─我昨天
   ┌─TP─┴ø
   │  └─""
CP─┴ø
 └─""

                             ┌─ClsP◁ 五碗飯
                        ┌─VP─┴吃
                        │  └─""
                ┌LightVP┴ø
                │ └─""
        ┌─AspP──┴─了
        │  └─我昨天
   ┌─TP─┴ø
   │  └─""
CP─┴ø
 └─""

 
Apply EPP movement

                           ┌─ClsP◁ 五碗飯
              ┌─了         │
              │       ┌─VP─┴吃
        ┌─AspP┴LightVP┴ø
        │  │    └─""
        │  └─[]昨天
   ┌─TP─┴ø   ║
   │  └─我 <═╝
CP─┴ø
 └─""

then apply verb raising

                           ┌─ClsP◁ 五碗飯
              ┌─吃了 <══════╪╗
              │       ┌─VP─┴[]
        ┌─AspP┴LightVP┴ø
        │  │    └─""
        │  └─[]昨天
   ┌─TP─┴ø   ║
   │  └─我 <═╝
CP─┴ø
 └─""


 

 備案:
                 ┌─ClsP◁ 五碗飯
    ┌─了         │
    │       ┌─VP─┴吃
    │       │  └─""
AspP┴LightVP┴ø
 │    └─""
 └─我昨天





"""


def swap(t1:Tree, field1:str, t2:Tree, field2:str):
    temp = t1.__dict__[field1]
    t1.__dict__[field1] = t2.__dict__[field2]
    t2.__dict__[field2] = temp

if __name__ == '__main__':
    ...