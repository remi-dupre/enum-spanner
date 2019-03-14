from enum import Enum
from functools import lru_cache


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
        performance purpose, beware of not changing the structure of the
        automata after calling it.
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
