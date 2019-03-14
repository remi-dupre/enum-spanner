from graphviz import Digraph

from va import VA, Variable


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
        Remove nodes that are not accessible or not co-accessible.
        '''
        accessible = list(self.run_from(self.initial))
        self.trim(accessible)

        coaccessible = list(self.corun_from(self.final))
        self.trim(coaccessible)

    def copy(self):
        pass

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
            elif a in ['*', t_a]:
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
