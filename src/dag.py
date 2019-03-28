from collections import deque
from functools import lru_cache
from graphviz import Digraph

import benchmark


class EmptyLangage(Exception):
    pass


class DAG:

    def __init__(self):
        # List of vertices in the DAG, all identified by a unique id
        self.vertices = set()

        # Initial and final vertices are defined as extrema by default
        self.initial = None
        self.final = None

        # Adjacency list of the DAG as a list of (label, target) or epsilon
        # transition (None, target) for each source vertex
        self.adj = dict()

    def add_vertex(self, node_id):
        assert node_id not in self.vertices
        self.vertices.add(node_id)
        self.adj[node_id] = list()

    @property
    @lru_cache(1)
    def coadj(self):
        '''
        Get the adjacency list of the co-DAG, this property is cached for
        performance reasons.

        Beware of not changing the structure of the DAG after calling it.
        '''
        coadj = {v : [] for v in self.vertices}

        for source, label, target in self.edges:
            coadj[target].append((label, source))

        return coadj

    @property
    def edges(self):
        '''Iterable of all edges of the graph, generated on the fly'''
        for source in self.vertices:
            for label, target in self.adj[source]:
                yield source, label, target

    def run_from(self, source):
        '''
        Enumerate accessible states from a given source.
        '''
        accessible = {state: False for state in self.vertices}
        accessible[source] = True
        heap = deque([source])

        while heap:
            s = heap.popleft()
            yield s

            for _, t in self.adj[s]:
                if not accessible[t]:
                    accessible[t] = True
                    heap.append(t)

    def corun_from(self, source: int):
        '''
        Enumerate co-accessible states from a given source.
        '''
        # Build DAG with reversed edges, initial and final states won't matter
        codag = DAG()

        codag.vertices = self.vertices
        codag.adj = self.coadj

        return codag.run_from(source)

    def trim(self, vertices: list):
        '''
        Trim the graph by only keeping states that belong to the input list of
        states. States are arbitrary reindexed.
        '''
        new_vertices = set(vertices)
        self.vertices = vertices.copy()
        new_adj = {v: [] for v in self.vertices}

        for source, label, target in self.edges:
            if target in new_vertices:
                new_adj[source].append((label, target))

        self.adj = new_adj

    @benchmark.track
    def remove_useless_nodes(self):
        '''
        Remove nodes that are not accessible or not co-accessible, if the
        initial state is not coaccessible or the final state is not accessible,
        the function fails with no predicate on the resulting DAG.
        '''
        accessible = list(self.run_from(self.initial))

        if self.final not in accessible:
            raise EmptyLangage()

        self.trim(accessible)
        coaccessible = list(self.corun_from(self.final))

        if self.initial not in coaccessible:
            raise EmptyLangage()

        self.trim(coaccessible)

    def render(self, name):
        dot = Digraph(name)
        dot.attr('node', shape='circle')

        def node_id(node):
            if node in ['vf']:
                return str(node)

            return ','.join(map(str, node))

        def label_str(label):
            if label[0] is None:
                return ' ε '

            return f' {label[0] } '

        #  levels = dict()
        #
        #  for node in self.vertices:
        #      if node != 'vf':
        #          if node[1] not in levels:
        #              levels[node[1]] = []
        #          levels[node[1]].append(node_id(node))
        #
        #  for level, nodes in levels.items():
        #      with dot.subgraph(name=f'cluster_{level}') as c:
        #          for node in nodes:
        #              c.node(node)

        for s in self.vertices:
            for label, t in self.adj[s]:
                dot.edge(node_id(s), node_id(t), label_str(label))

        dot.render()

    def __str__(self):
        def label_str(label):
            var, pos = label
            return f'ε({pos})' if var is None else f'{var}({pos})'

        transitions = [(s, label_str(a), t) for s in self.vertices
                       for a, t in self.adj[s]]
        return (f'DAG(vertices={self.vertices}, initial={self.initial}, '
                f'final={self.final}, adj={transitions})')
