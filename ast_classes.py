from dataclasses import dataclass
from typing import List, Optional

from lark import ast_utils


# ---- helpers ----


_Ast = ast_utils.Ast
_AsList = ast_utils.AsList

class _Expr(_Ast):
    pass

@dataclass
class Value(_Ast):
    value: object

@dataclass
class FormArgs(_Ast, _AsList):
    args: List[object]


# ---- the body ----


@dataclass
class Body(_Ast, _AsList):
    stmts: List[object]


# ---- commands ----


@dataclass
class PrintStmt(_Ast):
    value: _Expr

@dataclass
class PythonCallStmt(_Ast, _AsList):
    args: List[object]

@dataclass
class NonlocalVarStmt(_Ast):
    name: str
    value: _Expr

@dataclass
class IncludeStmt(_Ast):
    file: str


# ---- block statements ----


@dataclass
class FunctionStmt(_Ast):
    name: str
    form_args: FormArgs
    body: Body

@dataclass
class IfStmt(_Ast):
    cond: _Expr
    body: Body

@dataclass
class IfElseStmt(_Ast):
    cond: _Expr
    then_body: Body
    else_body: Body

@dataclass
class WhileStmt(_Ast):
    cond: _Expr
    body: Body

@dataclass
class DoWhileStmt(_Ast):
    body: Body
    cond: _Expr

@dataclass
class ForStmt(_Ast):
    start: Optional[_Expr]
    stop: Optional[_Expr]
    step: Optional[_Expr]
    body: Body


# ---- other statements ----


@dataclass
class ReturnStmt(_Ast):
    value: _Expr


# ---- expressions ----


@dataclass
class Exprs(_Expr, _AsList):
    exprs: List[_Expr]


@dataclass
class _AssignOp(_Expr):
    pattern: object
    value: _Expr

class _Pattern(_Ast):
    pass

@dataclass
class VarPattern(_Pattern):
    name: str

class Assign(_AssignOp):
    pass

class Iadd(_AssignOp):
    pass

class Isub(_AssignOp):
    pass

class Imul(_AssignOp):
    pass

class Idiv(_AssignOp):
    pass

class Imod(_AssignOp):
    pass

class Ifloordiv(_AssignOp):
    pass


@dataclass
class _BinaryOp(_Expr):
    lhs: _Expr
    rhs: _Expr

class Eq(_BinaryOp):
    pass

class Ne(_BinaryOp):
    pass

class Lt(_BinaryOp):
    pass

class Le(_BinaryOp):
    pass

class Gt(_BinaryOp):
    pass

class Ge(_BinaryOp):
    pass

class Add(_BinaryOp):
    pass

class Sub(_BinaryOp):
    pass

class Mul(_BinaryOp):
    pass

class Div(_BinaryOp):
    pass

class Mod(_BinaryOp):
    pass

class Floordiv(_BinaryOp):
    pass

class Pow(_BinaryOp):
    pass


@dataclass
class _UnaryOp(_Expr):
    operand: _Expr

class Pos(_UnaryOp):
    pass

class Neg(_UnaryOp):
    pass


@dataclass
class SpecArgs(_Ast, _AsList):
    args: List[_Expr]

@dataclass
class Call(_Expr):
    func: _Expr
    spec_args: SpecArgs


@dataclass
class Var(_Expr):
    name: str


@dataclass
class Function(_Expr):
    form_args: FormArgs
    body: Body
