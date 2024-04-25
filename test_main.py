from pytest import fixture

import main
import intr_classes

@fixture
def example_state():
    return main.state.copy()

def test_expression(example_state):
    assert main.interpret_expr("1 + 1", example_state).eq(intr_classes.Int(2))

def test_variable(example_state):
    main.interpret("a = 3;", example_state)
    assert example_state.get_var('a').eq(intr_classes.Int(3))

def test_if(example_state):
    main.interpret("""
        age = 18;
        if (age < 0) {
            res = 'error';
        } else if (age >= 18) {
            res = 'adult';
        } else if (age < 18) {
            res = 'child';
        } else {
            res = 'error';
        }
    """, example_state)
    assert example_state.get_var('res').eq(intr_classes.String('adult'));

def test_loops(example_state):
    main.interpret("""
        res = [];
        for (i = 0; i < 5; i += 2) {
            list_push(res, i);
        }
    """, example_state)
    assert example_state.get_var('res').eq(intr_classes.List_([0, 2, 4]))
