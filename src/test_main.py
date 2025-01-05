"""Unit tests"""

from pytest import fixture

from main import interpret, interpret_expr
from interpreter import ASTInterpreter, bl_types
from interpreter.bl_types import ExpressionResult


@fixture
def example_interp() -> ASTInterpreter:
    """Example interpreter"""
    return ASTInterpreter()


# pylint: disable=redefined-outer-name


def test_expression(example_interp: ASTInterpreter):
    """Test for expression parsing"""
    res = interpret_expr("2 + 3", example_interp)
    assert isinstance(res, ExpressionResult)
    assert res.is_equal(bl_types.Int(5), example_interp, meta=None)


def test_all_operators_int(example_interp: ASTInterpreter):
    """Test all integer operators"""
    def is_equal(a, b):
        return a.is_equal(b, example_interp, meta=None)
    assert is_equal(interpret_expr("2 + 3", example_interp), bl_types.Int(5))
    assert is_equal(interpret_expr("2 - 3", example_interp), bl_types.Int(-1))
    assert is_equal(interpret_expr("2 * 3", example_interp), bl_types.Int(6))
    assert is_equal(
        interpret_expr("2 / 3", example_interp), bl_types.Float(2 / 3)
    )
    assert is_equal(
        interpret_expr("2 == 3", example_interp), bl_types.Bool(False)
    )
    assert is_equal(
        interpret_expr("2 != 3", example_interp), bl_types.Bool(True)
    )
    assert is_equal(
        interpret_expr("2 < 3", example_interp), bl_types.Bool(True)
    )
    assert is_equal(
        interpret_expr("2 <= 3", example_interp), bl_types.Bool(True)
    )
    assert is_equal(
        interpret_expr("2 > 3", example_interp), bl_types.Bool(False)
    )
    assert is_equal(
        interpret_expr("2 >= 3", example_interp), bl_types.Bool(False)
    )
    assert is_equal(interpret_expr("2 && 3", example_interp), bl_types.Int(3))
    assert is_equal(interpret_expr("2 || 3", example_interp), bl_types.Int(2))


def test_error(example_interp: ASTInterpreter):
    """Test for errors"""
    res = interpret_expr("1 / 0", example_interp)
    assert isinstance(res, bl_types.BLError)
    assert res.value.class_ == bl_types.numbers.DivByZeroException


def test_variable(example_interp: ASTInterpreter):
    """Test for variable handling"""
    interpret("a = 3;", example_interp)
    assert example_interp.globals.get_var("a", meta=None).is_equal(
        bl_types.Int(3), example_interp, meta=None
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
        bl_types.String("adult"), example_interp, meta=None
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
        bl_types.Int(45), example_interp, meta=None
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
        bl_types.Int(3628800), example_interp, meta=None
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
        bl_types.Int(3), example_interp, meta=None
    )


def test_object(example_interp: ASTInterpreter):
    """Test for object support"""
    interpret(
        """
        class Vector3D {
            fun __init__(x, y, z) {
                this.x = x;
                this.y = y;
                this.z = z;
            }
        }

        res = new Vector3D(1., 2., 3.);
        """,
        example_interp,
    )
    cls = example_interp.globals.get_var("Vector3D", meta=None)
    res = example_interp.globals.get_var("res", meta=None)

    assert isinstance(cls, bl_types.Class)
    assert isinstance(res, bl_types.Instance)
    assert res.class_ == cls
    assert (
        res.get_attr("x", example_interp, None)
        .is_equal(bl_types.Float(1.), example_interp, meta=None)
    )


def test_op_overloading(example_interp: ASTInterpreter):
    """Test for operator overloading"""
    interpret(
        """
        class Vector3D {
            fun __init__(x, y, z) {
                this.x = x;
                this.y = y;
                this.z = z;
            }

            fun __add__(other) {
                return new Vector3D(
                    this.x + other.x, this.y + other.y, this.z + other.z
                );
            }

            fun __neg__() {
                return new Vector3D(-this.x, -this.y, -this.z);
            }

            fun __sub__(other) {
                return this + (-other);
            }

            fun scale(k) {
                return new Vector3D(k * this.x, k * this.y, k * this.z);
            }

            fun norm() {
                return (this.x**2 + this.y**2 + this.z**2) ** .5;
            }

            fun __eq__(other) {
                return this.x == other.x
                    && this.y == other.y
                    && this.z == other.z;
            }
        }

        v1 = new Vector3D(1., 2., 3.);
        v2 = new Vector3D(4., 5., 6.);

        truth_1 = v1 + v2 == new Vector3D(5., 7., 9.);
        truth_2 = v1 - v2 == new Vector3D(-3., -3., -3.);
        truth_3 = v1.scale(2) == new Vector3D(2., 4., 6.);
        truth_4 = -v1 == v1.scale(-1);
        truth_5 = v1.norm() == 14. ** .5;

        res = truth_1 && truth_2 && truth_3 && truth_4 && truth_5;
        """,
        example_interp,
    )
    example_interp.globals.get_var("res", meta=None).is_equal(
        bl_types.Bool(True), example_interp, meta=None
    )
