from dataclasses import dataclass
from typing import List, Optional

from lark import ast_utils


# ---- helpers ----


_Ast = ast_utils.Ast
_AsList = ast_utils.AsList

class _Stmt(_Ast):
    def interp(self, state):
        pass

class _Expr(_Stmt):
    pass

class _Result(_Ast):
    pass

@dataclass
class Value(_Result):
    value: object
    
    def interp(self, state):
        #pylint: disable=unused-argument
        return self

@dataclass
class Break(_Result):
    pass

@dataclass
class Continue(_Result):
    pass

# ---- the body ----


@dataclass
class Body(_Ast, _AsList):
    stmts: List[_Stmt]
    
    def interp(self, state):
        for st in self.stmts:
            res = st.interp(state)
            if isinstance(res, (Break, Continue)):
                return res


# ---- commands ----


@dataclass
class PrintStmt(_Stmt):
    expr: _Expr
    
    def interp(self, state):
        expr = self.expr.interp(state)
        print(expr.value)

@dataclass
class PythonCallStmt(_Stmt, _AsList):
    args: List[_Expr]

@dataclass
class NonlocalVarStmt(_Stmt):
    name: str
    value: _Expr

@dataclass
class IncludeStmt(_Stmt):
    file: str


# ---- block statements ----

@dataclass
class FormArgs(_Ast, _AsList):
    args: List[object]

@dataclass
class FunctionStmt(_Stmt):
    name: str
    form_args: FormArgs
    body: Body

@dataclass
class IfStmt(_Stmt):
    cond: _Expr
    body: Body
    
    def interp(self, state):
        cond = self.cond.interp(state)
        if cond.value:
            res = self.body.interp(state)
            if isinstance(res, (Break, Continue)):
                return res

@dataclass
class IfElseStmt(_Stmt):
    cond: _Expr
    then_body: Body
    else_body: Body
    
    def interp(self, state):
        cond = self.cond.interp(state)
        if cond.value:
            res = self.then_body.interp(state)
            if isinstance(res, (Break, Continue)):
                return res
        else:
            res = self.else_body.interp(state)
            if isinstance(res, (Break, Continue)):
                return res

@dataclass
class WhileStmt(_Stmt):
    cond: _Expr
    body: Body
    
    def interp(self, state):
        while self.cond.interp(state).value:
            res = self.body.interp(state)
            if isinstance(res, Break):
                break
            elif isinstance(res, Continue):
                continue

@dataclass
class DoWhileStmt(_Stmt):
    body: Body
    cond: _Expr

@dataclass
class ForStmt(_Stmt):
    start: Optional[_Expr]
    stop: Optional[_Expr]
    step: Optional[_Expr]
    body: Body


# ---- other statements ----


@dataclass
class ReturnStmt(_Stmt):
    value: _Expr
    
@dataclass
class BreakStmt(_Stmt):
    def interp(self, state):
        return Break()

@dataclass
class ContinueStmt(_Stmt):
    def interp(self, state):
        return Continue()


# ---- expressions ----


@dataclass
class Exprs(_Expr, _AsList):
    exprs: List[_Expr]
    
@dataclass
class _AssignOp(_Expr):
    name: str
    rhs: _Expr

class Assign(_AssignOp):
    def interp(self, state):
        rhs = self.rhs.interp(state)
        state.new_var(self.name, rhs.value)
        return Value(rhs.value)


@dataclass
class _BinaryOp(_Expr):
    lhs: _Expr
    rhs: _Expr

class Eq(_BinaryOp):
    def interp(self, state):
        lhs = self.lhs.interp(state)
        rhs = self.rhs.interp(state)
        return Value(lhs.value == rhs.value)

class Ne(_BinaryOp):
    def interp(self, state):
        lhs = self.lhs.interp(state)
        rhs = self.rhs.interp(state)
        return Value(lhs.value != rhs.value)

class Lt(_BinaryOp):
    def interp(self, state):
        lhs = self.lhs.interp(state)
        rhs = self.rhs.interp(state)
        return Value(lhs.value < rhs.value)

class Le(_BinaryOp):
    def interp(self, state):
        lhs = self.lhs.interp(state)
        rhs = self.rhs.interp(state)
        return Value(lhs.value <= rhs.value)

class Gt(_BinaryOp):
    def interp(self, state):
        lhs = self.lhs.interp(state)
        rhs = self.rhs.interp(state)
        return Value(lhs.value > rhs.value)

class Ge(_BinaryOp):
    def interp(self, state):
        lhs = self.lhs.interp(state)
        rhs = self.rhs.interp(state)
        return Value(lhs.value >= rhs.value)

class Add(_BinaryOp):
    def interp(self, state):
        lhs = self.lhs.interp(state)
        rhs = self.rhs.interp(state)
        return Value(lhs.value + rhs.value)

class Sub(_BinaryOp):
    def interp(self, state):
        lhs = self.lhs.interp(state)
        rhs = self.rhs.interp(state)
        return Value(lhs.value - rhs.value)

class Mul(_BinaryOp):
    def interp(self, state):
        lhs = self.lhs.interp(state)
        rhs = self.rhs.interp(state)
        return Value(lhs.value * rhs.value)

class Div(_BinaryOp):
    def interp(self, state):
        lhs = self.lhs.interp(state)
        rhs = self.rhs.interp(state)
        return Value(lhs.value / rhs.value)

class Mod(_BinaryOp):
    def interp(self, state):
        lhs = self.lhs.interp(state)
        rhs = self.rhs.interp(state)
        return Value(lhs.value % rhs.value)

class Floordiv(_BinaryOp):
    def interp(self, state):
        lhs = self.lhs.interp(state)
        rhs = self.rhs.interp(state)
        return Value(lhs.value // rhs.value)

class Pow(_BinaryOp):
    def interp(self, state):
        lhs = self.lhs.interp(state)
        rhs = self.rhs.interp(state)
        return Value(lhs.value ** rhs.value)


@dataclass
class _UnaryOp(_Expr):
    operand: _Expr

class Pos(_UnaryOp):
    def interp(self, state):
        op = self.operand.interp(state)
        return Value(+op)

class Neg(_UnaryOp):
    def interp(self, state):
        op = self.operand.interp(state)
        return Value(-op)


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
    
    def interp(self, state):
        return Value(state.get_var(self.name))


@dataclass
class Function(_Expr):
    form_args: FormArgs
    body: Body
