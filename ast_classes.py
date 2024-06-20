from dataclasses import dataclass

from lark import ast_utils

import intr_classes


# ---- helpers ----


_Ast = ast_utils.Ast
_AsList = ast_utils.AsList

class _Stmt(_Ast):
    def interp(self, state):
        #pylint: disable=unused-argument
        return intr_classes.StmtDone()

class _Expr(_Stmt):
    def interp(self, state):
        return intr_classes.Null()
    
@dataclass(frozen=True)
class FormArgs(_Ast, _AsList):
    args: list[str]


# ---- the body ----


@dataclass(frozen=True)
class Body(_Ast, _AsList):
    stmts: list[_Stmt]
    
    def interp(self, state):
        for stmt in self.stmts:
            res = stmt.interp(state)
            if isinstance(res, intr_classes.EarlyExit):
                return res
        return intr_classes.StmtDone()


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
            elif isinstance(res, intr_classes.Continue):
                pass
            elif isinstance(res, intr_classes.EarlyExit):
                return res
        return intr_classes.StmtDone()
    
@dataclass(frozen=True)
class FunctionStmt(_Stmt):
    name: str
    form_args: FormArgs
    body: Body
    
    def interp(self, state):
        state.new_var(self.name, intr_classes.Function(self.name, self.form_args.args, self.body, state.copy()))


# ---- other statements ----


@dataclass(frozen=True)
class ReturnStmt(_Stmt):
    value: _Expr
    def interp(self, state):
        if self.value:
            res = self.value.interp(state)
        else:
            res = intr_classes.Null()
        return intr_classes.Return(res)
    
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
    exprs: list[_Expr]
    
    def interp(self, state):
        for expr in self.exprs:
            res = expr.interp(state)
            if isinstance(res, intr_classes.Throw):
                break
        return res
    

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
class SubscriptPattern(_Pattern):
    container: _Expr
    key: _Expr
    
    def get_var(self, state):
        container = self.container.interp(state)
        if isinstance(container, intr_classes.Throw):
            return container
        key = self.key.interp(state)
        if isinstance(key, intr_classes.Throw):
            return key
        return container.get_item(key)
    
    def new_var(self, state, rhs):
        self.set_var(state, rhs)
        
    def set_var(self, state, rhs):
        container = self.container.interp(state)
        key = self.key.interp(state)
        container.set_item(key, rhs)
    
@dataclass(frozen=True)
class _AssignOp(_Expr):
    pattern: _Pattern
    rhs: _Expr
    
    def _assign_inplace(self, state, method):
        rhs = self.rhs.interp(state)
        if isinstance(rhs, intr_classes.Throw):
            return rhs
        oldvalue = self.pattern.get_var(state)
        if isinstance(oldvalue, intr_classes.Throw):
            return oldvalue
        newvalue = getattr(oldvalue, method)(rhs)
        if isinstance(newvalue, intr_classes.Throw):
            return newvalue
        self.pattern.set_var(state, newvalue)
        return rhs

class Assign(_AssignOp):
    def interp(self, state):
        rhs = self.rhs.interp(state)
        if isinstance(rhs, intr_classes.Throw):
            return rhs
        self.pattern.new_var(state, rhs)
        return rhs

class Iadd(_AssignOp):
    def interp(self, state):
        return self._assign_inplace(state, 'add')

class Isub(_AssignOp):
    def interp(self, state):
        return self._assign_inplace(state, 'sub')

class Imul(_AssignOp):
    def interp(self, state):
        return self._assign_inplace(state, 'mul')

class Idiv(_AssignOp):
    def interp(self, state):
        return self._assign_inplace(state, 'div')

class Imod(_AssignOp):
    def interp(self, state):
        return self._assign_inplace(state, 'mod')

class Ifloordiv(_AssignOp):
    def interp(self, state):
        return self._assign_inplace(state, 'floordiv')
        
class Ipow(_AssignOp):
    def interp(self, state):
        return self._assign_inplace(state, 'pow')

class Iand(_AssignOp):
    def interp(self, state):
        return self._assign_inplace(state, 'bit_and')

class Ior(_AssignOp):
    def interp(self, state):
        return self._assign_inplace(state, 'bit_or')

class Ixor(_AssignOp):
    def interp(self, state):
        return self._assign_inplace(state, 'bit_xor')

class Ilshift(_AssignOp):
    def interp(self, state):
        return self._assign_inplace(state, 'lshift')

class Irshift(_AssignOp):
    def interp(self, state):
        return self._assign_inplace(state, 'rshift')


# ---- binary operations ----


@dataclass(frozen=True)
class _BinaryOp(_Expr):
    lhs: _Expr
    rhs: _Expr
    
    def _eval(self, state, method):
        lhs = self.lhs.interp(state)
        if isinstance(lhs, intr_classes.Throw):
            return lhs
        rhs = self.rhs.interp(state)
        if isinstance(rhs, intr_classes.Throw):
            return rhs
        return getattr(lhs, method)(rhs)

class Eq(_BinaryOp):
    def interp(self, state):
        return self._eval(state, 'eq')

class Ne(_BinaryOp):
    def interp(self, state):
        return self._eval(state, 'ne')

class Lt(_BinaryOp):
    def interp(self, state):
        return self._eval(state, 'lt')

class Le(_BinaryOp):
    def interp(self, state):
        return self._eval(state, 'le')

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

class BitAnd(_BinaryOp):
    def interp(self, state):
        lhs = self.lhs.interp(state)
        rhs = self.rhs.interp(state)
        return lhs.bit_and(rhs)

class BitOr(_BinaryOp):
    def interp(self, state):
        lhs = self.lhs.interp(state)
        rhs = self.rhs.interp(state)
        return lhs.bit_or(rhs)

class BitXor(_BinaryOp):
    def interp(self, state):
        lhs = self.lhs.interp(state)
        rhs = self.rhs.interp(state)
        return lhs.bit_xor(rhs)

class Lshift(_BinaryOp):
    def interp(self, state):
        lhs = self.lhs.interp(state)
        rhs = self.rhs.interp(state)
        return lhs.lshift(rhs)

class Rshift(_BinaryOp):
    def interp(self, state):
        lhs = self.lhs.interp(state)
        rhs = self.rhs.interp(state)
        return lhs.rshift(rhs)


# ---- unary operations ----


@dataclass(frozen=True)
class _UnaryOp(_Expr):
    rhs: _Expr

class Pos(_UnaryOp):
    def interp(self, state):
        rhs = self.rhs.interp(state)
        return rhs.pos()

class Neg(_UnaryOp):
    def interp(self, state):
        rhs = self.rhs.interp(state)
        return rhs.neg()

class BitNot(_UnaryOp):
    def interp(self, state):
        rhs = self.rhs.interp(state)
        return rhs.bit_not()

class LogicalNot(_UnaryOp):
    def interp(self, state):
        rhs = self.rhs.interp(state)
        return rhs.logical_not()
    
    
# ---- subscripting ----


@dataclass(frozen=True)
class Subscript(_Expr):
    container: _Expr
    key: _Expr
    
    def interp(self, state):
        container = self.container.interp(state)
        key = self.key.interp(state)
        return container.get_item(key)


# ---- calls ----


@dataclass(frozen=True)
class SpecArgs(_Ast, _AsList):
    args: list[_Expr]

@dataclass(frozen=True)
class Call(_Expr):
    func: _Expr
    spec_args: SpecArgs
    
    def interp(self, state):
        func = self.func.interp(state)
        args = [arg.interp(state) for arg in self.spec_args.args]
        return func.call(state, args)


# ---- variable get ----


@dataclass(frozen=True)
class Var(_Expr):
    name: str
    
    def interp(self, state):
        return state.get_var(self.name)


# ---- values ----
    
# ---- constants ----

@dataclass(frozen=True)
class Null(_Expr):
    def interp(self, state):
        return intr_classes.Null()
    
@dataclass(frozen=True)
class Bool(_Expr):
    value: bool
    
    def interp(self, state):
        return intr_classes.Bool(self.value)
    
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
    
# ---- list ----

@dataclass(frozen=True)
class List_(_Expr, _AsList):
    values: list[_Expr]
    
    def interp(self, state):
        return intr_classes.List_([v.interp(state) for v in self.values])
    
# ---- dict ----

@dataclass(frozen=True)
class Pair(_Ast):
    key: _Expr
    value: _Expr
    
@dataclass(frozen=True)
class Dict_(_Expr, _AsList):
    pairs: list[Pair]
    
    def interp(self, state):
        return intr_classes.Dict_({p.key.interp(state): p.value.interp(state) for p in self.pairs})


# ---- function ----


@dataclass(frozen=True)
class Function(_Expr):
    form_args: FormArgs
    body: Body
    
    def interp(self, state):
        return intr_classes.Function('<anonymous>', self.form_args.args, self.body, state.copy())
