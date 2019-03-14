from graphviz import Digraph


class DAG:

    def __init__(self):
        # List of vertices in the DAG, all identified by a unique id
        self.vertices = set()

        # Initial and final vertices are defined as extremums by defaults
        self.initial = None
        self.final = None

        # Adjacency list of the DAG as a list of (label, target) or epsilon
        # transition (None, target) for each source vertex
        self.adj = dict()

    def add_vertex(self, node_id):
        assert node_id not in self.vertices
        self.vertices.add(node_id)
        self.adj[node_id] = list()

    def run_from(self, source):
        '''
        Enumerate accessible states from a given source.
        '''
        accessible = {state: False for state in self.vertices}
        accessible[source] = True
        heap = [source]

        while heap:
            s = heap.pop(0)
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

        for s in self.vertices:
            if s not in codag.vertices:
                codag.add_vertex(s)

            for label, t in self.adj[s]:
                if t not in codag.vertices:
                    codag.add_vertex(t)

                codag.adj[t].append((label, s))

        return codag.run_from(source)

    def trim(self, vertices: list):
        '''
        Trim the graph by only keeping states that belong to the input list of
        states. States are arbitrary reindexed.
        '''
        self.vertices = vertices.copy()
        new_adj = {v: [] for v in self.vertices}

        new_adj.update({
            s: [(label, t) for (label, t) in self.adj[s] if t in vertices]
            for s in vertices
        })
        self.adj = new_adj

    def remove_useless_nodes(self):
        '''
        Remove nodes that are not accessible or not co-accessible, if the
        initial state is not coaccessible or the final state is not accessible,
        the function fails with no predicate on the resulting DAG.
        '''
        accessible = list(self.run_from(self.initial))
        assert self.final in accessible
        self.trim(accessible)

        coaccessible = list(self.corun_from(self.final))
        assert self.initial in coaccessible
        self.trim(coaccessible)

    def view(self):
        dot = Digraph('Example')

        def node_id(node):
            if node in ['vf']:
                return str(node)

            return ','.join(map(str, node))

        def label_str(label):
            if label[0] is None:
                return 'ε'

            return str(label[0])

        for node in self.vertices:
            dot.node(node_id(node))

        for s in self.vertices:
            for label, t in self.adj[s]:
                dot.edge(node_id(s), node_id(t), label_str(label))

        dot.render(view=True)

    def __str__(self):
        def label_str(label):
            var, pos = label
            return f'ε({pos})' if var is None else f'{var}({pos})'

        transitions = [(s, label_str(a), t) for s in self.vertices
                       for a, t in self.adj[s]]
        return (f'DAG(vertices={self.vertices}, initial={self.initial}, '
                f'final={self.final}, adj={transitions})')
