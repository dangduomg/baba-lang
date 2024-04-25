import main
import intr_classes
from state import State

def test_expression():
    assert main.interpret("1 + 1", State()).eq(intr_classes.Int(2))
