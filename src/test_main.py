"""Unit tests"""

from pytest import fixture

from main import interpret, interpret_expr
from interpreter import ASTInterpreter, types
from interpreter.types import errors
from interpreter.types.base import ExpressionResult


@fixture
def example_interp() -> ASTInterpreter:
    """Example interpreter"""
    return ASTInterpreter()


# pylint: disable=redefined-outer-name


def test_expression(example_interp: ASTInterpreter):
    """Test for expression parsing"""
    res = interpret_expr("1 + 1", example_interp)
    assert isinstance(res, ExpressionResult)
    assert res.is_equal(types.Int(2), meta=None)


def test_error(example_interp: ASTInterpreter):
    """Test for errors"""
    res = interpret_expr("1 / 0", example_interp)
    assert isinstance(res, errors.BLError)
    assert res.value == errors.error_div_by_zero.value


def test_variable(example_interp: ASTInterpreter):
    """Test for variable handling"""
    interpret("a = 3;", example_interp)
    assert example_interp.globals.get_var("a", meta=None).is_equal(
        types.Int(3), meta=None
    )


def test_if(example_interp: ASTInterpreter):
    """Test for conditional block"""
    interpret(
        """
        age = 18;
        if age < 0 {
            res = 'error';
        } else if age >= 18 {
            res = 'adult';
        } else if age < 18 {
            res = 'child';
        } else {
            res = 'error';
        }
    """,
        example_interp,
    )
    assert example_interp.globals.get_var("res", meta=None).is_equal(
        types.String("adult"), meta=None
    )


def test_loops(example_interp: ASTInterpreter):
    """Loop test"""
    interpret(
        """
        res = 0;
        for (i = 1; i < 10; i += 1) {
            res += i;
        }
    """,
        example_interp,
    )
    assert example_interp.globals.get_var("res", meta=None).is_equal(
        types.Int(45), meta=None
    )


def test_function(example_interp: ASTInterpreter):
    """Function test"""
    interpret(
        """
        fun fact(n) {
            if n <= 0 {
                return 1;
            } else {
                return n * fact(n - 1);
            }
        }
        res = fact(10);
    """,
        example_interp,
    )
    assert example_interp.globals.get_var("res", meta=None).is_equal(
        types.Int(3628800), meta=None
    )


def test_closure(example_interp: ASTInterpreter):
    """Test for closure support"""
    interpret(
        """
        fun counter() {
            i = 0;
            return fun() {
                i += 1;
                return i;
            };
        }
        my_counter = counter();
        my_counter();
        my_counter();
        res = my_counter();
    """,
        example_interp,
    )
    assert example_interp.globals.get_var("res", meta=None).is_equal(
        types.Int(3), meta=None
    )
