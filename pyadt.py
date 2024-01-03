#!/usr/bin/env python
from typing import Generic, TypeVar, Tuple, List, Literal, Optional
from functools import partial
import sys
import io
import re
import parsy





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
    #tokenize
    toks = tokenize(input)


###----- AST ------
    
example="""
data Lst[a] = Nil
            | Cons(_:a, tail:Lst[a])
            
"""

class TypeExpr:
    typeName:str
    args:List['TypeExpr']
    def __init__(self,typeName:str,args:List['TypeExpr']):
        self.typeName = typeName
        self.args = args
    def __str__(self) -> str:
        return self.typeName+("" if len(self.args)==0 else f'[{",".join(map(str,self.args))}]')
    def __repr__(self) -> str:
        return self.__str__()

class CtorArg:
    var:str
    typ:TypeExpr
    def __init__(self,var:str,typ:TypeExpr):
        self.var = var
        self.typ = typ
    def __str__(self):
        return self.var+":"+str(self.typ)
    def __repr__(self) -> str:
        return self.__str__()

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

###-------parsers----------------

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

###-----------------------
        
from icecream import ic
if __name__ == "__main__":
    #main()  
    toks = tokenize('Nil')
    
    print(ctorP.parse(toks))