from collections import deque
import numpy

import benchmark
from atoms import Atom
from dag import DAG, EmptyLangage
from mapping import Variable
from va import VA


class LevelSet:
    '''
    Represent the partitioning into levels of the DAG.
    '''
    def __init__(self, max_level: int):
        self.max_level = max_level

        # Index vertex -> level
        self.levels = dict()
        # Index level -> vertex
        self.vertices = {level: [] for level in range(self.max_level + 1)}
        # Index of a vertex in its level
        self.vertex_index = dict()

    def register(self, vertex, level: int):
        self.levels[vertex] = level
        self.vertices[level].append(vertex)
        self.vertex_index[vertex] = len(self.vertices[level]) - 1

    def remove_from_level(self, level: int, del_vertices: set):
        new_vertices = []

        for old_vertex in self.vertices[level]:
            if old_vertex not in del_vertices:
                new_vertices.append(old_vertex)
                self.vertex_index[old_vertex] = len(new_vertices) - 1
            else:
                del self.vertex_index[old_vertex]
                del self.levels[old_vertex]

        self.vertices[level] = new_vertices


# ===== 🎜 A WHOLE NEW WOOOOORLD 🎜 =====


class IndexedDag:
    '''
    TODO
    '''
    def __init__(self, va: VA, document: str):
        self.va = va
        self.document = document

        self.dag = DAG()
        self.levelset = LevelSet(len(document) + 1)
        self.jl = dict()
        self.rlevel = {level: set() for level in range(len(document) + 2)}
        self.reach = dict()
        self.ingoing_assignations = set()

        self.__build_dag__()

    def __build_dag__(self):
        # Add initial an final vertices
        self.dag.initial = (self.va.initial, 0)
        self.dag.add_vertex(self.dag.initial)
        self.levelset.register(self.dag.initial, 0)
        self.jl[self.dag.initial] = 0
        self.ingoing_assignations.add(self.dag.initial)

        # Start a level by level run of the DAG
        self.__follow_assignations__(0)
        self.__update_rlevel__(0)

        for curr_level, curr_letter in enumerate(self.document):
            self.__read_letter__(curr_level, curr_letter)
            self.__follow_assignations__(curr_level + 1)
            self.__update_rlevel__(curr_level + 1)
            self.__update_reach__(curr_level, curr_letter)

        # Add Jump from final vertex
        self.dag.finals = []

        for state in self.va.final:
            vertex = (state, len(self.document))

            if vertex in self.dag.vertices:
                self.dag.finals.append(vertex)

    def __read_letter__(self, level, letter):
        for source, _ in self.levelset.vertices[level]:
            for label, target in self.va.adj[source]:
                if isinstance(label, Atom) and label.match(letter):
                    new_node = (target, level + 1)

                    if new_node not in self.dag.vertices:
                        self.dag.add_vertex(new_node)
                        self.levelset.register(new_node, level + 1)
                        self.jl[new_node] = -float('inf')

                    if (source, level) in self.ingoing_assignations:
                        self.jl[new_node] = level
                    else:
                        self.jl[new_node] = max(self.jl[new_node],
                                                self.jl[source, level])

    def __follow_assignations__(self, level):
        '''
        Follow variable assignations inside a level of the DAG.
        '''
        ## Register states accessible by variable assignations
        seen = [False for _ in range(self.va.nb_states)]
        heap = [state for state, _ in self.levelset.vertices[level]]

        for state in heap:
            seen[state] = True

        while heap:
            state = heap.pop()

            for label, target in self.va.adj[state]:
                if isinstance(label, Variable.Marker):
                    self.ingoing_assignations.add((target, level))
                    new_node = (target, level)

                    if not seen[target]:
                        # TODO: remove rendondancy in states infos
                        seen[target] = True
                        heap.append(target)
                        self.dag.add_vertex(new_node)
                        self.levelset.register(new_node, level)

                    self.dag.add_edge((state, level), (label, level),
                                      (target, level))

                    # TODO: check this 'strict' jump correctness (has it
                    # differs slightly from the paper)
                    if new_node not in self.jl:
                        self.jl[new_node] = self.jl[state, level]
                    else:
                        self.jl[new_node] = max(self.jl[new_node],
                                                self.jl[state, level])

    def __update_rlevel__(self, level):
        self.rlevel[level] = {self.jl[vertex]
                              for vertex in self.levelset.vertices[level]}

    def __update_reach__(self, level, letter):
        shape = (len(self.levelset.vertices[level]),
                 len(self.levelset.vertices[level+1]))
        self.reach[level, level+1] = numpy.zeros(shape, dtype=bool)

        for source, _ in self.levelset.vertices[level]:
            for label, target in self.va.adj[source]:
                if isinstance(label, Atom) and label.match(letter):
                    id_source = self.levelset.vertex_index[source, level]
                    id_target = self.levelset.vertex_index[target, level+1]
                    self.reach[level, level+1][id_source, id_target] = True

        for sublevel in self.rlevel[level+1]:
            if sublevel >= level:
                continue

            self.reach[sublevel, level+1] = numpy.dot(
                self.reach[sublevel, level], self.reach[level, level+1])

        if level not in self.rlevel[level+1]:
            del self.reach[level, level+1]

    def jump(self, gamma):
        if gamma == [self.dag.initial]:
            return gamma
        if gamma == ['vf']:
            return self.dag.finals

        i = self.levelset.levels[gamma[0]]
        j = max(self.jl[vertex] for vertex in gamma)

        if i == j:
            return []

        gamma2 = []

        for l, target in enumerate(self.levelset.vertices[j]):
            for source in gamma:
                k = self.levelset.vertex_index[source]

                if self.reach[j, i][l, k]:
                    gamma2.append(target)
                    break

        return gamma2
