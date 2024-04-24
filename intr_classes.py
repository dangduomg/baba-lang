from dataclasses import dataclass
from typing import Union, List, Dict, Callable

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
        return self.code_repr()
    
    def code_repr(self):
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
    
    def call(self, state, args):
        raise RuntimeError('operation not implemented')
    
    def get_item(self, k):
        raise RuntimeError('operation not implemented')
    
    def set_item(self, k, v):
        raise RuntimeError('operation not implemented')
    
    
# ---- null and booleans ----

@dataclass(frozen=True)
class Null(Value):
    _singleton = None
    
    def __new__(cls, *args, **kwargs):
        #pylint: disable=unused-argument
        if not cls._singleton:
            cls._singleton = super().__new__(cls)
        return cls._singleton
    
    def print_repr(self):
        return 'null'

@dataclass(frozen=True)
class Bool(Value):
    value: bool
    
    def code_repr(self):
        return str(self.value).lower()
    
    def eq(self, other):
        res = self.value == other.value
        return Bool(res)
    
    def ne(self, other):
        res = self.value != other.value
        return Bool(res)

# ---- numeric values ----

class Number(Value):
    value: Union[int, float]
    
    def code_repr(self):
        return str(self.value)
    
    @classmethod
    def _to_bl(cls, val):
        if isinstance(val, int):
            return Int(val)
        elif isinstance(val, float):
            return Float(val)
        else:
            raise ValueError
        
    def eq(self, other):
        if isinstance(other, Number):
            res = self.value == other.value
            return Bool(res)
        else:
            raise RuntimeError('only compare numbers with themselves')
        
    def ne(self, other):
        if isinstance(other, Number):
            res = self.value != other.value
            return Bool(res)
        else:
            raise RuntimeError('only compare numbers with themselves')
        
    def lt(self, other):
        if isinstance(other, Number):
            res = self.value < other.value
            return Bool(res)
        else:
            raise RuntimeError('only compare numbers with themselves')
        
    def le(self, other):
        if isinstance(other, Number):
            res = self.value <= other.value
            return Bool(res)
        else:
            raise RuntimeError('only compare numbers with themselves')
        
    def gt(self, other):
        if isinstance(other, Number):
            res = self.value > other.value
            return Bool(res)
        else:
            raise RuntimeError('only compare numbers with themselves')
        
    def ge(self, other):
        if isinstance(other, Number):
            res = self.value >= other.value
            return Bool(res)
        else:
            raise RuntimeError('only compare numbers with themselves')
    
    def add(self, other):
        res = self.value + other.value
        return self._to_bl(res)
    
    def sub(self, other):
        res = self.value - other.value
        return self._to_bl(res)
    
    def mul(self, other):
        res = self.value * other.value
        return self._to_bl(res)
    
    def div(self, other):
        res = self.value / other.value
        return self._to_bl(res)
    
    def mod(self, other):
        res = self.value % other.value
        return self._to_bl(res)
    
    def floordiv(self, other):
        res = self.value // other.value
        return self._to_bl(res)
    
    def pow(self, other):
        res = self.value ** other.value
        return self._to_bl(res)

@dataclass(frozen=True)
class Int(Number):
    value: int
    
    def pos(self):
        return Int(+self.value)
    
    def neg(self):
        return Int(-self.value)
    
@dataclass(frozen=True)
class Float(Number):
    value: float
    
    def pos(self):
        return Float(+self.value)
    
    def neg(self):
        return Float(-self.value)
    
# ---- strings -----
    
@dataclass(frozen=True)
class String(Value):
    value: str
    
    def print_repr(self):
        return self.value
    
    def code_repr(self):
        return f"'{self.value}'"
    
    def eq(self, other):
        if isinstance(other, String):
            res = self.value == other.value
            return Bool(res)
        else:
            raise RuntimeError('only compare strings with themselves')
        
    def ne(self, other):
        if isinstance(other, String):
            res = self.value != other.value
            return Bool(res)
        else:
            raise RuntimeError('only compare strings with themselves')
    
    def lt(self, other):
        if isinstance(other, String):
            res = self.value < other.value
            return Bool(res)
        else:
            raise RuntimeError('only compare strings with themselves')
        
    def le(self, other):
        if isinstance(other, String):
            res = self.value <= other.value
            return Bool(res)
        else:
            raise RuntimeError('only compare strings with themselves')
        
    def gt(self, other):
        if isinstance(other, String):
            res = self.value > other.value
            return Bool(res)
        else:
            raise RuntimeError('only compare strings with themselves')
        
    def ge(self, other):
        if isinstance(other, String):
            res = self.value >= other.value
            return Bool(res)
        else:
            raise RuntimeError('only compare strings with themselves')
    
    def add(self, other):
        if isinstance(other, String):
            res = self.value + other.value
            return String(res)
        else:
            raise RuntimeError('only add strings with themselves')
    
    def mul(self, other):
        if isinstance(other, Int):
            res = self.value * other.value
            return String(res)
        else:
            raise RuntimeError('only multiply strings with integers')
        
    def get_item(self, other):
        if isinstance(other, Int):
            return self.value[other.value]
        else:
            raise RuntimeError('only index strings with integers')
    
# ---- lists ----

@dataclass
class List_(Value):
    elems: List[Value]
    
    def code_repr(self):
        return '[' + ', '.join(e.code_repr() for e in self.elems) + ']'
    
    def get_item(self, k):
        if isinstance(k, Int):
            return self.elems[k.value]
        else:
            raise RuntimeError('only index lists with integers')
    
    def set_item(self, k, v):
        if isinstance(k, Int):
            self.elems[k.value] = v
        else:
            raise RuntimeError('only index lists with integers')
        
# ---- dicts ----

@dataclass
class Dict_(Value):
    elems: Dict[Value, Value]
    
    def code_repr(self):
        return '{' + ', '.join(f'{k.code_repr()}: {v.code_repr()}' for k, v in self.elems.items()) + '}'
    
    def get_item(self, k):
        return self.elems[k]
        
    def set_item(self, k, v):
        self.elems[k] = v
    
# ---- callables ----

@dataclass(frozen=True)
class Function(Value):
    form_args: 'FormArgs'
    body: 'Body'
    env: State
    
    def code_repr(self):
        return '<function>'
    
    def call(self, state, args):
        # decode args
        decoded_args = self._decode_args(args)
        # create new frame
        state.new_scope()
        for k, v in decoded_args.items():
            state.new_var(k, v)
        # evaluate the body
        res = self.body.interp(state)
        # return
        state.exit_scope()
        if isinstance(res, Return):
            return res.value
        elif isinstance(res, StmtDone):
            return Null()
        elif isinstance(res, EarlyExit):
            raise RuntimeError("early exit statement besides 'return' at function's top level")
        
    def _decode_args(self, args):
        if len(self.form_args.args) != len(args):
            raise RuntimeError('function call must have exactly {len(self.form_args.args)} arguments')
        return dict(zip(self.form_args.args, args))
    
@dataclass(frozen=True)
class PythonPureWrapper(Value):
    function: Callable
    
    def code_repr(self):
        return '<python wrapper>'
    
    def call(self, state, args):
        return self.function(*args)
        
class PythonWrapper(PythonPureWrapper):
    def call(self, state, args):
        # converts args into native python types if possible
        unwrapped_args = self._unwrap_args(args)
        # evaluate
        res = super().call(state, unwrapped_args)
        # converts python types back to BL types
        return self._wrap(res)
    
    @classmethod
    def _unwrap_args(cls, args):
        unwrapped_args = []
        for a in args:
            unwrapped_args.append(a)
        return [cls._unwrap(a) for a in args]
    
    @classmethod
    def _unwrap(cls, v):
        if v is Null():
            return None
        elif isinstance(v, (Bool, Number, String)):
            return v.value
        elif isinstance(v, List_):
            return [cls._unwrap(e) for e in v.elems]
        elif isinstance(v, Dict_):
            return {cls._unwrap(k): cls._unwrap(v) for k, v in v.elems.items()}
        else:
            return v
    
    @classmethod
    def _wrap(cls, v):
        if v is None:
            return Null()
        elif isinstance(v, bool):
            return Bool(v)
        elif isinstance(v, int):
            return Int(v)
        elif isinstance(v, float):
            return Float(v)
        elif isinstance(v, str):
            return String(v)
        elif isinstance(v, (tuple, list)):
            return List_([cls._wrap(x) for x in v])
        elif isinstance(v, dict):
            return Dict_({cls._wrap(k): cls._wrap(v) for k, v in v.items()})
        elif isinstance(v, Value):
            return v
        else:
            raise RuntimeError('python function returns something that cannot be converted into babalang values')