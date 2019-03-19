from benchmark import track
from dag import DAG
from enum_mappings.precompute_dag import Jump


def has_outgoing_epsilon(dag, s):
    '''
    Check if an edge in a DAG has an outgoing edge labeled with and
    epsilon-transition.
    '''
    for label, _ in dag.adj[s]:
        if label[0] is None:
            return True

    return False


def follow_SpSm(dag: DAG, gamma: list, Sp: list, Sm: list):
    Sm = set(Sm)
    path_set = {vertex: set() for vertex in gamma}
    queue = gamma.copy()

    while queue:
        source = queue.pop(0)

        for label, target in dag.adj[source]:
            if label[0] is not None and label[0] not in Sm:
                new_ps = path_set[source].copy()

                if label[0] in Sp:
                    new_ps.add(label[0])

                if target not in path_set:
                    path_set[target] = new_ps
                    queue.append(target)
                elif path_set[target] != new_ps:
                    path_set[target] = None

    Sp = set(Sp)
    return [vertex for vertex, ps in path_set.items() if ps == Sp]


def follow_epsilons(dag: DAG, gamma: list):
    gamma2 = set()

    for source in gamma:
        for label, target in dag.adj[source]:
            if label[0] is None:
                gamma2.add(target)

    return list(gamma2)


@track
def next_level(dag: DAG, gamma: list):
    K = set()

    # Get list of variables that are part of the level
    stack = gamma.copy()
    mark = set(gamma)

    while stack:
        source = stack.pop()

        for label, target in dag.adj[source]:
            if label[0] is not None:
                K.add(label[0])

                if target not in mark:
                    mark.add(target)
                    stack.append(target)

    K = list(K)
    stack = [([], [])]

    while stack:
        Sp, Sm = stack.pop()
        gamma2 = follow_epsilons(dag, follow_SpSm(dag, gamma, Sp, Sm))

        if not gamma2:
            continue

        while len(Sp) + len(Sm) < len(K):
            depth = len(Sp) + len(Sm)
            Sp.append(K[depth])
            gamma2 = follow_epsilons(dag, follow_SpSm(dag, gamma, Sp, Sm))

            if gamma2:
                new_Sp = Sp.copy()
                new_Sm = Sm.copy()
                new_Sm.append(new_Sp.pop())
                stack.append((new_Sp, new_Sm))
            else:
                Sm.append(Sp.pop())
                gamma2 = None

        if gamma2 is None:
            gamma2 = follow_epsilons(dag, follow_SpSm(dag, gamma, Sp, Sm))

        # TODO: less dirty level handling
        curr_level = gamma[0][1]
        Sp = [(var, curr_level) for var in Sp]
        yield Sp, gamma2


def enum_dag_mappings(dag: DAG):
    jump = Jump(dag)

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
