from colorama import Fore, Style
from enum import Enum


class Variable:

    def __init__(self, name):
        self.name = name

    def marker_open(self):
        return Variable.Marker(self, Variable.Marker.Type.OPEN)

    def marker_close(self):
        return Variable.Marker(self, Variable.Marker.Type.CLOSE)

    def __str__(self):
        return str(self.name)

    class Marker:

        def __init__(self, variable, m_type):
            self.variable = variable
            self.type = m_type

        def __eq__(self, other):
            return self.variable == other.variable and self.type == other.type

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

    for i in range(len(document) + 1):
        for marker in symbols[i]:
            if marker.type == Variable.Marker.Type.OPEN:
                print(f'{Style.DIM}|{marker}|{Style.BRIGHT}{Fore.RED}', end='')
            else:
                print(f'{Style.RESET_ALL}{Style.DIM}{Fore.WHITE}|{marker}|{Style.RESET_ALL}', end='')

        if i < len(document):
            print(document[i], end='')

    print('')
