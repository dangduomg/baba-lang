"""Base, error and essential value classes"""


from abc import ABC
from typing import Self, TYPE_CHECKING, override, cast
from dataclasses import dataclass, field

from lark import Token
from lark.tree import Meta

from bl_ast.nodes import FormArgs, Body

from .abc_protocols import (
    Result, Exit, SupportsBLCall, SupportsWrappedByPythonFunction
)

if TYPE_CHECKING:
    from .iterator import Item
    from ..main import ASTInterpreter


# pylint: disable=too-few-public-methods
# pylint: disable=too-many-public-methods
# pylint: disable=unused-argument
# pylint: disable=too-many-lines


# section Helpers


def cast_to_instance(value: "ExpressionResult") -> "Instance":
    """Cast a value to an instance"""
    return cast(Instance, value)


# section Result


@dataclass(frozen=True)
class Success(Result):
    """Object signaling sucessful statement execution (without returning
any value)"""


@dataclass(frozen=True)
class Return(Exit):
    """Return statement"""
    value: "Value"


type ExpressionResult = "Value | BLError"


# section Error


@dataclass(init=False)
class BLError(Exit):
    """Error result type"""

    value: "Instance"
    meta: Meta | None
    path: str | None

    def __init__(
        self, value: "Instance", meta: Meta | None, path: str | None
    ) -> None:
        self.value = value
        self.value.vars["meta"] = PythonValue(meta)
        self.meta = meta
        self.path = path


# section Values


class Value(Result, ABC):
    """Value base class"""

    def binary_op(
        self, op: str, other: "Value",
        interpreter: "ASTInterpreter", meta: Meta | None
    ) -> "ExpressionResult":
        """Binary operation"""
        # pylint: disable=too-many-return-statements
        match op:
            case "+":
                return self.add(other, interpreter, meta)
            case "-":
                return self.subtract(other, interpreter, meta)
            case "*":
                return self.multiply(other, interpreter, meta)
            case "/":
                return self.divide(other, interpreter, meta)
            case "%/%":
                return self.floor_div(other, interpreter, meta)
            case "%":
                return self.modulo(other, interpreter, meta)
            case "**":
                return self.power(other, interpreter, meta)
            case "&":
                return self.bit_and(other, interpreter, meta)
            case "|":
                return self.bit_or(other, interpreter, meta)
            case "^":
                return self.bit_xor(other, interpreter, meta)
            case "<<":
                return self.left_shift(other, interpreter, meta)
            case ">>":
                return self.right_shift(other, interpreter, meta)
            case "==":
                return self.is_equal(other, interpreter, meta)
            case "!=":
                return self.is_not_equal(other, interpreter, meta)
            case "<":
                return self.is_less(other, interpreter, meta)
            case "<=":
                return self.is_less_or_equal(other, interpreter, meta)
            case ">":
                return self.is_greater(other, interpreter, meta)
            case ">=":
                return self.is_greater_or_equal(other, interpreter, meta)
        return BLError(cast_to_instance(
            NotImplementedException.new(
                [String(f"Operator '{op}' is not supported")], interpreter,
                meta
            )
        ), meta, interpreter.path)

    def add(
        self, other: "Value", interpreter: "ASTInterpreter",
        meta: Meta | None
    ) -> ExpressionResult:
        """Addition"""
        return self._unimplemented_binary_op('+', other, interpreter, meta)

    def subtract(
        self, other: "Value", interpreter: "ASTInterpreter",
        meta: Meta | None
    ) -> ExpressionResult:
        """Subtraction"""
        return self._unimplemented_binary_op('-', other, interpreter, meta)

    def multiply(
        self, other: "Value", interpreter: "ASTInterpreter",
        meta: Meta | None
    ) -> ExpressionResult:
        """Multiplication"""
        return self._unimplemented_binary_op('*', other, interpreter, meta)

    def divide(
        self, other: "Value", interpreter: "ASTInterpreter",
        meta: Meta | None
    ) -> ExpressionResult:
        """Division"""
        return self._unimplemented_binary_op('/', other, interpreter, meta)

    def floor_div(
        self, other: "Value", interpreter: "ASTInterpreter",
        meta: Meta | None
    ) -> ExpressionResult:
        """Floor division"""
        return self._unimplemented_binary_op("%/%", other, interpreter, meta)

    def modulo(
        self, other: "Value", interpreter: "ASTInterpreter",
        meta: Meta | None
    ) -> ExpressionResult:
        """Modulo operator"""
        return self._unimplemented_binary_op("%", other, interpreter, meta)

    def power(
        self, other: "Value", interpreter: "ASTInterpreter",
        meta: Meta | None
    ) -> ExpressionResult:
        """Power operator"""
        return self._unimplemented_binary_op("**", other, interpreter, meta)

    def bit_and(
        self, other: "Value", interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        """Bitwise and"""
        return self._unimplemented_binary_op('&', other, interpreter, meta)

    def bit_or(
        self, other: "Value", interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        """Bitwise or"""
        return self._unimplemented_binary_op('|', other, interpreter, meta)

    def bit_xor(
        self, other: "Value", interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        """Bitwise exclusive or"""
        return self._unimplemented_binary_op('^', other, interpreter, meta)

    def left_shift(
        self, other: "Value", interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        """Left shift"""
        return self._unimplemented_binary_op('<<', other, interpreter, meta)

    def right_shift(
        self, other: "Value", interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        """Right shift"""
        return self._unimplemented_binary_op('>>', other, interpreter, meta)

    def is_equal(
        self, other: "Value", interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> "Bool | BLError":
        """Equality"""
        return BOOLS[self is other]

    def is_not_equal(
        self, other: "Value", interpreter: "ASTInterpreter",
        meta: Meta | None
    ) -> ExpressionResult:
        """Inequality"""
        converse = self.is_equal(other, interpreter, meta)
        if isinstance(converse, BLError):
            return converse
        return converse.logical_not(interpreter, meta)

    def is_less(
        self, other: "Value", interpreter: "ASTInterpreter",
        meta: Meta | None
    ) -> ExpressionResult:
        """Less than"""
        return self._unimplemented_binary_op('<', other, interpreter, meta)

    def is_less_or_equal(
        self, other: "Value", interpreter: "ASTInterpreter",
        meta: Meta | None
    ) -> ExpressionResult:
        """Less than or equal to"""
        return self._unimplemented_binary_op('<=', other, interpreter, meta)

    def is_greater(
        self, other: "Value", interpreter: "ASTInterpreter",
        meta: Meta | None
    ) -> ExpressionResult:
        """Greater than"""
        return self._unimplemented_binary_op('>', other, interpreter, meta)

    def is_greater_or_equal(
        self, other: "Value", interpreter: "ASTInterpreter",
        meta: Meta | None
    ) -> ExpressionResult:
        """Greater than or equal to"""
        return self._unimplemented_binary_op('>=', other, interpreter, meta)

    def _unimplemented_binary_op(
        self, op: str, other: "Value",
        interpreter: "ASTInterpreter", meta: Meta | None,
    ) -> BLError:
        """Unimplemented binary operation stub"""
        match self_dump := self.dump(interpreter, meta):
            case BLError():
                return self_dump
        match other_dump := other.dump(interpreter, meta):
            case BLError():
                return other_dump
        return BLError(cast_to_instance(
            NotImplementedException.new([String(
                f"Operator {op!r} is not supported for " +
                f"{self_dump.value} and {other_dump.value}"
            )], interpreter, meta)
        ), meta, interpreter.path)

    def unary_op(
        self, op: Token, interpreter: "ASTInterpreter", meta: Meta | None
    ) -> "ExpressionResult":
        """Unary operation"""
        match op:
            case "+":
                return self.plus(interpreter, meta)
            case "-":
                return self.neg(interpreter, meta)
            case "~":
                return self.bit_not(interpreter, meta)
            case "!":
                return self.logical_not(interpreter, meta)
        return BLError(cast_to_instance(
            NotImplementedException.new([], interpreter, meta)
        ), meta, interpreter.path)

    def plus(
        self, interpreter: "ASTInterpreter", meta: Meta | None
    ) -> ExpressionResult:
        """Unary plus"""
        return self._unimplemented_unary_op("+", interpreter, meta)

    def neg(
        self, interpreter: "ASTInterpreter", meta: Meta | None
    ) -> ExpressionResult:
        """Negation"""
        return self._unimplemented_unary_op("-", interpreter, meta)

    def bit_not(
        self, interpreter: "ASTInterpreter", meta: Meta | None
    ) -> ExpressionResult:
        """Bitwise not"""
        return self._unimplemented_unary_op("~", interpreter, meta)

    def logical_not(
        self, interpreter: "ASTInterpreter", meta: Meta | None
    ) -> "Bool | BLError":
        """Logical not"""
        return BOOLS[not self.to_bool(interpreter, meta).value]

    def _unimplemented_unary_op(
        self, op: str, interpreter: "ASTInterpreter", meta: Meta | None
    ) -> BLError:
        match self_dump := self.dump(interpreter, meta):
            case BLError():
                return self_dump
        return BLError(cast_to_instance(
            NotImplementedException.new([String(
                f"Operator {op!r} is not supported for {self_dump.value}"
            )], interpreter, meta)
        ), meta, interpreter.path)

    def get_attr(
        self, attr: str, interpreter: "ASTInterpreter", meta: Meta | None
    ) -> ExpressionResult:
        """Access an attribute"""
        return BLError(cast_to_instance(
            NotImplementedException.new(
                [String("Attribute access is not supported")],
                interpreter, meta
            )
        ), meta, interpreter.path)

    def set_attr(
        self, attr: str, value: "Value",
        interpreter: "ASTInterpreter", meta: Meta | None
    ) -> ExpressionResult:
        """Set an attribute"""
        return BLError(cast_to_instance(
            NotImplementedException.new(
                [String("Attribute assignment is not supported")],
                interpreter, meta,
            )
        ), meta, interpreter.path)

    def get_item(
        self, index: "Value", interpreter: "ASTInterpreter",
        meta: Meta | None
    ) -> ExpressionResult:
        """Access an item"""
        return BLError(cast_to_instance(
            NotImplementedException.new(
                [String("Subscripting is not supported")],
                interpreter, meta,
            )
        ), meta, interpreter.path)

    def set_item(
        self, index: "Value", value: "Value",
        interpreter: "ASTInterpreter", meta: Meta | None
    ) -> ExpressionResult:
        """Set an item"""
        return BLError(cast_to_instance(
            NotImplementedException.new(
                [String("Subscript assignment is not supported")],
                interpreter, meta,
            )
        ), meta, interpreter.path)

    def call(
        self, args: list["Value"], interpreter: "ASTInterpreter",
        meta: Meta | None
    ) -> ExpressionResult:
        """Call self as a function"""
        return BLError(cast_to_instance(
            NotImplementedException.new([], interpreter, meta)
        ), meta, interpreter.path)

    def new(
        self, args: list["Value"], interpreter: "ASTInterpreter",
        meta: Meta | None
    ) -> ExpressionResult:
        """Instantiation operation"""
        return BLError(cast_to_instance(
            NotImplementedException.new([], interpreter, meta)
        ), meta, interpreter.path)

    def to_bool(
        self, interpreter: "ASTInterpreter", meta: Meta | None
    ) -> "Bool | BLError":
        """Convert to boolean"""
        return TRUE

    def to_iter(
        self, interpreter: "ASTInterpreter", meta: Meta | None
    ) -> ExpressionResult:
        """Convert to iterator"""
        return BLError(cast_to_instance(
            NotImplementedException.new([], interpreter, meta)
        ), meta, interpreter.path)

    def next(
        self, interpreter: "ASTInterpreter", meta: Meta | None
    ) -> "Item | Null | BLError":
        """Advance an iterator"""
        return BLError(cast_to_instance(
            NotImplementedException.new([], interpreter, meta)
        ), meta, interpreter.path)

    def dump(
        self, interpreter: "ASTInterpreter", meta: Meta | None
    ) -> "String | BLError":
        """Return a detailed representation for introspection"""
        return String("<value>")

    def to_string(
        self, interpreter: "ASTInterpreter", meta: Meta | None
    ) -> "String | BLError":
        """Return an user-friendly string representation"""
        return self.dump(interpreter, meta)


@dataclass(frozen=True)
class PythonValue(Value):
    """Python value wrapper"""

    value: object

    @override
    def dump(
        self, interpreter: "ASTInterpreter", meta: Meta | None
    ) -> "String":
        return String(f"<python value {self.value!r}>")


@dataclass(frozen=True)
class Bool(Value):
    """Boolean type"""

    value: bool

    @override
    def to_bool(
        self, interpreter: "ASTInterpreter", meta: Meta | None
    ) -> Self:
        return self

    @override
    def dump(
        self, interpreter: "ASTInterpreter", meta: Meta | None
    ) -> "String":
        return String("true") if self.value else String("false")


FALSE = Bool(False)
TRUE = Bool(True)
BOOLS = FALSE, TRUE


@dataclass(frozen=True)
class Null(Value):
    """Null value"""

    @override
    def to_bool(
        self, interpreter: "ASTInterpreter", meta: Meta | None
    ) -> Bool:
        return FALSE

    @override
    def dump(
        self, interpreter: "ASTInterpreter", meta: Meta | None
    ) -> "String":
        return String("null")


NULL = Null()


@dataclass(frozen=True)
class String(Value):
    """String type"""

    value: str

    @override
    def add(
        self, other: "Value", interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        match other:
            case String(other_val):
                return String(self.value + other_val)
        return super().add(other, interpreter, meta)

    @override
    def multiply(
        self, other: "Value", interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        from .numbers import Int  # pylint: disable=import-outside-toplevel
        match other:
            case Int(times):
                return String(self.value * times)
        return super().multiply(other, interpreter, meta)

    @override
    def is_equal(
        self, other: "Value", interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> Bool | BLError:
        match other:
            case String(other_val):
                return BOOLS[self.value == other_val]
        return super().is_equal(other, interpreter, meta)

    @override
    def is_less(
        self, other: "Value", interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        match other:
            case String(other_val):
                return BOOLS[self.value < other_val]
        return super().is_less(other, interpreter, meta)

    @override
    def is_less_or_equal(
        self, other: "Value", interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        match other:
            case String(other_val):
                return BOOLS[self.value <= other_val]
        return super().is_less_or_equal(other, interpreter, meta)

    @override
    def is_greater(
        self, other: "Value", interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        match other:
            case String(other_val):
                return BOOLS[self.value > other_val]
        return super().is_greater(other, interpreter, meta)

    @override
    def is_greater_or_equal(
        self, other: "Value", interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        match other:
            case String(other_val):
                return BOOLS[self.value >= other_val]
        return super().is_greater_or_equal(other, interpreter, meta)

    @override
    def get_item(
        self, index: Value, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> Value | BLError:
        from .numbers import Int  # pylint: disable=import-outside-toplevel
        match index:
            case Int(other_val):
                return String(self.value[other_val])
        return super().get_item(index, interpreter, meta)

    @override
    def to_bool(
        self, interpreter: "ASTInterpreter", meta: Meta | None
    ) -> Bool | BLError:
        return BOOLS[bool(self.value)]

    @override
    def dump(
        self, interpreter: "ASTInterpreter", meta: Meta | None
    ) -> "String":
        return String(repr(self.value))

    @override
    def to_string(
        self, interpreter: "ASTInterpreter", meta: Meta | None
    ) -> Self:
        return self


# section Functions


@dataclass(frozen=True)
class Call:
    """Call site type for tracebacks"""
    function: SupportsBLCall
    meta: Meta | None
    path: str | None


@dataclass
class PythonFunction(Value):
    """Python function wrapper type"""

    function: SupportsWrappedByPythonFunction
    this: "Instance | None" = None

    @override
    def call(
        self, args: list[Value], interpreter: "ASTInterpreter",
        meta: Meta | None
    ) -> ExpressionResult:
        return self.function(meta, interpreter, self.this, *args)

    def bind(self, this: "Instance") -> "PythonFunction":
        """Return a version of PythonFunction bound to an object"""
        return PythonFunction(self.function, this)

    @override
    def dump(
        self, interpreter: "ASTInterpreter", meta: Meta | None
    ) -> String:
        return String(f"<python function {self.function!r}>")


@dataclass
class BLFunction(Value):
    """baba-lang function type"""

    name: str
    form_args: FormArgs
    body: Body
    env: "Env | None" = None
    this: "Instance | None" = None

    @override
    def call(
        self, args: list[Value], interpreter: "ASTInterpreter",
        meta: Meta | None
    ) -> ExpressionResult:
        # Add the function to the "call stack"
        interpreter.traceback.append(Call(self, meta, interpreter.path))
        # Create an environment (call frame)
        old_env = interpreter.locals
        env = Env(interpreter, parent=self.env)
        # Populate it with arguments
        form_args = self.form_args.args
        try:
            for farg, arg in zip(form_args, args, strict=True):
                env.new_var(farg, arg)
        except ValueError:
            return BLError(cast_to_instance(
                IncorrectTypeException.new([], interpreter, meta)
            ), meta, interpreter.path)
        # If function is bound to an object, add that object
        if self.this is not None:
            env.new_var("this", self.this)
        # Run the body
        interpreter.locals = env
        res = interpreter.visit_stmt(self.body)
        # Clean it up
        interpreter.locals = old_env
        # Return!
        match res:
            case Success():
                interpreter.traceback.pop()
                return NULL
            case Return(value=value):
                interpreter.traceback.pop()
                return value
            case BLError():
                return res
        return BLError(cast_to_instance(
            NotImplementedException.new([], interpreter, meta)
        ), meta, interpreter.path)

    def bind(self, this: "Instance") -> "BLFunction":
        """Return a version of BLFunction bound to an object"""
        return BLFunction(
            self.name, self.form_args, self.body, self.env, this
        )

    @override
    def dump(self, interpreter: "ASTInterpreter", meta: Meta | None) -> String:
        if self.this is not None:
            this_to_str = self.this.dump(interpreter, meta).value
            return String(f"<method '{self.name}' bound to {this_to_str}>")
        return String(f"<function '{self.name}'>")


# section OOP


@dataclass
class Class(Value):
    """baba-lang class"""

    name: String
    super: "Class | None" = None
    vars: dict[str, Value] = field(default_factory=dict)

    @override
    def get_attr(
        self, attr: str, interpreter: "ASTInterpreter", meta: Meta | None
    ) -> ExpressionResult:
        try:
            return self.vars[attr]
        except KeyError:
            if self.super is not None:
                return self.super.get_attr(attr, interpreter, meta)
            return BLError(cast_to_instance(
                AttrNotFoundException.new([], interpreter, meta)
            ), meta, interpreter.path)

    def has_attr(self, attr: str) -> bool:
        """Check if a class has an attribute"""
        if attr in self.vars:
            return True
        if self.super is not None:
            return self.super.has_attr(attr)
        return False

    @override
    def new(
        self, args: list[Value], interpreter: "ASTInterpreter",
        meta: Meta | None
    ) -> ExpressionResult:
        inst = Instance(self, {})
        if self.has_attr("__init__"):  # __init__ is the constructor method
            constr = inst.get_attr("__init__", interpreter, meta)
            if isinstance(constr, BLError):
                return constr
            match res := constr.call(args, interpreter, meta):
                case BLError():
                    return res
        return inst

    @override
    def dump(self, interpreter: "ASTInterpreter", meta: Meta | None) -> String:
        return String(f"<class {self.name.value}>")


# Base class for all objects
ObjectClass = Class(String("Object"))


# Exception objects


def exc_init(
    meta: Meta | None, interpreter: "ASTInterpreter", this: "Instance | None",
    /, *args
) -> Null | BLError:
    """Initialize an exception"""
    if this is not None:
        if args:
            msg, *_ = args
            this.vars["msg"] = msg
        return NULL
    return BLError(cast_to_instance(
        NotImplementedException.new([], interpreter, meta)
    ), meta, interpreter.path)


def exc_dump(
    meta: Meta | None, interpreter: "ASTInterpreter", this: "Instance | None",
    /, *_
) -> String | BLError:
    """Debugging representation of exception"""
    if this is None:
        return BLError(cast_to_instance(
            NotImplementedException.new([], interpreter, meta)
        ), meta, interpreter.path)
    if "msg" not in this.vars:
        return String(f"{this.class_.name.value}")
    msg = this.vars['msg'].dump(interpreter, meta).value
    return String(f"{this.class_.name.value}: {msg}")


exc_methods: dict[str, Value] = {
    "__init__": PythonFunction(exc_init),
    "dump": PythonFunction(exc_dump),
}

ExceptionClass = Class(String("Exception"), ObjectClass, exc_methods)

NotImplementedException = Class(
    String("NotImplementedException"), ExceptionClass
)
AttrNotFoundException = Class(String("AttrNotFoundException"), ExceptionClass)
VarNotFoundException = Class(String("VarNotFoundException"), ExceptionClass)
IncorrectTypeException = Class(
    String("IncorrectTypeException"), ExceptionClass
)


@dataclass(init=False)
class Instance(Value):
    """baba-lang instance"""

    # pylint: disable=too-many-public-methods

    class_: Class
    vars: dict[str, Value]

    def __init__(self, class_: Class, vars_: dict[str, Value]):
        self.class_ = class_
        self.vars = vars_

    @override
    def get_attr(
        self, attr: str, interpreter: "ASTInterpreter", meta: Meta | None
    ) -> ExpressionResult:
        try:
            return self.vars[attr]
        except KeyError:
            match res := self.class_.get_attr(attr, interpreter, meta):
                case SupportsBLCall():
                    return res.bind(self)
                case _:
                    return res

    @override
    def set_attr(
        self, attr: str, value: "Value",
        interpreter: "ASTInterpreter", meta: Meta | None,
    ) -> ExpressionResult:
        match value:
            case BLError():
                return value
            case Value():
                self.vars[attr] = value
                return value
        return super().set_attr(attr, value, interpreter, meta)

    @override
    def add(
        self, other: "Value", interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        return self._overloaded_binary_op("__add__", "add")(
            other, interpreter, meta
        )

    @override
    def subtract(
        self, other: "Value", interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        return self._overloaded_binary_op("__sub__", "subtract")(
            other, interpreter, meta
        )

    @override
    def multiply(
        self, other: "Value", interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        return self._overloaded_binary_op("__mul__", "multiply")(
            other, interpreter, meta
        )

    @override
    def divide(
        self, other: "Value", interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        return self._overloaded_binary_op("__div__", "divide")(
            other, interpreter, meta
        )

    @override
    def floor_div(
        self, other: "Value", interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        return self._overloaded_binary_op("__floordiv__", "floor_div")(
            other, interpreter, meta
        )

    @override
    def modulo(
        self, other: "Value", interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        return self._overloaded_binary_op("__mod__", "modulo")(
            other, interpreter, meta
        )

    @override
    def power(
        self, other: "Value", interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        return self._overloaded_binary_op("__pow__", "power")(
            other, interpreter, meta
        )

    @override
    def bit_and(
        self, other: "Value", interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        return self._overloaded_binary_op("__and__", "bit_and")(
            other, interpreter, meta
        )

    @override
    def bit_or(
        self, other: "Value", interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        return self._overloaded_binary_op("__or__", "bit_or")(
            other, interpreter, meta
        )

    @override
    def bit_xor(
        self, other: "Value", interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        return self._overloaded_binary_op("__xor__", "bit_xor")(
            other, interpreter, meta
        )

    @override
    def left_shift(
        self, other: "Value", interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        return self._overloaded_binary_op("__lshift__", "left_shift")(
            other, interpreter, meta
        )

    @override
    def right_shift(
        self, other: "Value", interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        return self._overloaded_binary_op("__rshift__", "right_shift")(
            other, interpreter, meta
        )

    @override
    def is_equal(
        self, other: "Value", interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> Bool | BLError:
        return cast(
            Bool | BLError, self._overloaded_binary_op("__eq__", "is_equal")(
                other, interpreter, meta
            )
        )

    @override
    def is_less(
        self, other: "Value", interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        return self._overloaded_binary_op("__lt__", "is_less")(
            other, interpreter, meta
        )

    @override
    def is_less_or_equal(
        self, other: "Value", interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        return self._overloaded_binary_op("__le__", "is_less_or_equal")(
            other, interpreter, meta
        )

    @override
    def is_greater(
        self, other: "Value", interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        return self._overloaded_binary_op("__gt__", "is_greater")(
            other, interpreter, meta
        )

    @override
    def is_greater_or_equal(
        self, other: "Value", interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        return self._overloaded_binary_op("__ge__", "is_greater_or_equal")(
            other, interpreter, meta
        )

    @override
    def plus(
        self, interpreter: "ASTInterpreter", meta: Meta | None
    ) -> ExpressionResult:
        return self._overloaded_unary_op("__pos__", "plus")(
            interpreter, meta
        )

    @override
    def neg(
        self, interpreter: "ASTInterpreter", meta: Meta | None
    ) -> ExpressionResult:
        return self._overloaded_unary_op("__neg__", "neg")(
            interpreter, meta
        )

    @override
    def bit_not(
        self, interpreter: "ASTInterpreter", meta: Meta | None
    ) -> ExpressionResult:
        return self._overloaded_unary_op("__bitnot__", "bit_not")(
            interpreter, meta
        )

    @override
    def get_item(
        self, index: "Value", interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        return self._overloaded_binary_op("__getitem__", "get_item")(
            index, interpreter, meta
        )

    @override
    def set_item(
        self, index: "Value", value: "Value",
        interpreter: "ASTInterpreter", meta: Meta | None,
    ) -> ExpressionResult:
        if isinstance(index, BLError):
            return index
        if isinstance(value, BLError):
            return value
        res = self._call_method_if_exists(
            "__setitem__", [index, value], interpreter, meta
        )
        if isinstance(res, BLError):
            if res.value.class_ == AttrNotFoundException:
                return super().set_item(
                    index, value, interpreter, meta
                )
        return res

    @override
    def to_bool(self, interpreter: "ASTInterpreter", meta: Meta | None):
        return cast(
            Bool | BLError, self._overloaded_typechecked_unary_op(
                "to_bool", "to_bool", Bool
            )(interpreter, meta)
        )

    @override
    def to_iter(
        self, interpreter: "ASTInterpreter", meta: Meta | None
    ) -> ExpressionResult:
        return self._overloaded_unary_op("iter", "to_iter")(
            interpreter, meta
        )

    @override
    def next(self, interpreter: "ASTInterpreter", meta: Meta | None):
        from .iterator import Item  # pylint: disable=import-outside-toplevel
        return cast(
            Item | Null | BLError, self._overloaded_typechecked_unary_op(
                "next", "next", (Item, Null)
            )(interpreter, meta)
        )

    @override
    def dump(self, interpreter: "ASTInterpreter", meta: Meta | None):
        return cast(
            String | BLError, self._overloaded_typechecked_unary_op(
                "dump", "dump", String
            )(interpreter, meta)
        )

    @override
    def to_string(self, interpreter: "ASTInterpreter", meta: Meta | None):
        return cast(
            String | BLError, self._overloaded_typechecked_unary_op(
                "to_string", "to_string", String
            )(interpreter, meta)
        )

    def _overloaded_typechecked_unary_op(
        self, name: str, fallback_name: str,
        expected_type: type | tuple[type, ...]
    ):
        def _wrapper(
            interpreter: "ASTInterpreter", meta: Meta | None
        ) -> ExpressionResult:
            res = self._call_method_if_exists(name, [], interpreter, meta)
            if not isinstance(res, expected_type):
                if isinstance(res, BLError):
                    if res.value.class_ == AttrNotFoundException:
                        return getattr(super(type(self), self), fallback_name)(
                            interpreter, meta
                        )
                    return res
                return BLError(cast_to_instance(
                    IncorrectTypeException.new([], interpreter, meta)
                ), meta, interpreter.path)
            return res
        return _wrapper

    def _overloaded_binary_op(self, name: str, fallback_name: str):
        def _wrapper(
            other: "Value", interpreter: "ASTInterpreter",
            meta: Meta | None,
        ) -> ExpressionResult:
            if isinstance(other, BLError):
                return other
            res = self._call_method_if_exists(
                name, [other], interpreter, meta
            )
            if isinstance(res, BLError):
                if res.value.class_ == AttrNotFoundException:
                    return getattr(super(type(self), self), fallback_name)(
                        other, interpreter, meta
                    )
            return res
        return _wrapper

    def _overloaded_unary_op(self, name: str, fallback_name: str):
        def _wrapper(
            interpreter: "ASTInterpreter", meta: Meta | None
        ) -> ExpressionResult:
            res = self._call_method_if_exists(name, [], interpreter, meta)
            if isinstance(res, BLError):
                if res.value.class_ == AttrNotFoundException:
                    return getattr(super(type(self), self), fallback_name)(
                        interpreter, meta
                    )
            return res
        return _wrapper

    def _call_method_if_exists(
        self, name: str, args: list[Value], interpreter: "ASTInterpreter",
        meta: Meta | None
    ) -> ExpressionResult:
        res = self.get_attr(name, interpreter, meta)
        if isinstance(res, SupportsBLCall):
            return res.bind(self).call(args, interpreter, meta)
        return res


# section Environment


@dataclass
class Var:
    """Interpreter mutable binding"""
    value: Value


class Env:
    """Interpreter environment"""

    interpreter: "ASTInterpreter"
    vars: dict[str, Var]
    parent: "Env | None"

    def __init__(
        self, interpreter: "ASTInterpreter",
        vars_: dict[str, Var] | None = None, parent: "Env | None" = None,
    ):
        if vars_ is None:
            self.vars = {}
        else:
            self.vars = vars_
        self.interpreter = interpreter
        self.parent = parent

    def new_var(self, name: str, value: Value) -> None:
        """Set a new/existing variable"""
        self.vars[name] = Var(value)

    def get_var(self, name: str, meta: Meta | None) -> ExpressionResult:
        """Retrieve the value of a variable"""
        resolve_result = self.resolve_var(name, meta)
        match resolve_result:
            case Var(value=value):
                return value
            case BLError():
                return resolve_result

    def set_var(self, name: str, value: Value, meta: Meta | None
                ) -> BLError | None:
        """Assign to an existing variable name"""
        resolve_result = self.resolve_var(name, meta)
        match resolve_result:
            case Var():
                resolve_result.value = value
            case BLError():
                return resolve_result

    def resolve_var(self, name: str, meta: Meta | None) -> Var | BLError:
        """Resolve a variable name"""
        if name in self.vars:
            return self.vars[name]
        if self.parent is not None:
            return self.parent.resolve_var(name, meta)
        return BLError(cast_to_instance(
            VarNotFoundException.new([], self.interpreter, meta)
        ), meta, self.interpreter.path)

    def copy(self) -> "Env":
        """Copy the environment (for capturing variables in closures)"""
        return Env(self.interpreter, self.vars.copy(), self.parent)
