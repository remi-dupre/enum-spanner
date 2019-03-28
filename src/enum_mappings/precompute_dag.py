import numpy

import benchmark
from collections import deque
from dag import DAG
from mapping import Variable
from va import VA


@benchmark.track
def product_dag(va: VA, text: str) -> DAG:
    dag = DAG()
    dag.add_vertex('vf')
    dag.add_vertex(('q0', 0))
    dag.initial = 'q0', 0
    dag.final = 'vf'

    for s in range(va.nb_states):
        for i in range(len(text) + 1):
            state_id = f'q{s}', i

            if state_id not in dag.vertices:
                dag.add_vertex(state_id)

    for s, a, t in va.transitions:
        for t_i, t_a in enumerate(text):
            id_s = f'q{s}', t_i

            if isinstance(a, Variable.Marker):
                id_t = f'q{t}', t_i
                label = a, t_i
                dag.adj[id_s].append((label, id_t))
            elif a.match(t_a):
                id_t = f'q{t}', t_i + 1
                label = None, t_i
                dag.adj[id_s].append((label, id_t))

        # Add transitions for the last level
        if isinstance(a, Variable.Marker):
            id_s = f'q{s}', len(text)
            id_t = f'q{t}', len(text)
            label = a, len(text)
            dag.adj[id_s].append((label, id_t))

    for s in va.final:
        id_s = f'q{s}', len(text)
        dag.adj[id_s].append(((None, len(text)), 'vf'))

    return dag


class LevelSet:
    '''
    Represent the partitioning into levels of the DAG.
    '''
    def __init__(self, dag: DAG):
        self.dag = dag
        self.levels = None        # index vertex -> level
        self.vertices = None      # index level -> vertex
        self.vertex_index = None  # index of a vertex in its level

        self.__init_levels__()

    def __init_levels__(self):
        # Init index
        self.levels = {}
        self.levels[self.dag.initial] = 0
        queue = deque([self.dag.initial])
        max_level = 0

        while queue:
            source = queue.popleft()
            max_level = max(max_level, self.levels[source])

            for label, target in self.dag.adj[source]:
                if target not in self.levels:
                    queue.append(target)

                self.levels[target] = (
                    self.levels[source] + int(label[0] is None))

        # Init reversed index
        self.vertices = [[] for _ in range(max_level + 1)]
        self.vertex_index = dict()

        for vertex, level in self.levels.items():
            self.vertex_index[vertex] = len(self.vertices[level])
            self.vertices[level].append(vertex)

    @property
    def max_level(self):
        return len(self.vertices) - 1

@benchmark.track
class Jump:
    '''
    Function that allows jumping from a set of vertices to the closest set of
    vertices where assignation will actually append.

    Notice that the constructor of this function is pretty heavy.
    '''
    def __init__(self, dag: DAG):
        self.dag = dag
        self.levelset = LevelSet(dag)
        self.jl = None      # level of the closest relevant node any node
        self.rlevel = None  # set of levels reachable by jl from a level
        self.reach = None   # for each pair of levels i < j, the vertices each
                            # vertex of i should jump to in j
        self.__init_jl__()
        self.__init_rlevel__()
        self.__init_reach__()

    def __init_jl__(self):
        self.jl = {self.dag.final: self.levelset.max_level}
        queue = [self.dag.final]

        while queue:
            vertex = queue.pop(0)

            for label, target in self.dag.coadj[vertex]:
                if not target in self.jl:
                    queue.append(target)
                    self.jl[target] = self.levelset.max_level

                if label[0] is None:
                    self.jl[target] = min(self.jl[target], self.jl[vertex])
                else:
                    self.jl[target] = self.levelset.levels[target]

    def __init_rlevel__(self):
        # TODO: try the linear time version: track in an array of booleans if a
        # level is already added:
        #  - apply this levelset by levelset
        #  - in a first pass, add a vertex's Jump level if it is not already
        #    marked to true (linear in the size of the levelset)
        #  - clean cells of the array marked to true (also linear)
        self.rlevel = [set() for _ in range(self.levelset.max_level + 1)]

        for vertex in self.dag.vertices:
            self.rlevel[self.levelset.levels[vertex]].add(self.jl[vertex])

    def __init_reach__(self):
        self.reach = dict()

        for i in range(self.levelset.max_level):
            shape = (len(self.levelset.vertices[i]),
                     len(self.levelset.vertices[i+1]))
            self.reach[i, i+1] = numpy.zeros(shape, dtype=bool)

            for k, vertex_k in enumerate(self.levelset.vertices[i]):
                for l, vertex_l in enumerate(self.levelset.vertices[i+1]):
                    self.reach[i, i+1][k, l] = vertex_l in (
                        x for label, x in self.dag.adj[vertex_k]
                        if label[0] is None)

        for i in range(self.levelset.max_level, -1, -1):
            for j in self.rlevel[i]:
                if j > i + 1:
                    self.reach[i, j] = numpy.dot(self.reach[i, i+1],
                                                 self.reach[i+1, j])

    def __call__(self, gamma: list):
        i = self.levelset.levels[gamma[0]]
        j = min(self.jl[vertex] for vertex in gamma)

        if i == j:
            return gamma

        gamma2 = []

        for l, target in enumerate(self.levelset.vertices[j]):
            for source in gamma:
                k = self.levelset.vertex_index[source]

                if self.reach[i, j][k, l]:
                    gamma2.append(target)
                    break

        return gamma2
