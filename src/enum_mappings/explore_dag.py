from benchmark import track


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
