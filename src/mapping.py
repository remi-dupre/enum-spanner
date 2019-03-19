import random
from colorama import Fore, Style
from enum import Enum


class Variable:

    def __init__(self, name):
        self.name = name
        self.id = random.getrandbits(128)

    def marker_open(self):
        return Variable.Marker(self, Variable.Marker.Type.OPEN)

    def marker_close(self):
        return Variable.Marker(self, Variable.Marker.Type.CLOSE)

    def __eq__(self, other):
        return isinstance(other, Variable) and self.id == other.id

    def __hash__(self):
        return self.id

    def __str__(self):
        return str(self.name)

    class Marker:

        def __init__(self, variable, m_type):
            self.variable = variable
            self.type = m_type

        def __eq__(self, other):
            return self.variable == other.variable and self.type == other.type

        def __lt__(self, other):
            if (self.type == Variable.Marker.Type.OPEN and
                    other.type == Variable.Marker.Type.CLOSE):
                return True

            return str(self.variable) < str(other.variable)

        def __hash__(self):
            ret = hash(self.variable)

            if self.type == Variable.Marker.Type.OPEN:
                ret += 1

            return ret

        def __repr__(self):
            if self.type is Variable.Marker.Type.OPEN:
                return '⊢' + str(self.variable)
            if self.type is Variable.Marker.Type.CLOSE:
                return str(self.variable) + '⊣'

            return 'wrong_marker'

        class Type(Enum):
            OPEN = 1
            CLOSE = 2


def is_valid_mapping(variables, mapping):
    '''
    Ensures that the given mapping assign each variable to a unique [i, i'>
    such that i ≤ i'.
    '''
    # Dictionnaries containing index for left and right bounds
    bounds = {Variable.Marker.Type.OPEN: dict(),
              Variable.Marker.Type.CLOSE: dict()}

    for x, i in mapping:
        # False if there is already a marker of this kind
        if x.variable in bounds[x.type]:
            return False

        bounds[x.type][x.variable] = i

    for v in variables:
        if (v not in bounds[Variable.Marker.Type.OPEN] or
                v not in bounds[Variable.Marker.Type.CLOSE] or
                bounds[Variable.Marker.Type.OPEN][v] > bounds[Variable.Marker.Type.CLOSE][v]):
            return False

    return True


def print_mapping(document: str, mapping: list):
    symbols = {i : [] for i in range(len(document) + 1)}

    for marker, i in mapping:
        symbols[i].append(marker)
        symbols[i].sort()

    for i in range(len(document) + 1):
        for marker in symbols[i]:
            if marker.type == Variable.Marker.Type.OPEN:
                print(f'{Style.DIM}|{marker}|{Style.BRIGHT}{Fore.RED}', end='')
            else:
                print(f'{Style.RESET_ALL}{Style.DIM}{Fore.WHITE}|{marker}|{Style.RESET_ALL}', end='')

        if i < len(document):
            print(document[i], end='')

    print('')
