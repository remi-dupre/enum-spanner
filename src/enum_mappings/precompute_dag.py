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
