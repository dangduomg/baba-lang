def test_expression():
    assert interpret("1 + 1").eq(intr_classes.Int(2))
