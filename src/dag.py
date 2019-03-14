from va import VA, Variable


class DAG:

    def __init__(self, nb_vertices):
        # Number of vertices in the DAG, they will be identified by indexes
        # starting from 0
        self.nb_vertices = nb_vertices

        # Initial and final vertices are defined as extremums by defaults
        self.initial = 0
        self.final = self.nb_vertices - 1

        # Adjacency list of the DAG as a list of (label, target) or epsilon
        # transition (None, target) for each source vertex
        self.adj = [[] for _ in range(nb_vertices)]

    def run_from(self, source: int):
        '''
        Enumerate accessible states from a given source.
        '''
        accessible = [False for i in range(self.nb_vertices)]
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
        codag = DAG(self.nb_vertices)

        for s in range(self.nb_vertices):
            for label, t in self.adj[s]:
                codag.adj[t].append((label, s))

        return codag.run_from(source)

    def trim(self, states: list):
        '''
        Trim the graph by only keeping states that belong to the input list of
        states. States are arbitrary reindexed.
        '''
        old_states = states
        new_states = {old: new for new, old in enumerate(old_states)}
        n = len(old_states)

        new_adj = [[] for _ in range(n)]

        for s in range(n):
            for a, t_old in self.adj[old_states[s]]:
                if t_old in new_states:
                    new_adj[s].append((a, new_states[t_old]))

        self.nb_vertices = n
        self.initial = 0
        self.final = new_states[self.final]
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

    def __str__(self):
        def label_str(label):
            var, pos = label
            return f'ε({pos})' if var is None else f'{var}({pos})'

        transitions = [(s, label_str(a), t) for s in range(self.nb_vertices)
                       for a, t in self.adj[s]]
        return (f'DAG(nb_vertices={self.nb_vertices}, initial={self.initial}, '
                f'final={self.final}, adj={transitions})')


def product_dag(va: VA, text: str) -> DAG:
    n = len(text)
    vf = (n + 1) * va.nb_states

    def state_of_pair(q, i):
        ret = q * (n + 1) + i
        assert ret < dag.nb_vertices
        return ret

    dag = DAG(vf + 1)
    dag.initial = state_of_pair(0, 0)
    dag.final = vf

    for s, a, t in va.transitions:
        for t_i, t_a in enumerate(text):
            if isinstance(a, Variable.Marker):
                id_s = state_of_pair(s, t_i)
                id_t = state_of_pair(t, t_i)
                label = a, t_i
                dag.adj[id_s].append((label, id_t))
            elif a in ['*', t_a]:
                id_s = state_of_pair(s, t_i)
                id_t = state_of_pair(t, t_i+1)
                label = None, t_i
                dag.adj[id_s].append((label, id_t))

    for s in va.final:
        id_s = state_of_pair(s, n)
        print(id_s)
        dag.adj[id_s].append(((None, n), vf))

    return dag
