from benchmark import track
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

def has_outgoing_epsilon(dag, s):
    '''
    Check if an edge in a DAG has an outgoing edge labeled with and
    epsilon-transition.
    '''
    for label, _ in dag.adj[s]:
        if label[0] is None:
            return True

    return False

# TODO correctly
@track
def next_level(dag, gamma):
    outputs = dict()
    outputs_Sp = dict()
    heap = [(e, []) for e in gamma]

    while heap:
        curr, Sp = heap.pop()

        if has_outgoing_epsilon(dag, curr):
            if str(Sp) not in outputs:
                outputs[str(Sp)] = []
                outputs_Sp[str(Sp)] = Sp

            for label, x in dag.adj[curr]:
                if label[0] is None:
                    outputs[str(Sp)].append(x)

        for label, t in dag.adj[curr]:
            if label[0] is not None:
                new_Sp = Sp.copy()
                new_Sp.append(label)
                heap.append((t, new_Sp))

    for key, gamma2 in outputs.items():
        yield outputs_Sp[key], list(set(gamma2))

def enum_dag_mappings(dag):

    def jump(x):
        return x

    # a stack of pairs (gamma, mapping)
    stack = [([dag.initial], [])]

    while stack:
        gamma, mapping = stack.pop()
        gamma = jump(gamma)

        if len(gamma) == 1 and gamma[0] == dag.final:
            yield mapping
        else:
            for Sp, new_gamma in next_level(dag, gamma):
                new_mapping = mapping.copy()
                new_mapping.extend(Sp)
                stack.append((new_gamma, new_mapping))

def enum_mappings(va: VA, text: str):
    dag = product_dag(va, text)
    dag.remove_useless_nodes()
    yield from enum_dag_mappings(dag)
