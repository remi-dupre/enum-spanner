from collections import deque

from benchmark import track


def follow_SpSm(adj, gamma: list, Sp: list, Sm: list):
    Sm = set(Sm)
    Sp = set(Sp)
    path_set = {state: set() for state in gamma}
    queue = deque(gamma.copy())

    while queue:
        source = queue.popleft()

        for label, target in adj[source]:
            if label not in Sm:
                if target not in path_set:
                    queue.append(target)

                new_ps = path_set[source].copy()

                if label in Sp:
                    new_ps.add(label)

                # If the state has a failure anotation, we can skip it
                if target in path_set and path_set[target] is None:
                    continue

                # Keep track of the biggest path set for each vertex of the
                # level, if two path have incomparable path sets, we may
                # anotate them with a failure anotation (None)
                if target not in path_set or new_ps >= path_set[target]:
                    path_set[target] = new_ps
                elif not (path_set[target] >= new_ps
                          or path_set[target] <= new_ps):
                    path_set[target] = None

    return [vertex for vertex, ps in path_set.items() if ps == Sp]

@track
def next_level(adj, gamma: list):
    K = set()

    # Get list of variables that are part of the level
    stack = gamma.copy()
    mark = set(gamma)

    while stack:
        source = stack.pop()

        for label, target in adj[source]:
            K.add(label)

            if target not in mark:
                mark.add(target)
                stack.append(target)

    K = list(K)
    stack = [([], [])]

    while stack:
        Sp, Sm = stack.pop()
        gamma2 = follow_SpSm(adj, gamma, Sp, Sm)

        if not gamma2:
            continue

        while len(Sp) + len(Sm) < len(K):
            depth = len(Sp) + len(Sm)
            Sp.append(K[depth])
            gamma2 = follow_SpSm(adj, gamma, Sp, Sm)

            if gamma2:
                new_Sp = Sp.copy()
                new_Sm = Sm.copy()
                new_Sm.append(new_Sp.pop())
                stack.append((new_Sp, new_Sm))
            else:
                Sm.append(Sp.pop())
                gamma2 = None

        if gamma2 is None:
            gamma2 = follow_SpSm(adj, gamma, Sp, Sm)

        Sp = [var for var in Sp]
        yield Sp, gamma2


def enum_dag_mappings(index):
    jump = index.jump
    va = index.va
    document = index.document

    # a stack of pairs (gamma, mapping)
    start = [state for state in va.final]
    stack = [(len(document), start, [])]

    while stack:
        level, gamma, mapping = stack.pop()

        for Sp, new_gamma in next_level(va.get_rev_assignations(), gamma):
            if not new_gamma:
                continue

            new_mapping = mapping.copy()
            new_mapping.extend((marker, level) for marker in Sp)

            if level == 0 and va.initial in new_gamma:
                yield new_mapping
            else:
                new_level, new_gamma = jump(level, new_gamma)
                if new_gamma:
                    stack.append((new_level, new_gamma, new_mapping))
