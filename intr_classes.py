from dataclasses import dataclass
from typing import Union, List

from state import State


class Result:
    pass

class StmtDone(Result):
    pass

class EarlyExit(Result):
    pass

@dataclass(frozen=True)
class Break(EarlyExit):
    pass

@dataclass(frozen=True)
class Continue(EarlyExit):
    pass

@dataclass(frozen=True)
class Return(EarlyExit):
    value: 'Value'


# ---- values ----


class Value(Result):
    def interp(self, state):
        #pylint: disable=unused-argument
        return self
    
    def print_repr(self):
        return '<value>'
    
    def eq(self, other):
        return Bool(self == other)
        
    def ne(self, other):
        return Bool(self != other)
        
    def lt(self, other):
        raise RuntimeError('operation not implemented')
        
    def le(self, other):
        raise RuntimeError('operation not implemented')
        
    def gt(self, other):
        raise RuntimeError('operation not implemented')
        
    def ge(self, other):
        raise RuntimeError('operation not implemented')
    
    def add(self, other):
        raise RuntimeError('operation not implemented')
    
    def sub(self, other):
        raise RuntimeError('operation not implemented')
    
    def mul(self, other):
        raise RuntimeError('operation not implemented')
    
    def div(self, other):
        raise RuntimeError('operation not implemented')
    
    def mod(self, other):
        raise RuntimeError('operation not implemented')
    
    def floordiv(self, other):
        raise RuntimeError('operation not implemented')
    
    def pow(self, other):
        raise RuntimeError('operation not implemented')
    
    def pos(self):
        raise RuntimeError('operation not implemented')
    
    def neg(self):
        raise RuntimeError('operation not implemented')
    
    def call(self, args):
        raise RuntimeError('operation not implemented')
    
# ---- null and booleans ----

@dataclass(frozen=True)
class Null(Value):
    def print_repr(self):
        return 'null'
    
    def eq(self, other):
        #pylint: disable=unused-argument
        return True

@dataclass(frozen=True)
class Bool(Value):
    value: bool
    
    def print_repr(self):
        return 'true' if self.value else 'false'
    
    def eq(self, other):
        res = self.value == other.value
        return Bool(res)
        
    def ne(self, other):
        res = self.value != other.value
        return Bool(res)

# ---- numeric values ----

class Number(Value):
    value: Union[int, float]
    
    def print_repr(self):
        return str(self.value)
    
    @classmethod
    def to_bl(cls, val):
        if isinstance(val, int):
            return Int(val)
        elif isinstance(val, float):
            return Float(val)
        else:
            raise ValueError
        
    def eq(self, other):
        res = self.value == other.value
        return Bool(res)
        
    def ne(self, other):
        res = self.value != other.value
        return Bool(res)
        
    def lt(self, other):
        res = self.value < other.value
        return Bool(res)
        
    def le(self, other):
        res = self.value <= other.value
        return Bool(res)
        
    def gt(self, other):
        res = self.value > other.value
        return Bool(res)
        
    def ge(self, other):
        res = self.value >= other.value
        return Bool(res)
    
    def add(self, other):
        res = self.value + other.value
        return self.to_bl(res)
    
    def sub(self, other):
        res = self.value - other.value
        return self.to_bl(res)
    
    def mul(self, other):
        res = self.value * other.value
        return self.to_bl(res)
    
    def div(self, other):
        res = self.value / other.value
        return self.to_bl(res)
    
    def mod(self, other):
        res = self.value % other.value
        return self.to_bl(res)
    
    def floordiv(self, other):
        res = self.value // other.value
        return self.to_bl(res)
    
    def pow(self, other):
        res = self.value ** other.value
        return self.to_bl(res)
    
    def pos(self):
        res = +self.value
        return self.to_bl(res)
    
    def neg(self):
        res = -self.value
        return self.to_bl(res)

@dataclass(frozen=True)
class Int(Number):
    value: int
    
@dataclass(frozen=True)
class Float(Number):
    value: float
    
# ---- strings -----
    
@dataclass(frozen=True)
class String(Value):
    value: str
    
    @classmethod
    def to_bl(cls, val):
        if isinstance(val, str):
            return cls(val)
        else:
            raise ValueError
    
    def print_repr(self):
        return self.value
    
    def eq(self, other):
        res = self.value == other.value
        return Bool(res)
        
    def ne(self, other):
        res = self.value != other.value
        return Bool(res)
    
    def lt(self, other):
        res = self.value < other.value
        return Bool(res)
        
    def le(self, other):
        res = self.value <= other.value
        return Bool(res)
        
    def gt(self, other):
        res = self.value > other.value
        return Bool(res)
        
    def ge(self, other):
        res = self.value >= other.value
        return Bool(res)
    
    def add(self, other):
        res = self.value + other.value
        return self.to_bl(res)
    
    def mul(self, other):
        res = self.value * other.value
        return self.to_bl(res)
    
# ---- functions ----

@dataclass(frozen=True)
class Function(Value):
    form_args: 'FormArgs'
    body: 'Body'
    env: State
    
    def print_repr(self):
        return '<function>'
    
    def call(self, state, args):
        # decode args
        decoded_args = self.decode_args(args)
        # create new frame
        state.new_scope()
        for k, v in decoded_args.items():
            state.new_var(k, v)
        # evaluate the body
        res = self.body.interp(state)
        state.exit_scope()
        if isinstance(res, Return):
            return res.value
        elif isinstance(res, StmtDone):
            return
        elif isinstance(res, EarlyExit):
            raise RuntimeError('break, continue outside a loop?')
        
            
    def decode_args(self, spec_args):
        if len(spec_args) < len(self.form_args.args):
            raise RuntimeError('Too little arguments!')
        if len(spec_args) > len(self.form_args.args):
            raise RuntimeError('Too many arguments!')
        return dict(zip(self.form_args.args, spec_args))