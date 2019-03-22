import benchmark
from collections import deque
from termcolor import cprint


class Match:

    def __init__(self, document, span: tuple, groups: dict):
        self.document = document
        self.span = span
        self.group_spans = groups

    @property
    def string(self):
        begin, end = self.span
        return self.document[begin:end]

    @benchmark.track
    def pretty_print(self):
        symbols = {i : deque() for i in range(len(self.document) + 1)}

        for group, (l, r) in self.group_spans.items():
            symbols[l].append(f'[⊢{group}]')
            symbols[r].appendleft(f'[{group}⊣]')


        for i in range(len(self.document) + 1):
            cprint(''.join(symbols[i]), 'red', attrs=['bold', 'dark'], end='')

            if i < len(self.document):
                if self.span[0] <= i < self.span[1]:
                    cprint(self.document[i], 'red', attrs=['bold'], end='')
                else:
                    cprint(self.document[i], end='')

        cprint('')

    def __repr__(self):
        return f'Match(span={self.span}, match=\'{self.string}\')'
