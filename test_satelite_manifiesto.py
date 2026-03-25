import satelite_manifiesto


def test_module_docstring():
    assert satelite_manifiesto.__doc__ is not None
    assert len(satelite_manifiesto.__doc__) > 0
