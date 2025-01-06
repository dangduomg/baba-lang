"""Base, error and essential value classes"""


from abc import ABC
from typing import Self, TYPE_CHECKING, override, cast
from dataclasses import dataclass, field
from collections.abc import Callable

from lark import Token
from lark.tree import Meta

from bl_ast.nodes import FormArgs, Body

from .abc_protocols import (
    Result, Exit, SupportsBLCall, SupportsWrappedByPythonFunction
)

if TYPE_CHECKING:
    from ..main import ASTInterpreter


# pylint: disable=too-few-public-methods
# pylint: disable=too-many-public-methods
# pylint: disable=unused-argument


# TODO: split this file up this is an absolute monolith


# section Helpers


def cast_to_instance(value: "ExpressionResult") -> "Instance":
    """Cast a value to an instance"""
    return cast("Instance", value)


# section Result


@dataclass(frozen=True)
class Success(Result):
    """Object signaling sucessful statement execution (without returning
any value)"""


@dataclass(frozen=True)
class Return(Exit):
    """Return statement"""
    value: "Value"


class ExpressionResult(Result, ABC):
    """Expression result base class"""

    def binary_op(
        self, op: str, other: "ExpressionResult",
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
                return (
                    self.is_equal(other, interpreter, meta)
                    .logical_not(interpreter, meta)
                )
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
                [String(f"Operator {op} is not supported")], interpreter, meta
            )
        ), meta)

    def add(
        self, other: "ExpressionResult", interpreter: "ASTInterpreter",
        meta: Meta | None
    ) -> "ExpressionResult":
        """Addition"""
        return self._unimplemented_binary_op('+', other, interpreter, meta)

    def subtract(
        self, other: "ExpressionResult", interpreter: "ASTInterpreter",
        meta: Meta | None
    ) -> "ExpressionResult":
        """Subtraction"""
        return self._unimplemented_binary_op('-', other, interpreter, meta)

    def multiply(
        self, other: "ExpressionResult", interpreter: "ASTInterpreter",
        meta: Meta | None
    ) -> "ExpressionResult":
        """Multiplication"""
        return self._unimplemented_binary_op('*', other, interpreter, meta)

    def divide(
        self, other: "ExpressionResult", interpreter: "ASTInterpreter",
        meta: Meta | None
    ) -> "ExpressionResult":
        """Division"""
        return self._unimplemented_binary_op('/', other, interpreter, meta)

    def bit_and(
        self, other: "ExpressionResult", interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> "ExpressionResult":
        """Bitwise and"""
        return self._unimplemented_binary_op('&', other, interpreter, meta)

    def bit_or(
        self, other: "ExpressionResult", interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> "ExpressionResult":
        """Bitwise or"""
        return self._unimplemented_binary_op('|', other, interpreter, meta)

    def bit_xor(
        self, other: "ExpressionResult", interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> "ExpressionResult":
        """Bitwise exclusive or"""
        return self._unimplemented_binary_op('^', other, interpreter, meta)

    def left_shift(
        self, other: "ExpressionResult", interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> "ExpressionResult":
        """Left shift"""
        return self._unimplemented_binary_op('<<', other, interpreter, meta)

    def right_shift(
        self, other: "ExpressionResult", interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> "ExpressionResult":
        """Right shift"""
        return self._unimplemented_binary_op('>>', other, interpreter, meta)

    def is_equal(
        self, other: "ExpressionResult", interpreter: "ASTInterpreter",
        meta: Meta | None
    ) -> "ExpressionResult":
        """Equality test"""
        return self._unimplemented_binary_op('==', other, interpreter, meta)

    def is_not_equal(
        self, other: "ExpressionResult", interpreter: "ASTInterpreter",
        meta: Meta | None
    ) -> "ExpressionResult":
        """Inequality test"""
        return self._unimplemented_binary_op('!=', other, interpreter, meta)

    def is_less(
        self, other: "ExpressionResult", interpreter: "ASTInterpreter",
        meta: Meta | None
    ) -> "ExpressionResult":
        """Less than"""
        return self._unimplemented_binary_op('<', other, interpreter, meta)

    def is_less_or_equal(
        self, other: "ExpressionResult", interpreter: "ASTInterpreter",
        meta: Meta | None
    ) -> "ExpressionResult":
        """Less than or equal to"""
        return self._unimplemented_binary_op('<=', other, interpreter, meta)

    def is_greater(
        self, other: "ExpressionResult", interpreter: "ASTInterpreter",
        meta: Meta | None
    ) -> "ExpressionResult":
        """Greater than"""
        return self._unimplemented_binary_op('>', other, interpreter, meta)

    def is_greater_or_equal(
        self, other: "ExpressionResult", interpreter: "ASTInterpreter",
        meta: Meta | None
    ) -> "ExpressionResult":
        """Greater than or equal to"""
        return self._unimplemented_binary_op('>=', other, interpreter, meta)

    def _unimplemented_binary_op(
        self, op: str, other: "ExpressionResult",
        interpreter: "ASTInterpreter", meta: Meta | None,
    ) -> "BLError":
        """Unimplemented binary operation stub"""
        match other:
            case BLError():
                return other
        return BLError(cast_to_instance(
            NotImplementedException.new(
                [String(f"Operator {op!r} is not supported")],
                interpreter, meta,
            )
        ), meta)

    def unary_op(
        self, op: Token, interpreter: "ASTInterpreter", meta: Meta | None
    ) -> "ExpressionResult":
        """Unary operation"""
        match op:
            case "-":
                return self.neg(interpreter, meta)
            case "!":
                return self.logical_not(interpreter, meta)
        return BLError(cast_to_instance(
            NotImplementedException.new([], interpreter, meta)
        ), meta)

    def neg(
        self, interpreter: "ASTInterpreter", meta: Meta | None
    ) -> "ExpressionResult":
        """Negation"""
        return self._unimplemented_unary_op("-", interpreter, meta)

    def logical_not(
        self, interpreter: "ASTInterpreter", meta: Meta | None
    ) -> "ExpressionResult":
        """Conversion to boolean"""
        return self._unimplemented_unary_op("!", interpreter, meta)

    def _unimplemented_unary_op(
        self, op: str, interpreter: "ASTInterpreter", meta: Meta | None
    ) -> "BLError":
        return BLError(cast_to_instance(
            NotImplementedException.new(
                [String(f"Operation {op!r} is not supported")],
                interpreter, meta,
            )
        ), meta)

    def get_attr(
        self, attr: str, interpreter: "ASTInterpreter", meta: Meta | None
    ) -> "ExpressionResult":
        """Access an attribute"""
        return BLError(cast_to_instance(
            NotImplementedException.new([], interpreter, meta)
        ), meta)

    def set_attr(
        self, attr: str, value: "ExpressionResult",
        interpreter: "ASTInterpreter", meta: Meta | None
    ) -> "ExpressionResult":
        """Set an attribute"""
        match value:
            case BLError():
                return value
        return BLError(cast_to_instance(
            NotImplementedException.new(
                [String("Subscript assignment is not supported")],
                interpreter, meta,
            )
        ), meta)

    def call(
        self, args: list["Value"], interpreter: "ASTInterpreter",
        meta: Meta | None
    ) -> "ExpressionResult":
        """Call self as a function"""
        return BLError(cast_to_instance(
            NotImplementedException.new([], interpreter, meta)
        ), meta)

    def new(
        self, args: list["Value"], interpreter: "ASTInterpreter",
        meta: Meta | None
    ) -> "ExpressionResult":
        """Instantiate an object"""
        return BLError(cast_to_instance(
            NotImplementedException.new([], interpreter, meta)
        ), meta)

    def dump(
        self, interpreter: "ASTInterpreter", meta: Meta | None
    ) -> "ExpressionResult":
        """Conversion to representation for debugging"""
        return BLError(cast_to_instance(
            NotImplementedException.new([], interpreter, meta)
        ), meta)


# section Error


@dataclass(init=False)
class BLError(Exit, ExpressionResult):
    """Error result type"""

    value: "Instance"
    meta: Meta | None = None

    def __init__(self, value: "Instance", meta: Meta | None) -> None:
        self.value = value
        self.value.vars["meta"] = PythonValue(meta)
        self.meta = meta

    @override
    def add(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> Self:
        return self

    @override
    def subtract(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> Self:
        return self

    @override
    def multiply(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> Self:
        return self

    @override
    def divide(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> Self:
        return self

    @override
    def bit_and(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> Self:
        return self

    @override
    def bit_or(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None
    ) -> Self:
        return self

    @override
    def bit_xor(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None
    ) -> Self:
        return self

    @override
    def left_shift(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None
    ) -> Self:
        return self

    @override
    def right_shift(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None
    ) -> Self:
        return self

    @override
    def is_equal(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> Self:
        return self

    @override
    def is_not_equal(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> Self:
        return self

    @override
    def is_less(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> Self:
        return self

    @override
    def is_less_or_equal(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> Self:
        return self

    @override
    def is_greater(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> Self:
        return self

    @override
    def is_greater_or_equal(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> Self:
        return self

    @override
    def neg(self, interpreter: "ASTInterpreter", meta: Meta | None) -> Self:
        return self

    @override
    def get_attr(
        self, attr: str, interpreter: "ASTInterpreter", meta: Meta | None
    ) -> Self:
        return self

    @override
    def set_attr(
        self, attr: str, value: ExpressionResult,
        interpreter: "ASTInterpreter", meta: Meta | None,
    ) -> Self:
        return self

    @override
    def call(
        self, args: list["Value"], interpreter: "ASTInterpreter",
        meta: Meta | None
    ) -> Self:
        return self

    @override
    def new(
        self, args: list["Value"], interpreter: "ASTInterpreter",
        meta: Meta | None
    ) -> Self:
        return self

    @override
    def dump(self, interpreter: "ASTInterpreter", meta: Meta | None) -> Self:
        return self


# section Values


class Value(ExpressionResult):
    """Value base class"""

    @override
    def is_equal(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> "Bool":
        return BOOLS[self is other]

    @override
    def _unimplemented_binary_op(
        self, op: str, other: ExpressionResult,
        interpreter: "ASTInterpreter", meta: Meta | None,
    ) -> BLError:
        """Unimplemented binary operation stub"""
        match other:
            case Value():
                match self_dump := self.dump(interpreter, meta):
                    case BLError():
                        return self_dump
                match other_dump := other.dump(interpreter, meta):
                    case BLError():
                        return other_dump
                return BLError(cast_to_instance(
                    NotImplementedException.new([String(
                        f"Operator {op!r} is not supported for" +
                        f"{self_dump.value} and {other_dump.value}"
                    )], interpreter, meta)
                ), meta)
        return super()._unimplemented_binary_op(op, other, interpreter, meta)

    @override
    def logical_not(
        self, interpreter: "ASTInterpreter", meta: Meta | None
    ) -> "Bool | BLError":
        return BOOLS[False]

    @override
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
        ), meta)

    @override
    def dump(
        self, interpreter: "ASTInterpreter", meta: Meta | None
    ) -> "String | BLError":
        return String("<value>")


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
    def logical_not(
        self, interpreter: "ASTInterpreter", meta: Meta | None
    ) -> "Bool":
        return BOOLS[not self.value]

    @override
    def dump(
        self, interpreter: "ASTInterpreter", meta: Meta | None
    ) -> "String":
        return String("true") if self.value else String("false")


BOOLS = Bool(False), Bool(True)


@dataclass(frozen=True)
class Null(Value):
    """Null value"""

    @override
    def logical_not(
        self, interpreter: "ASTInterpreter", meta: Meta | None
    ) -> Bool:
        return BOOLS[True]

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
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        match other:
            case String(other_val):
                return String(self.value + other_val)
        return super().add(other, interpreter, meta)

    @override
    def multiply(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        from .numbers import Int  # pylint: disable=import-outside-toplevel
        match other:
            case Int(times):
                return String(self.value * times)
        return super().multiply(other, interpreter, meta)

    @override
    def is_equal(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> Bool:
        match other:
            case String(other_val):
                return BOOLS[self.value == other_val]
        return super().is_equal(other, interpreter, meta)

    @override
    def is_less(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        match other:
            case String(other_val):
                return BOOLS[self.value < other_val]
        return super().is_less(other, interpreter, meta)

    @override
    def is_less_or_equal(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        match other:
            case String(other_val):
                return BOOLS[self.value <= other_val]
        return super().is_less_or_equal(other, interpreter, meta)

    @override
    def is_greater(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        match other:
            case String(other_val):
                return BOOLS[self.value > other_val]
        return super().is_greater(other, interpreter, meta)

    @override
    def is_greater_or_equal(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        match other:
            case String(other_val):
                return BOOLS[self.value >= other_val]
        return super().is_greater_or_equal(other, interpreter, meta)

    @override
    def logical_not(
        self, interpreter: "ASTInterpreter", meta: Meta | None
    ) -> Bool | BLError:
        return BOOLS[not self.value]

    @override
    def dump(
        self, interpreter: "ASTInterpreter", meta: Meta | None
    ) -> "String":
        return String(f"{self.value!r}")


# section Functions


@dataclass(frozen=True)
class Call:
    """Call site type for tracebacks"""
    function: SupportsBLCall
    meta: Meta | None


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
        interpreter.calls.append(Call(self, meta))
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
            ), meta)
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
                interpreter.calls.pop()
                return NULL
            case Return(value=value):
                interpreter.calls.pop()
                return value
            case BLError():
                return res
        return BLError(cast_to_instance(
            NotImplementedException.new([], interpreter, meta)
        ), meta)

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
            ), meta)

    @override
    def new(
        self, args: list[Value], interpreter: "ASTInterpreter",
        meta: Meta | None
    ) -> ExpressionResult:
        inst = Instance(self, {})
        if "__init__" in self.vars:  # __init__ is the constructor method
            constr = inst.get_attr("__init__", interpreter, meta)
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
    /, msg: String, *_
) -> Null | BLError:
    """Initialize an exception"""
    if this is not None:
        this.vars["msg"] = msg
        return NULL
    return BLError(cast_to_instance(
        NotImplementedException.new([], interpreter, meta)
    ), meta)


def exc_dump(
    meta: Meta | None, interpreter: "ASTInterpreter", this: "Instance | None",
    /, *_
) -> String | BLError:
    """Debugging representation of exception"""
    if this is not None:
        return String(f"{this.class_.name.value}")
    return BLError(cast_to_instance(
        NotImplementedException.new([], interpreter, meta)
    ), meta)


exc_methods: dict[str, Value] = {
    "__init__": PythonFunction(exc_init),
    "__dump__": PythonFunction(exc_dump),
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
        self, attr: str, value: ExpressionResult,
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
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        return self._overloaded_binary_op("__add__", "add")(
            other, interpreter, meta
        )

    @override
    def subtract(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        return self._overloaded_binary_op("__sub__", "subtract")(
            other, interpreter, meta
        )

    @override
    def multiply(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        return self._overloaded_binary_op("__mul__", "multiply")(
            other, interpreter, meta
        )

    @override
    def divide(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        return self._overloaded_binary_op("__div__", "divide")(
            other, interpreter, meta
        )

    @override
    def bit_and(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        return self._overloaded_binary_op("__and__", "bit_and")(
            other, interpreter, meta
        )

    @override
    def bit_or(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        return self._overloaded_binary_op("__or__", "bit_or")(
            other, interpreter, meta
        )

    @override
    def bit_xor(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        return self._overloaded_binary_op("__xor__", "bit_xor")(
            other, interpreter, meta
        )

    @override
    def left_shift(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        return self._overloaded_binary_op("__lshift__", "left_shift")(
            other, interpreter, meta
        )

    @override
    def right_shift(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        return self._overloaded_binary_op("__rshift__", "right_shift")(
            other, interpreter, meta
        )

    @override
    def is_equal(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> Bool:
        return self._overloaded_binary_op("__eq__", "is_equal")(
            other, interpreter, meta
        )

    @override
    def is_less(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        return self._overloaded_binary_op("__lt__", "is_less")(
            other, interpreter, meta
        )

    @override
    def is_less_or_equal(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        return self._overloaded_binary_op("__le__", "is_less_or_equal")(
            other, interpreter, meta
        )

    @override
    def is_greater(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        return self._overloaded_binary_op("__gt__", "is_greater")(
            other, interpreter, meta
        )

    @override
    def is_greater_or_equal(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        return self._overloaded_binary_op("__ge__", "is_greater_or_equal")(
            other, interpreter, meta
        )

    @override
    def neg(
        self, interpreter: "ASTInterpreter", meta: Meta | None
    ) -> ExpressionResult:
        return self._overloaded_unary_op("__neg__", "neg")(
            interpreter, meta
        )

    @override
    def logical_not(
        self, interpreter: "ASTInterpreter", meta: Meta | None
    ) -> Bool | BLError:
        return self._overloaded_unary_op("__not__", "logical_not")(
            interpreter, meta
        )

    @override
    def dump(
        self, interpreter: "ASTInterpreter", meta: Meta | None
    ) -> String | BLError:
        res = self._call_method_if_exists("__dump__", [], interpreter, meta)
        if not isinstance(res, String):
            if isinstance(res, BLError):
                if res.value.class_ == AttrNotFoundException:
                    class_to_str = self.class_.dump(interpreter, meta).value
                    return String(f"<object of {class_to_str}>")
                return res
            return BLError(cast_to_instance(
                IncorrectTypeException.new([], interpreter, meta)
            ), meta)
        return res

    def _overloaded_binary_op(self, name: str, fallback_name: str) -> Callable:
        def _wrapper(
            other: ExpressionResult, interpreter: "ASTInterpreter",
            meta: Meta | None,
        ) -> ExpressionResult:
            if isinstance(other, BLError):
                return other
            if isinstance(other, Value):
                res = self._call_method_if_exists(
                    name, [other], interpreter, meta
                )
                if isinstance(res, BLError):
                    if res.value.class_ == VarNotFoundException:
                        return super().__getattribute__(fallback_name)(
                            other, interpreter, meta
                        )
                return res
            return BLError(cast_to_instance(
                NotImplementedException.new([], interpreter, meta)
            ), meta)
        return _wrapper

    def _overloaded_unary_op(self, name: str, fallback_name: str) -> Callable:
        def _wrapper(
            interpreter: "ASTInterpreter", meta: Meta | None
        ) -> ExpressionResult:
            res = self._call_method_if_exists(name, [], interpreter, meta)
            if isinstance(res, BLError):
                if res.value.class_ == VarNotFoundException:
                    return super().__getattribute__(fallback_name)(
                        interpreter, meta
                    )
            return res
        return _wrapper

    def _call_method_if_exists(
        self, name: str, args: list[Value], interpreter: "ASTInterpreter",
        meta: Meta | None
    ) -> ExpressionResult:
        match res := self.get_attr(name, interpreter, meta):
            case SupportsBLCall():
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
        ), meta)

    def copy(self) -> "Env":
        """Copy the environment (for capturing variables in closures)"""
        return Env(self.interpreter, self.vars.copy(), self.parent)
