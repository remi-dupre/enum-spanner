from functools import partial
from termcolor import cprint

import benchmark
import mapping


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
    def pretty_print(self, only_matching: bool = False):
        symbols = {i : [] for i in range(len(self.document) + 1)}

        for group, (l, r) in self.group_spans.items():
            if l is not None and r is not None:
                var = mapping.Variable(group)
                symbols[l].append(var.marker_open())
                symbols[r].append(var.marker_close())

        def symbol_order(index, symbol):
            # Order for printing symbols: first close all previoulsly opened
            # variables in reversed order, then open all of them (and
            # immediatly close if necessary)
            l, r = self.group_spans[symbol.variable.name]

            if index > l:
                return (-l, r, symbol.variable.id, symbol.type)

            return (l, -r, -symbol.variable.id, symbol.type)

        def symbol_print(symbol):
            return f'[{symbol}]'

        display_range = (range(self.span[0], self.span[1] + 1) if only_matching
                         else range(len(self.document)+1))

        for i in display_range:
            symbols[i].sort(key=partial(symbol_order, i))
            cprint(''.join(map(symbol_print, symbols[i])), 'red',
                   attrs=['bold', 'dark'], end='')

            if i < max(display_range):
                if self.span[0] <= i < self.span[1]:
                    cprint(self.document[i], 'red', attrs=['bold'], end='')
                elif not only_matching:
                    cprint(self.document[i], end='')

        cprint('')

    def __repr__(self):
        return f'Match(span={self.span}, match=\'{self.string}\')'
