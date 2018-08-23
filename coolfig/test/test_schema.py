from coolfig.schema import ComputedValue, computed_value


def test_computed_value_func():
    func = lambda: None  # NOQA, NOCOV
    val = computed_value(func)
    assert isinstance(val, ComputedValue)
    assert val.callable is func
