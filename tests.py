import main
import intr_classes

def test_expression():
  assert main.interpret('1 + 1').eq(intr_classes.Int(2))
