"""Unit tests"""

from typing import cast
from pytest import fixture

from main import interpret
from interpreter import ASTInterpreter
from interpreter.bl_types import essentials, numbers, colls
from interpreter.bl_types.essentials import Value, Bool
from interpreter.bl_types.numbers import Int


@fixture
def example_interp() -> ASTInterpreter:
    """Example interpreter"""
    return ASTInterpreter()


# pylint: disable=redefined-outer-name


def test_expression(example_interp: ASTInterpreter):
    """Test for expression parsing"""
    res = interpret("2 + 3", example_interp)
    assert isinstance(res, Int)
    assert cast(Bool, res.is_equal(
        Int(5), example_interp, meta=None
    )).value


def test_all_operators_int(example_interp: ASTInterpreter):
    """Test all integer operators"""
    def is_equal(a, b):
        return cast(Bool, cast(Value, a).is_equal(
            cast(Value, b), example_interp, meta=None
        )).value
    assert is_equal(interpret("2 + 3", example_interp), Int(5))
    assert is_equal(interpret("2 - 3", example_interp), Int(-1))
    assert is_equal(interpret("2 * 3", example_interp), Int(6))
    assert is_equal(
        interpret("2 / 3", example_interp), numbers.Float(2 / 3)
    )
    assert is_equal(interpret("2 %/% 3", example_interp), Int(0))
    assert is_equal(interpret("2 % 3", example_interp), Int(2))
    assert is_equal(interpret("2 ** 3", example_interp), Int(8))
    assert is_equal(interpret("2 & 3", example_interp), Int(2))
    assert is_equal(interpret("2 | 3", example_interp), Int(3))
    assert is_equal(interpret("2 ^ 3", example_interp), Int(1))
    assert is_equal(
        interpret("2 == 3", example_interp), essentials.FALSE
    )
    assert is_equal(
        interpret("2 != 3", example_interp), essentials.TRUE
    )
    assert is_equal(
        interpret("2 < 3", example_interp), essentials.TRUE
    )
    assert is_equal(
        interpret("2 <= 3", example_interp), essentials.TRUE
    )
    assert is_equal(
        interpret("2 > 3", example_interp), essentials.FALSE
    )
    assert is_equal(
        interpret("2 >= 3", example_interp), essentials.FALSE
    )
    assert is_equal(interpret("2 && 3", example_interp), Int(3))
    assert is_equal(interpret("2 || 3", example_interp), Int(2))
    assert is_equal(
        interpret("!2", example_interp), essentials.FALSE
    )
    assert is_equal(interpret("+2", example_interp), Int(2))
    assert is_equal(interpret("-2", example_interp), Int(-2))
    assert is_equal(interpret("~2", example_interp), Int(-3))


def test_error(example_interp: ASTInterpreter):
    """Test for errors"""
    res = interpret("1 / 0", example_interp)
    assert isinstance(res, essentials.BLError)
    assert res.value.class_ == numbers.DivByZeroException


def test_variable(example_interp: ASTInterpreter):
    """Test for variable handling"""
    interpret("a = 3;", example_interp)
    a = example_interp.globals.get_var("a", meta=None)
    assert isinstance(a, Int)
    assert cast(Bool, a.is_equal(
        Int(3), example_interp, meta=None
    )).value


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
    res = example_interp.globals.get_var("res", meta=None)
    assert isinstance(res, essentials.String)
    assert cast(Bool, res.is_equal(
        essentials.String("adult"), example_interp, meta=None
    )).value


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
    res = example_interp.globals.get_var("res", meta=None)
    assert isinstance(res, Int)
    assert cast(Bool, res.is_equal(
        Int(45), example_interp, meta=None
    )).value


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
    res = example_interp.globals.get_var("res", meta=None)
    assert isinstance(res, Int)
    assert cast(Bool, res.is_equal(
        Int(3628800), example_interp, meta=None
    )).value


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
    res = example_interp.globals.get_var("res", meta=None)
    assert isinstance(res, Int)
    assert cast(Bool, res.is_equal(
        Int(3), example_interp, meta=None
    )).value


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

    assert isinstance(cls, essentials.Class)
    assert isinstance(res, essentials.Instance)
    assert res.class_ == cls
    x = res.get_attr("x", example_interp, meta=None)
    assert isinstance(x, numbers.Float)
    assert cast(Bool, x.is_equal(
        numbers.Float(1.), example_interp, meta=None
    )).value


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
    res = example_interp.globals.get_var("res", meta=None)
    assert isinstance(res, Bool)
    assert cast(Bool, res.is_equal(
        essentials.TRUE, example_interp, meta=None
    )).value


def test_foreach(example_interp: ASTInterpreter):
    """Test for iterator for"""
    interpret(
        """
        fun filter(f, lst) {
            acc = [];
            for x in lst {
                if f(x) {
                    acc.push(x);
                }
            }
            return acc;
        }

        res = filter(fun(x) -> x % 2 == 0, [1, 2, 3, 4, 5, 6, 7, 8]);
        """,
        example_interp,
    )
    res = example_interp.globals.get_var("res", meta=None)
    assert isinstance(res, colls.BLList)
    assert cast(Bool, res.is_equal(
        colls.BLList([Int(2), Int(4), Int(6), Int(8)]),
        example_interp, meta=None
    )).value


def test_custom_iter(example_interp: ASTInterpreter):
    """Test for custom iterators"""
    interpret(
        """
        class Range {
            fun __init__(start, stop, step) {
                this.i = start;
                this.stop = stop;
                this.step = step;
            }

            fun iter() {
                return this;
            }

            fun next() {
                if (this.i >= this.stop) {
                    return null;
                }
                i = this.i;
                this.i += this.step;
                return new Item(i);
            }
        }

        fun collect(iter) {
            res = [];
            for x in iter {
                res.push(x);
            }
            return res;
        }

        lst1 = collect(new Range(0, 10, 1));
        truth_1 = lst1 == [0, 1, 2, 3, 4, 5, 6, 7, 8, 9];

        it1 = new Range(1, 6, 3);
        truth_2 = it1.next().value == 1 && it1.next().value == 4;

        res = truth_1 && truth_2;
        """,
        example_interp,
    )

    res = example_interp.globals.get_var("res", meta=None)
    assert isinstance(res, Bool)
    assert res.is_equal(essentials.TRUE, example_interp, meta=None)
