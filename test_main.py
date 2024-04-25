from pytest import fixture

import main
import intr_classes
from state import State

@fixture
def example_state():
    return State()

def test_expression():
    assert main.interpret_expr("1 + 1", example_state).eq(intr_classes.Int(2))

def test_variable():
    main.interpret("a = 3;", example_state)
    assert example_state.get_var('a').eq(intr_classes.Int(3))
