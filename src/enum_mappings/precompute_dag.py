import numpy
import tqdm

import benchmark
from atoms import Atom
from dag import DAG, EmptyLangage
from mapping import Variable
from va import VA


class LevelSet:
    '''
    Represent the partitioning into levels of the DAG.
    '''
    def __init__(self):
        # Index vertex -> level
        self.levels = dict()
        # Index level -> vertex
        self.vertices = dict()
        # Index of a vertex in its level
        self.vertex_index = dict()

    def register(self, vertex, level: int):
        if level not in self.vertices:
            self.vertices[level] = []

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


# TODO: It may be relevent to store nodes of a level in a bit mask and to use
#       numpy operations instead
class IndexedDag:
    def __init__(self, va: VA, document: str):
        self.va = va
        self.document = document

        self.dag = DAG()
        self.levelset = LevelSet()
        self.jl = dict()
        self.rlevel = dict()
        self.rev_rlevel = dict()
        self.reach = dict()
        self.ingoing_assignations = set()

        # Pointer counters
        self.count_outgoing_assignations = dict()
        self.count_ingoing_jumps = dict()

        self.__build_dag__()

    def __build_dag__(self):
        # Add initial vertex
        self.dag.initial = (self.va.initial, 0)
        self.__init_vertex__(self.dag.initial, 0)
        self.ingoing_assignations.add(self.dag.initial)

        # Start a level by level run of the DAG
        self.__follow_assignations__(0)
        self.__update_rlevel__(0)

        levels_iter = tqdm.trange(len(self.document),
                                  desc='preprocessing',
                                  unit='B', unit_scale=True,
                                  dynamic_ncols=True)

        for curr_level in levels_iter:
            curr_letter = self.document[curr_level]

            self.__read_letter__(curr_level, curr_letter)

            if curr_level + 1 not in self.levelset.vertices:
                raise EmptyLangage

            self.__follow_assignations__(curr_level + 1)
            self.__update_rlevel__(curr_level + 1)
            self.__update_reach__(curr_level + 1, curr_letter)

            f = lambda x: x & -x  # greater power of 2 that divides x

            for level in range(curr_level-1, curr_level - f(curr_level) - 1, -1):
                if level in self.levelset.vertices:
                    if not self.clean_level(level):
                        pass

            levels_iter.set_postfix({'levels': len(self.levelset.vertices)})

        # Add Jump from final vertex
        self.dag.finals = []

        for state in self.va.final:
            vertex = (state, len(self.document))

            if vertex in self.dag.vertices:
                self.dag.finals.append(vertex)
                self.count_ingoing_jumps[vertex] += 1

    def __init_vertex__(self, vertex, level):
        self.dag.add_vertex(vertex)
        self.levelset.register(vertex, level)
        self.count_outgoing_assignations[vertex] = 0
        self.count_ingoing_jumps[vertex] = 0
        self.jl[vertex] = 0

    def clean_level(self, level):
        # Find out all vertices that need to be deleted
        del_vertices = set()
        heap = [vertex for vertex in self.levelset.vertices[level]
                if (self.count_ingoing_jumps[vertex] == 0
                    and self.count_outgoing_assignations[vertex] == 0)]

        while heap:
            vertex = heap.pop()
            del_vertices.add(vertex)

            for _, target in self.dag.adj[vertex]:
                # TODO: make clearer the fact that no e-transitions are in the
                #       dag
                self.count_outgoing_assignations[target] -= 1

                if (self.count_outgoing_assignations[target] == 0
                        and self.count_ingoing_jumps[target] == 0):
                    heap.append(target)

        if not del_vertices:
            return False

        # Update count of ingoing jump pointers for reachable levels
        removed_columns = [self.levelset.vertex_index[x] for x in del_vertices]

        for uplevel in self.rev_rlevel[level]:
            self.reach[level, uplevel] = numpy.delete(
                self.reach[level, uplevel], removed_columns, axis=0)

        for sublevel in self.rlevel[level]:
            removed_pointers = self.count_inbetween_jumps(
                del_vertices, level, sublevel)

            for i, count in enumerate(removed_pointers):
                subvertex = self.levelset.vertices[sublevel][i]
                self.count_ingoing_jumps[subvertex] -= count

            self.reach[sublevel, level] = numpy.delete(
                self.reach[sublevel, level], removed_columns, axis=1)

        # Apply deletion
        self.levelset.remove_from_level(level, del_vertices)

        for vertex in del_vertices:
            self.dag.remove_vertex(vertex)
            del self.count_outgoing_assignations[vertex]
            del self.count_ingoing_jumps[vertex]
            del self.jl[vertex]

            if vertex in self.ingoing_assignations:
                self.ingoing_assignations.remove(vertex)

        if not self.levelset.vertices[level]:
            del self.levelset.vertices[level]

            for sublevel in self.rlevel[level]:
                del self.reach[sublevel, level]

            for uplevel in self.rev_rlevel[level]:
                del self.reach[level, uplevel]
                self.rlevel[uplevel].remove(level)

            for sublevel in self.rlevel[level]:
                self.rev_rlevel[sublevel].remove(level)

            del self.rlevel[level]
            del self.rev_rlevel[level]

        return True

    def count_inbetween_jumps(self, vertices, level, sublevel):
        '''
        Count the number of jump pointers from a given vertices in a level to
        nodes of its sublevel.
        '''
        if not vertices:
            return [0 for _ in self.levelset.vertices[sublevel]]

        # TODO: it is also used for lists (implement with a for loop)
        del_mask = numpy.array(
            [[vertex in vertices]
              for vertex in self.levelset.vertices[level]], dtype=int)
        update_counts = numpy.dot(self.reach[sublevel, level], del_mask)
        return [count for (count, ) in update_counts]

    def __read_letter__(self, level, letter):
        '''
        Read a letter from a level and create accessed node in next level.
        '''
        for source, _ in self.levelset.vertices[level]:
            for label, target in self.va.adj[source]:
                if isinstance(label, Atom) and label.match(letter):
                    new_node = (target, level + 1)

                    if new_node not in self.dag.vertices:
                        self.__init_vertex__(new_node, level + 1)

                    if (source, level) in self.ingoing_assignations:
                        self.jl[new_node] = level
                    else:
                        self.jl[new_node] = max(self.jl[new_node],
                                                self.jl[source, level])

    def __follow_assignations__(self, level):
        '''
        Follow variable assignations inside a level of the DAG.
        '''
        # Register states accessible by variable assignations
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
                        seen[target] = True
                        heap.append(target)
                        self.__init_vertex__(new_node, level)

                    self.dag.add_edge((target, level), (label, level),
                                      (state, level))
                    self.count_outgoing_assignations[state, level] += 1

                    # TODO: prove this 'strict' jump correctness (has it
                    # differs slightly from the paper)
                    if new_node not in self.jl:
                        self.jl[new_node] = self.jl[state, level]
                    else:
                        self.jl[new_node] = max(self.jl[new_node],
                                                self.jl[state, level])

    def __update_rlevel__(self, level):
        self.rlevel[level] = {self.jl[vertex]
                              for vertex in self.levelset.vertices[level]
                              if self.jl[vertex] < level}

        if level not in self.rev_rlevel:
            self.rev_rlevel[level] = set()

        for sublevel in self.rlevel[level]:
            self.rev_rlevel[sublevel].add(level)

    def __update_reach__(self, level, letter):
        shape = (len(self.levelset.vertices[level-1]),
                 len(self.levelset.vertices[level]))
        self.reach[level-1, level] = numpy.zeros(shape, dtype=bool)

        for source, _ in self.levelset.vertices[level-1]:
            for label, target in self.va.adj[source]:
                if isinstance(label, Atom) and label.match(letter):
                    id_source = self.levelset.vertex_index[source, level-1]
                    id_target = self.levelset.vertex_index[target, level]
                    self.reach[level-1, level][id_source, id_target] = True

        for sublevel in self.rlevel[level]:
            if sublevel >= level-1:
                continue

            self.reach[sublevel, level] = numpy.dot(
                self.reach[sublevel, level-1], self.reach[level-1, level])

        if level-1 not in self.rlevel[level]:
            del self.reach[level-1, level]

        # Update jump counters
        for sublevel in self.rlevel[level]:
            removed_pointers = self.count_inbetween_jumps(
                self.levelset.vertices[level], level, sublevel)

            for i, count in enumerate(removed_pointers):
                subvertex = self.levelset.vertices[sublevel][i]
                self.count_ingoing_jumps[subvertex] += count

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
