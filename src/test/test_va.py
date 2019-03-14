from va import Variable


def test_variables():
    var1 = Variable('x')
    var2 = Variable('y')

    assert var1 == var1
    assert var2 == var2


def test_markers():
    var1 = Variable('x')
    var2 = Variable('y')

    assert var1.marker_open() == var1.marker_open()
    assert var1.marker_open() != var1.marker_close()
    assert var1.marker_open() != var2.marker_close()
