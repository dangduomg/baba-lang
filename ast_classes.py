from dataclasses import dataclass
from typing import List, Optional

from lark import ast_utils

import intr_classes


# ---- helpers ----


_Ast = ast_utils.Ast
_AsList = ast_utils.AsList

class _Stmt(_Ast):
    def interp(self, state):
        #pylint: disable=unused-argument
        return

class _Expr(_Stmt):
    def interp(self, state):
        return

# ---- the body ----


@dataclass
class Body(_Ast, _AsList):
    stmts: List[_Stmt]
    
    def interp(self, state):
        for stmt in self.stmts:
            res = stmt.interp(state)
            if isinstance(res, intr_classes.EarlyExit):
                return res
        return intr_classes.StmtDone()


# ---- commands ----


@dataclass(frozen=True)
class PrintStmt(_Stmt):
    expr: _Expr
    
    def interp(self, state):
        res = self.expr.interp(state)
        print(res.print_repr())
        return intr_classes.StmtDone()

@dataclass(frozen=True)
class IncludeStmt(_Stmt):
    file: str


# ---- block statements ----

@dataclass(frozen=True)
class IfStmt(_Stmt):
    cond: _Expr
    body: Body
    
    def interp(self, state):
        if self.cond.interp(state).value:
            res = self.body.interp(state)
            if isinstance(res, intr_classes.EarlyExit):
                return res
        return intr_classes.StmtDone()

@dataclass(frozen=True)
class IfElseStmt(_Stmt):
    cond: _Expr
    then_body: Body
    else_body: Body
    
    def interp(self, state):
        if self.cond.interp(state).value:
            res = self.then_body.interp(state)
            if isinstance(res, intr_classes.EarlyExit):
                return res
        else:
            res = self.else_body.interp(state)
            if isinstance(res, intr_classes.EarlyExit):
                return res
        return intr_classes.StmtDone()

@dataclass(frozen=True)
class WhileStmt(_Stmt):
    cond: _Expr
    body: Body
    
    def interp(self, state):
        while self.cond.interp(state).value:
            res = self.body.interp(state)
            if isinstance(res, intr_classes.Break):
                return intr_classes.StmtDone()
        return intr_classes.StmtDone()

@dataclass(frozen=True)
class DoWhileStmt(_Stmt):
    body: Body
    cond: _Expr
    
    def interp(self, state):
        res = self.body.interp(state)
        if isinstance(res, intr_classes.Break):
            return intr_classes.StmtDone()
        while self.cond.interp(state).value:
            res = self.body.interp(state)
            if isinstance(res, intr_classes.Break):
                return intr_classes.StmtDone()
        return intr_classes.StmtDone()

@dataclass(frozen=True)
class ForStmt(_Stmt):
    start: Optional[_Expr]
    cond: Optional[_Expr]
    step: Optional[_Expr]
    body: Body
    
    def interp(self, state):
        if self.start:
            start_res = self.start.interp(state)
        while True:
            if self.cond:
                cond_res = self.cond.interp(state)
                if not cond_res.value:
                    return intr_classes.StmtDone()
            body_res = self.body.interp(state)
            if self.step:
                step_res = self.step.interp(state)
            if isinstance(body_res, intr_classes.Break):
                return intr_classes.StmtDone()


# ---- other statements ----


@dataclass(frozen=True)
class ReturnStmt(_Stmt):
    value: _Expr
    
@dataclass(frozen=True)
class BreakStmt(_Stmt):
    def interp(self, state):
        return intr_classes.Break()

@dataclass(frozen=True)
class ContinueStmt(_Stmt):
    def interp(self, state):
        return intr_classes.Continue()


# ---- expressions ----


@dataclass(frozen=True)
class Exprs(_Expr, _AsList):
    exprs: List[_Expr]
    

# ---- assignment expressions ----


class _Pattern(_Expr):
    def get_var(self, state):
        pass
    
    def new_var(self, state, rhs):
        pass
    
    def set_var(self, state, rhs):
        pass

@dataclass(frozen=True)
class VarPattern(_Pattern):
    name: str
    
    def get_var(self, state):
        return state.get_var(self.name)
    
    def new_var(self, state, rhs):
        state.new_var(self.name, rhs)
        
    def set_var(self, state, rhs):
        state.set_var(self.name, rhs)
    
@dataclass(frozen=True)
class _AssignOp(_Expr):
    pattern: _Pattern
    rhs: _Expr

class Assign(_AssignOp):
    def interp(self, state):
        self.pattern.new_var(state, self.rhs.interp(state))

class Iadd(_AssignOp):
    def interp(self, state):
        newvalue = self.pattern.get_var(state).add(self.rhs.interp(state))
        self.pattern.set_var(state, newvalue)

class Isub(_AssignOp):
    def interp(self, state):
        newvalue = self.pattern.get_var(state).sub(self.rhs.interp(state))
        self.pattern.set_var(state, newvalue)

class Imul(_AssignOp):
    def interp(self, state):
        newvalue = self.pattern.get_var(state).mul(self.rhs.interp(state))
        self.pattern.set_var(state, newvalue)

class Idiv(_AssignOp):
    def interp(self, state):
        newvalue = self.pattern.get_var(state).div(self.rhs.interp(state))
        self.pattern.set_var(state, newvalue)

class Imod(_AssignOp):
    def interp(self, state):
        newvalue = self.pattern.get_var(state).mod(self.rhs.interp(state))
        self.pattern.set_var(state, newvalue)

class Ifloordiv(_AssignOp):
    def interp(self, state):
        newvalue = self.pattern.get_var(state).floordiv(self.rhs.interp(state))
        self.pattern.set_var(state, newvalue)
        
class Ipow(_AssignOp):
    def interp(self, state):
        newvalue = self.pattern.get_var(state).pow(self.rhs.interp(state))
        self.pattern.set_var(state, newvalue)

# ---- binary operations ----


@dataclass(frozen=True)
class _BinaryOp(_Expr):
    lhs: _Expr
    rhs: _Expr

class Eq(_BinaryOp):
    def interp(self, state):
        lhs = self.lhs.interp(state)
        rhs = self.rhs.interp(state)
        return lhs.eq(rhs)

class Ne(_BinaryOp):
    def interp(self, state):
        lhs = self.lhs.interp(state)
        rhs = self.rhs.interp(state)
        return lhs.ne(rhs)

class Lt(_BinaryOp):
    def interp(self, state):
        lhs = self.lhs.interp(state)
        rhs = self.rhs.interp(state)
        return lhs.lt(rhs)

class Le(_BinaryOp):
    def interp(self, state):
        lhs = self.lhs.interp(state)
        rhs = self.rhs.interp(state)
        return lhs.le(rhs)

class Gt(_BinaryOp):
    def interp(self, state):
        lhs = self.lhs.interp(state)
        rhs = self.rhs.interp(state)
        return lhs.gt(rhs)

class Ge(_BinaryOp):
    def interp(self, state):
        lhs = self.lhs.interp(state)
        rhs = self.rhs.interp(state)
        return lhs.ge(rhs)

class Add(_BinaryOp):
    def interp(self, state):
        lhs = self.lhs.interp(state)
        rhs = self.rhs.interp(state)
        return lhs.add(rhs)

class Sub(_BinaryOp):
    def interp(self, state):
        lhs = self.lhs.interp(state)
        rhs = self.rhs.interp(state)
        return lhs.sub(rhs)

class Mul(_BinaryOp):
    def interp(self, state):
        lhs = self.lhs.interp(state)
        rhs = self.rhs.interp(state)
        return lhs.mul(rhs)

class Div(_BinaryOp):
    def interp(self, state):
        lhs = self.lhs.interp(state)
        rhs = self.rhs.interp(state)
        return lhs.div(rhs)

class Mod(_BinaryOp):
    def interp(self, state):
        lhs = self.lhs.interp(state)
        rhs = self.rhs.interp(state)
        return lhs.mod(rhs)

class Floordiv(_BinaryOp):
    def interp(self, state):
        lhs = self.lhs.interp(state)
        rhs = self.rhs.interp(state)
        return lhs.floordiv(rhs)

class Pow(_BinaryOp):
    def interp(self, state):
        lhs = self.lhs.interp(state)
        rhs = self.rhs.interp(state)
        return lhs.pow(rhs)


# ---- unary operations ----


@dataclass(frozen=True)
class _UnaryOp(_Expr):
    operand: _Expr

class Pos(_UnaryOp):
    def interp(self, state):
        return self.operand.interp(state).pos()

class Neg(_UnaryOp):
    def interp(self, state):
        return self.operand.interp(state).neg()


# ---- calls ----


@dataclass(frozen=True)
class SpecArgs(_Ast, _AsList):
    args: List[_Expr]

@dataclass(frozen=True)
class Call(_Expr):
    func: _Expr
    spec_args: SpecArgs


# ---- variable get ----


@dataclass(frozen=True)
class Var(_Expr):
    name: str
    
    def interp(self, state):
        return state.get_var(self.name)


# ---- values ----
    
# ---- null ----

@dataclass(frozen=True)
class Null(_Expr):
    pass

@dataclass(frozen=True)
class Bool(_Expr):
    value: bool
    
# ---- numeric types ----

@dataclass(frozen=True)
class Int(_Expr):
    value: int
    
    def interp(self, state):
        return intr_classes.Int(self.value)
    
@dataclass(frozen=True)
class Float(_Expr):
    value: float
    
    def interp(self, state):
        return intr_classes.Float(self.value)
    
# ---- string ----

@dataclass(frozen=True)
class String(_Expr):
    value: str
    
    def interp(self, state):
        return intr_classes.String(self.value)

# ---- function ----

@dataclass(frozen=True)
class FormArgs(_Ast, _AsList):
    args: List[object]
    
@dataclass
class Function(_Expr):
    form_args: FormArgs
    body: Body