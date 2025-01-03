"""Base, error and essential value classes"""


from abc import ABC
from typing import Self, TYPE_CHECKING, override, cast
from dataclasses import dataclass, field
from collections.abc import Callable

from lark import Token
from lark.tree import Meta

from bl_ast.nodes import FormArgs, Body

from .abc_protocols import Result, Exit, SupportsBLCall

if TYPE_CHECKING:
    from ..main import ASTInterpreter


# pylint: disable=too-few-public-methods
# pylint: disable=too-many-public-methods
# pylint: disable=unused-argument


# TODO: split this file up this is an absolute monolith


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
        return BLError(cast(
            Instance, NotImplementedException.new([], interpreter, meta)
        ), meta)

    def add(
        self, other: "ExpressionResult", interpreter: "ASTInterpreter",
        meta: Meta | None
    ) -> "ExpressionResult":
        """Addition"""
        return self._unimplemented_binary_op(other, interpreter, meta)

    def subtract(
        self, other: "ExpressionResult", interpreter: "ASTInterpreter",
        meta: Meta | None
    ) -> "ExpressionResult":
        """Subtraction"""
        return self._unimplemented_binary_op(other, interpreter, meta)

    def multiply(
        self, other: "ExpressionResult", interpreter: "ASTInterpreter",
        meta: Meta | None
    ) -> "ExpressionResult":
        """Multiplication"""
        return self._unimplemented_binary_op(other, interpreter, meta)

    def divide(
        self, other: "ExpressionResult", interpreter: "ASTInterpreter",
        meta: Meta | None
    ) -> "ExpressionResult":
        """Division"""
        return self._unimplemented_binary_op(other, interpreter, meta)

    def is_equal(
        self, other: "ExpressionResult", interpreter: "ASTInterpreter",
        meta: Meta | None
    ) -> "ExpressionResult":
        """Equality test"""
        return self._unimplemented_binary_op(other, interpreter, meta)

    def is_not_equal(
        self, other: "ExpressionResult", interpreter: "ASTInterpreter",
        meta: Meta | None
    ) -> "ExpressionResult":
        """Inequality test"""
        return self._unimplemented_binary_op(other, interpreter, meta)

    def is_less(
        self, other: "ExpressionResult", interpreter: "ASTInterpreter",
        meta: Meta | None
    ) -> "ExpressionResult":
        """Less than"""
        return self._unimplemented_binary_op(other, interpreter, meta)

    def is_less_or_equal(
        self, other: "ExpressionResult", interpreter: "ASTInterpreter",
        meta: Meta | None
    ) -> "ExpressionResult":
        """Less than or equal to"""
        return self._unimplemented_binary_op(other, interpreter, meta)

    def is_greater(
        self, other: "ExpressionResult", interpreter: "ASTInterpreter",
        meta: Meta | None
    ) -> "ExpressionResult":
        """Greater than"""
        return self._unimplemented_binary_op(other, interpreter, meta)

    def is_greater_or_equal(
        self, other: "ExpressionResult", interpreter: "ASTInterpreter",
        meta: Meta | None
    ) -> "ExpressionResult":
        """Greater than or equal to"""
        return self._unimplemented_binary_op(other, interpreter, meta)

    def _unimplemented_binary_op(
        self, other: "ExpressionResult", interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> "BLError":
        """Unimplemented binary operation stub"""
        match other:
            case BLError():
                return other
        return BLError(cast(
            Instance, NotImplementedException.new([], interpreter, meta)
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
        return BLError(cast(
            Instance, NotImplementedException.new([], interpreter, meta)
        ), meta)

    def neg(
        self, interpreter: "ASTInterpreter", meta: Meta | None
    ) -> "ExpressionResult":
        """Negation"""
        return BLError(cast(
            Instance, NotImplementedException.new([], interpreter, meta)
        ), meta)

    def logical_not(
        self, interpreter: "ASTInterpreter", meta: Meta | None
    ) -> "ExpressionResult":
        """Conversion to boolean"""
        return BLError(cast(
            Instance, NotImplementedException.new([], interpreter, meta)
        ))

    def get_attr(
        self, attr: str, interpreter: "ASTInterpreter", meta: Meta | None
    ) -> "ExpressionResult":
        """Access an attribute"""
        return BLError(cast(
            Instance, NotImplementedException.new([], interpreter, meta)
        ), meta)

    def set_attr(
        self, attr: str, value: "ExpressionResult",
        interpreter: "ASTInterpreter", meta: Meta | None
    ) -> "ExpressionResult":
        """Set an attribute"""
        return self._unimplemented_binary_op(value, interpreter, meta)

    def call(
        self, args: list["Value"], interpreter: "ASTInterpreter",
        meta: Meta | None
    ) -> "ExpressionResult":
        """Call self as a function"""
        return BLError(cast(
            Instance, NotImplementedException.new([], interpreter, meta)
        ), meta)

    def new(
        self, args: list["Value"], interpreter: "ASTInterpreter",
        meta: Meta | None
    ) -> "ExpressionResult":
        """Instantiate an object"""
        return BLError(cast(
            Instance, NotImplementedException.new([], interpreter, meta)
        ), meta)

    def dump(
        self, interpreter: "ASTInterpreter", meta: Meta | None
    ) -> "ExpressionResult":
        """Conversion to representation for debugging"""
        return BLError(cast(
            Instance, NotImplementedException.new([], interpreter, meta)
        ), meta)


# section Error


@dataclass
class BLError(Exit, ExpressionResult):
    """Error result type"""

    value: "Instance"
    meta: Meta | None = None

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


# endsection


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
    def logical_not(
        self, interpreter: "ASTInterpreter", meta: Meta | None
    ) -> "Bool | BLError":
        return BOOLS[False]

    @override
    def dump(
        self, interpreter: "ASTInterpreter", meta: Meta | None
    ) -> "String | BLError":
        return String("<value>")


@dataclass(frozen=True)
class Bool(Value):
    """Boolean type"""

    value: bool

    @override
    def logical_not(
        self, interpreter: "ASTInterpreter", meta: Meta | None
    ) -> "Bool":
        return Bool(not self.value)

    @override
    def dump(
        self, interpreter: "ASTInterpreter", meta: Meta | None
    ) -> "String":
        if self.value:
            return String("true")
        return String("false")


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

    def is_less(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        match other:
            case String(other_val):
                return BOOLS[self.value < other_val]
        return super().is_less(other, interpreter, meta)

    def is_less_or_equal(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        match other:
            case String(other_val):
                return BOOLS[self.value <= other_val]
        return super().is_less_or_equal(other, interpreter, meta)

    def is_greater(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        match other:
            case String(other_val):
                return BOOLS[self.value > other_val]
        return super().is_greater(other, interpreter, meta)

    def is_greater_or_equal(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        match other:
            case String(other_val):
                return BOOLS[self.value >= other_val]
        return super().is_greater_or_equal(other, interpreter, meta)

    def dump(
        self, interpreter: "ASTInterpreter", meta: Meta | None
    ) -> "String":
        return String(f"{self.value!r}")


# section Numbers


@dataclass(frozen=True)
class Int(Value):
    """Integer type"""

    value: int

    def add(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        match other:
            case Int(other_val):
                return Int(self.value + other_val)
            case Float(other_val):
                return Float(self.value + other_val)
        return super().add(other, interpreter, meta)

    def subtract(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        match other:
            case Int(other_val):
                return Int(self.value - other_val)
            case Float(other_val):
                return Float(self.value - other_val)
        return super().subtract(other, interpreter, meta)

    def multiply(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        match other:
            case Int(other_val):
                return Int(self.value * other_val)
            case Float(other_val):
                return Float(self.value * other_val)
        return super().multiply(other, interpreter, meta)

    def divide(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        match other:
            case Int(other_val) | Float(other_val):
                try:
                    return Float(self.value / other_val)
                except ZeroDivisionError:
                    return BLError(cast(
                        Instance, DivByZeroException.new([], interpreter, meta)
                    ))
        return super().divide(other, interpreter, meta)

    def is_equal(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> Bool:
        match other:
            case Int(other_val) | Float(other_val):
                return BOOLS[self.value == other_val]
        return super().is_equal(other, interpreter, meta)

    def is_less(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        match other:
            case Int(other_val) | Float(other_val):
                return BOOLS[self.value < other_val]
        return super().is_less(other, interpreter, meta)

    def is_less_or_equal(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        match other:
            case Int(other_val) | Float(other_val):
                return BOOLS[self.value <= other_val]
        return super().is_less_or_equal(other, interpreter, meta)

    def is_greater(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        match other:
            case Int(other_val) | Float(other_val):
                return BOOLS[self.value > other_val]
        return super().is_greater(other, interpreter, meta)

    def is_greater_or_equal(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        match other:
            case Int(other_val) | Float(other_val):
                return BOOLS[self.value >= other_val]
        return super().is_greater_or_equal(other, interpreter, meta)

    def neg(self, interpreter: "ASTInterpreter", meta: Meta | None) -> "Int":
        return Int(-self.value)

    def dump(self, interpreter: "ASTInterpreter", meta: Meta | None) -> String:
        return String(repr(self.value))


@dataclass(frozen=True)
class Float(Value):
    """Float type"""

    value: float

    def add(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        match other:
            case Float(other_val) | Int(other_val):
                return Float(self.value + other_val)
        return super().add(other, interpreter, meta)

    def subtract(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        match other:
            case Float(other_val) | Int(other_val):
                return Float(self.value - other_val)
        return super().subtract(other, interpreter, meta)

    def multiply(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        match other:
            case Float(other_val) | Int(other_val):
                return Float(self.value * other_val)
        return super().multiply(other, interpreter, meta)

    def divide(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        match other:
            case Float(other_val) | Int(other_val):
                try:
                    return Float(self.value / other_val)
                except ZeroDivisionError:
                    return BLError(cast(
                        Instance, DivByZeroException.new([], interpreter, meta)
                    ))
        return super().divide(other, interpreter, meta)

    def is_equal(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> Bool:
        match other:
            case Float(other_val) | Int(other_val):
                return BOOLS[self.value == other_val]
        return super().is_equal(other, interpreter, meta)

    def is_less(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        match other:
            case Float(other_val) | Int(other_val):
                return BOOLS[self.value < other_val]
        return super().is_less(other, interpreter, meta)

    def is_less_or_equal(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        match other:
            case Float(other_val) | Int(other_val):
                return BOOLS[self.value <= other_val]
        return super().is_less_or_equal(other, interpreter, meta)

    def is_greater(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        match other:
            case Float(other_val) | Int(other_val):
                return BOOLS[self.value > other_val]
        return super().is_greater(other, interpreter, meta)

    def is_greater_or_equal(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        match other:
            case Float(other_val) | Int(other_val):
                return BOOLS[self.value >= other_val]
        return super().is_greater_or_equal(other, interpreter, meta)

    def neg(
        self, interpreter: "ASTInterpreter", meta: Meta | None
    ) -> "Float":
        return Float(-self.value)

    def dump(
        self, interpreter: "ASTInterpreter", meta: Meta | None
    ) -> String:
        return String(repr(self.value))


# section Functions


@dataclass(frozen=True)
class Call:
    """Call site type for tracebacks"""
    function: "SupportsBLCall"
    meta: Meta | None


@dataclass(frozen=True)
class BLFunction(Value):
    """baba-lang function type"""

    name: str
    form_args: FormArgs
    body: Body
    env: "Env | None" = None
    this: "Instance | None" = None

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
            return BLError(cast(
                Instance, IncorrectTypeException.new([], interpreter, meta)
            ))
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
        return BLError(cast(
            Instance, NotImplementedException.new([], interpreter, meta)
        ))

    def bind(self, object_: "Instance") -> "BLFunction":
        """Return a version of BLFunction bound to an object"""
        return BLFunction(
            self.name, self.form_args, self.body, self.env, object_
        )

    def dump(self, interpreter: "ASTInterpreter", meta: Meta | None) -> String:
        if self.this is not None:
            this_to_str = self.this.dump(interpreter, meta).value
            return String(f"<method '{self.name}' bound to {this_to_str}>")
        return String(f"<function '{self.name}'>")


# section OOP


@dataclass(frozen=True)
class Class(Value):
    """baba-lang class"""

    name: str
    super: "Class | None" = None
    vars: dict[str, Value] = field(default_factory=dict)

    def get_attr(
        self, attr: str, interpreter: "ASTInterpreter", meta: Meta | None
    ) -> ExpressionResult:
        try:
            return self.vars[attr]
        except KeyError:
            if self.super is not None:
                return self.super.get_attr(attr, interpreter, meta)
            return BLError(cast(
                Instance, AttrNotFoundException.new([], interpreter, meta)
            ))

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

    def dump(self, interpreter: "ASTInterpreter", meta: Meta | None) -> String:
        return String("<class>")


# Base class for all objects
ObjectClass = Class("Object")

# Base class for all exceptions
ExceptionClass = Class("Exception", ObjectClass)
NotImplementedException = Class("NotImplementedException", ExceptionClass)
DivByZeroException = Class("DivByZeroException", ExceptionClass)
AttrNotFoundException = Class("AttrNotFoundException", ExceptionClass)
VarNotFoundException = Class("VarNotFoundException", ExceptionClass)
IncorrectTypeException = Class("IncorrectTypeException", ExceptionClass)


@dataclass(frozen=True)
class Instance(Value):
    """baba-lang instance"""

    # pylint: disable=too-many-public-methods

    class_: Class
    vars: dict[str, Value]

    def get_attr(
        self, attr: str, interpreter: "ASTInterpreter", meta: Meta | None
    ) -> ExpressionResult:
        try:
            return self.vars[attr]
        except KeyError:
            match res := self.class_.get_attr(attr, interpreter, meta):
                case BLFunction():
                    return res.bind(self)
                case _:
                    return res

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

    def add(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        return self._overloaded_binary_op("__add__", "add")(
            other, interpreter, meta
        )

    def subtract(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        return self._overloaded_binary_op("__sub__", "subtract")(
            other, interpreter, meta
        )

    def multiply(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        return self._overloaded_binary_op("__mul__", "multiply")(
            other, interpreter, meta
        )

    def divide(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        return self._overloaded_binary_op("__div__", "divide")(
            other, interpreter, meta
        )

    def is_equal(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> Bool:
        return self._overloaded_binary_op("__eq__", "is_equal")(
            other, interpreter, meta
        )

    def is_less(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        return self._overloaded_binary_op("__lt__", "is_less")(
            other, interpreter, meta
        )

    def is_less_or_equal(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        return self._overloaded_binary_op("__le__", "is_less_or_equal")(
            other, interpreter, meta
        )

    def is_greater(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        return self._overloaded_binary_op("__gt__", "is_greater")(
            other, interpreter, meta
        )

    def is_greater_or_equal(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        return self._overloaded_binary_op("__ge__", "is_greater_or_equal")(
            other, interpreter, meta
        )

    def neg(
        self, interpreter: "ASTInterpreter", meta: Meta | None
    ) -> ExpressionResult:
        res = self._call_method_if_exists("__neg__", [], interpreter, meta)
        if isinstance(res, BLError):
            if res.value.class_ == VarNotFoundException:
                return super().neg(interpreter, meta)
        return res

    def dump(
        self, interpreter: "ASTInterpreter", meta: Meta | None
    ) -> String | BLError:
        res = self._call_method_if_exists("__dump__", [], interpreter, meta)
        if not isinstance(res, String):
            if isinstance(res, BLError):
                if res.value.class_ == VarNotFoundException:
                    class_to_str = self.class_.dump(interpreter, meta).value
                    return String(f"<object of {class_to_str}>")
            return BLError(cast(
                Instance, IncorrectTypeException.new([], interpreter, meta)
            ))
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
            return BLError(cast(
                Instance, NotImplementedException.new([], interpreter, meta)
            ))
        return _wrapper

    def _call_method_if_exists(
        self, name: str, args: list[Value], interpreter: "ASTInterpreter",
        meta: Meta | None
    ) -> ExpressionResult:
        match res := self.get_attr(name, interpreter, meta):
            case BLFunction():
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
        return BLError(cast(
            Instance, VarNotFoundException.new([], self.interpreter, meta)
        ))

    def copy(self) -> 'Env':
        """Copy the environment (for capturing variables in closures)"""
        return Env(self.interpreter, self.vars.copy(), self.parent)
