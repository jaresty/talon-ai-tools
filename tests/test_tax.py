def test_calculate_tax():
    from lib.tax import calculate_tax
    assert calculate_tax(100, 0.1) == 10.0
