from abc import abstractmethod


class Atom:
    '''
    Generic class for an atom, which is a term matching only one character
    '''
    @abstractmethod
    def match(self, char: str) -> bool:
        pass


class Wildcard(Atom):
    '''
    Match any symbol.
    '''
    def match(self, char):
        return True

    def __str__(self):
        return '*'


class Char(Atom):
    '''
    Match a specific symbol.
    '''
    def __init__(self, char: str):
        self.char = char

    def match(self, char):
        return self.char == char

    def __str__(self):
        return self.char


class CharClass:
    '''
    Match unions of intervals of characters.
    '''
    def __init__(self, intervals: list):
        self.intervals = intervals

    def match(self, char):
        return any(ord(l) <= ord(char) <= ord(r) for l, r in self.intervals)

    def __str__(self):
        ret = ''

        for l, r in self.intervals:
            if l != r:
                ret += f'{l}-{r}'
            else:
                ret += str(l)

        return f'[{ret}]'


class CharClassComplement:
    '''
    Match unions of intervals of characters.
    '''
    def __init__(self, intervals: list):
        self.intervals = intervals

    def match(self, char):
        return not any(ord(l) <= ord(char) <= ord(r) for l, r in self.intervals)

    def __str__(self):
        ret = ''

        for l, r in self.intervals:
            if l != r:
                ret += f'{l}-{r}'
            else:
                ret += str(l)

        return f'[^{ret}]'
