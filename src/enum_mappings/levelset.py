class LevelSet:
    '''
    Represent the partitioning into levels of a product graph. A same vertex
    can be store in several levels, and this level hierarchy can be accessed
    rather efficiently.
    '''
    def __init__(self):
        # Index level -> vertices list
        self.vertices = dict()
        # Index of a vertex in its level
        self.vertex_index = dict()

    def register(self, vertex, level: int):
        '''
        Save a given vertex in a level, the vertex need to be unique inside
        this level but can be registered in other levels.
        '''
        if level not in self.vertices:
            self.vertices[level] = []
            self.vertex_index[level] = dict()

        if vertex not in self.vertex_index[level]:
            self.vertices[level].append(vertex)
            self.vertex_index[level][vertex] = len(self.vertices[level]) - 1

    def remove_from_level(self, level: int, del_vertices: set):
        '''
        Remove a set of vertices from a level, if the level is left empty, it
        is then removed.
        '''
        new_vertices = []

        for old_vertex in self.vertices[level]:
            if old_vertex not in del_vertices:
                new_vertices.append(old_vertex)
                self.vertex_index[level][old_vertex] = len(new_vertices) - 1
            else:
                del self.vertex_index[level][old_vertex]

        if new_vertices:
            self.vertices[level] = new_vertices
        else:
            del self.vertex_index[level]
            del self.vertices[level]

    def remove_level(self, level: int):
        '''
        Remove all vertices registered in a level, the level is the removed.
        '''
        if level in self.vertices:
            del self.vertices[level]
            del self.vertex_index[level]
