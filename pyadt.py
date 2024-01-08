#!/usr/bin/env python
from typing import Generic, TypeVar, Tuple, List, Literal, Optional, Dict, Iterable, Callable
from functools import partial
from itertools import chain,count
import sys
import io
import re
import parsy

from string import ascii_uppercase
upperCases : list[str] = [c for c in ascii_uppercase]

# 
# Run this script with an argument of a filepath, 
# it will generate the python scripts according to the type definition written
# in string blocks starting with "adt:\n".
#
# The generated script will be appended to the block where the type is defined.
# Here is an example of defining a linked-list:
#
# """ adt:
#
# data Lst a = Nil
#         | Cons a (Lst a)
#
# """
# 
# _A = TypeVar('_A')
# _T_ = TypeVar('_T_')
# class Lst(Generic[_A]):
#     "Is either Nil or Cons."
#     def match(self,*,
#               nil:_T_,
#               cons:Callable[[_A,'Lst[_A]'],_T_]
#               )->_T_:
#         ...

# class Nil(Lst[Any]):
#     def match(self,*,
#               nil:_T_,
#               cons:Callable[[_A,'Lst[_A]'],_T_]
#               )->_T_:
#         return nil
# nil = Nil()

# class Cons(Generic[_A],Lst[_A]):
#     data:_A
#     tail:Lst[_A]
#     def __init__(self,data:_A,tail:Lst[_A]):
#         self.data = data
#         self.tail = tail
#     def match(self,*,
#               nil:_T_,
#               cons:Callable[[_A,'Lst[_A]'],_T_]
#               )->_T_:
#         return cons(self.data,self.tail)

# def isCons(x:Lst[_A])->TypeGuard[Cons[_A]]:
#     return type(x) is Cons
# def isNil(x:Lst[Any])->TypeGuard[Nil]:
#     return type(x) is Nil



def main():
    print('success')
    # if len(sys.argv) != 2:
    #     print("Usage: python script.py <filename>")
    #     sys.exit(1)

    # filename = sys.argv[1]

    # # Prompt the user for their choice
    # choice = input("Do you want to print the file on the screen? (yes/no): ").strip().lower()




def process_the_file(filename):
    try:
        with open(filename, 'r') as file:
            content = file.read()


    except FileNotFoundError:
        print(f"Error: The file '{filename}' was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

    
def process_the_adt_block(input:str)->List[str]:
    """
    
    """
    toks = tokenize(input)
    dataDefs = parseAST(toks)


###------------------- AST --------------------------
    
example="""
data Lst[a] = Nil
            | Cons(_:a, tail:Lst[a])
data Maybe[b] = Nothing
              | Just(_:b)
"""

class TypeExpr:
    typeName:str
    args:List['TypeExpr']
    def __init__(self,typeName:str,args:List['TypeExpr']):
        self.typeName = typeName
        self.args = args
    def __str__(self) -> str:
        return self.replacedStr({})
    def replacedStr(self,replace_map:Dict[str,str])->str:
        x = replace_map.get(self.typeName)
        replaced = x if x else self.typeName
        if len(self.args)==0:
            return replaced
        else:
            return "{}[{}]".format(replaced, 
                                   ','.join(map(lambda x:x.replacedStr(replace_map),
                                                self.args)))

    def __repr__(self) -> str:
        return self.__str__()

class CtorArg:
    fieldName:str
    typ:TypeExpr
    def __init__(self,fieldName:str,typ:TypeExpr):
        self.fieldName = fieldName
        self.typ = typ
    def __str__(self):
        return self.fieldName+":"+str(self.typ)
    def __repr__(self) -> str:
        return self.__str__()

def lowercase_head(name:str)->str:
    return name[0].lower()+name[1:]
# def typeExpr_convert(typevar_map:Dict[str,str],te:TypeExpr)->str:
#     if len(te.args) == 0:
#         converted = typevar_map.get(te.typeName)
#         return converted if converted else te.typeName
#     else:
#         return "{}[{}]".format(
#             te.typeName,
#             ','.join(map(lambda x:typeExpr_convert(typevar_map,x), 
#                          te.args))
#         )

class Ctor:
    ctorName:str
    args:List[CtorArg]
    def __init__(self,ctorName:str,args:List[CtorArg]):
        """
        ctorName: leading by uppercase
        args: List[Tuple[lowercase identifier, type expression]]
        """
        self.ctorName = ctorName
        self.args = args
    def __str__(self):
        return self.ctorName + \
                f"({'' if len(self.args)==0 else ','.join(map(str,self.args))})"
    def __repr__(self) -> str:
        return self.__str__()
    


class DataDef:
    typeName:str
    typeVars:List[str]
    ctors:List[Ctor]
    def __init__(self,typeName:str,typeVars:List[str],ctors:List[Ctor]):
        """
        typeName: leading by uppercase
        typeVars: leading by lowercase
        """
        self.typeName = typeName
        self.typeVars = typeVars
        self.ctors = ctors
    def __str__(self):
        return "data {}{} = {}".format(
                    self.typeName,
                    '' if len(self.typeVars)==0 else f"[{','.join(self.typeVars)}]",
                    '\n\t| '.join(map(str,self.ctors))
                    )
    def __repr__(self) -> str:
        return self.__str__()


###----------
tokenize = lambda input:re.findall(r'data|[a-zA-Z_][\w]*|=|\||\(|\)|:|,|\[|\]',input)

###---------------- Parsers ----------------

identifier = parsy.test_item(str.isidentifier,'identifier')
upIdentifier = parsy.test_item(lambda x:str.isidentifier(x) and 
                                        str.isupper(x[0]),
                               'uppercase headed identifier')
loIdentifier = parsy.test_item(lambda x:str.isidentifier(x) and 
                                        (str.islower(x[0]) or x[0]=='_'),
                               'lowercase headed identifier')
def token(tok:str)->parsy.Parser:
    return parsy.test_item(lambda x:x==tok,'token:"'+tok+'"')


def parenList(paren:Literal['()','[]'],p:parsy.Parser)->parsy.Parser: 
    "return the parser of the list of result of p"
    return token(paren[0]) >> p.sep_by(token(','),min=1) << token(paren[1])

def optParenList(paren:Literal['()','[]'],p:parsy.Parser)->parsy.Parser:
    """
    Is different from parenList.optional(). parenList.optional() will still pass
    if the content between the parenthesis is in wrong format.
    When optParenList receives any lparen, the rest of the stream must then be 
    the right format.
    """
    @parsy.generate
    def g():
        lp = yield parsy.peek(token(paren[0]).optional())
        if lp is None:
            return None
        else:
            return (yield parenList(paren,p))
    return g

#typeexpt:Parser[Tuple[str,List[str]]]
@parsy.generate
def typeExpr_vars_only():
    id = yield identifier
    param = yield optParenList('[]',loIdentifier)
    return (id, param if param else [])


#Parser[TypeExpr]
typeExprP = parsy.forward_declaration()
@parsy.generate
def _typeExprP():
    id = yield identifier
    param:Optional[List[TypeExpr]] = yield optParenList('[]',typeExprP) 
    return TypeExpr(id,param if param else [])
typeExprP.become(_typeExprP)


@parsy.generate
def ctorP():
    ctor = yield upIdentifier
    params: Optional[List[CtorArg]] =\
        yield optParenList('()', 
                parsy.seq((loIdentifier << token(':')),
                            typeExprP
                ).combine(CtorArg).sep_by(token(',')))
    return Ctor(ctor,params if params else [])

def combine_DataDef(dataname:Tuple[str,List[str]],ctors:List[Ctor])->DataDef:
    return DataDef(dataname[0], dataname[1], ctors)
parseDataDef = parsy.seq(
    _data =    token('data'),
    dataname = typeExpr_vars_only,
    _eq =      token('='),
    ctors =    ctorP.sep_by(token('|'),min=1)
).combine_dict(combine_DataDef)

def parseAST(stream:List[str])->List[DataDef]:
    return parseDataDef.many().parse(stream)


###--------------- Code Generation ---------------------

def generate_code(datas:List[DataDef])->List[str]:
    # construct the typevar map
    # the idea: the typevar in ast map to an actual typevar name
    typevar_num = max(*map(lambda dd:len(dd.typeVars), datas))
    typevars = typevar_list(typevar_num)
    typevar_map = 
    gen_aux(typevar_num) # add 1 for the return type of matching, e.g., foldr: (a -> b -> b) -> b -> [a] -> b


def typevar_list(n:int)->List[str]:
    "Generate the list: _A,_B,_C..,_A1,_B1...,_A2,_B2,..."
    it = map(lambda x:'_'+x,
            chain(iter(upperCases),# chain: *Iterable[T] -> Iterable[T]
                chain.from_iterable(# from_iterable: Iterable[Iterable[T]]->Iterable[T]
                    #Iterable[Iterable[str]]
                    map(lambda i:map(lambda x:x+str(i),upperCases),
                        count(1)))
            )
        )
    return [next(it) for _ in range(n)]

def typevarMap(typevars:List[str],data:DataDef)->Dict[str,str]:
    return dict(zip(data.typeVars,
                    typevars))

def gen_aux(typevars:List[str])->List[str]:
    "Generate TypeVar declarations"

    return [ "from typing import TypeVar,TypeGuard,Generic,Callable",
             ','.join(typevars)\
                 + " = "\
                 + ','.join(map(lambda t:f"TypeVar('{t}')", typevars)),
             "_T_ = TypeVar('_T_')"
           ]

def ctorMatchSignature(retType:str,typevar_map:Dict[str,str])->Callable[[Ctor],str]:
    "example: Cons ==> 'cons:Callable[[_T,Lst[_T]],Lst[_T]]'"
    def f(ctor:Ctor)->str:
        return "{}: Callable[[{}], {}],"\
                .format(lowercase_head(ctor.ctorName),
                        ','.join(map(lambda x:x.typ.replacedStr(typevar_map), 
                                     ctor.args)),
                        retType
                )
    return f

def gen_match_signature(typevars:Dict[str,str], dataDef:DataDef)->List[str]:
    "Generate the match method's def clause and type signature."
    return ["def match(self,*,"]\
           + list(map(lambda l:"          "+l, # indentation
                      map(ctorMatchSignature('_T_',typevars), 
                          dataDef.ctors)))\
           + ["         )->_T_:"]
    
def gen_typedef():
    "Generate the class for the type, e.g., List"
    ...
def gen_ctors():
    "Generate the class for a constructor, e.g., Cons"
    ...

def gen_one_DataDef():
    ...

###-----------------------
        
from icecream import ic
if __name__ == "__main__":
    #main()  
    toks = tokenize(example)
    datas = parseAST(toks)
    print(gen_aux(3))
    
    