from mapping import Variable
from va import VA


def example_1():
    '''Enumerate all maximal blocks of a'''
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
    '''Match all email address other alphabet {a,b} delimited with spaces'''
    x = Variable('x')
    transitions = [
        (0, ' ', 0), (0, '*', 1), (0, x.marker_open(), 2),
        (1, ' ', 0), (1, '*', 1),
        (2, '@', 3), (2, 'a', 2), (2, 'b', 2),
        (3, x.marker_close(), 4), (3, 'a', 3), (3, 'b', 3),
        (4, ' ', 5),
        (5, '*', 5)]
    final = [4, 5]
    return VA(6, transitions, final)

def example_3():
    '''Enumerate all subword'''
    x = Variable('x')
    transitions = [
        (0, '*', 0), (0, x.marker_open(), 1),
        (1, '*', 1), (1, x.marker_close(), 2),
        (2, '*', 2)
    ]
    final = [2]
    return VA(3, transitions, final)

def example_4():
    '''Enumerate all pairs of a block of b's followed by blocks of a's'''
    x = Variable('x')
    y = Variable('y')
    transitions = [
        (0, 'b', 0), (0, 'a', 1), (0, x.marker_open(), 3),
        (1, '*', 1), (1, 'b', 2),
        (2, x.marker_open(), 3),
        (3, 'a', 3), (3, x.marker_close(), 4),
        (4, 'b', 5), (4, y.marker_open(), 7),
        (5, '*', 5), (5, 'a', 6),
        (6, y.marker_open(), 7),
        (7, 'b', 7), (7, y.marker_close(), 8),
        (8, 'a', 9),
        (9, '*', 9)
    ]
    final = [8, 9]
    return VA(10, transitions, final)


INSTANCES = [
    {
        'name': 'automata 1',
        'automata': example_1(),
        'documents': ['', 'aaaaaaaaaaaaa', 'bbbbb', 'aaaabbaaababbbb']
    }, {
        'name': 'automata 2',
        'automata': example_2(),
        'documents': ['a bba a@b b@a aaa@bab abbababaa@@@babbabb']
    }, {
        'name': 'automata 3',
        'automata': example_3(),
        'documents': ['abcdefghijklmnopqrstuvwxyz']
    }, {
        'name': 'automata 4',
        'automata': example_4(),
        'documents': ['ab', 'aaaabbbb', 'bbbaaababaaaaaabbbbabbbababbababbabb']
    },
]
