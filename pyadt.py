#!/usr/bin/env python
from typing import Generic, TypeVar, Tuple, List, Literal, Optional, Dict, Iterable, Callable, Iterator
from functools import partial
from itertools import chain,count,repeat
import sys
import io
import re
import parsy

from string import ascii_uppercase
_upperCases : list[str] = [c for c in ascii_uppercase]
indent = "    "

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
        if self.args:#len>0
            return "{}[{}]".format(self.typeName, 
                                   ','.join(map(str,self.args)))
        else:
            return self.typeName

    def __repr__(self) -> str:
        return self.__str__()
    
    @classmethod
    def from_mere_typevars(cls,typename:str, tvs:List[str])->'TypeExpr':
        return TypeExpr(typename,[TypeExpr(tv,[]) for tv in tvs])
    
    def subst_with_dict(self,typeVar_map:Dict[str,str])->'TypeExpr':
        "This method MUTATES the fields."
        if self.args:#len>0
            for te in self.args:
                te.subst_with_dict(typeVar_map)
        else:
            x = typeVar_map.get(self.typeName)
            if x:
                self.typeName = x
        return self
    
    def copy(self)->'TypeExpr':
        return TypeExpr(self.typeName,[te.copy() for te in self.args])
    
    def extract_typevars(self)->Iterator[str]:
        """
        Return all TypeExprs that is kind * in terms of Haskell.
        (for example, the 'list' in 'list[a]' is kind (*->*), and 'a' is kind *)
        """
        if self.args:
            return chain.from_iterable(
                arg.extract_typevars() for arg in self.args)
        else:
            return iter([self.typeName])


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
        return "{}({})".format(
            self.ctorName,
            ','.join(map(str,self.args)) if self.args else ""
        )
    def __repr__(self) -> str:
        return self.__str__()
    def extract_typevars(self)->set[str]:
        return set(chain.from_iterable(
            arg.typ.extract_typevars() for arg in self.args))
    


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
                    f"[{','.join(self.typeVars)}]" if self.typeVars else "",
                    '\n\t| '.join(map(str,self.ctors))
                    )
    def __repr__(self) -> str:
        return self.__str__()
    def subst_with_dict(self,typeVar_map:Dict[str,str])->None:
        "Change the name of type variables according to the given table."
        for i,tv in enumerate(self.typeVars):
            x = typeVar_map.get(tv)
            if x:
                self.typeVars[i] = x
        typeVars_in_ctors = (x.typ for x in 
                                chain.from_iterable(ctor.args for ctor in self.ctors))
        for tv in typeVars_in_ctors:
            tv.subst_with_dict(typeVar_map)



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
                ).combine(CtorArg))
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



def generate_code(datas:List[DataDef])->Iterator[str]:
    # construct the typevar map
    # the idea: the typevar in ast map to an actual typevar name
    typevar_num = max(*map(lambda dd:len(dd.typeVars), datas))
    typevar_list = typevarList(typevar_num)
    
    gen_aux(typevar_list)


def typevarList(n:int)->List[str]:
    "Generate the list: _A,_B,_C..,_A1,_B1...,_A2,_B2,..."
    it = ('_'+x for x in
            chain(# chain: *Iterable[T] -> Iterable[T]
                _upperCases,
                chain.from_iterable(# from_iterable: Iterable[Iterable[T]]->Iterable[T]
                    #Iterable[Iterable[str]]
                    ((x+str(i) for x in _upperCases) for i in
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

def wrap_recursive_type(t:TypeExpr, rt:str)->str:
    """
    If t is the same as the type we're defining, wrap a pair of `\'` around it.
    For example, when defining the class `Lst`, all the occurrences of `Lst`
    should be wrapped like `'Lst[int]'`, `'Lst[Lst[Any]]'`.
    """
    if t.typeName==rt:
        return f"'{str(t)}'"
    else:
        return str(t)
def ctorMatchSignature(retType:str, rectype:str)->Callable[[Ctor],str]:
    "example: Cons ==> 'cons:Callable[[_T,Lst[_T]],Lst[_T]]'"
    def f(ctor:Ctor)->str:
        return "{}: Callable[[{}], {}],"\
                .format(lowercase_head(ctor.ctorName),
                        ','.join(wrap_recursive_type(arg.typ, rectype) 
                                    for arg in ctor.args),
                        retType
                )
    return f

def gen_match_signature( dataDef:DataDef)->Iterator[str]:
    "Generate the match method's def clause and type signature."
    return chain(
        ["def match(self,*,"],
        ("          "+line for line in 
            map(ctorMatchSignature('_T_', dataDef.typeName), 
                dataDef.ctors)),
        ["         )->_T_:"]
    )
    
def gen_typedef(dataDef:DataDef)->Iterator[str]:
    "Generate the class for the type, e.g., List"
    ctors = dataDef.ctors
    inherit_part = "(Generic[{}])".format(','.join(dataDef.typeVars))\
                        if dataDef.typeVars else ""
    
    #description
    ctorNum = len(ctors)
    if ctorNum==0:
        description = "Cannot be constructed because there's no constructor defined."
    elif ctorNum==1:
        description = f"Can only be {ctors[0].ctorName}."
    else:
        description = "Can be either "\
                      + ','.join([c.ctorName for c in ctors[:-1]])\
                      + "," if ctorNum>2 else ""\
                      + f" or {ctors[-1].ctorName}."
    return chain(
        [f"class {dataDef.typeName}{inherit_part}:"],
        [indent+f"\"{description}\""],
        (indent+line for line in gen_match_signature(dataDef)),
        [indent*2+"..."]
    )

def gen_one_ctor(dataDef:DataDef, ctor:Ctor)->Iterator[str]:
    typeName: str = dataDef.typeName
    def_typevars: List[str] = dataDef.typeVars
    ctor_typevars: set[str] = ctor.extract_typevars()
    def_type: TypeExpr = TypeExpr.from_mere_typevars(typeName, def_typevars)
    
    # constructing inherit_part
    if ctor.args:
        inherit_part = \
            "Generic[{}],{}".format(
                ','.join(ctor_typevars),
                str(def_type.copy().subst_with_dict(
                    dict(zip(set(def_typevars)-ctor_typevars,
                             repeat('Any')))))
            )
    else:
        # If the Ctor has no typevar, the typevar positions of the inherited type 
        # should be all Any
        # e.g., in the `Lst` example, the inheritance of `Nil` should be `(Lst[Any])`
        inherit_part = \
            str(def_type.copy().subst_with_dict(
                dict(zip(def_typevars,
                         repeat('Any')))))
    
    argtypes: list[tuple[str,TypeExpr]] = [(arg.fieldName, arg.typ) for arg in ctor.args]
    
    return chain(
        #class declaration
        [f"class {typeName}({inherit_part}):"],
        #field declaration
        #__init__
        #match signature
        #match body
        #isCtor test function
    )
def gen_ctors(dataDef: DataDef)->Iterator[str]:
    """
    Generate the class for a constructor, e.g., Cons, including the checking 
    method, e.g., `def isCons(x:Lst[_A])->TypeGuard[Cons[_A]]`
    """
    

def gen_one_DataDef(typevars:Dict[str,str], dataDef: DataDef)->Iterator[str]:
    ...

###-----------------------
        
from icecream import ic
if __name__ == "__main__":
    #main()  
    toks = tokenize(example)
    datas = parseAST(toks)
    # ic(datas)
    # for dd in datas:
    #     print("dd.typeName:")
    #     dd.subst_with_dict({'a':'_A'})
    #     for ctor in dd.ctors:
    #         print(ctor.ctorName+": "+ str(ctor.extract_typevars()))
    
    