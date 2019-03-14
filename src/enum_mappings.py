def has_outgoing_epsilon(dag, s):
    '''
    Check if an edge in a DAG has an outgoing edge labeled with and
    epsilon-transition
    '''
    for label, _ in dag.adj[s]:
        if label[0] is None:
            return True

    return False

# TODO correctly
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

# TODO: heap instead of recursion
def enum_mappings(dag, gamma, mapping):

    def jump(x):
        return x

    gamma = jump(gamma)

    # Check if final state is reached
    if len(gamma) == 1 and gamma[0] == dag.final:
        yield mapping
    else:
        #  print('NextLevel of', gamma, 'is', list(next_level(dag, gamma)))
        for Sp, gamma2 in next_level(dag, gamma):
            new_mapping = mapping.copy()
            new_mapping.extend(Sp)
            yield from enum_mappings(dag, gamma2, new_mapping)
