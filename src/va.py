import re
from collections import deque
from functools import lru_cache
from graphviz import Digraph

from atoms import Atom
from mapping import Variable


class VA:

    def __init__(self, nb_states=0, transitions=None, final=None):
        # States are identified by integers starting from 0
        self.initial = 0
        self.nb_states = nb_states

        # There is only one initial state 0, by default the only final state is
        # the last one
        self.final = final if final is not None else [nb_states-1]

        # The set of transitions as tuples of the form (source, label, target)
        # Label can either be a letter from the alphabet either a variable
        # marker
        self.transitions = transitions if transitions is not None else []

    def cache_clear(self):
        self.get_adj.cache_clear()
        self.get_coadj.cache_clear()
        self.get_variables.cache_clear()
        self.get_adj_for_char.cache_clear()
        self.get_adj_for_assignations.cache_clear()

    @property
    def adj(self):
        return self.get_adj()

    @lru_cache(1)
    def get_adj(self):
        '''
        Get the adjacency list of the automata, this property is cached for
        performance reasons.
        '''
        ret = [[] for _ in range(self.nb_states)]

        for source, label, target in self.transitions:
            ret[source].append((label, target))

        return ret

    @property
    def coadj(self):
        return self.get_coadj()

    @lru_cache(1)
    def get_coadj(self):
        '''
        Get the adjacency list of the automata, this property is cached for
        performance reasons.
        '''
        ret = [[] for _ in range(self.nb_states)]

        for source, label, target in self.transitions:
            ret[target].append((label, source))

        return ret

    @property
    def variables(self):
        return self.get_variables()

    @lru_cache(1)
    def get_variables(self):
        '''
        Get the list of variables used in the automata
        '''
        ret = set()

        for _, label, _ in self.transitions:
            if isinstance(label, Variable.Marker):
                ret.add(label.variable)

        return list(ret)

    @lru_cache(None)
    def get_adj_for_char(self, char):
        '''
        Get the adjacency list representing transitions of the automaton that
        can be used when reading a given char.
        '''
        res = [[] for _ in range(self.nb_states)]

        for source, label, target in self.transitions:
            if isinstance(label, Atom) and label.match(char):
                res[source].append(target)

        return res

    @lru_cache(1)
    def get_adj_for_assignations(self):
        '''
        Get the adjacency matrix of transitions that can be followed by only
        reading transitions holding an assignation label.
        '''
        return [list(set(target for _, target in neighbours))
                for neighbours in self.get_assignations()]

    @lru_cache(1)
    def get_assignations(self):
        '''
        Get the adjacency matrix of transitions that can be followed by only
        reading transitions holding an assignation label, keeping the
        information of the label hold by every edge.
        '''
        # Compute adjacency list
        adj = [[] for _ in range(self.nb_states)]

        for source, label, target in self.transitions:
            if isinstance(label, Variable.Marker):
                adj[source].append((label, target))

        # Compute closure
        ret = [[] for _ in range(self.nb_states)]

        for state in range(self.nb_states):
            seen = {state}
            heap = [state]

            while heap:
                source = heap.pop()

                for (label, target) in adj[source]:
                    ret[state].append((label, target))

                    if target not in seen:
                        heap.append(target)
                        seen.add(target)

        return ret

    @lru_cache(1)
    def get_rev_assignations(self):
        '''
        Get the reverse of adjacency matrix obtained with `get_assignations`.
        '''
        adj = [[] for _ in range(self.nb_states)]

        for source in range(self.nb_states):
            for label, target in self.get_assignations()[source]:
                adj[target].append((label, source))

        return adj

    def is_valid(self):
        for state in self.final:
            assert state in range(self.nb_states)

        for s, _, t in self.transitions:
            assert s in range(self.nb_states)
            assert t in range(self.nb_states)

    def reorder_states(self):
        '''
        Reorder states in a topological order.
        '''
        perm = [None for _ in range(self.nb_states)]
        curr_index = perm[0] = 0
        queue = deque([0])

        while queue:
            source = queue.popleft()

            for _, target in self.adj[source]:
                if perm[target] is None:
                    curr_index += 1
                    perm[target] = curr_index
                    queue.append(target)

        self.final = [perm[s] for s in self.final]
        self.transitions = [(perm[source], label, perm[target])
                            for source, label, target in self.transitions]

        self.cache_clear()

    def render(self, name, display=False):
        dot = Digraph(name)

        dot.attr('node', shape='point')
        dot.node(f'before_q{self.initial}')

        dot.attr('node', shape='doublecircle')
        for final in self.final:
            dot.node(f'q{final}')

        dot.attr('node', shape='circle')
        dot.edge(f'before_q{self.initial}', f'q{self.initial}')

        for source, label, target in self.transitions:
            label_repr = repr(str(label))[1:-1]
            dot.edge(f'q{source}', f'q{target}', re.escape(f' {label_repr} '))

        dot.render(f'figures/{name}', view=display)
