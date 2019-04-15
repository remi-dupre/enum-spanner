from functools import lru_cache

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


class Jump:

    def __init__(self, initial_layer, nonjump_adj):
        # Layers in the levelset will be built one by one
        self.levelset = LevelSet()
        self.last_level = 0

        # Closest level where an assignation is done accessible from any node
        self.jl = dict()
        # Set of levels accessible from any level using jl, and reverse of this
        # dictionnary
        self.rlevel = {0: set()}
        self.rev_rlevel = {0: set()}
        # For any pair of level (i, j) such that i in rlevel[j], reach[i, j] is
        # the accessibility of vertices from level i to level j
        self.reach = dict()

        # Set of vertices that can't be jumped since it has an ingoing
        # non-jumpable edge
        self.nonjump_vertices = set()
        # Keep track of number of jumps to a given vertex
        self.count_ingoing_jumps = dict()

        # Register initial layer
        for state in initial_layer:
            self.levelset.register((state, self.last_level), self.last_level)
            self.jl[state, self.last_level] = 0  # TODO: no special case for initial state

        self.extend_layer(0, nonjump_adj)
        self.count_ingoing_jumps[0] = numpy.zeros(
            len(self.levelset.vertices[0]), dtype=int)

    @benchmark.track
    def next_layer(self, jump_adj, nonjump_adj):
        '''
        Compute next level given the adjacency list of jumpable edges from
        current level to the next one and adjacency list of non-jumpable edges
        inside the next level.
        '''
        last_level = self.last_level
        next_level = self.last_level + 1


        # Register jumpable transitions from this level to next one
        for source, _ in self.levelset.vertices[last_level]:
            for target in jump_adj[source]:
                if target not in self.jl:
                    self.levelset.register((target, next_level), next_level)
                    self.jl[target, next_level] = 0

                if (source, last_level) in self.nonjump_vertices:
                    self.jl[target, next_level] = last_level
                else:
                    self.jl[target, next_level] = max(self.jl[target, next_level],
                                                      self.jl[source, last_level])

        if next_level not in self.levelset.vertices:
            raise EmptyLangage

        self.extend_layer(next_level, nonjump_adj)
        self.compute_reach(next_level, jump_adj)
        self.last_level = next_level

    @benchmark.track
    def extend_layer(self, layer, nonjump_adj):
        # Register non-jumpable transitions inside next level
        for source, _ in self.levelset.vertices[layer]:
            for target in nonjump_adj[source]:
                if (target, layer) not in self.jl:
                    self.levelset.register((target, layer), layer)

                self.nonjump_vertices.add((target, layer))

    @benchmark.track
    def compute_reach(self, layer, jump_adj):
        # Update rlevel
        self.rlevel[layer] = {
            self.jl[vertex] for vertex in self.levelset.vertices[layer]
            if vertex in self.jl}
        self.rev_rlevel[layer] = set()

        for sublevel in self.rlevel[layer]:
            self.rev_rlevel[sublevel].add(layer)

        # Update reach
        prev_layer = layer - 1

        shape = (len(self.levelset.vertices[prev_layer]),
                 len(self.levelset.vertices[layer]))
        self.reach[prev_layer, layer] = numpy.zeros(shape, dtype=bool)

        for source, _ in self.levelset.vertices[prev_layer]:
            for target in jump_adj[source]:
                id_source = self.levelset.vertex_index[source, prev_layer]
                id_target = self.levelset.vertex_index[target, layer]
                self.reach[prev_layer, layer][id_source, id_target] = True

        for sublevel in self.rlevel[layer]:
            if sublevel >= prev_layer:
                continue

            self.reach[sublevel, layer] = numpy.dot(
                self.reach[sublevel, prev_layer],
                self.reach[prev_layer, layer])

        if prev_layer not in self.rlevel[layer]:
            del self.reach[prev_layer, layer]

        # Update jump counters
        self.count_ingoing_jumps[layer] = numpy.zeros(
            len(self.levelset.vertices[layer]), dtype=int)

        for sublevel in self.rlevel[layer]:
            self.count_ingoing_jumps[sublevel] += (
                self.count_inbetween_jumps(None, layer, sublevel))

    @benchmark.track
    def count_inbetween_jumps(self, vertices, level, sublevel):
        '''
        Count the number of jump pointers from a given set of vertices in a
        level to nodes of its sublevel.
        '''
        if vertices is None:
            return numpy.sum(self.reach[sublevel, level], axis=1)

        return numpy.sum(self.reach[sublevel, level][:, vertices], axis=1)

    def __call__(self, layer, gamma):
        i = layer
        j = max((self.jl[vertex] for vertex in gamma if vertex in self.jl),
                default=None)

        if j is None:
            return []

        if i == j:
            assert i == 0
            return []

        gamma2 = []

        for l, target in enumerate(self.levelset.vertices[j]):
            for source in gamma:
                if source in self.jl:
                    k = self.levelset.vertex_index[source]

                    if self.reach[j, i][l, k]:
                        gamma2.append(target)
                        break

        return gamma2


# TODO: It may be relevent to store nodes of a level in a bit mask and to use
#       numpy operations instead
class IndexedDag:

    def __init__(self, va: VA, document: str):
        self.va = va
        self.document = document

        self.jump = Jump([self.va.initial], self.va.get_adj_for_assignations())
        levels_iter = tqdm.trange(len(self.document),
                                  desc='preprocessing',
                                  unit='B', unit_scale=True,
                                  dynamic_ncols=True)

        for curr_level in levels_iter:
            curr_letter = self.document[curr_level]
            self.jump.next_layer(self.va.get_adj_for_char(curr_letter),
                                 self.va.get_adj_for_assignations())

    #  def clean_level(self, level):
    #      # Find out all vertices that need to be deleted
    #      del_vertices = set()
    #      heap = [vertex for vertex in self.levelset.vertices[level]
    #              if (self.count_ingoing_jumps[vertex] == 0
    #                  and self.count_outgoing_assignations[vertex] == 0)]
    #
    #      while heap:
    #          vertex = heap.pop()
    #          del_vertices.add(vertex)
    #
    #          for _, target in self.dag.adj[vertex]:
    #              # TODO: make clearer the fact that no e-transitions are in the
    #              #       dag
    #              self.count_outgoing_assignations[target] -= 1
    #
    #              if (self.count_outgoing_assignations[target] == 0
    #                      and self.count_ingoing_jumps[target] == 0):
    #                  heap.append(target)
    #
    #      if not del_vertices:
    #          return False
    #
    #      # Update count of ingoing jump pointers for reachable levels
    #      removed_columns = [self.levelset.vertex_index[x] for x in del_vertices]
    #
    #      for uplevel in self.rev_rlevel[level]:
    #          self.reach[level, uplevel] = numpy.delete(
    #              self.reach[level, uplevel], removed_columns, axis=0)
    #
    #      for sublevel in self.rlevel[level]:
    #          removed_pointers = self.count_inbetween_jumps(
    #              del_vertices, level, sublevel)
    #
    #          for i, count in enumerate(removed_pointers):
    #              subvertex = self.levelset.vertices[sublevel][i]
    #              self.count_ingoing_jumps[subvertex] -= count
    #
    #          self.reach[sublevel, level] = numpy.delete(
    #              self.reach[sublevel, level], removed_columns, axis=1)
    #
    #      # Apply deletion
    #      self.levelset.remove_from_level(level, del_vertices)
    #
    #      for vertex in del_vertices:
    #          self.dag.remove_vertex(vertex)
    #          del self.count_outgoing_assignations[vertex]
    #          del self.count_ingoing_jumps[vertex]
    #          del self.jl[vertex]
    #
    #          if vertex in self.ingoing_assignations:
    #              self.ingoing_assignations.remove(vertex)
    #
    #      if not self.levelset.vertices[level]:
    #          del self.levelset.vertices[level]
    #
    #          for sublevel in self.rlevel[level]:
    #              del self.reach[sublevel, level]
    #
    #          for uplevel in self.rev_rlevel[level]:
    #              del self.reach[level, uplevel]
    #              self.rlevel[uplevel].remove(level)
    #
    #          for sublevel in self.rlevel[level]:
    #            self.rev_rlevel[sublevel].remove(level)
    #
    #        del self.rlevel[level]
    #        del self.rev_rlevel[level]
    #
    #    return True
