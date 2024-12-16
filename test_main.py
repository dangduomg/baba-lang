"""Unit tests"""


from pytest import fixture

from src.main import interpret, interpret_expr
from src.interpreter import base, values, ASTInterpreter
from src.interpreter.base import ExpressionResult

@fixture
def example_interp() -> ASTInterpreter:
    """Example interpreter"""
    return ASTInterpreter()


#pylint: disable=redefined-outer-name


def test_expression(example_interp: ASTInterpreter):
    """Test for expression parsing"""
    res = interpret_expr("1 + 1", example_interp)
    assert isinstance(res, ExpressionResult)
    assert res.is_equal(values.Int(2), meta=None)


def test_error(example_interp: ASTInterpreter):
    """Test for errors"""
    res = interpret_expr("1 / 0", example_interp)
    assert isinstance(res, base.BLError)
    assert res.value == base.error_div_by_zero.value


def test_variable(example_interp: ASTInterpreter):
    """Test for variable handling"""
    interpret("a = 3;", example_interp)
    assert example_interp.globals.get_var('a', meta=None).is_equal(values.Int(3), meta=None)


# def test_if(example_interp: ASTInterpreter):
#     main.interpret("""
#         age = 18;
#         if (age < 0) {
#             res = 'error';
#         } else if (age >= 18) {
#             res = 'adult';
#         } else if (age < 18) {
#             res = 'child';
#         } else {
#             res = 'error';
#         }
#     """, example_interp)
#     assert example_interp.globals.get_var('res', meta=None) \
#                                  .is_equal(values.String('adult'), meta=None);


# def test_loops(example_interp: ASTInterpreter):
#     main.interpret("""
#         res = [];
#         for (i = 0; i < 5; i += 2) {
#             list_push(res, i);
#         }
#     """, example_interp)
#     target_list = values.BLList([values.Int(0), values.Int(2), values.Int(4)])
#     assert example_interp.globals.get_var('res', meta=None).is_equal(target_list, meta=None)


# def test_function(example_interp: ASTInterpreter):
#     main.interpret("""
#         function fact(n) {
#             if (n <= 0) {
#                 return 1;
#             } else {
#                 return n * fact(n - 1);
#             }
#         }
#         res = fact(10);
#     """, example_interp)
#     assert example_interp.globals.get_var('res', meta=None) \
#                                  .is_equal(values.Int(3628800), meta=None)
