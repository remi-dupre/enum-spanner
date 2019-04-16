import numpy

import benchmark
from enum_mappings.levelset import LevelSet


class EmptyLevel(Exception):
    pass


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
        # non-jumpable edge (TODO: it may only be required to store it for the
        # last level)
        self.nonjump_vertices = set()
        # Keep track of number of jumps to a given vertex
        self.count_ingoing_jumps = dict()

        # Register initial layer
        for state in initial_layer:
            self.levelset.register(state, self.last_level)
            self.jl[state, self.last_level] = 0

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
        for source in self.levelset.vertices[last_level]:
            for target in jump_adj[source]:
                if (target, next_level) not in self.jl:
                    self.levelset.register(target, next_level)
                    self.jl[target, next_level] = 0

                if (source, last_level) in self.nonjump_vertices:
                    self.jl[target, next_level] = last_level
                else:
                    self.jl[target, next_level] = max(self.jl[target, next_level],
                                                      self.jl[source, last_level])

        if next_level not in self.levelset.vertices:
            raise EmptyLevel

        # TODO: isn't there a better way of organizing this?
        self.extend_layer(next_level, nonjump_adj)
        self.compute_reach(next_level, jump_adj)
        self.last_level = next_level

    @benchmark.track
    def extend_layer(self, layer, nonjump_adj):
        # Register non-jumpable transitions inside next level
        for source in self.levelset.vertices[layer]:
            for target in nonjump_adj[source]:
                if (target, layer) not in self.jl:
                    self.levelset.register(target, layer)

                self.nonjump_vertices.add((target, layer))

    @benchmark.track
    def compute_reach(self, layer, jump_adj):
        # Update rlevel
        self.rlevel[layer] = {self.jl[vertex, layer]
                              for vertex in self.levelset.vertices[layer]
                              if (vertex, layer) in self.jl}
        self.rev_rlevel[layer] = set()

        for sublevel in self.rlevel[layer]:
            self.rev_rlevel[sublevel].add(layer)

        # Update reach
        prev_layer = layer - 1

        shape = (len(self.levelset.vertices[prev_layer]),
                 len(self.levelset.vertices[layer]))
        self.reach[prev_layer, layer] = numpy.zeros(shape, dtype=bool)

        for source in self.levelset.vertices[prev_layer]:
            for target in jump_adj[source]:
                id_source = self.levelset.vertex_index[prev_layer][source]
                id_target = self.levelset.vertex_index[layer][target]
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
        level to nodes of its sublevel. The vertices given as input shall be
        represented by their index in `self.levelset.vertices[level]`.
        '''
        if vertices is None:
            return numpy.sum(self.reach[sublevel, level], axis=1)

        return numpy.sum(self.reach[sublevel, level][:, vertices], axis=1)

    def clean_layer(self, layer, adj):
        # TODO: doc
        if layer not in self.levelset.vertices:
            return False

        # Run over the level and eliminate all path that are not usefull ie.
        # paths that don't access to a jumpable vertex
        seen = set()
        lvl_vertices = set(self.levelset.vertices[layer])
        del_vertices = set(self.levelset.vertices[layer])

        for start in self.levelset.vertices[layer]:
            if start in seen:
                continue

            heap = [(start, [start])]

            while heap:
                source, path = heap.pop()
                source_id = self.levelset.vertex_index[layer][source]
                seen.add(source)

                # If the path can be identified as usefull, remove it from the
                # set of vertices to delete
                usefull_path = (
                    self.count_ingoing_jumps[layer][source_id] > 0
                    or any(vertex not in del_vertices
                           for vertex in adj[source] if vertex in lvl_vertices))

                if usefull_path:
                    for vertex in path:
                        if vertex in del_vertices:
                            del_vertices.remove(vertex)

                    path = []

                for target in adj[source]:
                    if target in lvl_vertices and target not in seen:
                        assert target in del_vertices
                        target_path = path.copy()
                        target_path.append(target)
                        heap.append((target, target_path))

        if not del_vertices:
            return False

        # Update count of ingoing jump pointers for reachable levels
        removed_columns = [self.levelset.vertex_index[layer][x]
                           for x in del_vertices]

        for uplayer in self.rev_rlevel[layer]:
            self.reach[layer, uplayer] = numpy.delete(
                self.reach[layer, uplayer], removed_columns, axis=0)

        for sublayer in self.rlevel[layer]:
            self.count_ingoing_jumps[sublayer] -= self.count_inbetween_jumps(
                removed_columns, layer, sublayer)

            self.reach[sublayer, layer] = numpy.delete(
                self.reach[sublayer, layer], removed_columns, axis=1)

        # Apply deletion
        self.levelset.remove_from_level(layer, del_vertices)
        self.count_ingoing_jumps[layer] = numpy.delete(
            self.count_ingoing_jumps[layer], removed_columns)

        for vertex in del_vertices:
            if (vertex, layer) in self.jl:
                del self.jl[vertex, layer]

        if layer not in self.levelset.vertices:
            for sublevel in self.rlevel[layer]:
                del self.reach[sublevel, layer]

            for uplayer in self.rev_rlevel[layer]:
                del self.reach[layer, uplayer]
                self.rlevel[uplayer].remove(layer)

            for sublayer in self.rlevel[layer]:
                self.rev_rlevel[sublayer].remove(layer)

            del self.rlevel[layer]
            del self.rev_rlevel[layer]

        return True

    def __call__(self, layer, gamma):
        i = layer
        j = max((self.jl[vertex, layer]
                 for vertex in gamma
                 if (vertex, layer) in self.jl), default=None)

        if j is None:
            return j, []

        if i == j:
            assert i == 0
            return j, []

        gamma2 = []

        for l, target in enumerate(self.levelset.vertices[j]):
            for source in gamma:
                if (source, layer) in self.jl:
                    k = self.levelset.vertex_index[layer][source]

                    if self.reach[j, i][l, k]:
                        gamma2.append(target)
                        break

        return j, gamma2
