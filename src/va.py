import re
from functools import lru_cache
from graphviz import Digraph

from mapping import Variable


class VA:

    def __init__(self, nb_states=0, transitions=None, final=None):
        # States are identified by integer starting from 0
        self.initial = 0
        self.nb_states = nb_states

        # There is only one initial state 0, by default the only final state is
        # the last one
        self.final = final if final is not None else [nb_states-1]

        # The set of transitions as tuples of the form (source, label, target)
        # Label can either be a letter from the alphabet either a variable
        # marker
        self.transitions = transitions if transitions is not None else []

    @property
    @lru_cache(1)
    def adj(self):
        '''
        Get the adjacency list of the automata, this property is cached for
        performance purpose.

        Beware of not changing the structure of the automata after calling it.
        '''
        ret = [[] for _ in range(self.nb_states)]

        for source, label, target in self.transitions:
            ret[source].append((label, target))

        return ret

    @property
    def variables(self):
        '''
        Get the list of variables used in the automata
        '''
        ret = set()

        for _, label, _ in self.transitions:
            if isinstance(label, Variable.Marker):
                ret.add(label.variable)

        return list(ret)

    def is_valid(self):
        for state in self.final:
            assert state in range(self.nb_states)

        for s, _, t in self.transitions:
            assert s in range(self.nb_states)
            assert t in range(self.nb_states)

    def render(self, name):
        dot = Digraph(name)

        dot.attr('node', shape='point')
        dot.node(f'before_q{self.initial}')

        dot.attr('node', shape='doublecircle')
        for final in self.final:
            dot.node(f'q{final}')

        dot.attr('node', shape='circle')
        dot.edge(f'before_q{self.initial}', f'q{self.initial}')

        for source, label, target in self.transitions:
            dot.edge(f'q{source}', f'q{target}', re.escape(f' {label} '))

        dot.render()
