from va import VA, Variable


def example_1():
    x = Variable('x')
    transitions = [
        (0, 'b', 0), (0, 'a', 1), (0, x.marker_open(), 3),
        (1, '*', 1), (1, 'b', 2),
        (2, x.marker_open(), 3),
        (3, 'a', 3), (3, x.marker_close(), 4),
        (4, 'b', 5),
        (5, '*', 5)
    ]
    final = [4, 5]
    return VA(6, transitions, final)


def example_2():
    x = Variable('x')
    transitions = [
        (0, ' ', 1), (0, '*', 0), (0, x.marker_open(), 2),
        (1, x.marker_open(), 2),
        (2, '@', 3), (2, 'a', 2), (2, 'b', 2),
        (3, x.marker_close(), 4), (3, 'a', 3), (3, 'b', 3),
        (4, ' ', 5),
        (5, '*', 5)]
    final = [4, 5]
    return VA(6, transitions, final)
