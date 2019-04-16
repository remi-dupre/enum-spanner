import numpy

import benchmark
from enum_mappings.levelset import LevelSet


class EmptyLevel(Exception):
    pass


class Jump:
    '''
    Generic Jump function inside a product DAG.

    The DAG will be built layer by layer by specifying the adjacency matrix
    from one level to the next one, an adjancency matrix can specify the
    structure inside of a level, made of 'assignation edges'. The goal of the
    structure is to be able to be able to navigate quickly from the last to the
    first layer by being able to skip any path that do not contain any
    assignation edges.
    '''
    def __init__(self, initial_level, nonjump_adj):
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

        # Register initial level
        for state in initial_level:
            self.levelset.register(state, self.last_level)
            self.jl[state, self.last_level] = 0

        self.extend_level(0, nonjump_adj)
        self.count_ingoing_jumps[0] = numpy.zeros(
            len(self.levelset.vertices[0]), dtype=int)

    @benchmark.track
    def next_level(self, jump_adj, nonjump_adj):
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
        self.extend_level(next_level, nonjump_adj)
        self.compute_reach(next_level, jump_adj)
        self.last_level = next_level

    @benchmark.track
    def extend_level(self, level, nonjump_adj):
        '''
        Extend current level by reading non-jumpable edges inside the given
        level.
        '''
        # Register non-jumpable transitions inside next level
        for source in self.levelset.vertices[level]:
            for target in nonjump_adj[source]:
                if (target, level) not in self.jl:
                    self.levelset.register(target, level)

                self.nonjump_vertices.add((target, level))

    @benchmark.track
    def compute_reach(self, level, jump_adj):
        '''
        Compute reach and rlevel, that is the effective jump points to all
        levels reachable from the current level.
        '''
        # Update rlevel
        self.rlevel[level] = {self.jl[vertex, level]
                              for vertex in self.levelset.vertices[level]
                              if (vertex, level) in self.jl}
        self.rev_rlevel[level] = set()

        for sublevel in self.rlevel[level]:
            self.rev_rlevel[sublevel].add(level)

        # Update reach
        prev_level = level - 1

        shape = (len(self.levelset.vertices[prev_level]),
                 len(self.levelset.vertices[level]))
        self.reach[prev_level, level] = numpy.zeros(shape, dtype=bool)

        for source in self.levelset.vertices[prev_level]:
            for target in jump_adj[source]:
                id_source = self.levelset.vertex_index[prev_level][source]
                id_target = self.levelset.vertex_index[level][target]
                self.reach[prev_level, level][id_source, id_target] = True

        for sublevel in self.rlevel[level]:
            if sublevel >= prev_level:
                continue

            self.reach[sublevel, level] = numpy.dot(
                self.reach[sublevel, prev_level],
                self.reach[prev_level, level])

        if prev_level not in self.rlevel[level]:
            del self.reach[prev_level, level]

        # Update jump counters
        self.count_ingoing_jumps[level] = numpy.zeros(
            len(self.levelset.vertices[level]), dtype=int)

        for sublevel in self.rlevel[level]:
            self.count_ingoing_jumps[sublevel] += (
                self.count_inbetween_jumps(None, level, sublevel))

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

    def clean_level(self, level, adj):
        '''
        Remove all useless nodes inside current level. A useless node is a node
        from which there is no path of assignation to a node which can be
        jumped to.
        '''
        if level not in self.levelset.vertices:
            return False

        # Run over the level and eliminate all path that are not usefull ie.
        # paths that don't access to a jumpable vertex
        seen = set()
        lvl_vertices = set(self.levelset.vertices[level])
        del_vertices = set(self.levelset.vertices[level])

        for start in self.levelset.vertices[level]:
            if start in seen:
                continue

            heap = [(start, [start])]

            while heap:
                source, path = heap.pop()
                source_id = self.levelset.vertex_index[level][source]
                seen.add(source)

                # If the path can be identified as usefull, remove it from the
                # set of vertices to delete
                usefull_path = (
                    self.count_ingoing_jumps[level][source_id] > 0
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
        removed_columns = [self.levelset.vertex_index[level][x]
                           for x in del_vertices]

        for uplevel in self.rev_rlevel[level]:
            self.reach[level, uplevel] = numpy.delete(
                self.reach[level, uplevel], removed_columns, axis=0)

        for sublevel in self.rlevel[level]:
            self.count_ingoing_jumps[sublevel] -= self.count_inbetween_jumps(
                removed_columns, level, sublevel)

            self.reach[sublevel, level] = numpy.delete(
                self.reach[sublevel, level], removed_columns, axis=1)

        # Apply deletion
        self.levelset.remove_from_level(level, del_vertices)
        self.count_ingoing_jumps[level] = numpy.delete(
            self.count_ingoing_jumps[level], removed_columns)

        for vertex in del_vertices:
            if (vertex, level) in self.jl:
                del self.jl[vertex, level]

        if level not in self.levelset.vertices:
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

    def __call__(self, level, gamma):
        '''
        Jump to the next relevel level from vertices in gamma at a given level.
        A relevent level has a node from which there is a path to gamma and
        that has an ingoing assignation.
        '''
        i = level
        j = max((self.jl[vertex, level]
                 for vertex in gamma
                 if (vertex, level) in self.jl), default=None)

        if j is None:
            return j, []

        if i == j:
            assert i == 0
            return j, []

        gamma2 = []

        for l, target in enumerate(self.levelset.vertices[j]):
            for source in gamma:
                if (source, level) in self.jl:
                    k = self.levelset.vertex_index[level][source]

                    if self.reach[j, i][l, k]:
                        gamma2.append(target)
                        break

        return j, gamma2
