"""AST node classes"""


from abc import ABC
from dataclasses import dataclass

from lark import Token
from lark.ast_utils import AsList
from lark.tree import Meta

from .base import _AstNode


# pylint: disable=too-few-public-methods


# Statements


class _Stmt(_AstNode, ABC):
    """Statement base class"""
    meta: Meta


@dataclass(frozen=True)
class Body(_Stmt, AsList):
    """Body (list of statements inside a block or at the top level)"""
    meta: Meta
    statements: list[_Stmt]


@dataclass(frozen=True)
class IncludeStmt(_Stmt):
    """Include statement"""
    meta: Meta
    path: str


@dataclass(frozen=True)
class ReturnStmt(_Stmt):
    """Return statement"""
    meta: Meta
    value: '_Expr | None'


@dataclass
class IfStmt(_Stmt):
    """If statements"""
    meta: Meta
    condition: '_Expr'
    body: Body


@dataclass
class IfElseStmt(_Stmt):
    """If..else statements"""
    meta: Meta
    condition: '_Expr'
    then_body: Body
    else_body: _Stmt


@dataclass
class WhileStmt(_Stmt):
    """While (and do..while) statements"""
    meta: Meta
    condition: '_Expr'
    body: Body
    eval_cond_after_body: bool = False


@dataclass(frozen=True)
class BreakStmt(_Stmt):
    """Break statement"""
    meta: Meta


@dataclass(frozen=True)
class ContinueStmt(_Stmt):
    """Continue statement"""
    meta: Meta


@dataclass
class FunctionStmt(_Stmt):
    """Function declaration"""
    meta: Meta
    name: Token
    form_args: 'FormArgs'
    body: Body


@dataclass(frozen=True)
class FormArgs(_AstNode, AsList):
    """Formal argument list"""
    meta: Meta
    args: list[Token]


@dataclass(frozen=True)
class ModuleStmt(_Stmt, AsList):
    """Module"""
    meta: Meta
    name: Token
    entries: list[_Stmt]


@dataclass(frozen=True)
class ClassStmt(_Stmt, AsList):
    """Class"""
    meta: Meta
    name: Token
    super: Token | None
    entries: list[_Stmt]


@dataclass(frozen=True)
class NopStmt(_Stmt):
    """No-op statement"""
    meta: Meta


# Expressions


class _Expr(_Stmt, ABC):
    """Expression base class"""
    meta: Meta


@dataclass(frozen=True)
class Exprs(_Expr, AsList):
    """Comma-separated expressions (C comma operator)"""
    meta: Meta
    expressions: list[_Expr]


# Assignment expressions and assignment patterns


@dataclass(frozen=True)
class Assign(_Expr):
    """Assignment"""
    meta: Meta
    pattern: '_Pattern'
    right: _Expr


@dataclass(frozen=True)
class Inplace(_Expr):
    """Inplace assignment"""
    meta: Meta
    pattern: '_Pattern'
    op: Token
    right: _Expr


class _Pattern(_AstNode, ABC):
    """Assignment pattern base class"""


@dataclass(frozen=True)
class VarPattern(_Pattern):
    """Variable name pattern, the simplest pattern"""
    meta: Meta
    name: str


@dataclass(frozen=True)
class DotPattern(_Pattern):
    """Dot pattern"""
    meta: Meta
    accessee: _Expr
    attr_name: Token


# Binary and unary operations


@dataclass(frozen=True)
class Logical(_Expr):
    """Logical operations"""
    meta: Meta
    left: _Expr
    op: Token
    right: _Expr


@dataclass(frozen=True)
class BinaryOp(_Expr):
    """Binary operations"""
    meta: Meta
    left: _Expr
    op: Token
    right: _Expr


@dataclass(frozen=True)
class Prefix(_Expr):
    """Unary (prefix) operations"""
    meta: Meta
    op: Token
    operand: _Expr


# Function call


@dataclass(frozen=True)
class SpecArgs(_AstNode, AsList):
    """Specific argument list"""
    meta: Meta
    args: list[_Expr]


@dataclass(frozen=True)
class Call(_Expr):
    """Function call operation"""
    meta: Meta
    callee: _Expr
    args: SpecArgs


@dataclass(frozen=True)
class New(_Expr):
    """Instantiation operation"""
    meta: Meta
    class_name: Token
    args: SpecArgs | None


# Subscript


# Dot access


@dataclass(frozen=True)
class Dot(_Expr):
    """Dot access operation"""
    meta: Meta
    accessee: _Expr
    attr_name: Token


# Atoms


@dataclass(frozen=True)
class Var(_Expr):
    """Variable reference"""
    meta: Meta
    name: Token


@dataclass(frozen=True)
class String(_Expr):
    """String"""
    meta: Meta
    value: str


@dataclass(frozen=True)
class Int(_Expr):
    """Integer"""
    meta: Meta
    value: int


@dataclass(frozen=True)
class Float(_Expr):
    """Floating point number"""
    meta: Meta
    value: float


@dataclass(frozen=True)
class TrueLiteral(_Expr):
    """True literal"""
    meta: Meta


@dataclass(frozen=True)
class FalseLiteral(_Expr):
    """False literal"""
    meta: Meta


@dataclass(frozen=True)
class NullLiteral(_Expr):
    """Null literal"""
    meta: Meta


@dataclass
class FunctionLiteral(_Expr):
    """Function literal"""
    meta: Meta
    form_args: FormArgs
    body: Body


@dataclass(frozen=True)
class List(_Expr, AsList):
    """List literal"""
    meta: Meta
    elems: list[_Expr]


@dataclass(frozen=True)
class Dict(_Expr, AsList):
    """Dictionary literal"""
    meta: Meta
    pairs: list['Pair']


@dataclass(frozen=True)
class Pair(_AstNode):
    """Dictionary pair"""
    meta: Meta
    key: _Expr
    value: _Expr
