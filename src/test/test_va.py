from mapping import Variable


def test_variables():
    var1 = Variable('x')
    var2 = Variable('y')

    assert var1 == var1
    assert var1 != var2


def test_markers_eq():
    var1 = Variable('x')
    var2 = Variable('y')

    assert var1.marker_open() == var1.marker_open()
    assert var1.marker_open() != var1.marker_close()
    assert var1.marker_open() != var2.marker_close()

def test_makers_order():
    var1 = Variable('x')
    var2 = Variable('y')

    assert var1.marker_open() < var1.marker_close()
    assert var2.marker_open() < var1.marker_close()
    assert var1.marker_open() < var2.marker_close()
