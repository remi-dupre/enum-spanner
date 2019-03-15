import numpy

from dag import DAG
from mapping import Variable
from va import VA


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

def max_level(dag):
    return dag.coadj[dag.final][0][1][1] + 1  # TODO: no-yolo

def level(dag, vertex):
    if vertex == dag.final:
        return max_level(dag)

    return vertex[1]

def precompute_levels(dag: DAG) -> list:
    levels = [[] for _ in range(max_level(dag) + 1)]

    for vertex in dag.vertices:
        levels[level(dag, vertex)].append(vertex)

    return [sorted(level) for level in levels]

def precompute_levels_index(dag: DAG) -> dict:
    levels = precompute_levels(dag)
    index_levels = dict()

    for level in levels:
        for index, vertex in enumerate(level):
            index_levels[vertex] = index

    return index_levels

def precompute_JL(dag: DAG) -> dict:
    JL = {vertex: level(dag, dag.final) for vertex in dag.vertices}
    seen = {vertex: False for vertex in dag.vertices}
    seen[dag.final] = True
    stack = [dag.final]

    while stack:
        vertex = stack.pop(0)

        for label, target in dag.coadj[vertex]:
            if label[0] is None:
                JL[target] = min(JL[target], JL[vertex])
            else:
                JL[target] = level(dag, target)

            if not seen[target]:
                stack.append(target)
                seen[target] = True

    return JL

def precompute_Rlevel(dag: DAG) -> list:
    JL = precompute_JL(dag)
    Rlevel = [set() for _ in range(max_level(dag) + 1)]

    for vertex in dag.vertices:
        Rlevel[level(dag, vertex)].add(JL[vertex])

    return Rlevel

def precompute_Reach(dag: DAG) -> dict:
    levels = precompute_levels(dag)
    Rlevel = precompute_Rlevel(dag)
    Reach = dict()

    for i in range(max_level(dag)):
        Reach[i, i+1] = numpy.zeros((len(levels[i]), len(levels[i+1])), dtype=bool)

        for k, vertex_k in enumerate(levels[i]):
            for l, vertex_l in enumerate(levels[i+1]):
                # TODO: double index vertices part of a level
                Reach[i, i+1][k, l] = vertex_l in (
                    x for label, x in dag.adj[vertex_k] if label[0] is None)

    for i in range(max_level(dag), -1, -1):
        for j in Rlevel[i]:
            if j > i + 1:
                Reach[i, j] = numpy.dot(Reach[i, i+1], Reach[i+1, j])

    return Reach

def precompute_jump(dag: DAG):
    levels = precompute_levels(dag)
    levels_index = precompute_levels_index(dag)
    reach = precompute_Reach(dag)
    jl = precompute_JL(dag)

    def jump(gamma):
        i = level(dag, gamma[0])
        j = min(jl[v] for v in gamma)

        if i == j:
            return gamma

        gamma2 = []

        for l, target in enumerate(levels[j]):
            for source in gamma:
                k = levels_index[source]

                if reach[i, j][k, l]:
                    gamma2.append(target)
                    break

        return gamma2

    return jump
